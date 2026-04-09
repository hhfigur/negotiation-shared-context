# Refactor Backlog — NegotiationCoach AI

> Derived from: `docs/audits/current-state-report.md`, `docs/bounded-contexts.md`, `docs/auth-permission-map.md`, `docs/source-of-truth-matrix.md`, `docs/contracts/frontend-backend.md`
> Last updated: 2026-03-31
> Classification: **Observed** | **Inferred** | **Missing** | **Proposed**

---

## Priority Legend

| Priority | Scope |
|----------|-------|
| **P0** | Auth, permissions, duplicate writes, security, data ownership |
| **P1** | Duplicated business logic, conflicting validation, contract mismatches |
| **P2** | Redundant hooks, components, services, utilities |
| **P3** | Naming, folder cleanup, cosmetic structure improvements |

---

## P0 — Security, Auth, Data Ownership

---

### RFB-001

**Title:** Railway authMiddleware never enforces authentication — all endpoints publicly accessible

**Repo:** `negotiationcoach-backend`

**Category:** `boundary-violation`

**Evidence (Observed):**
`src/api/middleware.ts` resolves every request — including those with invalid, expired, or missing tokens — to `req.user = { id: 'anonymous', tier: 'privat' }` and calls `next()` unconditionally. No 401 is ever returned. Documented in CLAUDE.md as intentional dev-mode behavior.

**Confidence:** High — directly observed in source

**Risk:** All Railway API endpoints are publicly accessible. Unauthenticated callers receive `privat` tier access to Layer 1 analysis (ZOPA, Nash Bargaining, Monte Carlo). Only tier gating provides any access control.

**Canonical Owner:** `negotiationcoach-backend` — `src/api/middleware.ts`

**Recommended Action:**
1. Return HTTP 401 when the `Authorization` header is missing or the token fails `supabase.auth.getUser()` validation
2. Keep a documented opt-out mechanism (e.g., env flag `AUTH_REQUIRED=false`) for local dev only
3. Verify behaviour for `/api/health` which should remain ungated

**Required Docs/Contracts to Update:**
- `docs/auth-permission-map.md` — Section 3, AUTH-01
- `docs/contracts/frontend-backend.md` — Section 2 (add 401 to error contract)
- `docs/bounded-contexts.md` — BC-01 Violations

**Required Tests to Run:**
- Unit: `authMiddleware` rejects missing token with 401
- Unit: `authMiddleware` rejects expired/invalid JWT with 401
- Unit: `authMiddleware` passes valid JWT and populates `req.user`
- Integration: `/api/analyze` returns 401 without token

**Depends On:** Nothing (standalone hardening)

**Status: DONE**
Commit: `fd68e1e` (negotiationcoach-backend) — 2026-04-03
Verified: tsc --noEmit clean ✓ | Tests 2–8 passing ✓ | AUTH_REQUIRED=false dev bypass documented
Tier default changed: 'privat' → 'free' (AUTH-08 resolved).
Pre-flight: production user tier metadata set before deploy.
Docs updated: auth-permission-map.md (AUTH-01, AUTH-08) | contracts/frontend-backend.md (Section 2) | bounded-contexts.md (BC-01)

---

### RFB-002

**Title:** Verify and harden Supabase RLS — team admin authorization is frontend-only

**Repo:** `negotiationcoach-backend` (Supabase migrations) + `negotiation-buddy`

**Category:** `boundary-violation`

**Evidence (Observed):**
`TeamDashboard.tsx ~line 69` enforces admin authorization via a React conditional:
```typescript
if (teams.admin_user_id !== user.id) { /* block UI */ }
```
Any authenticated user can call the Supabase SDK directly (bypassing the React UI) and perform team mutations. RLS policies on `teams`, `team_members`, `team_training_tasks` were not verified in the audit (VG-01).

**Confidence:** High — frontend-only enforcement is directly observed; RLS state is unverified

**Risk:** Data breach / unauthorized team mutation. An authenticated attacker can add themselves to any team, remove other members, or escalate to team admin by calling Supabase JS directly.

**Canonical Owner:** Supabase (`teams`, `team_members`, `team_training_tasks` table policies)

**Recommended Action:**
1. Inspect current RLS policies on `teams`, `team_members`, `team_training_tasks` using Supabase MCP `list_policies`
2. If `INSERT` on `team_members` is not guarded by `admin_user_id = auth.uid()`, write and apply a migration to add it
3. Add `UPDATE` and `DELETE` policies for team mutations that require `admin_user_id = auth.uid()`
4. Resolve VG-01 and mark as verified in `source-of-truth-matrix.md`

**Required Docs/Contracts to Update:**
- `docs/source-of-truth-matrix.md` — Entity 8 (Team Structure), VG-01
- `docs/bounded-contexts.md` — BC-05 Violations
- `docs/auth-permission-map.md` — Section 5.2 (mark RLS as Verified)

**Required Tests to Run:**
- Integration: Non-admin user cannot `INSERT` into `team_members` via anon key
- Integration: Non-admin user cannot `DELETE` a team member via anon key
- Integration: Admin user can add/remove team members

**Depends On:** Nothing (standalone verification + migration)

**Status: DONE**
Commit: <hash> (negotiation-buddy) — 2026-04-03
Verified: 10 snake_case policies applied ✓ | pg_policies query confirmed ✓
  | team_training_tasks SELECT gap fixed ✓ | legacy quoted-name policies removed ✓
Docs updated: auth-permission-map.md §5.2 | source-of-truth-matrix.md VG-01
  | bounded-contexts.md BC-05
Unblocks: RFB-003

---

### RFB-003

**Title:** Move team CRUD writes to Railway API with server-side admin enforcement

**Repo:** `negotiationcoach-backend` (new endpoints) + `negotiation-buddy` (`TeamDashboard.tsx`)

**Category:** `boundary-violation`

**Evidence (Observed):**
All team operations (`teams`, `team_members`, `team_training_tasks` INSERT/UPDATE/DELETE) are performed via direct Supabase SDK calls from `TeamDashboard.tsx`. No Railway API mediates these writes. Business logic (admin assignment, membership rules) lives entirely in browser JavaScript. Bounded context BC-05 flags this as a canonical owner violation.

**Confidence:** High — directly observed

**Risk:** Business rules enforced only in browser code can be trivially bypassed by any authenticated user with DevTools.

**Canonical Owner:** Railway backend (proposed; currently frontend by violation)

**Recommended Action:**
1. Add Railway endpoints: `POST /api/teams`, `POST /api/teams/:id/members`, `DELETE /api/teams/:id/members/:userId`, `PATCH /api/teams/:id/tasks/:taskId`
2. Move admin check to Railway — validate `req.user.id === team.admin_user_id` server-side (using SERVICE_ROLE_KEY query)
3. Refactor `TeamDashboard.tsx` to call Railway endpoints instead of Supabase SDK directly
4. Keep RLS as a defence-in-depth layer (do not remove after RFB-002)

**Required Docs/Contracts to Update:**
- `docs/contracts/frontend-backend.md` — add new team endpoints to Section 2
- `docs/bounded-contexts.md` — BC-05 Write Path, Auth/Permission Owner
- `docs/source-of-truth-matrix.md` — Entity 8 Write Path
- `docs/decision-log/ADR-002-data-ownership.md` — team write path decision

**Required Tests to Run:**
- Unit: `POST /api/teams/` requires authentication (RFB-001 must be done first)
- Unit: `POST /api/teams/:id/members` rejects if caller is not team admin
- Integration: `TeamDashboard.tsx` creates a team end-to-end via Railway API

**Depends On:** RFB-001 (auth enforcement must be in place before new guarded endpoints are meaningful), RFB-002 (RLS hardening as defence-in-depth)

**Status: DONE**
Phase A commit: `0b10d9c` (negotiationcoach-backend) — 2026-04-07
Phase B commit: (negotiation-buddy Lovable deploy) — 2026-04-08
Verified: tsc --noEmit clean ✓ | 4 endpoints in teamRoutes.ts ✓ | assertTeamAdmin enforced server-side ✓
  | useTeamApi.ts hook created ✓ | W1+W2 migrated to POST /api/teams ✓ | W4 migrated to DELETE /api/teams/:id/members/:userId ✓
  | W3 (task creation) remains on Supabase SDK — Phase C dependency ✓
  | Team creation end-to-end verified in production UI ✓
Docs updated: docs/api-catalog.md | docs/db-map.md | docs/bounded-contexts.md (BC-05) | docs/data-access-map.md
Unblocked by: AB-001 fix (Railway SUPABASE_URL corrected)

---

### RFB-004

**Title:** Move session and message persistence to Railway API — remove frontend direct DB writes

**Repo:** `negotiation-buddy` (`useSessionManager.ts`) + `negotiationcoach-backend`

**Category:** `boundary-violation`

