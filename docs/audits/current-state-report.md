# Current State Audit Report — NegotiationCoach AI

> Classification legend: **Observed** | **Inferred** | **Missing** | **Proposed**
> Audit date: 2026-03-27
> Scope: Full system — frontend (negotiation-buddy) + backend (negotiationcoach-backend) + Supabase

---

## Executive Summary

NegotiationCoach AI is a functioning product in active development. The core negotiation analysis engine (Layer 1: ZOPA, Nash, Monte Carlo) is implemented correctly and produces mathematically sound results. The chat interface and PDF export work end-to-end. Market data enrichment (Layer 2) is live for kmu/profi tiers.

However, the system has accumulated **significant architectural debt** from a frontend-first development history. Key patterns that need attention before scale:

1. **Frontend bypasses the API** for all session, message, team, and profile writes (direct Supabase SDK calls from browser JavaScript with no server-side validation beyond inferred RLS)
2. **Two parallel Layer 1 implementations** exist with incompatible type schemas and no sync mechanism
3. **Auth is not enforced** — Railway backend never issues 401
4. **Team admin authorization is frontend-only** — no server-side enforcement verified
5. **Three incompatible tier definitions** exist across frontend, backend, and Edge Functions

---

## Finding Registry

### Critical

#### CRIT-01: Dual Layer 1 Implementations With Incompatible Schemas
**Classification:** Observed
**Affected:** `negotiationcoach-backend/src/layer1/`, `negotiationcoach-backend/supabase/functions/_shared/engine/`

The ZOPA, Nash Bargaining, Monte Carlo, Deadline Effect, and Strategy Score algorithms exist in two independent implementations. They use different input schemas:

| Field | src/layer1/ | supabase/functions/_shared/engine/ |
|-------|------------|-------------------------------------|
| User target | `own_target` | `user_goal` |
| User minimum | `own_minimum` | `user_walkaway` |
| Opponent max | `opponent_estimated_max` | `counterpart_goal` |
| Opponent min | `opponent_estimated_min` | `counterpart_walkaway` |

Any algorithm change must be applied in both locations. No mechanism enforces this. The two implementations are currently at divergent states (tests reference the Edge Function schema but run against the Express schema — tests are broken).

**Risk:** Silent algorithm divergence. A fix to Nash Bargaining in one implementation is invisible to the other.

---

#### CRIT-02: Team Admin Authorization Frontend-Only
**Classification:** Observed
**Affected:** `negotiation-buddy/src/pages/TeamDashboard.tsx`

All team mutations (create team, add/remove members, assign tasks) are performed via direct Supabase SDK calls from browser JavaScript. The admin check is a React conditional:
```typescript
if (teams.admin_user_id !== user.id) { /* block UI */ }
```

If Supabase RLS on the `teams` and `team_members` tables does not independently enforce `admin_user_id = auth.uid()`, any authenticated user can bypass the UI and call the Supabase SDK directly to perform unauthorized team mutations.

**Verification gap:** RLS policies on `teams`, `team_members`, `team_training_tasks` not verified in this audit. See VG-01.

---

#### CRIT-03: Railway authMiddleware Never Enforces Auth
**Classification:** Observed
**Affected:** `negotiationcoach-backend/src/api/middleware.ts`

The middleware resolves to anonymous/privat on any failure including invalid/expired tokens. No 401 is ever returned. Documented as intentional dev-mode behavior.

```typescript
// src/api/middleware.ts — always calls next(), never rejects
req.user = { id: 'anonymous', tier: 'privat' }; // fallback
next();
```

**Risk:** All Railway endpoints are publicly accessible. Tier gating is the only access control. An anonymous request gets privat-tier access to Layer 1 analysis without authentication.

---

### High

#### HIGH-01: Frontend Direct DB Writes Without API Mediation
**Classification:** Observed
**Affected:** `useSessionManager.ts`, `TeamDashboard.tsx`, `Profile.tsx`

The following tables are written directly from browser JavaScript via the Supabase anon key, without passing through the Railway API:

| Table | Operation | File | Business Logic in Frontend |
|-------|-----------|------|---------------------------|
| `negotiation_sessions` | INSERT, UPDATE | `useSessionManager.ts` | Title truncation (40 chars), mode selection |
| `session_history` | INSERT | `useSessionManager.ts` | Retry logic (2x, 1500ms), count limit (50) |
| `teams` | INSERT | `TeamDashboard.tsx` | Admin assignment |
| `team_members` | INSERT, DELETE | `TeamDashboard.tsx` | Membership logic |
| `team_training_tasks` | INSERT, UPDATE | `TeamDashboard.tsx` | Task assignment |
| `user_profiles` | UPDATE | `Profile.tsx` | Persona sync to localStorage |

**Risk:** Business rules (retry count, message limits, admin checks) live in browser code that can be modified or bypassed. Server-side validation is absent or unverified.

