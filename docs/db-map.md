# DB Access Pattern Map — NegotiationCoach AI

> Classification legend: **Observed** | **Inferred** | **Missing** | **Proposed**
> Last updated: 2026-04-09

Canonical reference for which service reads and writes each Supabase table, what key is used, and whether RLS is active. Used to identify ownership violations and unguarded access paths.

---

## Access Pattern Summary

| Table | Reader(s) | Writer(s) | Key Used (write) | RLS Active | Canonical Owner |
|-------|-----------|-----------|-----------------|------------|-----------------|
| `negotiation_sessions` | Railway (`GET /api/sessions/:id`), Frontend SDK (reads) | Railway (`POST /api/sessions`, `PATCH /api/sessions/:id`, `POST /api/analyze`, `POST /api/enrich`) + Frontend SDK (violation — Phase B pending) | SERVICE_ROLE_KEY (Railway); anon key (frontend violation) | Yes — `user_sees_own_sessions` (pre-existing, verified 2026-04-09) | Railway backend |
| `session_history` | Frontend SDK (`useSessionManager.ts` — direct select, last 50) | Railway (`POST /api/sessions/:id/messages` — RFB-031 fixed `2c51cb4`) + Frontend SDK (violation — Phase B pending) | SERVICE_ROLE_KEY (Railway); anon key (frontend violation) | Yes — `user_sees_own_session_history` (pre-existing, verified 2026-04-09) | Railway API (`sessionRoutes.ts`) |
| `teams` | Frontend SDK (`TeamDashboard.tsx`) | Railway (`POST /api/teams`, Phase A DONE commit `0b10d9c`) | SERVICE_ROLE_KEY (Railway); anon key removed (Phase B complete) | Yes — migration `20260403120000` (snake_case policies) | Railway backend |
| `team_members` | Frontend SDK (`TeamDashboard.tsx`) | Railway (`POST /api/teams/:id/members`, `DELETE /api/teams/:id/members/:userId`) | SERVICE_ROLE_KEY (Railway) | Yes — migration `20260403120000` | Railway backend |
| `team_training_tasks` | Frontend SDK (`TeamDashboard.tsx`) | Frontend SDK (`supabase.from('team_training_tasks').update()`) — Phase C write migration pending | anon key (frontend) | Yes — migration `20260403120000` | Supabase DB (interim) → Railway (Phase C) |
| `knowledge_graph` | Railway Layer 2 (cache hit check) | Railway Layer 2 (`knowledge_graph` INSERT on cache miss) | SERVICE_ROLE_KEY | Inferred — no confirmation | Railway backend (Layer 2) |
| `user_profiles` | Frontend (`Profile.tsx`) | Frontend (`Profile.tsx` → `.update()`) | anon key + RLS | Inferred — no confirmation | Supabase DB |

---

## Session Tables — Detailed Access Map

### `negotiation_sessions`

**Columns of interest:** `id`, `user_id`, `title`, `mode`, `status`, `persona_type`, `layer1_result`, `layer2_result`, `task_type`, `model_used`, `model_degraded`, `created_at`, `updated_at`

| Operation | Caller | Method | Auth | Business Rule |
|-----------|--------|--------|------|---------------|
| CREATE | Railway `POST /api/sessions` | `supabase.from('negotiation_sessions').insert()` | SERVICE_ROLE_KEY | Title truncated to 40 chars server-side |
| UPDATE (metadata) | Railway `PATCH /api/sessions/:id` | `.update()` | SERVICE_ROLE_KEY | `assertSessionOwner()` guards — returns 404 for wrong owner (hides existence) |
| UPDATE (analysis) | Railway `POST /api/analyze` / `POST /api/analyze-full` | `.update({ layer1_result })` | SERVICE_ROLE_KEY | Ownership verified via route authMiddleware |
| UPDATE (enrichment) | Railway `POST /api/enrich` | `.update({ layer2_result })` | SERVICE_ROLE_KEY | Tier gate: kmu/profi only |
| READ (single) | Railway `GET /api/sessions/:id` | `.select().eq('id').eq('user_id')` | SERVICE_ROLE_KEY | User ownership scoped in query |
| CREATE (violation) | Frontend `useSessionManager.ts` | `supabase.from('negotiation_sessions').insert()` | anon key | No server-side title enforcement — **Phase B pending** |
| UPDATE (violation) | Frontend `useSessionManager.ts` | `.update({ status: 'archived' })` | anon key | Direct SDK — bypasses Railway — **Phase B pending** |
| READ | Frontend `useSessionManager.ts` | `.select()` | anon key | User-scoped via Supabase auth context |