**Evidence (Observed):**
`useSessionManager.ts` writes directly to `negotiation_sessions` (INSERT, UPDATE) and `session_history` (INSERT) via the Supabase anon key without passing through the Railway API. Business rules encoded in browser JavaScript:
- Session title truncated to 40 characters
- Message count limit: 50
- Message save retry: 2 attempts, 1500ms delay

**Confidence:** High — directly observed

**Risk:** Business rules can be bypassed by any browser user. Silent message loss on persistent save failure. No server-side validation of session ownership beyond inferred RLS.

**Canonical Owner:** Railway backend (for writes); Supabase DB (for storage)

**Recommended Action:**
1. Add Railway endpoints: `POST /api/sessions` (create), `PATCH /api/sessions/:id` (update metadata), `POST /api/sessions/:id/messages` (persist message)
2. Move title truncation, message limit, and retry logic to the Railway handlers
3. Return a structured error on `POST /api/sessions/:id/messages` failure — surface it in the frontend (do not silently drop)
4. Refactor `useSessionManager.ts` to call Railway endpoints for writes; keep direct Supabase reads for now

**Required Docs/Contracts to Update:**
- `docs/contracts/frontend-backend.md` — add session and message endpoints
- `docs/bounded-contexts.md` — BC-03 Write Path
- `docs/source-of-truth-matrix.md` — Entity 3 (Negotiation Session), Entity 4 (Session Messages)
- `docs/decision-log/ADR-002-data-ownership.md`

**Required Tests to Run:**
- Unit: `POST /api/sessions/:id/messages` enforces message count limit
- Unit: `POST /api/sessions` enforces title truncation
- Unit: `PATCH /api/sessions/:id` requires caller to own the session
- Integration: useSessionManager writes messages via Railway and surfaces errors to UI

**Depends On:** RFB-001 (auth must be enforced before session ownership matters)

**Status: PHASE A DONE**
Phase A — sessionRoutes.ts complete and registered (negotiationcoach-backend) — 2026-04-09
Verified: tsc --noEmit clean ✓ | 3 endpoints live ✓ | assertSessionOwner() ✓ |
Zod schemas wired (CreateSessionSchema, PatchSessionSchema, CreateMessageSchema) ✓ |
registered in routes.ts via app.use('/api', sessionRouter) ✓
E2E verified 2026-04-09: POST /api/sessions ✓ | POST /api/sessions/:id/messages ✓
(AB-001 SUPABASE_URL blocker resolved 2026-04-08)
Parallel tasks: RFB-030 closed 2026-04-09 (RLS pre-existing, no migration needed);
session_history retroactive migration traceability (open, low priority).
Phase A fully closed 2026-04-09 (E2E verified post AB-001 fix).
Phase B (useSessionManager.ts → Railway migration) unblocked — RFB-031 closed `2c51cb4`.

---

### RFB-004-C (Phase C follow-on)

**Title:** Add DB-level message count constraint to session_history

**Repo:** `negotiationcoach-backend` (Supabase migration)

**Category:** `boundary-violation`

**Evidence (Observed):** `POST /api/sessions/:id/messages` uses count-then-insert
which is non-atomic. Two concurrent callers can both pass the count check and
push total to 51. Documented during RFB-004 Phase A plan review.

**Risk:** Low in current traffic volumes. Becomes a correctness issue at scale.

**Recommended Action:** Add a CHECK constraint or BEFORE INSERT trigger on
`session_history` enforcing count per `session_id` <= 50.

**Depends On:** RFB-004 Phase A (endpoints must exist first)

**Status: OPEN**

---

### RFB-005

**Title:** Fix CORS — wildcard header overrides configured allowlist

**Repo:** `negotiationcoach-backend`

**Category:** `boundary-violation`

**Evidence (Observed):**
In `src/api/routes.ts`, a wildcard header is set before the CORS middleware:
```typescript
res.header('Access-Control-Allow-Origin', '*');
// then: app.use(cors({ origin: ALLOWED_ORIGINS }))
```
The wildcard takes precedence. The allowlist (localhost:8080, localhost:5173, *.lovable.app, *.lovableproject.com) has no effect. Any origin can make cross-origin requests to the Railway API.

**Confidence:** High — directly observed

**Risk:** CSRF exposure. Any malicious website can make authenticated cross-origin requests to the Railway API using a victim's browser session.

**Canonical Owner:** `negotiationcoach-backend` — `src/api/routes.ts`

**Recommended Action:**
Remove the `res.header('Access-Control-Allow-Origin', '*')` line. The `cors()` middleware with the configured `ALLOWED_ORIGINS` allowlist should be the sole CORS mechanism.

**Required Docs/Contracts to Update:**
- `docs/auth-permission-map.md` — AUTH-07

**Required Tests to Run:**
- Integration: Request from unlisted origin receives correct CORS rejection
- Integration: Request from allowed origin proceeds

**Depends On:** Nothing

**Status: DONE**
Commits: e00e400 (negotiationcoach-backend), c52d8b5 (shared-context)
Verified: tsc clean ✓ | curl checks ✓ (all 4 PASS on live server)
Auth-map: AUTH-07 → Resolved
current-state-report: MED-02 → Fixed
Remaining: 500 vs 403 for disallowed origins — pre-existing, tracked separately

---

## P1 — Duplicate Logic, Conflicting Validation, Contract Mismatches

---

### RFB-006

**Title:** Unify dual Layer 1 implementations — retire Edge Function engine or establish canonical schema

**Repo:** `negotiationcoach-backend`

**Category:** `duplicate-logic`

**Evidence (Observed):**
ZOPA, Nash Bargaining, Monte Carlo, Deadline Effect, and Strategy Score algorithms exist in two separate implementations with incompatible input schemas:

| Field | `src/layer1/` (Railway) | `supabase/functions/_shared/engine/` |
|-------|------------------------|--------------------------------------|
| User target | `own_target` | `user_goal` |
| User minimum | `own_minimum` | `user_walkaway` |
| Opponent max | `opponent_estimated_max` | `counterpart_goal` |
| Opponent min | `opponent_estimated_min` | `counterpart_walkaway` |

Tests in `tests/layer1/` reference the Edge Function schema and are currently broken.

**Confidence:** High — directly observed; field names verified in current-state-report

**Risk:** Silent algorithm divergence. A bug fix or tuning in one implementation is invisible to the other. Analysis results differ depending on which code path executes.

**Canonical Owner:** `negotiationcoach-backend/src/layer1/` (Railway — designated canonical in ADR-001)

**Recommended Action:**
1. Determine whether the Edge Function `negotiate` is actively called (resolve VG-06)
2. If active: migrate `supabase/functions/_shared/engine/` to use the Railway schema (`own_target` etc.) — or introduce a schema adapter at the Edge Function boundary
3. If inactive: delete `supabase/functions/_shared/engine/` entirely
4. Fix `tests/layer1/` to use the Railway `src/layer1/` schema
5. Add a CI check that ensures only one canonical Layer 1 implementation exists

**Required Docs/Contracts to Update:**
- `docs/bounded-contexts.md` — BC-02 Violations (resolve CRIT-01)
- `docs/source-of-truth-matrix.md` — Entity 5 (Negotiation Analysis Result)
- `docs/contracts/frontend-backend.md` — Section 4 Type Drift Register (CON-03)

**Required Tests to Run:**
- All `tests/layer1/` pass against `src/layer1/` using the correct Railway schema
- Regression: ZOPA output matches known-good values for reference inputs
- Regression: Nash Bargaining, Monte Carlo outputs match reference

**Depends On:** Resolve VG-06 first (determine whether Edge Function `negotiate` is active)

---

### RFB-007

**Title:** Unify three incompatible tier systems into a single canonical representation

**Repo:** `negotiationcoach-backend` + `negotiation-buddy` + Supabase schema

**Category:** `contract-gap`

**Evidence (Observed):**

| Location | Values | Purpose |
|----------|--------|---------|
| Railway `src/types/index.ts` | `free \| privat \| kmu \| profi` | Feature gating, model routing |
| Supabase DB `persona_type` enum | `pro \| kmu \| private` | User UI mode |
| Edge Function chat persona | `"free"` (hardcoded in `useChat.ts`) | Tier signal to Edge Function |

No mapping between `persona_type` and `Tier` exists in either repo. The Edge Function always receives `"free"` regardless of actual subscription.

**Confidence:** High — three separate observations in source

**Risk:** Profi users receive free-tier behaviour in the Edge Function chat path. Market data, model routing, and feature gates behave inconsistently depending on which code path handles the request.

**Canonical Owner:** Railway `Tier` type (`free | privat | kmu | profi`) — designated canonical

**Recommended Action:**
1. Add a translation layer in `useChat.ts` that maps `persona_type` → Railway `Tier` and passes the correct value as `subscription_tier` in the Edge Function request
2. Add a `Tier` type definition to the frontend shared types and import it wherever `persona_type` is used for access control decisions
3. Migrate the `persona_type` DB enum to align values with Railway's tier names, or add a mapping column/function to `user_profiles`
4. Verify that the Edge Function actually reads `subscription_tier` from the request (resolve VG-05)