---

#### HIGH-02: Session Message Persistence Fire-and-Forget
**Classification:** Observed
**Affected:** `negotiation-buddy/src/hooks/useSessionManager.ts`

HIGH-02: PARTIALLY RESOLVED 2026-04-03 — Sonner toast now surfaces message
save failure to user after retries exhausted (useSessionManager.ts).
Silent data loss UX gap closed. Write path still fire-and-forget —
full resolution deferred to RFB-004 (Railway session message API).

---

#### HIGH-03: Incompatible Tier Systems
**Classification:** Observed
**Affected:** System-wide

Three distinct tier representations:

| Location | Values | Purpose |
|----------|--------|---------|
| Railway backend (src/types/index.ts) | `free \| privat \| kmu \| profi` | Feature gating, model routing |
| Supabase DB persona_type enum | `pro \| kmu \| private` | User UI mode |
| Edge Function chat persona | `"free"` (hardcoded) | Tier signaling to Edge Function |

The frontend `persona_type` (pro/kmu/private) has no defined mapping to Railway `Tier` (free/privat/kmu/profi). The Edge Function always receives `"free"` regardless of the user's actual subscription. Market data, model routing, and feature gating behave differently depending on which path the request takes.

---

### Medium

#### MED-01: modelRouter Bypassed in High-Traffic Endpoints
**Classification:** Observed
**Affected:** `negotiationcoach-backend/src/api/routes.ts`, `chatHelpers.ts`, `planHelpers.ts`
**Status:** Fixed — resolved in commit 60848db (rfb-011). Both /api/chat and /api/plan now use selectModel() with tier-aware routing.

`modelRouter.ts` provides tier-aware model selection with cost optimization (haiku for free tier, sonnet for standard, opus for profi). However:
- `/api/chat` hardcodes `claude-haiku-4-5-20251001`
- `/api/plan` hardcodes `claude-sonnet-4-6`

These are the two highest-traffic endpoints. Profi users do not get upgraded models for chat/plan. Free users do not get haiku degradation for plan generation.

---

#### MED-02: CORS Wildcard Overrides Allowlist
**Classification:** Observed
**Affected:** `negotiationcoach-backend/src/api/routes.ts`
**Status: Fixed** — resolved in commit e00e400 (rfb-005). Wildcard middleware removed. Single cors() mechanism now enforces allowlist.

A wildcard CORS header is set before the CORS middleware:
```typescript
res.header('Access-Control-Allow-Origin', '*');
// then: app.use(cors({ origin: ALLOWED_ORIGINS }))
```

The wildcard takes precedence. The allowlist (localhost:8080, localhost:5173, *.lovable.app, *.lovableproject.com) has no effect. Any origin can make cross-origin requests to the Railway API.

---

#### MED-03: localStorage State Without TTL, Versioning, or Size Limit
**Classification:** Resolved 2026-04-03

MED-03: RESOLVED 2026-04-03 — localStorage versioning and TTL added to
AnalysisContext.tsx. STORAGE_VERSION=2 clears stale state on schema change.
STORAGE_TTL=7 days clears expired sessions on load.
knowledge_candidates accumulation remains open — tracked as RFB-016.

---

#### MED-04: Token Fetching Duplicated in 6 Frontend Files
**Classification:** Observed
**Affected:** `useSessionManager.ts`, `NegotiationCanvas.tsx`, `DebriefDashboard.tsx`, and 3 inferred locations

```typescript
// Pattern repeated 6× across frontend:
const { data: { session } } = await supabase.auth.getSession();
const token = session?.access_token;
```

No `getToken()` accessor exists in `useAuth.tsx`. Any change to token acquisition (e.g., refresh handling) must be applied in 6 places.

---

#### MED-05: webSearch.ts Does Not Call External APIs
**Classification:** Observed
**Affected:** `negotiationcoach-backend/src/layer2/webSearch.ts`

The function is named `searchMarketData` and conceptually described as web search. In reality it uses Claude's training-data knowledge via a structured `tool_use` call. No external web search API (Serper, Bing, Brave, Tavily, etc.) is integrated. Market data reflects Claude's training cutoff, not current market conditions. This gap is marked in CLAUDE.md as a future Stufe 2 feature.

---

### Low

#### LOW-01: Knowledge Candidate Pipeline Broken
**Classification:** Observed
**Affected:** `negotiation-buddy/src/hooks/useChat.ts`, `knowledge_queue` table

Edge Function `/chat` emits `[KNOWLEDGE_CANDIDATE]` tags. Frontend extracts them and writes to `localStorage.knowledge_candidates`. No UI exists to review or submit these candidates to the `knowledge_queue` table. The extraction infrastructure is complete; the submission path is missing.

---

#### LOW-02: Dual Toast Systems
**Classification:** Observed
**Affected:** `negotiation-buddy`

Both Radix `useToast` and Sonner `toast` are installed and used inconsistently across components.

