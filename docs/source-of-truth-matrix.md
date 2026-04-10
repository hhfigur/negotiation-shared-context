# Source of Truth Matrix — NegotiationCoach AI

> Classification legend: **Observed** | **Inferred** | **Missing** | **Proposed**
> Last audit: 2026-03-27

This matrix identifies the canonical owner and access rules for every core entity and capability in the system.

---

## Entities

### 1. User Identity / Session Token

| Property | Value |
|----------|-------|
| Canonical Owner | Supabase Auth |
| Primary Datastore | Supabase Auth internal schema |
| Write Path | `supabase.auth.signUp()` / `signIn()` → JWT issued by Supabase |
| Read Path | Frontend: `useAuth().user` via `onAuthStateChange`; Railway: `auth.getUser(token)` in middleware |
| Sync Rule | JWT stored in browser localStorage by Supabase JS; Railway validates on each request |
| Business Logic Owner | Supabase (issuance) + Railway authMiddleware (validation) |
| Auth Owner | Supabase Auth |
| Violations | Railway never rejects invalid tokens (dev mode). Token fetched in 6 different frontend files. |

---

### 2. Subscription Tier

| Property | Value |
|----------|-------|
| Canonical Owner | Supabase JWT metadata — **Inferred** |
| Primary Datastore | `user_metadata.tier` or `app_metadata.tier` on Supabase JWT |
| Write Path | **CONFIRMED ABSENT** — No Stripe webhook handler exists in either repo. `stripe` npm package not installed. `app_metadata.tier` is never written post-signup. Tier is immutable after account creation. Implementation registered as RFB-032 (DEFERRED — pre-billing). |
| Read Path | Railway: `user.user_metadata.tier \|\| user.app_metadata.tier` in `authMiddleware.ts`; defaults to `'free'` (changed from `'privat'` — AUTH-08, 2026-04-03) |
| Sync Rule | Read fresh from JWT on each Railway request. No caching. |
| Business Logic Owner | Railway `authMiddleware` + `modelRouter.ts` |
| Auth Owner | Stripe (billing) → Supabase (stored) |
| Violations | Three incompatible tier schemas: `free/privat/kmu/profi` (Railway), `pro/kmu/private` (Supabase persona_type enum), `"free"` hardcoded in Edge Function chat persona |

---

### 3. Negotiation Session Record

| Property | Value |
|----------|-------|
| Canonical Owner | Railway backend |
| Primary Datastore | `negotiation_sessions` table (Supabase PostgreSQL) |
| Write Path (create) | Railway `POST /api/sessions` → `negotiation_sessions` INSERT with SERVICE_ROLE_KEY — **Phase A DONE (RFB-004)** |
| Write Path (analyze) | Railway `POST /api/analyze` / `POST /api/analyze-full` → `negotiation_sessions` INSERT (analysis columns) |
| Write Path (update) | Railway `PATCH /api/sessions/:id` → `.update()` with SERVICE_ROLE_KEY — **Phase A DONE** |
| Write Path (enrich) | Railway `POST /api/enrich` → `.update({layer2_result})` with SERVICE_ROLE_KEY |
| Write Path (frontend) | **RETIRED** — `useSessionManager.ts` now calls `POST /api/sessions` + `PATCH /api/sessions/:id` via `apiClient.ts` — since `2415f72` (2026-04-08) |
| Read Path | Railway `GET /api/sessions/:id` (owner-scoped) or `useSessionManager.ts` direct select |
| Sync Rule | AnalysisContext (localStorage) mirrors in-session result. DB write is synchronous via Railway API since Phase B. |
| Business Logic Owner | Railway `sessionRoutes.ts` — title truncation (40 chars), session ownership, status management |
| Auth Owner | Railway: `assertSessionOwner()` + `.eq('user_id', req.user.id)` code-enforced. RLS pre-existing: `user_sees_own_sessions` policy (FOR ALL, USING auth.uid() = user_id). Verified 2026-04-09. |
| Violations | None — Phase B complete `2415f72`. |

> **Phase B DONE:** `useSessionManager.ts` migrated 2026-04-08 (`2415f72`). Canonical writer: Railway `POST /api/sessions` + `PATCH /api/sessions/:id`.

---

### 4. Session History (Messages)

