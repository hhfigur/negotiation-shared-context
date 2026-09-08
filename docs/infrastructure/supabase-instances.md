# Supabase Instance Map

**Last updated:** 2026-09-04
**Status:** Authoritative — always refer here, never guess

## Current active project (owner-confirmed, 2026-09-04)

- **Project ID:** `gpllrgkuozytyrmpfwbb`
- **Used by:** Both `negotiation-buddy` (frontend) and `negotiationcoach-backend` (backend) —
  **intentionally shared**, confirmed as the project owner's authoritative architecture decision.
  This is not a defect and is not a candidate for a split-instance migration.
- **Confirmed via:** `negotiation-buddy/supabase/config.toml`, both repos' `supabase/.temp/project-ref`,
  and both repos' `MEMORY.md`.
- **Governance of the shared model:** see `../../sdlc/policies/supabase.md` for the approved
  governance controls (RLS enforcement, authentication/JWT boundary, service-role custody,
  frontend-vs-backend access rights, schema/migration/table/Edge-Function ownership, environment
  separation, privileged-access auditability). This file records *what* the project is; that file
  records *how* it must be governed.

## Historical / retired project IDs — documentation debt, not currently operationally relevant

These IDs appeared in earlier versions of this document and in both repos' `tasks/lessons.md`.
Per owner instruction (2026-09-04): treat as documentation debt unless repository evidence shows
otherwise. No repository evidence found in this migration's discovery contradicts that.

- `ujnyioggxipvuxxxcivr` — previously labeled "Lovable/Railway shared" production project in an
  earlier version of this file. Not the current active project. Also once accidentally committed
  to a `.env` file (see `negotiation-buddy/tasks/lessons.md`) — treat as a legacy footgun, not a
  live target for any tool or credential.
- `ivrfsjxdfzxrimexvoft` — previously labeled a "local development" project. Not the current
  active project. **Caution:** `negotiationcoach-backend/tasks/lessons.md` (entry L-004) reports
  that this environment's Supabase MCP tool may still be wired to this retired project rather than
  the current active one. This was **not independently re-verified** during the migration analysis
  (deliberately avoided invoking live MCP tools under `ANALYZE_ONLY`). Before relying on any
  Supabase MCP tool output (`list_tables`, `execute_sql`, etc.) in this environment, confirm which
  project it actually reaches — do not assume it is `gpllrgkuozytyrmpfwbb`.

## Access matrix

| Tool | Current active (`gpllrgkuozytyrmpfwbb`) |
|---|---|
| `negotiation-buddy` (frontend) | Anon/publishable key only (`VITE_SUPABASE_PUBLISHABLE_KEY`) — no service-role key present in this repo |
| `negotiationcoach-backend` (backend) | Service-role key (`SUPABASE_SERVICE_KEY` / `SERVICE_ROLE_KEY`) — bypasses RLS; ownership enforced in application code |
| Supabase CLI (`db push`) | Each repo pushes to this project independently from its own `supabase/migrations/` directory — see the migration-coordination note below |
| This environment's Supabase MCP tool | **Unverified this pass** — see caution above |

## Migration coordination (real, evidence-backed gap)

Both repositories maintain their own `supabase/migrations/*.sql` directory targeting this same
live project. Several migrations in each repo exist specifically to reconcile schema drift with
the other repo (e.g. frontend's `20260515120000_align_negotiation_sessions_schema.sql`, backend's
`20260721131832_create_simulation_sessions.sql`). `negotiationcoach-backend/tasks/lessons.md`
(L-006) documents that migrations must currently be manually duplicated across repos. There is no
single designated migration-apply path or automated reconciliation check today. See
`../../sdlc/policies/supabase.md` control 3 for the recommended governance approach — not yet
implemented, tracked as an open item, not resolved by this migration pass.

## Auth architecture

JWT tokens are issued by the shared project (`gpllrgkuozytyrmpfwbb`). Both repos independently
consume these tokens: the frontend via `supabase.auth.getSession()`/`getUser()` client-side, the
backend via `supabase.auth.getUser(token)` server-side in `src/api/middleware.ts`. Tier is read
from JWT `user_metadata.tier`/`app_metadata.tier` (backend) or via `persona_type` mapping
(frontend) — see `docs/decision-log/ADR-006-tier-mapping.md`.

Reference: `docs/decision-log/ADR-001-system-boundaries.md`
