# Stage 1 — Supabase Boundary Map

No secret values (API keys, service-role tokens, JWTs) appear anywhere below — only project references (not secret), migration filenames, and variable *names*.

## Delta review — owner decision C2 RESOLVED (2026-09-04)

The project owner has confirmed, as an authoritative current-state fact overriding the migration kit's assumptions: **there is exactly one active Supabase instance/project for Negotiation AI, and frontend/backend sharing it is intentional.** This settles the open question this file originally raised (see "Open questions carried into Stage 2" below, now answered) — the shared-project architecture is **not** a defect to migrate away from, and no action in this migration should propose splitting it into separate frontend/backend instances.

The owner has directed that the analysis instead **assess whether the shared-instance architecture requires additional access-control, security, ownership, migration, or governance rules.** That assessment follows in a new section below ("Governance implications of the shared instance"). Everything under "Headline finding" through "Open questions" is Stage 1's original discovery and is left factually intact below, since it correctly identified the sharing (it just posed as an open question something the owner has now settled as intentional).

## Headline finding: frontend and backend currently point at the SAME Supabase project

| | Frontend (`negotiation-buddy`) | Backend (`negotiationcoach-backend`) |
|---|---|---|
| Active project reference | `gpllrgkuozytyrmpfwbb` (from `supabase/config.toml` and `supabase/.temp/project-ref`) | `gpllrgkuozytyrmpfwbb` (from `supabase/.temp/project-ref`; no `config.toml` in this repo) |

This is the **same project ID**, corroborated independently by each repo's own `MEMORY.md`. This directly contradicts `04-repository-registry.yaml`'s model of two separate instances (`frontend_supabase` / `backend_supabase`) and the current-state input's caution to "not assume frontend and backend share a Supabase schema or authentication model." The sharing appears **intentional and coordinated**, not accidental: both repos' migration histories contain files explicitly reconciling schema between the two sides —
- frontend: `20260515120000_align_negotiation_sessions_schema.sql`, `20260519120000_fix_negotiation_sessions_user_id_fk.sql`, `20260519130000_create_session_history.sql`, `20260522120000_add_missing_backend_columns.sql`
- backend: `20260320162431_add_model_routing_columns.sql` through `20260721131832_create_simulation_sessions.sql`, several of which target tables the frontend also migrates (`negotiation_sessions`, `session_history`)

**Historical project-reference churn** (do not treat these as currently active): `ivrfsjxdfzxrimexvoft` (per backend `tasks/lessons.md` L-004, the project the environment's Supabase MCP tool is permanently — and wrongly — connected to; not independently reconfirmed this pass) and `ujnyioggxipvuxxxcivr` (per frontend `tasks/lessons.md`, an earlier "Lovable-managed" project; also the project shared-context's `docs/infrastructure/supabase-instances.md` incorrectly still labels as production — see `01-current-inventory.md` and `10-conflicts-and-decisions.md`).

**Caution for any future automation or MCP use**: because a Supabase MCP tool in this environment is reported to be wired to `ivrfsjxdfzxrimexvoft` rather than the real active project `gpllrgkuozytyrmpfwbb`, any Stage 3+ tooling that queries live schema via MCP must first confirm which project it is actually talking to — this analysis did not invoke any Supabase MCP tool, precisely to avoid acting on that unverified assumption.

## Frontend (`negotiation-buddy`) Supabase footprint

- **`supabase/config.toml`**: present. Sets `project_id` and per-function `verify_jwt` flags: `false` for `chat`, `summarize-session`, `analyze-progress`, `send-password-reset`, `verify-reset-token`, `analyze-document`; `generate-plan` is not listed (defaults to `verify_jwt = true`).
- **Migrations**: 15 files, `20260309105420` → `20260721090454` (Mar 9 – Jul 21, 2026). Includes one explicit rollback file (`20260416120001_rollback_subscription_tier_values.sql`, marked "do NOT apply unless rollback is explicitly decided").
- **RLS policies**: present — referenced/created across multiple migrations including `20260403120000_add_team_rls_policies.sql` (explicit RLS + snake_case policy migration) and later migrations for `session_history` / added backend columns. `.claude/rules/db-boundaries.md` states RLS is enabled on `negotiation_sessions`.
- **Auth**: Supabase Auth via `config.toml`'s `verify_jwt` settings (see above) — JWT verification is disabled for most functions, a documented and accepted trade-off per `.claude/rules/api-contracts.md`.
- **Storage buckets**: none referenced in the files sampled this pass (no exhaustive repo-wide grep for `.storage.` performed by the discovery agent).
- **Edge functions** (7 total, `supabase/functions/`):
  - `chat` — SSE streaming chat; transforms Anthropic stream → OpenAI-compatible SSE; the only one called directly from the frontend per `docs/lovable-workspace-knowledge.md`.
  - `generate-plan` — negotiation plan generation, requires Bearer JWT, uses service-role client.
  - `analyze-progress` — progress analysis, requires Bearer JWT.
  - `analyze-document` — document analysis, also does an Anthropic→OpenAI stream transform.
  - `summarize-session` — session summarization, requires Bearer JWT.
  - `send-password-reset` — password reset email via Resend, generates reset token.
  - `verify-reset-token` — verifies reset token, SHA-256 hashed.