> **TABLE NAME CORRECTION (RFB-030, 2026-04-09):** Previously documented as `session_messages`. Live DB confirms actual table name is `session_history`. TypeScript call sites fixed in RFB-031 (`2c51cb4`, 2026-04-09).

| Property | Value |
|----------|-------|
| Canonical Owner | Railway API (`src/api/sessionRoutes.ts`) — **Phase A DONE (RFB-004)** — RFB-031 closed `2c51cb4` |
| Primary Datastore | `session_history` table |
| Write Path | Railway `POST /api/sessions/:id/messages` → INSERT into `session_history` with SERVICE_ROLE_KEY — **Phase A DONE (RFB-031 closed `2c51cb4`)** |
| Write Path (frontend) | **RETIRED** — `useSessionManager.ts` now calls `POST /api/sessions/:id/messages` via `apiClient.ts` — since `2415f72` (2026-04-08) |
| Read Path | `useSessionManager.ts` → direct select, last 50 messages |
| Sync Rule | In-session: `AnalysisContext.messages[]`; Persisted: `session_history` table. Write acknowledged synchronously via Railway API since Phase B. |
| Business Logic Owner | Railway `sessionRoutes.ts` — 50-message limit enforced server-side via count-before-insert (non-atomic — DB constraint pending RFB-004-C) |
| Auth Owner | Supabase RLS: `user_sees_own_session_history` policy (FOR ALL, transitive ownership via `negotiation_sessions.user_id`). Verified pre-existing 2026-04-09. |
| Violations | None — Phase B complete `2415f72`. `session_history` table origin untracked — no CREATE TABLE migration file in repo. |

> **Phase B DONE:** `useSessionManager.ts` migrated 2026-04-08 (`2415f72`). Canonical writer: Railway `POST /api/sessions/:id/messages`.

---

### 5. Negotiation Analysis Result (Layer 1)

| Property | Value |
|----------|-------|
| Canonical Owner | Railway backend (Layer 1) |
| Primary Datastore | `negotiation_sessions.layer1_result` (JSONB column) |
| Write Path | Railway → `POST /api/analyze` → compute → store in negotiation_sessions |
| Read Path | `GET /api/sessions/:id` → layer1_result; also held in `AnalysisContext` in-session |
| Sync Rule | Computed on-demand. Stored once. Not invalidated unless re-analyzed. |
| Business Logic Owner | `src/layer1/` (zopaCalculator, nashBargaining, monteCarlo, deadlineEffect, strategyScore, batnaDetector) |
| Auth Owner | Railway authMiddleware + user_id validation |
| Violations | **CRITICAL:** Algorithms duplicated verbatim in `supabase/functions/_shared/engine/`. The two implementations use different type schemas and may diverge. |

---

### 6. Market Intelligence / Enrichment Result (Layer 2)

| Property | Value |
|----------|-------|
| Canonical Owner | Railway backend (Layer 2) |
| Primary Datastore | `knowledge_graph` table (cache, 7-day TTL) + `negotiation_sessions.layer2_result` |
| Write Path | Railway Layer 2 → Claude tool_use call → `knowledge_graph` INSERT → `negotiation_sessions` UPDATE |
| Read Path | Railway → `knowledge_graph` SELECT (cache hit) or fresh generation |
| Sync Rule | Cache-first, 7-day TTL. No explicit invalidation. |
| Business Logic Owner | `src/layer2/` (marketDataResolver, webSearch, realityScore, knowledgeGraph) |
| Auth Owner | Implicit tier gate in `layer2/index.ts` (privat/free skip enrichment) + explicit `requireTier('kmu')` on `/api/enrich` |
| Violations | "webSearch" does not call external APIs — uses Claude training data. Naming is misleading. No real web search integration exists. |

---

### 7. User Profile & Preferences

| Property | Value |
|----------|-------|
| Canonical Owner | Supabase DB (`user_profiles` table) |
| Primary Datastore | `user_profiles` + `localStorage` (mirrored) |
| Write Path | `Profile.tsx` → `supabase.from('user_profiles').update()` → localStorage sync |
| Read Path | `Profile.tsx` → Supabase select on mount; some reads from localStorage |
| Sync Rule | DB is written first, then localStorage is synced. No conflict resolution. |
| Business Logic Owner | Frontend `Profile.tsx` |
| Auth Owner | Supabase RLS (inferred) |
| Violations | Initial profile creation mechanism is missing (no INSERT observed). persona_type enum (pro/kmu/private) does not align with Railway tier system (free/privat/kmu/profi). |

