# Stage 2 — Proposed File Diffs

Diffs below are real (computed against verbatim current content read directly this pass), not hypothetical, for the items where full current text was available. Where full current text was not read this pass, that is stated explicitly rather than fabricated.

## Delta review — owner corrections applied (2026-09-04)

Diff 1 below originally proposed leaving `docs/infrastructure/supabase-instances.md` in a "pending verification, do not treat as authoritative" state pending further investigation. **The owner has now supplied that confirmation directly**: `gpllrgkuozytyrmpfwbb` is the one active, intentionally-shared Supabase project. Diff 1 is revised below to state this as settled fact rather than an unresolved caution, and gains a governance section sourced from `04-supabase-boundary-map.md`'s new "Governance implications of the shared instance" analysis. The Railway-naming corrections (Diff 3) and the `.sdlc/config.yaml` `logical_instance` comments (New files section) are similarly de-hedged below.

## Correction to Stage 1 characterization (found while gathering diff evidence)

While reading `docs/infrastructure/supabase-instances.md` in full for this section, its content turns out to be **worse** than the Stage 1 summary conveyed: it documents exactly two project IDs — `ujnyioggxipvuxxxcivr` (labeled production) and `ivrfsjxdfzxrimexvoft` (labeled local dev) — and **neither one is the actual current active project** (`gpllrgkuozytyrmpfwbb`, confirmed independently in both code repos' `MEMORY.md` and `supabase/config.toml`/`.temp/project-ref`). This file needs a full rewrite of its factual content, not a single-ID swap.

Also found: `shared-context/product/releases/current.md` (the *current, active* release scope doc) already flags this exact class of problem in its own "Explicitly out of scope" section: *"RFB-041 / RFB-042 — vermutlich veraltete Backlog-Einträge (referenzieren 'Railway' und ein nicht mehr existierendes Supabase-Projekt), nie zu AR-Items promoted. Empfehlung: separat prüfen und ggf. als obsolet schließen."* — the team has already noticed this class of staleness and flagged it for review; this migration's findings corroborate and extend that, they don't discover it from nothing.

Also found: `shared-context/AGENTS.md`'s "Critical Issues (Quick Reference)" table — the single most visibility-privileged summary in the whole shared-context repo (loaded via `@AGENTS.md` in every session's `CLAUDE.md`) — repeats two findings that Stage 1's backend inventory determined are already fixed in code: `CRIT-03` ("backend authMiddleware never returns 401") and `MED-02` ("CORS wildcard header overrides allowlist"). This is added as a remediation item below.

## Delta review pass 2 — C1 canonical API contract, C3 canonical closure (2026-09-04)

Diff 3 is superseded below: it originally proposed a base-URL/missing-endpoint fix-in-place; owner decision C1 changes the file's role entirely (frontend consumes, does not redefine). Diffs 5 and 6 are new — the actual completion migration for the now-confirmed canonical `negotiationcoach-backend/docs/api-catalog.md`, and the corresponding reduction of `shared-context/docs/contracts/frontend-backend.md`, which turned out on full read to be the most complete of the three original competing files (it already contains the 6 routes the canonical file was missing — relocated, not re-authored, in Diff 5). Diffs 7-9 are new: small pointer additions the Controller/CLAUDE.md templates need (C1), LEGACY markers for the four superseded close-task Skills (C3), and a proposed-but-not-applied `close-change` gate-check addition pending an owner ruling on a genuine ambiguity found in that Skill's current text (C3) — see `10-conflicts-and-decisions.md` for both decisions' full detail.

---

## Diff 1 — `shared-context/docs/infrastructure/supabase-instances.md` (full content replacement)

**Action**: MERGE/correct. **Not a kit template** — this is a factual correction to existing content, based on cross-repo evidence gathered in Stage 1 (`04-supabase-boundary-map.md`).