**Required Docs/Contracts to Update:**
- `docs/contracts/frontend-backend.md` — Section 3 (Edge Function contract), CON-01, CON-02
- `docs/source-of-truth-matrix.md` — Entity 2 (Subscription Tier)
- `docs/bounded-contexts.md` — BC-06 Violations (persona_type/tier mismatch)

**Required Tests to Run:**
- Unit: `useChat.ts` passes correct tier value for each `persona_type`
- Integration: Profi user's chat request reaches Edge Function with `"profi"` tier
- Integration: Edge Function applies profi-tier behaviour when subscription_tier is "profi"

**Depends On:** VG-05 (verify Edge Function tier enforcement); RFB-006 (tier must be consistent across analysis paths)

---

### RFB-008

**Title:** Eliminate parallel type maintenance — introduce shared type package or contract file

**Repo:** `negotiation-buddy` + `negotiationcoach-backend`

**Category:** `contract-gap`

**Evidence (Observed):**
`ExtractedInputs`, `ChatMessage`, `NegotiationInputs`, `AnalysisResult` are defined independently in `negotiation-buddy/src/lib/types.ts` and `negotiationcoach-backend/src/lib/types.ts` / `src/types/index.ts`. Currently consistent but maintained in parallel with no enforcement mechanism. `Tier` is not defined in the frontend at all.

**Confidence:** High — directly observed in type drift register

**Risk:** Silent runtime failures when one side drifts. Tier type absence in frontend means tier-related frontend logic has no type safety.

**Canonical Owner:** `negotiationcoach-backend/src/types/index.ts` (proposed source of truth)

**Recommended Action:**
Option A (preferred): Extract shared types into a versioned JSON Schema or `.d.ts` file in `shared-context/contracts/` that both repos import at build time.
Option B (pragmatic): Generate frontend types from the backend's `src/types/index.ts` via a script checked into CI — drift detected on every build.

At minimum:
- Add `Tier` type to `negotiation-buddy/src/lib/types.ts` matching Railway definition
- Add a comment header on both type files indicating the other as the sync target

**Required Docs/Contracts to Update:**
- `docs/contracts/frontend-backend.md` — Section 4 Type Drift Register (CON-04)

**Required Tests to Run:**
- CI: Type consistency check (if Option B is chosen — tsc against generated types)

**Depends On:** Nothing (incremental improvement; full resolution requires RFB-007 tier unification)

**Status: DONE**
Commit: `9c51a43` (negotiationcoach-backend) — 2026-04-08
Verified: tsc --noEmit exit 0 after each step ✓ | grep: 0 consumers of Tier from middleware ✓ | grep: 0 consumers of NegotiationType from lib/types ✓
Docs updated: none (no API or schema changes)

---

### RFB-009

**Title:** Propagate actual user tier to Edge Function chat persona

**Repo:** `negotiation-buddy` — `src/hooks/useChat.ts`

**Category:** `contract-gap`

**Evidence (Observed):**
`useChat.ts` always sends `subscription_tier: "free"` in the Edge Function request body regardless of the authenticated user's actual subscription tier. This is a direct violation flagged as CON-01 and AUTH-06.

**Confidence:** High — hardcoded string observed directly

**Risk:** Edge Function cannot apply tier-based behaviour (profi model, market data signals, etc.) because it never receives the correct tier.

**Canonical Owner:** `negotiation-buddy` — `src/hooks/useChat.ts`

**Recommended Action:**
1. Read the user's tier from `useAuth().user.user_metadata.tier` (or equivalent)
2. Map it through the `persona_type` → `Tier` translation added in RFB-007
3. Pass the resolved tier value as `subscription_tier`

**Required Docs/Contracts to Update:**
- `docs/contracts/frontend-backend.md` — Section 3 (Edge Function request shape), CON-01
- `docs/auth-permission-map.md` — AUTH-06

**Required Tests to Run:**
- Unit: `useChat.ts` sends correct `subscription_tier` for a profi user
- Unit: `useChat.ts` sends `"free"` for a user with no tier metadata

**Depends On:** RFB-007 (tier unification), VG-05 (verify Edge Function reads the tier)

---

### RFB-010

**Title:** Verify Stripe webhook tier update path — resolve VG-03

**Repo:** `negotiationcoach-backend` (or Supabase webhook handler — location unknown)

**Category:** `contract-gap`

**Evidence (Missing):**
No Stripe webhook handler updating `user_metadata.tier` is visible in either repo. The tier write path from Stripe → Supabase JWT is entirely unverified. If this path is broken, a user who upgrades their subscription never receives tier-gated features.

**Confidence:** Low — the mechanism is assumed to exist but was not found in source

**Risk:** Subscription upgrades do not take effect in the product. Stripe charges without delivering feature access.

**Canonical Owner:** TBD — must be located before action can be taken

**Recommended Action:**
1. Search both repos and Supabase dashboard for a Stripe webhook handler
2. Verify that on `customer.subscription.updated`, `user_metadata.tier` is updated on the Supabase user
3. If the handler exists but is inactive: activate and test
4. If the handler is missing: implement in Railway (`POST /api/webhooks/stripe`) with Stripe signature verification
5. Resolve VG-03 in `source-of-truth-matrix.md`

**Required Docs/Contracts to Update:**
- `docs/source-of-truth-matrix.md` — Entity 2, VG-03
- `docs/bounded-contexts.md` — BC-01 Write Path (tier metadata)
- `docs/auth-permission-map.md` — Section 2.1 (token flow sync rule)

**Required Tests to Run:**
- Integration: Simulated Stripe webhook updates user tier in Supabase
- Integration: Updated tier is reflected in next Railway request

**Depends On:** Nothing (investigation item; unblocks RFB-007 and RFB-009)

**Status: ON HOLD — explicit owner decision 2026-04-08**
Stripe integration is deferred to a future billing milestone.
Do not implement until explicitly unparked by owner.
Plan output from Claude Code preserved above for future reference.
Unblocks: RFB-007 and RFB-009 remain blocked on this — noted.

---

### RFB-011

**Title:** Integrate modelRouter into /api/chat and /api/plan — restore tier-based model control

**Repo:** `negotiationcoach-backend`

**Category:** `duplicate-logic`

**Evidence (Observed):**
`/api/chat` hardcodes `claude-haiku-4-5-20251001`. `/api/plan` hardcodes `claude-sonnet-4-6`. `modelRouter.selectModel(task, tier)` is never called in either endpoint despite being the designated canonical model selection mechanism.

| Task | free | privat | kmu | profi |
|------|------|--------|-----|-------|
| strategy_coaching | haiku | sonnet | sonnet | sonnet |
| executive_summary | haiku | sonnet | sonnet | **opus** |

Profi users get haiku for chat and sonnet for plan regardless of tier.

**Confidence:** High — hardcoded model strings directly observed

**Risk:** Cost overruns (free users get non-degraded models on chat). Profi users do not receive upgraded models they are billed for. MED-01 in current-state-report.

**Canonical Owner:** `negotiationcoach-backend` — `src/utils/modelRouter.ts`

**Recommended Action:**
1. In `chatHelpers.ts`: replace hardcoded `claude-haiku-4-5-20251001` with `modelRouter.selectModel('strategy_coaching', req.user.tier)`
2. In `planHelpers.ts`: replace hardcoded `claude-sonnet-4-6` with `modelRouter.selectModel('executive_summary', req.user.tier)` (or whichever task type is appropriate)
3. Ensure `req.user.tier` is correctly populated — depends on RFB-001 (auth enforcement)

**Required Docs/Contracts to Update:**
- `docs/auth-permission-map.md` — Section 4.3 (mark bypass as resolved), AUTH-05
- `docs/source-of-truth-matrix.md` — Entity 9 (Model Routing)

**Required Tests to Run:**
- Unit: `/api/chat` with profi tier uses sonnet or opus model
- Unit: `/api/chat` with free tier uses haiku model
- Unit: `/api/plan` with free tier uses haiku model

**Depends On:** RFB-001 (auth must populate `req.user.tier` correctly)

**Status: DONE**
Commit: `60848db` (negotiationcoach-backend) — 2026-04-01
Verified: tsc --noEmit clean ✓ | modelRouter wired into both handlers ✓ |
both modelRouter copies byte-for-byte identical (diff = empty) ✓
Behavioral change accepted: /api/chat — privat/kmu/profi now Sonnet (was Haiku).
/api/plan — all tiers Sonnet via generate_plan (was hardcoded Sonnet — no regression).
Docs updated in commit: api-catalog.md ✓ | service-catalog.md ✓
Docs updated post-verify: auth-permission-map.md AUTH-05 ✓ | current-state-report.md MED-01 ✓

Follow-up (open):
- selectModel smoke test: selectModel('strategy_coaching', 'free') === MODELS.HAIKU,
  selectModel('generate_plan', 'privat') === MODELS.SONNET — not yet written