---

### 8. Team Structure

| Property | Value |
|----------|-------|
| Canonical Owner | Supabase DB (`teams`, `team_members`, `team_training_tasks`) |
| Primary Datastore | Supabase PostgreSQL |
| Write Path | `TeamDashboard.tsx` → direct `supabase.from('teams').insert()/update()/delete()` — **no Railway API** |
| Read Path | `TeamDashboard.tsx` → direct Supabase select |
| Sync Rule | Read on mount, no real-time subscription observed |
| Business Logic Owner | Frontend only |
| Auth Owner | **CRITICAL GAP:** Frontend check `admin_user_id === user.id` — RLS enforcement unverified |
| Violations | All team operations are direct-from-browser DB writes. No server-side admin validation confirmed. |

---

### 9. Model Routing / LLM Cost Control

| Property | Value |
|----------|-------|
| Canonical Owner | Railway backend (`src/utils/modelRouter.ts`) |
| Primary Datastore | `negotiation_sessions` columns: `task_type`, `model_used`, `model_degraded` |
| Write Path | Railway routes → `modelRouter.selectModel(task, tier)` → logged to negotiation_sessions |
| Read Path | `getRoutingOverview(tier)` debug helper |
| Sync Rule | Stateless per-request decision |
| Business Logic Owner | `modelRouter.ts` |
| Auth Owner | N/A (internal routing) |
| Violations | `/api/chat` and `/api/plan` hardcode models (haiku and sonnet respectively) and do NOT call `modelRouter`. Cost optimization and tier-based degradation is bypassed for the two highest-traffic endpoints. |

---

### 10. PDF Export

| Property | Value |
|----------|-------|
| Canonical Owner | Frontend (`src/utils/exportPlanPdf.ts`) |
| Primary Datastore | None — generated on demand, not stored |
| Write Path | Frontend → `planHtmlTemplate.ts` → `window.print()` |
| Read Path | N/A |
| Sync Rule | N/A |
| Business Logic Owner | Frontend |
| Auth Owner | None (print dialog) |
| Violations | None for current scope. |

---

## Verification Gaps

| Gap ID | What Needs Verification | Risk |
|--------|--------------------------|------|
| VG-01 | ~~Supabase RLS policies on `teams` and `team_members` — do they enforce `admin_user_id = auth.uid()`?~~ **RESOLVED** — 10 snake_case policies applied via migration `20260403120000` (negotiation-buddy). Admin enforcement verified at DB level. | ~~Critical~~ |
| ~~VG-02~~ | ~~Supabase RLS on `negotiation_sessions`~~ **RESOLVED 2026-04-09** — `user_sees_own_sessions` policy confirmed pre-existing. No conflict: SERVICE_ROLE_KEY bypasses RLS for Railway writes; `assertSessionOwner()` is defence-in-depth. | ~~High~~ |
| VG-03 | ~~Stripe webhook handler — how is `user_metadata.tier` updated on subscription change?~~ — **RESOLVED 2026-04-09:** Confirmed absent. No handler, no stripe package. RFB-032 registered (DEFERRED). | ~~High~~ Closed |
| VG-04 | Profile creation on sign-up — what creates the initial `user_profiles` row? | Medium |
| VG-05 | Edge Function `/chat` tier enforcement — **RESOLVED 2026-04-09** — `subscription_tier` IS read from request body (`index.ts:82`) and injected into system prompt as plain text only (`Abo-Stufe: ${value}`). No model selection, no feature gating, no branching on tier value. No JWT auth at all — function accepts any request. Tier is decorative metadata. Consequence: RFB-009 (fix `useChat.ts`) alone has no functional effect — Edge Function logic must also enforce tier server-side. New finding: VG-05-A (no JWT auth, severity High). | ~~Medium~~ Closed |
| VG-06 | Edge Function `generate-plan` — is this actively used, or has Railway `/api/plan` superseded it? | Low |
| VG-07 | **RESOLVED 2026-04-09 — ADR-004 accepted:** Edge Function `/functions/v1/chat` remains canonical chat path for all tiers. Tier enforcement added inside EF via JWT read (`supabase.auth.getUser()`). Railway `/api/chat` retained for structured extraction only. |