**RLS Status:** Pre-existing policy `user_sees_own_sessions` (FOR ALL, USING `auth.uid() = user_id`) confirmed 2026-04-09 (RFB-030). SERVICE_ROLE_KEY bypasses RLS for Railway writes — no conflict. Code-level guard (`assertSessionOwner()`) provides defence-in-depth.

---

### `session_history`

**Columns of interest:** `id`, `session_id`, `role`, `content`, `created_at`

| Operation | Caller | Method | Auth | Business Rule |
|-----------|--------|--------|------|---------------|
| INSERT | Railway `POST /api/sessions/:id/messages` | `supabase.from('session_history').insert()` | SERVICE_ROLE_KEY | Count-before-insert enforces 50-message limit (non-atomic — DB constraint pending RFB-004-C) |
| SELECT | Frontend `useSessionManager.ts` | `.select().eq('session_id').order('created_at').limit(50)` | anon key | Last 50 messages, user-scoped via session ownership |
| INSERT (violation) | Frontend `useSessionManager.ts` | `supabase.from('session_history').insert()` | anon key | Fire-and-forget with retry — no 50-message limit enforced client-side — **Phase B pending** |

**RLS Status:** Pre-existing policy `user_sees_own_session_history` (FOR ALL, transitive ownership via `negotiation_sessions.user_id`) confirmed 2026-04-09 (RFB-030). No migration needed.

**RFB-031 CLOSED `2c51cb4` (2026-04-09):** Both `.from('session_messages')` calls renamed to `.from('session_history')`. `turn_number: (count ?? 0) + 1` added to INSERT. Railway message writes now functional.

**Note:** `session_history` origin is untracked — no `CREATE TABLE` migration exists in either repo. Confirmed schema (live DB, 2026-04-09): `id`, `session_id`, `turn_number`, `role`, `content`, `metadata`, `created_at`.

---

### `teams` / `team_members` / `team_training_tasks`

**RLS Status:** Active — migration `20260403120000` (negotiation-buddy) applied 10 snake_case policies. Admin enforcement (`admin_user_id = auth.uid()`) verified at DB level (RFB-002 resolution).

See `docs/bounded-contexts.md § BC-05` for write path details.

---

## No-RLS Risk Register

Tables with confirmed absence of RLS policies:

| Table | Risk | Blocking Migration | Notes |
|-------|------|-------------------|-------|
| ~~`negotiation_sessions`~~ | ~~High~~ | ~~RFB-030~~ | **RESOLVED 2026-04-09** — `user_sees_own_sessions` policy confirmed pre-existing |
| ~~`session_history`~~ | ~~High~~ | ~~RFB-030~~ | **RESOLVED 2026-04-09** — `user_sees_own_session_history` policy confirmed pre-existing |
| `knowledge_graph` | Medium — inferred, no confirmation | None registered | Shared cache; user_id column presence unconfirmed |

---

## Verification Gaps

| VG-ID | Question | Risk |
|-------|----------|------|
| ~~VG-02~~ | ~~Does RLS on `negotiation_sessions` exist?~~ **RESOLVED 2026-04-09** — `user_sees_own_sessions` policy confirmed. No conflict with `assertSessionOwner()` (SERVICE_ROLE_KEY bypasses RLS for Railway writes). | ~~High~~ |
| VG-DB-01 | `session_history` confirmed in live DB (RFB-030, 2026-04-09). Schema: id, session_id, turn_number, role, content, metadata, created_at. No `CREATE TABLE` migration exists in either repo — table origin untracked. Low priority. | Low |
| VG-DB-02 | Does `knowledge_graph` have a `user_id` column? Is RLS active? | Medium |
| VG-04 | What creates the initial `user_profiles` row on signup? INSERT never observed in either repo. | Medium |