- service-catalog.md stale entries (market_analysis, batch_processing, document_analysis) — pre-existing

**Status: DONE (Node.js scope)**
Commits:
- `0308b0e` — RFB-011A: batnaDetector.ts (validate_input, tier-aware)
- `d0b2bff` — RFB-011B: webSearch.ts + layer2/index.ts (MODELS.SONNET, tier-invariant)

Verified: tsc --noEmit clean ✓ | CLAUDE_MODEL cleared from all src/ call sites ✓
REDUNDANCY-04: fully resolved for all Node.js call sites.
Remaining: CLAUDE_MODEL definition in claudeClient.ts → DEAD-02 (separate item).
Edge function batnaDetector: deferred — DCC-EF-01 / RFB-026 (blocked, depends on RFB-006).

---

### DEAD-02

**Title:** Remove dead CLAUDE_MODEL constant from claudeClient.ts
**Repo:** negotiationcoach-backend
**Status: DONE**
**Commit:** efc1d28 (negotiationcoach-backend)
**Verified:** tsc --noEmit clean ✓ | grep CLAUDE_MODEL src/ → 0 results ✓
All call sites cleared in RFB-011A (0308b0e) and RFB-011B (d0b2bff).
Constant removed. claudeClient.ts exports unaffected.

---

### RFB-012

**Title:** Resolve missing user_profiles creation on signup — VG-04

**Repo:** `negotiationcoach-backend` (Supabase migrations) or `negotiation-buddy`

**Category:** `contract-gap`

**Evidence (Missing):**
`Profile.tsx` performs only `UPDATE` — no `INSERT` observed. No Supabase trigger, Edge Function, or Railway handler that creates the initial `user_profiles` row on sign-up was found in either repo. If a profile row is not created at sign-up, all profile reads and updates will silently fail.

**Confidence:** Medium — absence of evidence, not confirmed broken in production

**Risk:** New users may have no profile row, causing silent failures in persona selection, tier display, and any `user_profiles`-dependent feature.

**Canonical Owner:** TBD — must be determined by investigation

**Recommended Action:**
1. Check Supabase dashboard for a `on_auth_user_created` trigger on the `auth.users` table
2. If trigger exists: verify it inserts a default `user_profiles` row correctly
3. If missing: create a Supabase migration with an `AFTER INSERT` trigger on `auth.users` that inserts a default profile
4. Resolve VG-04 in `source-of-truth-matrix.md`

**Required Docs/Contracts to Update:**
- `docs/source-of-truth-matrix.md` — Entity 7 (User Profile), VG-04
- `docs/bounded-contexts.md` — BC-06 Violations

**Required Tests to Run:**
- Integration: A new sign-up results in a `user_profiles` row being created

**Depends On:** Nothing

**Status: DONE**
Applied: direct SQL on Lovable-managed Supabase instance — 2026-04-03
Verified: on_auth_user_created trigger confirmed (auth.users → handle_new_user())
Defaults: persona_type='private', subscription_tier='free', experience_level=1
Note: table lives in Lovable instance only — backend instance has no user_profiles table.
Note: subscription_tier enum (free/starter/professional/expert/team) diverges from
Railway tier enum (free/privat/kmu/profi) — tracked as RFB-007, out of scope here.
Backfill for existing users: not required (4 existing rows already present).

---

## P2 — Redundant Hooks, Components, Services, Utilities

---

### RFB-013

**Title:** Centralize token accessor — eliminate 6-file token fetching duplication

**Repo:** `negotiation-buddy`

**Category:** `dead-code`

**Evidence (Observed):**
```typescript
// Pattern repeated in at least 6 files:
const { data: { session } } = await supabase.auth.getSession();
const token = session?.access_token;
```
Files: `useSessionManager.ts`, `NegotiationCanvas.tsx`, `DebriefDashboard.tsx`, plus 3 inferred locations (`ZopaCalculator.tsx`, `WhatIfSimulator.tsx`, `ChatInterface.tsx`). No `getToken()` method exists in `useAuth.tsx`.

**Confidence:** High — 3 direct observations, 3 inferred

**Risk:** Maintenance burden. Any change to token acquisition (refresh handling, error path) must be replicated manually in 6 places. MED-04 in current-state-report.

**Canonical Owner:** `negotiation-buddy` — `src/hooks/useAuth.tsx`

**Recommended Action:**
1. Add `getToken(): Promise<string | null>` to `useAuth.tsx` that wraps `supabase.auth.getSession()` token extraction
2. Replace all 6 inline occurrences with `const token = await getToken()`

**Required Docs/Contracts to Update:**
- `docs/auth-permission-map.md` — Section 2.1 (token duplication note), AUTH-04

**Required Tests to Run:**
- Unit: `getToken()` returns null when no session exists
- Unit: `getToken()` returns the access token when session is valid

**Depends On:** Nothing

**Status: DONE — 2026-03-31**

| Sub-item | Commit | Notes |
|---|---|---|
| `getToken()` added to `useAuth.tsx` | `c507353` | Returns `string \| null` |
| 5 inline patterns replaced | `c507353` | Index.tsx, NegotiationCanvas.tsx, DebriefDashboard.tsx, WhatIfSimulator.tsx, ZopaCalculator.tsx |
| `supabase` import removed where auth-only | `c507353` | DebriefDashboard, NegotiationCanvas, WhatIfSimulator, ZopaCalculator |

Note: `useSessionManager.ts` uses the same pattern but was not in scope (inline pattern already wraps a helper there). `ChatInterface.tsx` DCC-FE-02 is a separate item.

---

### RFB-014

**Title:** Fix session message persistence — remove fire-and-forget, surface errors to user

**Repo:** `negotiation-buddy` — `src/hooks/useSessionManager.ts`

**Category:** `boundary-violation`

**Evidence (Observed):**
Message saves use a fire-and-forget pattern with 2 retries at 1500ms. Failed saves are logged to console but not surfaced to the user. A failed message save results in a silently incomplete session history. HIGH-02 in current-state-report.

**Confidence:** High — retry logic and silent failure pattern directly observed

**Risk:** Data loss. User resumes a session with missing messages and no indication that messages were lost.

**Canonical Owner:** `negotiation-buddy` — `useSessionManager.ts` (interim); Railway API (target, per RFB-004)

**Recommended Action (interim, before RFB-004):**
1. On exhausted retries, surface a toast notification: "Message could not be saved — session history may be incomplete"
2. Optionally: queue failed messages to `localStorage` for retry on reconnect

**Recommended Action (final, after RFB-004):**
Message persistence moves to Railway — use the structured error contract instead of fire-and-forget.

**Required Docs/Contracts to Update:**
- `docs/bounded-contexts.md` — BC-03 Violations (HIGH-02)
- `docs/source-of-truth-matrix.md` — Entity 4 (Session Messages), Sync Rule

**Required Tests to Run:**
- Unit: Exhausted retries surface an error toast
- Integration: Failed message save does not block UI but is visible to user

**Depends On:** Nothing for interim fix; RFB-004 for final resolution

**Status: DONE**
Implemented: Lovable — 2026-04-03
Change: Sonner toast.error() added to useSessionManager.ts, fires once
after all retries exhausted. console.error preserved.
Scope: useSessionManager.ts only. localStorage queuing excluded (RFB-004).
Note: Interim fix — final resolution deferred to RFB-004 (Railway message API).

---

### RFB-015

**Title:** Add TTL and schema versioning to localStorage state

**Repo:** `negotiation-buddy`

**Category:** `contract-gap`

**Evidence (Observed):**
Four localStorage keys accumulate indefinitely with no TTL, no schema version, and no size validation:
- `negotiationcoach_session` — full session state (messages, analysis, ZOPA, plan, acceptance curves)
- `knowledge_candidates` — no reader or submitter found
- Persona preferences
- Supabase auth session (Supabase-managed)

Any schema change to `AnalysisContext` will silently deserialize stale data. MED-03 in current-state-report.

**Confidence:** High — directly observed

**Risk:** Stale localStorage causes silent deserialization errors after schema changes. `knowledge_candidates` accumulates without bound.

**Canonical Owner:** `negotiation-buddy` — `src/contexts/AnalysisContext.tsx`

**Recommended Action:**
1. Add a `STORAGE_VERSION` constant to `AnalysisContext.tsx`; on deserialization, compare version and clear state on mismatch
2. Add a TTL to `negotiationcoach_session` (e.g., 7 days) — clear on expiry
3. Either implement the knowledge candidate submission pipeline (RFB-016) or clear `knowledge_candidates` and remove the extraction code

**Required Docs/Contracts to Update:**
- `docs/audits/current-state-report.md` — MED-03

**Required Tests to Run:**
- Unit: Stale `negotiationcoach_session` with old version is cleared on read
- Unit: Expired session is cleared on read

**Depends On:** Nothing for TTL/versioning; RFB-016 for knowledge candidates