```diff
 # Supabase Instance Map

-**Last updated:** 2026-04-21
+**Last updated:** <TO BE SET AT APPLY TIME>
 **Status:** Authoritative — always refer here, never guess

-## Production instance — Lovable/Railway shared
-- **Project ID:** ujnyioggxipvuxxxcivr
-- **URL:** https://ujnyioggxipvuxxxcivr.supabase.co
-- **Used by:** Lovable Frontend + Railway Backend (production)
-- **JWT authority:** YES — all user JWTs issued here
-- **External access:** Only via Lovable SQL Editor or
-  Lovable UI — NOT via Supabase CLI or MCP
-- **Modify schema via:** Lovable SQL Editor only
-- **Tables:**
-  - knowledge_base (curated, read-only)
-  - knowledge_graph (Layer 2 cache — created 2026-04-21)
-  - knowledge_queue
-  - negotiation_sessions
-  - session_messages
-  - team_members, team_training_tasks, teams
-  - user_profiles
-
-## Local development instance — negotiationAI
-- **Project ID:** ivrfsjxdfzxrimexvoft
-- **URL:** https://ivrfsjxdfzxrimexvoft.supabase.co
-- **Used by:** Local development only — NOT production
-- **Local MCP points to:** THIS instance
-- **Supabase CLI linked to:** THIS instance
-- **Status:** Empty (0 rows in all tables as of 2026-04-21)
-- **Decision pending:** Archive or delete — no active use
-
-## Access matrix
-
-| Tool | ujnyioggxipvuxxxcivr | ivrfsjxdfzxrimexvoft |
-|---|---|---|
-| Lovable UI | ✅ read/write | ❌ |
-| Lovable SQL Editor | ✅ schema changes | ❌ |
-| Supabase CLI (db push) | ❌ | ✅ |
-| Local MCP | ❌ | ✅ |
-| Railway (runtime) | ✅ service_role | ❌ |
-| Claude Code MCP | ❌ | ✅ |
-
-## Permanent rules
-
-1. Schema changes to production → Lovable SQL Editor only
-2. supabase db push → deploys to ivrfsjxdfzxrimexvoft only
-   (local dev, not production)
-3. Claude Code MCP → ivrfsjxdfzxrimexvoft only
-   (cannot reach production instance)
-4. knowledge_graph lives in ujnyioggxipvuxxxcivr
-5. Railway SUPABASE_URL must always point to
-   ujnyioggxipvuxxxcivr
-6. Never assume MCP verification = production verification
-
-## Auth architecture (ARCH-01)
-JWT tokens issued by ujnyioggxipvuxxxcivr.
-Railway validates tokens from this instance.
-Permissive auth in dev: unauthenticated requests
-receive tier: privat (middleware.ts).
-Option C (single Supabase for everything) deferred
-to pre-production release.
-
-Reference: docs/adr/ADR-001-system-boundaries.md
+## Current active project — confirmed by project owner 2026-09-04 (was: pending verification)
+
+This file's prior project IDs (`ujnyioggxipvuxxxcivr`, `ivrfsjxdfzxrimexvoft`) do not match the
+project ID both `negotiation-buddy/MEMORY.md`/`supabase/config.toml` and
+`negotiationcoach-backend/MEMORY.md`/`supabase/.temp/project-ref` currently record as active:
+`gpllrgkuozytyrmpfwbb` — the single active project, per the project owner's direct confirmation
+(2026-09-04) that it is intentionally shared, not separate instances. Both prior IDs are retired (see
+`negotiation-buddy/tasks/lessons.md` and `negotiationcoach-backend/tasks/lessons.md` L-004/L-006
+for the migration history) and should be treated as documentation debt, not restoration
+candidates, unless future repository evidence shows either is still operationally relevant (none
+was found in this analysis).
+
+## Current active project — confirmed by project owner (2026-09-04)
+- **Project ID:** gpllrgkuozytyrmpfwbb — the single active Supabase project for Negotiation AI.
+- **Confirmed via:** `negotiation-buddy/supabase/config.toml`, both repos' `supabase/.temp/project-ref`, both repos' `MEMORY.md`, and directly by the project owner.
+- **Used by:** both `negotiation-buddy` and `negotiationcoach-backend` — **intentionally shared by design**, not separate instances and not accidental coupling. Do not propose splitting this into per-repo instances.
+- **Tables, RLS, edge functions:** see `04-supabase-boundary-map.md` for the full per-repo breakdown gathered this pass — not yet consolidated into this file's original per-instance/per-tool format; that consolidation is Stage 3 work requiring owner review, not a mechanical replacement.
+- **Governance for the shared model:** see `04-supabase-boundary-map.md`'s "Governance implications of the shared instance" section (migration-coordination rule, per-table ownership map, VG-01/VG-02 as a precondition for new shared-table work, service-role-key custody staying backend-only) — replaces the old file's per-instance access-matrix/permanent-rules format with rules appropriate to one shared project.
+- **Still open, unaffected by the above:** `negotiationcoach-backend/tasks/lessons.md` L-004 claims this environment's Supabase MCP tool is wired to `ivrfsjxdfzxrimexvoft` rather than the real active project — not settled by the owner's corrections, remains an open read-only validation item (`10-conflicts-and-decisions.md`, validation item 1).
```