---

#### LOW-03: Index.tsx God Component
**Classification:** Resolved (Phase 1) — 2026-04-08
Index.tsx von 931 auf 870 Zeilen reduziert. CoachHeader, ChatProgressBar,
buildPlanData extrahiert. Hook-Extraktion (useGuidedFlow, useProgressEngine)
offen als RFB-020b / RFB-020c.

---

#### LOW-04: Broken Test Suite
**Classification:** Resolved
**Affected:** `negotiationcoach-backend/tests/layer1/`, `tests/layer2/`

~~Tests reference `user_goal / user_walkaway / counterpart_goal / counterpart_walkaway` (Edge Function schema).~~ Schema aligned in RFB-022 (`ccc4460`). Runner wired in RFB-027 (`0665780`) — `npm test` now invokes ts-node directly. Live execution requires `SUPABASE_SERVICE_KEY` + `ANTHROPIC_API_KEY` env vars. Tests contain no assertions (execution-proof only) — correctness coverage remains a gap.

---

#### LOW-05: Zod Installed But Unused
**Classification:** Observed
**Affected:** `negotiationcoach-backend/package.json`

`zod: ^4.3.6` is installed. All input validation is manual (explicit field checks in batnaDetector, chatHelpers). No schema validation at API entry points.

---

## Historical Frontend-First Workarounds

These patterns appear to be artifacts of a Lovable-generated frontend that was built before the Railway backend existed:

| Pattern | Location | Recommended Retirement |
|---------|----------|----------------------|
| Direct `negotiation_sessions` writes from `useSessionManager.ts` | Frontend hook | Move to Railway `POST /api/sessions` endpoint |
| Direct `session_history` writes from `useSessionManager.ts` | Frontend hook | Move to Railway `POST /api/sessions/:id/messages` endpoint |
| Team CRUD via direct Supabase SDK | `TeamDashboard.tsx` | Move to Railway team management endpoints |
| Business rules (title truncation, message limit, retry logic) in frontend hooks | `useSessionManager.ts` | Move to server |
| persona_type enum separate from tier system | DB schema + frontend | Unify under single tier contract |

---

## Verification Gaps (Items Requiring Manual Review)

| ID | Question | Risk Level |
|----|----------|-----------|
| VG-01 | Do Supabase RLS policies on `teams` and `team_members` enforce `admin_user_id = auth.uid()`? | Critical |
| VG-02 | Does Supabase RLS on `negotiation_sessions` prevent cross-user access when anon_key is used? | High |
| VG-03 | Where does the Stripe webhook update `user_metadata.tier`? Is this active? | High |
| VG-04 | What creates the initial `user_profiles` row on signup (trigger, function, or frontend)? | Medium |
| VG-05 | ~~Does the Edge Function `/chat` actually enforce tier via JWT or receive only the hardcoded "free"?~~ **RESOLVED 2026-04-09** — `subscription_tier` IS read from request body (`index.ts:82`) and injected into system prompt as plain text only. No model selection, no feature gating, no branching. Model hardcoded to `google/gemini-3-flash-preview` for all tiers. No JWT auth at all. Tier is decorative metadata. RFB-009 scope must expand to include Edge Function enforcement. | ~~Medium~~ Closed |
| VG-05-A | Edge Function `/chat` has no authentication — no JWT validation, no `supabase.auth.getUser()`, any caller with `LOVABLE_API_KEY` can invoke it | High | Observed 2026-04-09 |
| VG-06 | Is Edge Function `generate-plan` active, or has Railway `/api/plan` replaced it? | Low |

---

## Prioritized Action List

| Priority | Action | Effort | Risk If Deferred |
|----------|--------|--------|-----------------|
| P0 | Verify + harden Supabase RLS on teams tables (CRIT-02) | Low | Data breach |
| P0 | Enforce auth in Railway authMiddleware (CRIT-03) | Low | Open API |
| P1 | Unify dual Layer 1 implementations or retire Edge Function negotiate/ (CRIT-01) | High | Algorithm drift |
| P1 | Move session/message persistence to Railway API (HIGH-01) | Medium | Business logic in browser |
| P1 | Unify tier system across frontend, backend, Edge Functions (HIGH-03) | Medium | Inconsistent feature gating |
| P2 | Integrate modelRouter into /api/chat and /api/plan (MED-01) | Low | Cost overruns, wrong model per tier |
| P2 | Fix CORS configuration (MED-02) | Low | Security exposure |
| P2 | Add localStorage TTL and versioning (MED-03) | Low | Stale state corruption |
| P3 | Centralize token accessor in useAuth.tsx (MED-04) | Low | Maintenance burden |
| P3 | Fix broken test suite (LOW-04) | Medium | No regression coverage |
| P3 | Implement knowledge submission pipeline or remove infrastructure (LOW-01) | Low | Dead localStorage accumulation |