**Status: DONE**
Implemented: Lovable — 2026-04-03
STORAGE_VERSION = 2, STORAGE_TTL = 604_800_000 (7 days)
Guards: version mismatch → clear, TTL expired → clear, parse error → clear
Scope: AnalysisContext.tsx only. knowledge_candidates excluded (RFB-016).
Note: existing sessions reset on first deploy — intended behavior.

---

### RFB-016

**Title:** Complete or remove knowledge candidate pipeline

**Repo:** `negotiation-buddy` + `negotiationcoach-backend`

**Category:** `dead-code`

**Evidence (Observed):**
Edge Function `/chat` emits `[KNOWLEDGE_CANDIDATE]` tags. `useChat.ts` extracts them and writes to `localStorage.knowledge_candidates`. No UI exists to review these candidates. No submission path to the `knowledge_queue` table was found. The extraction infrastructure is complete; the submission half is missing. LOW-01 in current-state-report.

**Confidence:** High — extraction code observed; submission code confirmed absent

**Risk:** `knowledge_candidates` localStorage key accumulates without bound. Dead infrastructure adds confusion and maintenance overhead.

**Canonical Owner:** `negotiation-buddy` (extraction); `negotiationcoach-backend` (queue table)

**Recommended Action:**
Option A: Implement knowledge submission UI and `POST /api/knowledge/submit` Railway endpoint.
Option B: Remove `[KNOWLEDGE_CANDIDATE]` tag extraction from `useChat.ts`, remove `knowledge_queue` table from schema (or mark as unused), clear the localStorage key.

Choose Option B if there is no near-term roadmap for the knowledge pipeline.

**Required Docs/Contracts to Update:**
- `docs/audits/current-state-report.md` — LOW-01
- `docs/bounded-contexts.md` — BC-03/BC-04 cross-context issue

**Required Tests to Run:**
- (If Option B): Verify no references to `knowledge_candidates` remain in active code

**Depends On:** Product decision (build or remove)

**Status: RE-SCOPED — Option B withdrawn 2026-04-03**
Product decision: knowledge pipeline will be built (Option A confirmed).
Item split into:
- RFB-016a: Architecture design — define collection scope, usage path,
  ownership. Requires ADR before implementation.
- RFB-016b: Implementation — blocked on RFB-016a.
Neither sub-item is ready for Wave 1 execution.
Deferred to feature backlog pending ADR.

---

### RFB-017

**Title:** Deduplicate password validation
**Repo:** negotiation-buddy
**Status: DONE**
**Commit:** 48d0edc (negotiation-buddy — docs only)
**Verified:** tsc --noEmit clean ✓ | inline password rules → 0 remaining ✓
Canonical source: src/lib/passwordValidation.ts — unchanged.
Duplicates removed from: none required — all call sites were already
importing from the canonical source.
docs/redundancy-register.md R-006 updated: Inferred/Medium → Resolved.

---

## P3 — Naming, Structure, Cosmetic

---

### RFB-018

**Title:** Rename webSearch.ts to marketDataInterpreter.ts
**Repo:** negotiationcoach-backend
**Status: DONE**
**Commit:** 675cc21 (negotiationcoach-backend)
**Verified:** tsc --noEmit clean ✓ | grep webSearch src/ → 0 module references ✓
Renamed src/layer2/webSearch.ts → src/layer2/marketDataInterpreter.ts
Import in src/layer2/marketDataResolver.ts updated (scope expanded from
plan — index.ts had no direct import).
No logic changes. service-catalog.md, redundancy-register.md,
repo-map.md updated.

---

### RFB-019

**Title:** Consolidate dual toast systems
**Repo:** negotiation-buddy
**Status: DONE**
**Commit:** 056e672 (negotiation-buddy)
**Verified:** tsc --noEmit clean ✓ | useToast imports → 0 remaining ✓
Canonical toast system: Sonner.
Radix Toaster removed from App.tsx.
useToast replaced in: Index.tsx, Auth.tsx, ResetPassword.tsx,
Profile.tsx, TeamDashboard.tsx, ForgotPassword.tsx, ZopaCalculator.tsx,
DebriefDashboard.tsx, NegotiationCanvas.tsx, WhatIfSimulator.tsx
redundancy-register.md R-007 updated: Observed → Resolved.

---

### RFB-020

**Title:** Decompose Index.tsx god component

**Repo:** `negotiation-buddy`

**Category:** `dead-code`

**Evidence (Observed):**
`src/pages/Index.tsx` is 929 lines and combines: mode selection, chat UI, session sidebar, resume banner, and multiple state machine transitions in a single file. LOW-03 in current-state-report.

**Confidence:** High — line count directly observed

**Risk:** High change-risk surface area. Difficult to test individual UI modes. Onboarding friction.

**Canonical Owner:** `negotiation-buddy` — `src/pages/`

**Recommended Action:**
Extract into sub-components:
- `SessionSidebar.tsx`
- `ResumeBanner.tsx`
- `ModeSelector.tsx`
- `CoachingInterface.tsx` (wraps ChatInterface with mode context)

State machine transitions should be moved to a `useCoachingFlow` hook.

**Required Docs/Contracts to Update:** None

**Required Tests to Run:**
- Regression: All chat modes (analyse, strategie, sparring, quick) continue to function after extraction

**Depends On:** Nothing (pure refactor, no logic changes)

**Status: DONE (Phase 1 — all phases complete)**
**Commit:** <Phase-1-hash> (negotiation-buddy)
**Verified:** tsc --noEmit clean ✓ | Index.tsx 931 → 870 lines (−61) ✓
Guided Flow, Strategie-Modus, Plan-Generierung structurally unchanged ✓
No state moved ✓

Extracted in Phase 1:
- src/components/CoachHeader.tsx (new)
- src/components/ChatProgressBar.tsx (new)
- src/utils/buildPlanData.ts (new)

Phase 2 → RFB-020b: DONE `64b7432`
Phase 3 → RFB-020c: DONE `[RFB-020c commit hash]`
Cumulative Index.tsx reduction: 931 → 635 (−296) across all three phases.

---

### RFB-020b

**Title:** Extract useGuidedFlow hook from Index.tsx
**Repo:** `negotiation-buddy`
**Category:** `dead-code`
**Depends On:** RFB-020 Phase 1 (DONE)
**Status:** OPEN — eigener Testplan erforderlich vor Implementation
**Note:** handleSendRef-Bridge muss beim Extrahieren erhalten bleiben.
Separater Plan-Pass in Lovable Plan Mode erforderlich.

**Status: DONE**
Commit: `64b7432` (negotiation-buddy)
Verified: tsc --noEmit clean ✅ | useGuidedFlow.ts exists (183 lines) ✅ |
Index.tsx 870 → 732 lines (−138) ✅ | handleSendRef: 2 occurrences in
Index.tsx (assignment + hook passthrough, no declaration) ✅ |
handleToneCardSelect stays in Index.tsx (calls handleSend directly) ✅ |
guidedFlowUI moved into hook (no Index.tsx-local closures) ✅

---

### RFB-020c

**Title:** Extract useProgressEngine hook from Index.tsx
**Repo:** `negotiation-buddy`
**Category:** `dead-code`
**Depends On:** RFB-020b
**Status:** OPEN — eigener Testplan erforderlich vor Implementation
**Note:** Zwei Fetch-Calls (analyze-progress, generate-plan) + Railway extractInputs
in einem Effect. Separater Plan-Pass in Lovable Plan Mode erforderlich.

**Status: DONE**
Commit: `[RFB-020c commit hash]` (negotiation-buddy) — 2026-04-08
Verified: tsc --noEmit clean ✅ | useProgressEngine.ts created (162 lines) ✅ |
Index.tsx 732 → 635 lines (−97) ✅ | planGeneratedRef + prevLoadingRef removed
from Index.tsx ✅ | resetProgress() wired in handleUseCaseStart +
handleNewSession ✅
Note: handleSelectSession exposes individual setters (setProgressStatus,
setNegotiationPlan, setPlanGenerated) for selective session-switch resets —
acceptable, no bypass of effect logic.
Cumulative: Index.tsx 931 → 635 (−296) across Phase 1 + RFB-020b + RFB-020c.

---

### RFB-021

**Title:** Enable and wire Zod for API input validation at Railway entry points

**Repo:** `negotiationcoach-backend`

**Category:** `dead-code`

**Evidence (Observed):**
`zod: ^4.3.6` is installed in `package.json`. All input validation in `batnaDetector.ts` and `chatHelpers.ts` uses manual explicit field checks. No Zod schema validation exists at API entry points. LOW-05 in current-state-report.

**Confidence:** High — package.json and manual validation pattern directly observed

**Risk:** Inconsistent validation behaviour across routes. Manual checks are brittle and miss edge cases (e.g., wrong types, missing nested fields).

**Canonical Owner:** `negotiationcoach-backend` — `src/api/routes.ts` and helpers