**Rollback**: `git revert` the correction commit; the deleted content is fully recoverable from git history regardless (`ALLOW_DELETIONS_OR_RENAMES: false` is respected — nothing here is a rename or a silent loss, the old content is superseded in a tracked commit).

**Validation**: cross-check the new project ID against a **read-only** Supabase call (e.g., `get_project_url`) only after confirming which MCP connection actually reaches it — do not assume the environment's `mcp__supabase`/`mcp__claude_ai_Supabase` tools are correctly wired without checking first (per the L-004 caveat above).

---

## Diff 2 — `shared-context/AGENTS.md` Critical Issues table (2 rows)

**Action**: MERGE/correct.

```diff
 | ID | Severity | Summary |
 |----|----------|---------|
 | CRIT-01 | Critical | Layer 1 algorithms duplicated in Backend Layer 1 AND Supabase Edge Function with incompatible schemas |
 | CRIT-02 | Critical | Team admin check is frontend React code only — no server-side enforcement verified |
-| CRIT-03 | Critical | backend authMiddleware never returns 401 — all endpoints publicly accessible |
+| ~~CRIT-03~~ | ~~Critical~~ | ~~backend authMiddleware never returns 401~~ — **RESOLVED**: current `negotiationcoach-backend/src/api/middleware.ts` returns 401 via `AuthError` when a required token is missing/invalid (code comment cites "RFB-001 — 401 enforced"). Re-verify directly before fully removing this row. |
 | HIGH-01 | High | Frontend writes negotiation_sessions, session_messages, teams directly (no API mediation) |
 | HIGH-02 | High | Message saves are fire-and-forget — silent data loss possible |
 | HIGH-03 | High | Three incompatible tier systems: backend tier, Supabase persona_type, Edge Function hardcoded "free" |
 | MED-01 | Medium | modelRouter bypassed in /api/chat and /api/plan — cost optimization and tier routing absent |
-| MED-02 | Medium | CORS wildcard header overrides allowlist in Express backend |
+| ~~MED-02~~ | ~~Medium~~ | ~~CORS wildcard header overrides allowlist~~ — **RESOLVED**: `negotiationcoach-backend/docs/api-catalog.md` documents this as "Fixed (RFB-005)" and Stage 1 discovery confirms current `src/api/routes.ts` uses a proper origin-callback allowlist, no wildcard. Re-verify directly before fully removing this row. |
```

Both corrections are proposed as struck-through + annotated rather than silently deleted, so a reader can see what changed and why — consistent with not silently erasing prior findings. A full removal (once independently re-confirmed by whoever applies this) is a smaller follow-up edit.