- **Generated types**: `src/integrations/supabase/types.ts` — hook-protected from direct edit (`protected-file-warn.sh`), though `tasks/lessons.md` documents one prior user-approved manual `sed`-based bypass.
- **Environment separation**: weak/implicit — a single `config.toml` with one `project_id`; no local/staging/prod split found. `.env.local` (gitignored, present on disk) carries an undocumented variable `VITE_DEV_TIER_MOCK` not listed in `.env.example`.

## Backend (`negotiationcoach-backend`) Supabase footprint

- **No `supabase/config.toml`** in this repo — confirmed absent; local CLI project linkage is not version-controlled here (project ref is only recoverable from the gitignored `supabase/.temp/project-ref` cache).
- **Migrations**: 8 files, `20260320162431` → `20260721131832` (add_model_routing_columns, add_team_rls_policies, add_analysis_columns_to_negotiation_sessions, fix_negotiation_id_constraint, session_history_message_count_trigger, create_knowledge_graph, create_opponent_simulation_tables, create_simulation_sessions). `YYYYMMDDHHMMSS_description.sql` naming, append-only discipline documented and apparently followed.
- **RLS policies**: present — explicit policy SQL in `20260403120000_add_team_rls_policies.sql` (10 policies across `teams`/`team_members`/`team_training_tasks`); `docs/db-map.md` documents pre-existing RLS on `negotiation_sessions`/`session_history` applied outside a migration file (presumably via dashboard).
- **Auth**: no local `config.toml`; consumed via `@supabase/supabase-js` `auth.getUser(token)` in `src/api/middleware.ts`, tier read from JWT `user_metadata.tier`/`app_metadata.tier`.
- **Storage buckets**: none referenced in `src/` or `supabase/functions/` per the discovery agent's grep.
- **Edge functions**: one — `negotiate` (`supabase/functions/negotiate/index.ts`), a thin Deno proxy forwarding to the Node backend's `/api/analyze`. An orphaned empty `_shared/` directory remains (previously held duplicate Layer-1 logic, retired per ADR-007-A). A second edge function (`chat`, a Gemini prototype) was fully removed per commit history.
- **Generated types**: `src/types/supabase.ts` (referenced as a regeneration target in `tasks/todo.md` RFB-029).
- **Environment separation**: `tasks/lessons.md` L-004 documents historical churn across 2-3 Supabase projects (see "Historical project-reference churn" above) and notes (L-006) that migrations must be *duplicated* into the sibling frontend repo since the two repos' `supabase db push` targets are configured independently even though — per this analysis — they currently resolve to the same project.

## Shared-context's own Supabase documentation

`docs/infrastructure/supabase-instances.md` (in shared-context) is the one place meant to be the authoritative cross-repo map of this boundary — and it is currently wrong (see `01-current-inventory.md` and `10-conflicts-and-decisions.md`): it labels the retired `ujnyioggxipvuxxxcivr` project as production, not the actual active `gpllrgkuozytyrmpfwbb`. This is flagged as the single highest-risk stale document found across the entire inventory, precisely because it sits in the one repo meant to be the cross-repository control plane.

## Open questions carried into Stage 2

- ~~Whether the "separate frontend/backend Supabase instances" framing in `04-repository-registry.yaml` was ever true historically...~~ **RESOLVED 2026-09-04 (owner decision C2, see `10-conflicts-and-decisions.md`)**: regardless of history, the shared single-project model is the confirmed intended architecture going forward. `04-repository-registry.yaml`'s separate-instance framing is superseded for all target-state work in this migration.
- Whether the Supabase MCP tool's reported wrong-project connection (`ivrfsjxdfzxrimexvoft`) is still true today — **still open**, unaffected by the owner's C2 decision. This analysis deliberately did not invoke Supabase MCP tools to check, to avoid acting on live infrastructure state under `ANALYZE_ONLY` / `ALLOW_PRODUCTION_CHANGES: false`. Re-verifying this (read-only, e.g. `get_project_url`/`list_tables` against the *expected* project ref `gpllrgkuozytyrmpfwbb`) is a reasonable Stage 3 pre-check, not a Stage 2 action.
- Whether any true environment separation (local/staging/prod) exists for this single shared project, or whether "the" project *is* production with no lower environment — no evidence of a second project/environment was found in either repo. **Still open** — this is exactly the kind of question the new governance section below turns into an explicit rule requirement rather than leaving implicit.