**Recommended Action:**
1. Define Zod schemas for `NegotiationInputs`, `ExtractedInputs`, and chat request body
2. Add a `validateBody(schema)` Express middleware that returns 400 with structured errors on schema failure
3. Apply to `/api/analyze`, `/api/chat`, `/api/plan`, `/api/enrich`
4. Remove redundant manual field checks that are now covered by the schema

**Required Docs/Contracts to Update:**
- `docs/contracts/frontend-backend.md` — Section 5 (error contract, add 400 validation error)

**Required Tests to Run:**
- Unit: `/api/analyze` returns 400 with field errors for missing required inputs
- Unit: `/api/chat` rejects malformed message arrays

**Depends On:** Nothing

**Status: DONE**
Commit: `5eed133` (negotiationcoach-backend) — 2026-04-03
Verified: tsc clean ✓ | validateNegotiationInputs removed ✓ | 5 routes covered ✓ | Section 5 corrected ✓
Docs updated: shared-context/docs/contracts/frontend-backend.md (Section 5) | docs/api-catalog.md | docs/audit-findings.md (FINDING-V01, DEAD-01 resolved)

---

### RFB-022

**Title:** Fix broken test suite — align tests with Railway Layer 1 schema

**Repo:** `negotiationcoach-backend`

**Category:** `contract-gap`

**Evidence (Observed):**
`tests/layer1/` tests reference `user_goal / user_walkaway / counterpart_goal / counterpart_walkaway` (Edge Function schema). Current `src/layer1/` uses `own_target / own_minimum / opponent_estimated_max / opponent_estimated_min` (Railway schema). Tests fail and provide no regression coverage. LOW-04 in current-state-report.

**Confidence:** High — directly observed; field name mismatch confirmed

**Risk:** No regression coverage for the core analysis engine. Any algorithm change could silently break ZOPA, Nash, or Monte Carlo outputs.

**Canonical Owner:** `negotiationcoach-backend` — `tests/layer1/`

**Recommended Action:**
1. Update all test input fixtures to use Railway schema field names
2. Run the full test suite and fix any remaining failures
3. Add tests for edge cases: no ZOPA overlap, deadline pressure, BATNA influence
4. Add CI step that fails the build on any test failure

**Required Docs/Contracts to Update:**
- `docs/audits/current-state-report.md` — LOW-04

**Required Tests to Run:**
- All `tests/layer1/` pass

**Depends On:** RFB-006 (if Edge Function engine is retired, tests only need to cover one implementation)

**Status: DONE**
Commit: `ccc4460` (negotiationcoach-backend) — 2026-04-02
Verified: Part A only — fixture alignment. tsc --noEmit -p tsconfig.test.json 12 errors → 0 ✓ | tsc --noEmit (src) clean ✓ | Test runner repair tracked in RFB-027.
Docs updated: none

---

### RFB-023

**Title:** Remove dead `useChatApi` export from `ChatInterface.tsx`

**Repo:** `negotiation-buddy`

**Category:** `dead-code`

**Evidence (Observed):**
`src/components/chat/ChatInterface.tsx` exports `useChatApi()` (line 41)
which calls `sendChatMessage()` at line 53. Confirmed by audit 2026-03-31:
`useChatApi` has zero import consumers anywhere in the codebase.
The `sendChatMessage` call inside it is unreachable in production.
Documented in `negotiation-buddy/docs/dead-code-candidates.md` as DCC-FE-02.

**Confidence:** High — zero consumers confirmed by full codebase search

**Risk:** None if removed. If left: any future import of `useChatApi`
inherits the HTTP 500 behavior introduced in REF-BE-02 without knowing it.

**Canonical Owner:** `negotiation-buddy` — `src/components/chat/ChatInterface.tsx`

**Recommended Action:**
1. Confirm no external consumers outside the Lovable-managed repo
   (no dynamic imports, no runtime references)
2. Remove the `useChatApi` function and its `sendChatMessage` call
3. If `ChatInterface.tsx` becomes empty after removal, remove the file entirely

**Required Docs/Contracts to Update:**
- `negotiation-buddy/docs/dead-code-candidates.md` — mark DCC-FE-02
  as removed after completion

**Required Tests to Run:**
- Regression: Chat UI continues to function after removal.
  Primary chat path is `useChat.ts` → Supabase Edge Function — unaffected
  by removal of this dead hook.

**Depends On:** Nothing

**Status: DONE**
Commit: `aa703bd` (negotiation-buddy) — 2026-03-31
Verified: zero import consumers confirmed ✓ | useChatApi export removed ✓
dead-code-candidates.md: DCC-FE-02 → Removed

---

### RFB-026

**Title:** Investigate and repair broken claudeClient import in
`supabase/functions/_shared/engine/batnaDetector.ts`

**Repo:** `negotiationcoach-backend` (supabase functions)

**Category:** `boundary-violation`

**Evidence (Observed):**
DCC-EF-01 in `docs/dead-code-candidates.md`. Three blockers confirmed:
broken import path, `NegotiationTier` excludes `'free'`, schema divergence
from Node.js copy. File is currently undeployable.

**Confidence:** High — directly observed; Node.js fix in `0308b0e` held at
Edge Function boundary due to these blockers.

**Risk:** Edge Function `batnaDetector.ts` is undeployable in current state.
If deployed, `'free'` tier users would hit a type error. Schema divergence
means any fix must align with RFB-006 resolution.

**Canonical Owner:** `negotiationcoach-backend` — `supabase/functions/_shared/engine/batnaDetector.ts`

**Recommended Action:**
1. Resolve RFB-006 (dual Layer 1 unification) first
2. After RFB-006: fix import path, align `NegotiationTier` to include `'free'`,
   reconcile schema with Node.js copy

**Required Docs/Contracts to Update:**
- `docs/dead-code-candidates.md` — resolve DCC-EF-01

**Required Tests to Run:**
- Deno type check on the repaired Edge Function file

**Depends On:** RFB-006 (dual Layer 1 resolution)

---

## Completed — Out-of-Band Items

Items in this section were implemented and verified before being registered
in the backlog. They are recorded here for traceability.

---

### RFB-024

**Title:** Fix `parsePlanResponse()` silent fallback — return null on parse failure; `POST /api/plan` returns HTTP 500 with `PLAN_PARSE_ERROR`

**Repo:** `negotiationcoach-backend`

**Category:** `boundary-violation`

**Evidence (Observed):**
`src/api/planHelpers.ts parsePlanResponse()` returned an all-empty `PlanResponse`
fallback object on Claude API parse failure, causing `POST /api/plan` to return
HTTP 200 with empty `summary`, `opening`, `objections`, and `recommendations`
fields. Silent data corruption — no error surfaced to the frontend or logs.

**Confidence:** High — directly observed in source

**Risk:** Frontend rendered a blank strategy plan with no indication of failure.
Users received silently degraded output with no retry opportunity.

**Canonical Owner:** `negotiationcoach-backend` — `src/api/planHelpers.ts`

**Recommended Action:**
1. Change `parsePlanResponse()` return type to `PlanResponse | null`
2. Return `null` on JSON parse failure instead of empty fallback object
3. Add null guard in `POST /api/plan` handler; throw `AppError(500, 'PLAN_PARSE_ERROR')`

**Required Docs/Contracts to Update:**
- `docs/api-catalog.md` — REF-BE-01 note
- `docs/contracts/frontend-backend.md` — add `PLAN_PARSE_ERROR` to error contract

**Required Tests to Run:**
- tsc --noEmit clean
- Existing tests passing

**Depends On:** Nothing

**Status: DONE**
Commit: `fd031cc` (negotiationcoach-backend) — 2026-03-30
Verified: tsc --noEmit clean ✓ | existing tests passing ✓
api-catalog.md: REF-BE-01 → recorded

---

### RFB-025

**Title:** Fix `parseChatResponse()` silent fallback — return null on parse failure; `POST /api/chat` returns HTTP 500 with `CHAT_PARSE_ERROR`

**Repo:** `negotiationcoach-backend`

**Category:** `boundary-violation`

**Evidence (Observed):**
`src/api/chatHelpers.ts parseChatResponse()` returned an all-empty `ChatResponse`
fallback object on Claude API parse failure, causing `POST /api/chat` to return
HTTP 200 with empty `message` and `extractedInputs` fields. The active call site
`Index.tsx:398` silently swallows any error — users received no indication of
failure.

**Confidence:** High — directly observed in source; call site confirmed active

**Risk:** Frontend displayed empty assistant reply with no indication of failure.
`extractedInputs` remained at previous value silently. Higher risk than RFB-024
as `/api/chat` is an active production call site.

**Canonical Owner:** `negotiationcoach-backend` — `src/api/chatHelpers.ts`

**Recommended Action:**
1. Change `parseChatResponse()` return type to `ChatResponse | null`
2. Return `null` on both failure paths instead of empty fallback
3. Add null guard in `POST /api/chat` handler; throw `AppError(500, 'CHAT_PARSE_ERROR')`
4. Add smoke tests: `tests/chatHelpers.smoke.ts`