**Rollback**: `git revert`. **Validation**: read `negotiationcoach-backend/src/api/middleware.ts` and `src/api/routes.ts` directly (not just this analysis's summary) before finalizing.

---

## Diff 3 — `negotiation-buddy/.claude/rules/api-contracts.md` (reduce to pointer — supersedes the original fix-in-place plan)

**Action**: MERGE/correct. **Superseded by owner decision C1 (2026-09-04, `10-conflicts-and-decisions.md`)**: "negotiation-buddy consumes the canonical contract but must not redefine it." This file's role changes from "the frontend's own contract copy, factually corrected" to "a pointer to the canonical backend contract plus frontend-only implementation notes." Full current text (107 lines) was read this pass; the diff below is a near-full-body replacement of the `## Railway Backend API` section through the endpoint list, keeping the file's other sections (`## Supabase Edge Functions`, `## Contract Change Protocol`, `## Type Source of Truth`) intact since those are legitimately frontend-repo content.

```diff
-## Railway Backend API
-
-Base URL: `https://negotiationcoach-backend-production.up.railway.app`
-Auth: `Authorization: Bearer <supabase-jwt>`
-
-### Endpoints
-
-#### `POST /api/analyze-full`
-Full negotiation analysis.
-
-**Request:**
-```ts
-{
-  situation: string;       // User's negotiation situation description
-  persona: 'pro' | 'kmu' | 'private';
-  userId?: string;         // Omit for private persona
-}
-```
-
-**Response:** Full analysis object (see `src/lib/types.ts`).
-
----
-
-#### `POST /api/analyze`
-Analysis without plan generation.
-
-**Request:** Same as `/api/analyze-full`.
-
----
-
-#### `POST /api/chat`
-Single LLM chat turn.
- ... (all remaining endpoint bodies removed — see canonical source)
-
-#### `GET /api/sessions/:sessionId`
-Fetch persisted session.
-
-**Response:** Session object or 404.
+## Backend API (Render.com)
+
+**Canonical contract:** `../negotiationcoach-backend/docs/api-catalog.md` — this repository consumes
+that contract and must not redefine or duplicate it here (owner decision C1, 2026-09-04).
+
+**Base URL:** `VITE_API_URL` env var, falling back to `https://negotiationcoach-backend.onrender.com`
+(see `src/lib/apiClient.ts`).
+
+**Auth:** `Authorization: Bearer <supabase-jwt>`, injected automatically from the Supabase session
+by `apiClient.ts` — no call site needs to attach it manually.
+
+**Client file:** `src/lib/apiClient.ts` — every backend call goes through this file; do not inline
+`fetch()` calls elsewhere (see `.claude/rules/data-access.md`).
+
+For request/response shapes, error codes, and tier gates for any endpoint, read the canonical
+contract in the backend repository, not this file.
```

**Rollback**: `git revert`. **Validation**: `contract-check` skill run against the corrected file; confirm it no longer restates full request/response shapes anywhere; cross-check that `src/lib/apiClient.ts`'s actual exported functions are still discoverable from this file's pointer.

---

## Diff 5 — `negotiationcoach-backend/docs/api-catalog.md` (completion migration — add the 6 missing routes)

**Action**: MERGE. **C1 RESOLVED (2026-09-04)**: this file is now the confirmed canonical API contract. Its only material gap is the entire `/api/simulate/*` and `/api/opponent-simulation/*` route families. Content for both families already exists, fully written and evidently source-verified, in `shared-context/docs/contracts/frontend-backend.md` (read in full this pass) — this diff relocates/adapts that content rather than re-authoring it from scratch. **Not independently re-verified against `src/api/simulationRoutes.ts`/`src/api/opponentSimulationRoutes.ts` by this analysis** — recommended as a validation step before this diff is applied, since `frontend-backend.md`'s content, while detailed and internally consistent, was itself last self-dated "2026-03-27" at the header even though the simulate/* content is clearly newer (references through 2026-07-24).

```diff
 ### GET /api/sessions/:id
 **File:** `src/api/routes.ts:268-285`
 ...
 **Error:** 404 if not found or not owned by requester.

 ---

+---
+
+## Simulation Endpoints — NC-L3-OPPONENT (legacy, preserved not deprecated) and NC-L3-SIM (current)
+
+> Relocated from `shared-context/docs/contracts/frontend-backend.md` during the C1 canonical-contract
+> migration (2026-09-04). `/api/opponent-simulation/*` remains deployed and functional but is no
+> longer called from the frontend as of decision P-3 (`product/discovery/substance-activation-brief.md`,
+> commit `8503e8d`) — the frontend now calls `/api/simulate/*` exclusively. Neither family is deleted
+> or deprecated at the API-contract level.
+
+### POST /api/opponent-simulation/start
+**Auth:** `authMiddleware`. **Tier gate:** `requireTier('profi')` — 403 for privat/kmu/free.
+**Model:** `claude-opus-4-6` via `selectModel('opponent_simulation', 'profi')`, `{ timeout: 30_000 }`.
+**Request:** `negotiation_type`, `opponent_style`, `scenario_difficulty`, `own_target`, `own_minimum`,
+`opponent_estimated_max`, `opponent_estimated_min` (all required), `negotiation_session_id?` (uuid).
+**Response (201):** `{ simulation_session_id, status: 'active', max_turns, opening_message }` —
+hidden opponent ZOPA fields are never included.
+**DB writes:** `opponent_simulation_sessions` (INSERT, hidden columns server-side only).
+
+### POST /api/opponent-simulation/:id/turn
+**Auth/Tier:** same as above. **Request:** `content` (string, max 2000 chars), `client_turn_id`
+(uuid, idempotency key). **Response (200):** `{ assistant_message, turn_count, max_turns, finished }`,
+or `{ idempotent: true, assistant_message }` on retry, or `{ finished: true, reason: 'turn_limit_reached', turn_count }`.
+**DB writes:** `opponent_simulation_turns` upsert on `(simulation_session_id, client_turn_id)`.
+
+### POST /api/opponent-simulation/:id/finish
+**Auth/Tier:** same as above. **Request:** `final_offer` (number). **Response (200):** an `evaluation`
+object (final_outcome, own_zopa_min/max, nash_solution, outcome_vs_nash, outcome_percentile,
+tactic_assessment) plus `hidden_opponent_minimum`/`hidden_opponent_target` — the only endpoint that
+reveals those. **DB writes:** updates `opponent_simulation_sessions` (status='finished', evaluation).
+
+### POST /api/simulate/start — current, session-grounded (loads real L1/L2 results server-side)
+**Auth/Tier:** same as above. **Model:** Sonnet/Opus via `l3_sim_intake`/`l3_sim_debrief` router entries.
+**Request:** `session_id` (uuid, references `negotiation_sessions.id`, must already have `layer1_result`).
+**Response (201):** `{ simulation_id, status: 'intake'|'ready', clarifying_questions[], scenario_preview? }`.
+**DB writes:** `simulation_sessions` (INSERT — scenario_object, layer1_snapshot, layer2_snapshot, private_state).
+
+### POST /api/simulate/turn
+**Auth/Tier:** same. **Request:** `simulation_id`, `user_message`, `client_turn_id` (idempotency key).
+**Response (200):** `{ opponent_message?, coach_message?, clarifying_question?, turn_number, offer_detected?, status, idempotent? }`.
+**DB writes:** `simulation_turns` upsert on `client_turn_id`; updates `simulation_sessions.turn_count/status/intake_complete`.
+
+### POST /api/simulate/debrief
+**Auth/Tier:** same. **Request:** `simulation_id`, `final_offer?` (omitted for abort/no-deal).
+**Response (200) — `DebriefResult`:** deal_reached, final_offer?, walkaway_reason?,
+final_vs_zopa_percentile, final_vs_nash_distance, final_vs_nash_direction, vs_monte_carlo_p50/p90,
+vs_market_median?, market_comparison?, concession_timeline[], total_user/opponent_concession_pct,
+tactics_used_well[], tactics_missed[], opponent_tactics_observed[], key_mistakes[], recommendations[],
+overall_score, hidden_opponent_minimum, hidden_opponent_target, no_zopa_scenario?.
+**DB writes:** updates `simulation_sessions` (status='finished', final_outcome, evaluation, finished_at).
+
 ## CORS Configuration
```

**Header refresh** (separate small edit, same file): change `> Status: Observed (from src/api/routes.ts direct read, 2026-03-27)` to reflect that this is now the actively-maintained canonical source, not a point-in-time snapshot — e.g. add `> Canonical since: 2026-09-04 (owner decision C1). Kept in sync per .claude/rules/api-contracts.md.`

**Rollback**: `git revert`. **Validation**: cross-check every relocated field name/type against `src/api/simulationRoutes.ts` and `src/api/opponentSimulationRoutes.ts` directly before treating this as verified-complete — this diff is a relocation of already-written content, not independently re-derived from source by this analysis.

---

## Diff 6 — `shared-context/docs/contracts/frontend-backend.md` (reduce to pointer)

**Action**: MERGE. Once Diff 5 lands, this file's route-detail sections become redundant with the canonical backend copy. Reduce §2 ("Backend REST API") to a pointer; **keep** §1 (Transport Overview — genuinely cross-repo), §3 (Supabase Edge Function Contract — these Edge Functions are frontend-repo-owned code but their *contract* is legitimately cross-repo reference material, per the open scoping question in `10-conflicts-and-decisions.md` C1), §4 (Type Drift Register), §5 (Error Contract, if not already in the backend copy), and §6 (Known Contract Violations) — these are audit-trail/cross-cutting content, not the contract itself, and match the `product/audit/refactor-backlog.md` thin-pointer precedent.

```diff
 ## 2. Backend REST API

-**Base URL:** `VITE_API_URL` env var, falling back to `https://negotiationcoach-backend.onrender.com`
-**Client:** `src/lib/apiClient.ts`
-
-### `POST /api/chat`
- ... (full route bodies removed)
+**Canonical contract:** `NegotiationCoach-backend/docs/api-catalog.md` (owner decision C1, 2026-09-04
+— shared-context references the canonical contract, it does not maintain a competing one). This
+section previously duplicated the full REST API contract; that content has been relocated to the
+canonical file (see that file's Simulation Endpoints section, added 2026-09-04, for the routes that
+existed only here before the relocation).
```

**Rollback**: `git revert` (the removed content remains fully recoverable from git history and from Diff 5's relocation target).

---

## Diff 4 — `negotiationcoach-backend/.claude/rules/db-boundaries.md` (stale path reference)

**Action**: MERGE/correct. Full current text read this pass (69 lines).

```diff
 ## What-If Machine Schema

 The What-If Machine uses a 9-table schema (Profi-only).
 All related tables must have RLS policies checking `user_tier = 'profi'`.
-Core algorithms: `src/engine/simulationEngine.ts` (ZOPA, Monte Carlo, Nash).
+Core algorithms: `src/layer1/*` (ZOPA, Nash Bargaining, Monte Carlo, deadline effect, strategy
+score) and `src/layer3/*` (opponentEngine, debriefEngine, promptBuilder, smlParser,
+simulationLoop) — there is no `src/engine/` directory in this repository.
```

**Rollback**: `git revert`. **Validation**: `ls src/engine` confirms absence (already confirmed in Stage 1); `ls src/layer1 src/layer3` confirms presence.

---

## Diff 7 — Controller and CLAUDE.md-template pointers to the canonical contract (C1)

**Action**: ADD one line each, three locations. Small, low-risk additions surfaced by C1's resolution.

`shared-context-overlay/controllers/DEVELOPMENT_CONTROLLER.md`, in the "Source-of-truth contract" bullet list:
```diff
 - Cross-repository lifecycle state: `Shared-context/sdlc/changes/<change-id>/`.
 - Product and governance policies: approved files under `Shared-context/sdlc/policies/`.
+- Canonical API contract: `NegotiationCoach-backend/docs/api-catalog.md` (backend-owned; Shared-context
+  and negotiation-Buddy reference it and must not maintain a competing copy — owner decision C1, 2026-09-04).
 - Frontend implementation and tests: `negotiation-Buddy`.
 - Backend implementation and tests: `NegotiationCoach-backend`.
```

`repo-overlays/frontend/CLAUDE.md.template`, "Architecture orientation" list:
```diff
 - Frontend Supabase ownership and generated types: `<DISCOVER_AND_LINK>`
+- API contract (canonical, backend-owned): `../negotiationcoach-backend/docs/api-catalog.md`
```

`repo-overlays/backend/CLAUDE.md.template`, "Architecture orientation" list:
```diff
 - Backend Supabase ownership and generated types: `<DISCOVER_AND_LINK>`
+- API contract (canonical, this repository): `docs/api-catalog.md`
```

**Rollback**: remove the added line in each case. **Note**: these are kit-file edits (`shared-context-overlay/`, `repo-overlays/`), not shared-context-repo edits — out of this session's kit-editing authorization for this turn, held here as a proposed diff for the next authorized kit pass, consistent with how Diff 5/6 target the product repos (in-scope) while this diff targets the kit (out of scope this turn).

---

## Diff 8 — LEGACY markers on the four superseded close-task Skills (C3)

**Action**: ADD a one-line header note to each file. No behavior change, no deletion, no rename — satisfies the owner's explicit "do not delete legacy variants during the first migration pass."

Applies identically to `shared-context/.claude/skills/close-task/SKILL.md`, `shared-context/.claude/skills/close-task-dev/SKILL.md`, `negotiationcoach-backend/.claude/skills/close-task/SKILL.md`, `negotiation-buddy/.claude/skills/close-task/SKILL.md`:

```diff
 ---
 name: close-task
 ...
 ---

+> **LEGACY (2026-09-04):** superseded by `/negotiation-ai-sdlc:close-change` for all new
+> SDLC-managed changes (owner decision C3). Do not use this Skill for new `sdlc/changes/<id>/`
+> work. Preserved, unmodified, for traceability and rollback of already-closed items only.
+
 # Close Task
 ...
```

**Rollback**: remove the added block. **Validation**: confirm the Skill still functions identically for any legitimate continued use on pre-migration, non-SDLC-managed tasks — the marker is advisory text, not a functional gate.

---

## Diff 9 — Proposed `close-change` gate-check addition (NOT APPLIED — held pending owner ruling)

**Action**: proposed only, per `10-conflicts-and-decisions.md` C3's "literal reading." **Do not apply without an explicit owner decision** on which reading of rule 5 applies — this is recorded so the exact change is ready either way, not as a recommendation to make it.

If the owner rules that `close-change` must itself re-verify the full closure gate (rather than relying on the already-distributed per-Skill entry gates), the addition to `shared-context-overlay/tooling/claude-marketplace/plugins/negotiation-ai-sdlc/skills/close-change/SKILL.md` would be a new step inserted before the existing workflow:

```diff
 ## Entry gate

 Require a recorded release or explicitly document why outcome measurement is being performed for a partial, rolled-back, or failed release. Do not infer production success from merged code.

+## Closure gate (pre-outcome-measurement check)
+
+Before proceeding to outcome measurement, confirm and record each of the following against the
+canonical change artifacts — do not proceed on an assumed pass:
+
+1. `intent.md` exists and is `accepted`.
+2. `spec.md` exists and is `accepted`.
+3. `plan.md` exists and is `accepted`.
+4. Implementation is complete against the accepted plan (no open plan steps without a recorded deviation).
+5. `verification.md` exists and its result is a pass (not `BLOCKED`/`FAIL`/unrecorded).
+6. `review.md` exists and its gate recommendation is `APPROVE` or `CONDITIONAL_APPROVAL` with conditions met.
+7. No finding in `review.md` remains `OPEN` at severity `BLOCKER` or `HIGH`.
+8. `traceability.yaml` maps every acceptance criterion to implementation, evidence, and (where
+   applicable) release.
+9. Where the change type requires `release.md` and/or `outcome.md`, confirm those exist and are
+   in the expected state before continuing.
+
+If any check fails, stop and return the change to the appropriate prior stage rather than
+proceeding to outcome measurement. Record the gate result in `traceability.yaml`.
+
 ## Workflow
```

**Rollback**: remove the added section. **Note**: same out-of-scope status as Diff 7 — a kit-file edit, not applied this session, held for the next authorized kit pass and contingent on the owner's ruling.

---

## New files — `.sdlc/` scaffolding (frontend, backend, shared-context)

These are brand-new files (no existing content to diff against), shown as full proposed content, adapting the kit templates read in full this pass with real values from `access-and-paths.local.yaml` and `04-repository-registry.yaml`.

### `shared-context/sdlc/registry.yaml`

```yaml
schema_version: 1
project_id: negotiation-ai
artifact_home: sdlc/changes
change_id_pattern: '^[0-9]{8}-[a-z0-9]+(?:-[a-z0-9]+)*$'
status_vocabulary:
  - draft
  - in_review
  - accepted
  - rejected
  - superseded
  - blocked
  - completed
  - released
  - measured
required_at_creation:
  - intent.md
  - traceability.yaml
stage_artifacts:
  capture: intent.md
  define: spec.md
  plan: plan.md
  diagnose: debug-evidence.md
  verify: verification.md
  review: review.md
  release: release.md
  learn: outcome.md
  incident: incident.md
repositories:
  # Logical names only - real absolute paths stay in each repo's gitignored .sdlc/config.local.yaml,
  # never committed here (constraint: local paths never become canonical project knowledge).
  shared_context: Shared-context
  frontend: negotiation-Buddy
  backend: NegotiationCoach-backend
policies:
  root: sdlc/policies
  enforce_only_when_status: approved
plugin:
  marketplace: tooling/claude-marketplace
  name: negotiation-ai-sdlc
```

### `negotiation-buddy/.sdlc/config.yaml` (tracked)

```yaml
schema_version: 1
project_id: negotiation-ai
repository:
  logical_name: negotiation-Buddy
  role: frontend
shared_context:
  logical_name: Shared-context
  artifact_root: sdlc/changes
  policy_root: sdlc/policies
  local_path_file: .sdlc/config.local.yaml
active_change_file: .sdlc/active-change.yaml
supabase:
  logical_instance: frontend_supabase
  # NOTE (owner-confirmed 2026-09-04, C2 RESOLVED): this is the SAME physical Supabase project as
  # the backend's (gpllrgkuozytyrmpfwbb), intentionally and by design - "frontend_supabase" here is
  # a logical/ownership label only, not evidence of or a step toward a separate physical instance.
  # See sdlc/migration/20260904T132634Z/04-supabase-boundary-map.md's governance section and
  # 10-conflicts-and-decisions.md C2.
  ownership_reference: ../shared-context/docs/infrastructure/supabase-instances.md
commands_reference: CLAUDE.md
```

### `negotiation-buddy/.sdlc/config.local.yaml` (gitignored)

```yaml
schema_version: 1
shared_context_path: "/Volumes/MF_extern/app-workspace/shared-context"
# Keep this file local. Do not commit machine-specific paths.
```

### `negotiationcoach-backend/.sdlc/config.yaml` (tracked)

```yaml
schema_version: 1
project_id: negotiation-ai
repository:
  logical_name: NegotiationCoach-backend
  role: backend
shared_context:
  logical_name: Shared-context
  artifact_root: sdlc/changes
  policy_root: sdlc/policies
  local_path_file: .sdlc/config.local.yaml
active_change_file: .sdlc/active-change.yaml
supabase:
  logical_instance: backend_supabase
  # Same shared-instance note as the frontend config.yaml above (owner-confirmed, intentional).
  ownership_reference: ../shared-context/docs/infrastructure/supabase-instances.md
commands_reference: CLAUDE.md
```

### `negotiationcoach-backend/.sdlc/config.local.yaml` (gitignored)

```yaml
schema_version: 1
shared_context_path: "/Volumes/MF_extern/app-workspace/shared-context"
# Keep this file local. Do not commit machine-specific paths.
```

### `.gitignore` addition (both `negotiation-buddy` and `negotiationcoach-backend`)

```diff
+# Local AI-native SDLC path resolution
+.sdlc/config.local.yaml
```

---

## CLAUDE.md restructuring — deliberately deferred, not punted

Full current text of all three repos' `CLAUDE.md` was read this pass. Rather than propose a wholesale rewrite (which the master prompt explicitly forbids — "Do not rewrite the repositories wholesale"), the recommended diff shape is **purely additive**: insert a new subsection near the top of each file (after "Working Context", before the existing rule table) that adds the kit template's session-start resolution steps and points to the new `.sdlc/config.yaml`, without touching any existing section. Example for the frontend:

```diff
 ## Working Context
 Always read MEMORY.md first — current frontend state.

 # CLAUDE.md — negotiation-buddy

 > See **AGENTS.md** for full agent context: architecture, critical rules, known debt, persona types, env vars.

+## SDLC session start (additive)
+
+1. Read `.sdlc/config.yaml` and, if present, `.sdlc/config.local.yaml`.
+2. Resolve the active change from explicit input or `.sdlc/active-change.yaml`, if one exists.
+3. If an active change exists, read its accepted `intent.md`/`spec.md`/`plan.md` from
+   `<shared_context_path>/sdlc/changes/<change-id>/` before implementing.
+4. This does not replace the PM-aware delivery rules or Delivery Workflow below - both remain
+   in effect during the transition. See `10-conflicts-and-decisions.md` for the open question of
+   which task-closing mechanism (`/close-task`, `/close-task-dev`, or the new plugin's
+   `close-change`) is canonical going forward.
+
 ## Operating Rules
```

The same additive pattern applies to the backend's `CLAUDE.md`. Shared-context's `CLAUDE.md` already has an equivalent, working, repo-native mechanism — the German "Cross-Repo-Betrieb" section (`TARGET REPO` header requirement, repo-mapping table, per-skill cross-repo behavior table) — which functions today as a lightweight, harness-native alternative to a pasted Claude.ai Project Controller for *dispatch*, even though it doesn't cover gates/traceability/independent review. That section should be **kept as-is**; the new `sdlc/` machinery supplements it (formal gates, traceability, independent assurance) rather than replacing a working mechanism — see `06-gap-analysis.md` item 9's nuance and `10-conflicts-and-decisions.md`.

A full "make CLAUDE.md concise" pass (moving the Delivery Workflow / Side-Effect-Check / Non-Negotiable Defaults sections into `.claude/rules/` or Skills) is a legitimate but separate, larger decision — proposed as a Stage 3+ follow-up item, not bundled into this migration, because these sections are actively-used, working process (Stage 1 found no evidence they're stale or broken, only that the target model prefers them externalized).