## Governance implications of the shared instance (owner-directed assessment, 2026-09-04)

Per the owner's instruction to evaluate the shared-instance architecture on its actual security and ownership boundaries rather than treat sharing itself as a defect, this section lists what a *governed* shared-Supabase-project model needs that today's repository evidence shows is either present, weak, or missing. None of these are migration actions taken by this pass — they are candidate `sdlc/policies/supabase.md` content for Stage 3, replacing the kit's current draft `POL-SUP-001` wording (which forbids the status quo — see `10-conflicts-and-decisions.md` C2).

| Governance dimension | Current evidence (Stage 1) | Gap for a *shared* instance specifically |
|---|---|---|
| **Migration coordination** | Each repo has its own `supabase/migrations/*` directory, both targeting the same project; backend `tasks/lessons.md` L-006 documents that migrations must be *manually duplicated* into the sibling repo because `supabase db push` is configured independently per repo even though both resolve to the same project | Highest-priority real gap: no automated check that a migration applied from one repo's CLI session doesn't silently drift from the other repo's migration history for the same live schema. A shared instance needs either (a) one designated repo as the sole migration-apply path, or (b) a reconciliation check before any `db push`. Not decided by this analysis — an owner/Stage-3 decision. |
| **Schema/table ownership** | RLS policies exist in both repos' migrations (`add_team_rls_policies.sql` in each) for overlapping tables (`negotiation_sessions`, `session_history`, `teams`/`team_members`) | No single documented "which repo owns which table's schema changes" map exists for the shared project — `docs/infrastructure/supabase-instances.md` (once corrected, see `09-proposed-file-diffs.md` Diff 1) is the natural home for this, and should be expanded beyond just "which project ID" to include a per-table ownership column |
| **Auth/JWT boundary** | Both frontend (`config.toml` `verify_jwt` per-function) and backend (`auth.getUser(token)` in `middleware.ts`) independently consume the same project's JWTs; tier is read from `user_metadata.tier`/`app_metadata.tier` | Two independent JWT-consumption implementations against one shared identity provider is a real dual-maintenance risk (already partially tracked as HIGH-03 "three incompatible tier systems" in `shared-context/AGENTS.md`) — not new, but the shared-instance framing makes it more clearly one governance surface, not two |
| **Access-control (who/what can write)** | No RLS-policy inventory cross-check was performed this pass (out of scope for read-only Stage 1); VG-01/VG-02 in `shared-context/AGENTS.md` ("Do Supabase RLS policies on `teams`/`team_members` enforce `admin_user_id = auth.uid()`?", "Does RLS on `negotiation_sessions` prevent cross-user reads with anon_key?") are still open per that file | These pre-existing open verification gaps become *more* consequential under a confirmed-shared-instance model, since both frontend anon-key access and backend service-role access hit the same tables — recommend VG-01/VG-02 resolution be sequenced ahead of or alongside any new `supabase.md` policy, not after |
| **Service-role key custody** | Backend holds a service-role key (per `SUPABASE_URL`/service usage in `negotiationcoach-backend/.env`); frontend uses only the publishable/anon key (`VITE_SUPABASE_PUBLISHABLE_KEY`) | Consistent with least-privilege (frontend never holds service-role), which is a point *in favor* of the current shared-project model rather than against it — worth stating explicitly in the corrected `supabase.md` policy so it isn't miscast as unmanaged sharing |
| **Environment separation** | No evidence of a second (staging/dev) Supabase project for either repo — "the" project appears to be production with no lower environment | A real, if unglamorous, gap independent of the sharing question: neither repo can currently test a schema change without touching the live project. Flag as a candidate future governance/infra item, not something this migration proposes to fix |

**Recommendation for Stage 3** (not a decision made by this analysis): rewrite `sdlc/policies/supabase.md`'s `POL-SUP-001` from "never assume shared identity" (which the owner has now settled as false — it *is* shared, deliberately) to a set of affirmative controls for the confirmed shared model: (1) a single documented migration-apply path or reconciliation rule, (2) a per-table ownership map in the corrected `docs/infrastructure/supabase-instances.md`, (3) explicit tracking of VG-01/VG-02 RLS verification as a precondition for any new feature touching shared tables, (4) an explicit statement that service-role custody stays backend-only (already true, should be codified rather than left implicit).