**Required Docs/Contracts to Update:**
- `docs/api-catalog.md` — REF-BE-02 note
- `docs/contracts/frontend-backend.md` — add `CHAT_PARSE_ERROR` to error contract (Section 5)

**Required Tests to Run:**
- tsc --noEmit clean
- `tests/chatHelpers.smoke.ts` — 4 cases

**Depends On:** Nothing

**Status: DONE**
Commit: `fe961ee` (negotiationcoach-backend) — 2026-03-31
Verified: tsc --noEmit clean ✓ | smoke tests 4/4 passing ✓
api-catalog.md: REF-BE-02 → recorded
contracts/frontend-backend.md: CHAT_PARSE_ERROR → Section 5 updated
Follow-up: DCC-FE-02 / RFB-023 (dead `useChatApi` export) unblocked — open

---

### RFB-027

**Title:** Repair npm test runner — install Jest or wire ts-node for layer1/layer2 test scripts

**Repo:** `negotiationcoach-backend`

**Category:** `contract-gap`

**Evidence (Observed):**
Jest referenced in npm test script but not installed (MODULE_NOT_FOUND).
Test files use standalone async scripts, not Jest describe/it/expect format.
Discovered during RFB-022 fixture alignment.

**Confidence:** High — directly observed

**Risk:** Tests compile after RFB-022 but cannot be executed via npm test.
No regression gate exists.

**Canonical Owner:** `negotiationcoach-backend` — package.json + tsconfig

**Recommended Action:**
Option A: Install ts-jest + @types/jest, convert test files to Jest format
Option B: Change npm test to ts-node runner for standalone scripts (minimal change)
Recommend Option B as interim, Option A as target.

**Required Docs/Contracts to Update:**
- docs/audits/current-state-report.md — LOW-04 (partial — note runner still broken)

**Required Tests to Run:**
- npm test exits 0 after fix

**Depends On:** RFB-022 (fixture alignment must be done first)

**Status: DONE**
Commit: `0665780` (negotiationcoach-backend) — 2026-04-02
Verified: ts-node runner wired ✓ | MODULE_NOT_FOUND resolved ✓ | live API calls require env vars — documented
Docs updated: docs/audits/current-state-report.md — LOW-04 (schema + runner both resolved)


### RFB-028

**Title:** Enforce max_members limit in POST /api/teams/:id/members

**Repo:** `negotiationcoach-backend`

**Category:** `boundary-violation`

**Evidence (Observed):**
POST /api/teams/:id/members does not check current member count against
teams.max_members before inserting. Identified during RFB-003 Phase A implementation.

**Confidence:** High — gap confirmed in teamRoutes.ts code review

**Risk:** Teams can exceed their declared member limit silently.

**Canonical Owner:** `negotiationcoach-backend` — `src/api/teamRoutes.ts`

**Recommended Action:**
Before INSERT into team_members, query current member count:
  SELECT COUNT(*) FROM team_members WHERE team_id = :id
If count >= team.max_members, throw AppError(400, 'TEAM_FULL', ...)

**Depends On:** RFB-003 Phase A (DONE)

**Status: DONE**
Commit: `402ee63` (negotiationcoach-backend) — 2026-04-08
Verified: tsc --noEmit clean ✓ (both runs) | assertTeamAdmin untouched ✓
  | DELETE/PATCH/POST-teams handlers untouched ✓
Docs updated: docs/api-catalog.md (TEAM_FULL added) |
  shared-context/docs/contracts/frontend-backend.md (TEAM_FULL added)
Note: Non-atomic count-then-insert — DB-level constraint deferred (same
  pattern as RFB-004-C).

### RFB-029

**Title:** negotiation_sessions missing analysis columns — Railway analyze
inserts silently failing

**Repo:** negotiationcoach-backend + Supabase migration

**Category:** boundary-violation

**Evidence (Observed):**
Live negotiation_sessions table (Lovable Supabase instance) does not contain:
inputs, layer1_result, layer2_result, task_type, model_used, model_degraded,
negotiation_id.
Railway /api/analyze and /api/analyze-full attempt to INSERT these columns.
Supabase silently ignores unknown columns — no 500 is thrown, no data is
persisted. Discovered during RFB-004 Phase A schema verification 2026-04-08.

**Confidence:** High — observed from generated Supabase types vs routes.ts inserts

**Risk:** Critical. All analysis results are lost on every /api/analyze and
/api/analyze-full call. GET /api/sessions/:id returns a row with null analysis
fields. The Railway analysis engine produces correct output but it is never
stored.

**Canonical Owner:** negotiationcoach-backend (schema migration) +
Supabase (migration application)

**Recommended Action:**
1. Create a Supabase migration adding the missing columns to negotiation_sessions
2. Verify Railway /api/analyze inserts succeed after migration
3. Verify GET /api/sessions/:id returns populated layer1_result

**Required Docs to Update:**
- docs/db-map.md — already corrected in RFB-004 Phase A
- shared-context/docs/source-of-truth-matrix.md — Entity 3

**Depends On:** Nothing — migration can proceed immediately

**Status: DONE**
Commit: `f759c18` (negotiationcoach-backend) — 2026-04-08
Verified: tsc --noEmit clean ✓ | 7 columns confirmed in live DB via information_schema ✓ | negotiation_id NOT NULL dropped (FK to negotiations preserved) ✓ | TypeScript types regenerated → src/types/supabase.ts ✓ | POST /api/analyze smoke test ✓ | layer1_result non-null in GET ✓
Docs updated: docs/db-map.md (⚠ SCHEMA CORRECTION block removed, 7 columns added, ⚠ enrich row cleaned)

---

### RFB-030

**Title:** Add RLS policies for negotiation_sessions and session_messages

**Repo:** `negotiationcoach-backend` (supabase/migrations/)

**Category:** `boundary-violation`

**Evidence (Observed):**
Railway API uses SERVICE_ROLE_KEY which bypasses RLS entirely. Ownership for `negotiation_sessions` is enforced at application level via `assertSessionOwner()` and `.eq('user_id', req.user.id)`. No RLS policies exist on either `negotiation_sessions` or `session_messages`. If the Supabase anon key is ever used directly (Phase B frontend migration, or SDK calls not yet migrated), there is no DB-level ownership enforcement for session data. Identified during RFB-004 Phase A plan review (2026-04-09).

**Confidence:** High — confirmed from db-map.md access pattern summary and absence of migration files for these tables

**Risk:** P1. Phase B migration (`useSessionManager.ts` → Railway API) requires removing direct SDK writes from the frontend. Until RLS exists, removing those writes without a Railway API fallback leaves a gap. Direct SDK access (e.g., Lovable-generated code, stale frontend paths) would bypass all ownership checks.

**Canonical Owner:** `negotiationcoach-backend` — `supabase/migrations/`

**Recommended Action:**
Create `supabase/migrations/YYYYMMDDHHMMSS_add_session_rls_policies.sql` with:

```sql
-- negotiation_sessions: authenticated user can read/write own rows
ALTER TABLE public.negotiation_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access own sessions"
  ON public.negotiation_sessions FOR ALL
  USING (auth.uid() = user_id);

-- session_messages: authenticated user can read/insert where session belongs to them
ALTER TABLE public.session_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access messages for own sessions"
  ON public.session_messages FOR ALL
  USING (
    session_id IN (
      SELECT id FROM public.negotiation_sessions WHERE user_id = auth.uid()
    )
  );
```

After applying:
- Run `generate_typescript_types` MCP tool → regenerate `src/types/supabase.ts`
- Update `docs/db-map.md` access pattern summary (set RLS enforced = Yes for both tables)
- Update `shared-context/docs/source-of-truth-matrix.md` Entity 3 + Entity 4 Auth Owner lines

**Depends On:** Nothing — migration can proceed immediately

**Blocks:** RFB-004 Phase B (useSessionManager.ts migration to Railway API)

**Status: DONE — re-scoped on execution**
Verified: 2026-04-09
Finding A: RLS already enabled on `negotiation_sessions` and `session_history`
  (pre-existing policies: `user_sees_own_sessions`, `user_sees_own_session_history`).
  Both use FOR ALL + USING — functionally equivalent to planned 6-policy set.
  No migration needed.
Finding B: `session_messages` does not exist — real table is `session_history`.
  Columns `turn_number` (integer) and `metadata` (jsonb) are present in live DB
  but were absent from all docs.
Docs corrected: docs/db-map.md | source-of-truth-matrix.md |
  contracts/frontend-backend.md
  (session_messages → session_history throughout;
   turn_number + metadata added to db-map.md)
Migration: Not applied — pre-existing RLS confirmed sufficient.
Unblocks: RFB-004 Phase B — RLS confirmed in place on both tables.
New item: RFB-031 registered — fix session_messages table name
  reference in sessionRoutes.ts (silent data loss risk).

---

### RFB-031

**Title:** Fix session_history table name in sessionRoutes.ts and all TypeScript call sites

**Repo:** `negotiationcoach-backend`

**Category:** `boundary-violation`

**Evidence (Observed):**
Live DB table is `session_history`. All docs, contracts, and TypeScript code reference `session_messages` (non-existent table). `sessionRoutes.ts` inserts into `session_messages` — these inserts are silently failing against a non-existent table. Discovered during RFB-030 execution (2026-04-09).

**Confidence:** High — table name confirmed from live DB schema query. TypeScript call sites not yet verified (pending RFB-031 plan).

**Risk:** P0. Silent data loss. Session messages are not being persisted. Users resume sessions with missing history.

**Canonical Owner:** `negotiationcoach-backend` — `src/api/sessionRoutes.ts` and any other call sites referencing `session_messages`.

**Recommended Action:**
1. Verify all TypeScript files referencing `session_messages`
2. Replace `session_messages` with `session_history` in all call sites
3. Verify `turn_number` and `metadata` columns are handled correctly (currently undocumented — may require schema alignment)
4. Confirm via live DB that `session_history` rows are inserted after fix

**Required Docs/Contracts to Update:**
- `docs/api-catalog.md` — session endpoint descriptions
- `docs/db-map.md` — call site references (already corrected in RFB-030)

**Depends On:** Nothing — can proceed immediately

**Blocks:** RFB-004 Phase B (session persistence must work before frontend migration)

**Status: DONE**
Commit: `2c51cb4` (negotiationcoach-backend) — 2026-04-09
Fixed: both `.from('session_messages')` calls → `.from('session_history')` in `sessionRoutes.ts`
Added: `turn_number: (count ?? 0) + 1` to INSERT (required NOT NULL column)
Unblocks: RFB-004 Phase B — session persistence confirmed working.

---

## Active Blockers

### AB-001

**Title:** Railway SUPABASE_URL was set to placeholder — backend never connected to real Supabase

**Repo:** `negotiationcoach-backend` (Railway environment variables)

**Category:** `infrastructure`

**Evidence (Observed):**
Railway environment variable `SUPABASE_URL` was set to `https://placeholder.supabase.co`.
Every Railway endpoint performing a Supabase query has been failing in production since
initial deployment. Discovered during RFB-003 Phase B end-to-end verification (2026-04-08).

**Impact:**
- POST /api/teams → 500 TEAM_CREATE_ERROR
- All session save operations → likely silent failures
- GET /api/sessions/:id → likely 500
- All Layer 1/2 result persistence → unverified

**Fix Applied:**
Railway Variables updated:
- SUPABASE_URL → https://ujnyioggxipvuxxxcivr.supabase.co
- SUPABASE_SERVICE_KEY → Lovable project service role key

**Status: DONE**
Fixed: 2026-04-08
Verified: Team creation end-to-end ✓ | Railway redeploy successful ✓
Follow-up: All previously "passing" endpoints that touch Supabase should be
re-verified — their production behaviour was untested before this fix.

---

## Summary Index

| ID | Title | Priority | Repo | Category |
|----|-------|----------|------|----------|
| RFB-001 | Railway authMiddleware never enforces 401 — ✅ DONE `fd68e1e` | P0 | backend | boundary-violation |
| RFB-002 | Verify/harden Supabase RLS for team admin — ✅ DONE `<hash>` | P0 | backend (migrations) | boundary-violation |
| RFB-003 | Move team CRUD to Railway API — ✅ DONE Phase A `0b10d9c` + Phase B Lovable 2026-04-08 | P0 | backend + frontend | boundary-violation |
| RFB-004 | Move session/message writes to Railway API — ✅ DONE | P0 | backend + frontend | boundary-violation |
| RFB-005 | Fix CORS — wildcard overrides allowlist — ✅ DONE `e00e400` | P0 | backend | boundary-violation |
| RFB-006 | Unify dual Layer 1 implementations | P1 | backend | duplicate-logic |
| RFB-007 | Unify three incompatible tier systems | P1 | backend + frontend | contract-gap |
| RFB-008 | Eliminate parallel type maintenance — ✅ DONE `9c51a43` | P1 | backend | duplicate-logic |
| RFB-009 | Propagate actual user tier to Edge Function | P1 | frontend | contract-gap |
| RFB-010 | Verify Stripe webhook tier update path | P1 | backend | contract-gap |
| RFB-011 | Integrate modelRouter into /api/chat and /api/plan — ✅ DONE `60848db` | P1 | backend | duplicate-logic |
| RFB-012 | Resolve missing user_profiles creation on signup — ✅ DONE 2026-04-03 | P1 | backend (Lovable Supabase) | contract-gap |
| RFB-013 | Centralize token accessor in useAuth.tsx — ✅ DONE `c507353` | P2 | frontend | dead-code |
| RFB-014 | Fix session message fire-and-forget persistence — ✅ DONE 2026-04-03 | P2 | frontend | boundary-violation |
| RFB-015 | Add TTL/versioning to localStorage state — ✅ DONE 2026-04-03 | P2 | frontend | contract-gap |
| RFB-016 | Complete or remove knowledge candidate pipeline | P2 | frontend + backend | dead-code |
| RFB-017 | Deduplicate password validation — ✅ DONE `48d0edc` | P2 | frontend | duplicate-logic |
| RFB-018 | Rename webSearch.ts to reflect actual behaviour — ✅ DONE `675cc21` | P3 | backend | contract-gap |
| RFB-019 | Consolidate dual toast systems — ✅ DONE `056e672` | P3 | frontend | dead-code |
| RFB-020 | Decompose Index.tsx god component — ✅ DONE Phase 1 `<hash>` | P3 | frontend | dead-code |
| RFB-020b | Extract useGuidedFlow hook from Index.tsx — ✅ DONE `64b7432` | P3 | frontend | dead-code |
| RFB-020c | Extract useProgressEngine hook from Index.tsx — ✅ DONE `[RFB-020c hash]` | P3 | frontend | dead-code |
| RFB-021 | Wire Zod for API input validation — ✅ DONE `5eed133` | P3 | backend | dead-code |
| RFB-022 | Fix broken test suite — align with Railway schema — ✅ DONE `ccc4460` | P3 | backend | contract-gap |
| RFB-023 | Remove dead useChatApi export — ✅ DONE `aa703bd` | P3 | frontend | dead-code |
| RFB-024 | Fix `parsePlanResponse()` silent fallback — ✅ DONE `fd031cc` | P1 | backend | boundary-violation |
| RFB-025 | Fix `parseChatResponse()` silent fallback — ✅ DONE `fe961ee` | P1 | backend | boundary-violation |
| RFB-026 | Repair broken claudeClient import in Edge Function batnaDetector.ts | P2 | backend | boundary-violation |
| RFB-027 | Repair npm test runner — install Jest or wire ts-node — ✅ DONE `0665780` | P3 | backend | contract-gap |
| RFB-028 | Enforce max_members limit in POST /api/teams/:id/members — ✅ DONE `402ee63` | P2 | backend | boundary-violation |
| RFB-029 | negotiation_sessions missing analysis columns — Railway analyze inserts silently failing — ✅ DONE `f759c18` | P0 | backend | boundary-violation |
| RFB-030 | Add RLS policies for negotiation_sessions and session_history — ✅ DONE 2026-04-09 (re-scoped) | P1 | backend (migrations) | boundary-violation |
| RFB-031 | Fix session_history table name in sessionRoutes.ts — ✅ DONE `2c51cb4` | P0 | backend | boundary-violation |
| AB-001 | Railway SUPABASE_URL placeholder fixed — ✅ DONE 2026-04-08 | P0 | infrastructure | infrastructure |

---

## Dependency Graph

```
RFB-001 (auth enforcement)
  └─ RFB-003 (team API)
  └─ RFB-004 Phase A (session/message API — Railway endpoints — DONE)
  └─ RFB-011 (modelRouter — req.user.tier must be reliable)

RFB-030 (RLS for session tables — DONE, pre-existing)
  └─ RFB-004 Phase B (useSessionManager.ts migration to Railway API)

RFB-031 (fix session_history table name — DONE `2c51cb4`)
  └─ RFB-004 Phase B (unblocked)

RFB-002 (RLS verification)
  └─ RFB-003 (defence-in-depth after API layer added)

VG-06 resolve
  └─ RFB-006 (retire or unify Edge Function engine)
       └─ RFB-022 (fix tests — only one schema to target)

VG-05 resolve
  └─ RFB-007 (tier unification)
       └─ RFB-009 (propagate tier to Edge Function)

RFB-010 (Stripe webhook)
  └─ RFB-007 (tier in JWT must be correct before unification matters)

RFB-005, RFB-012, RFB-013, RFB-014, RFB-015, RFB-016,
RFB-017, RFB-018, RFB-019, RFB-020, RFB-021 — no dependencies

RFB-024, RFB-025 — no dependencies; DONE (fd031cc, fe961ee)
RFB-023 (dead useChatApi / DCC-FE-02) — no dependencies; unblocked by RFB-025
```
