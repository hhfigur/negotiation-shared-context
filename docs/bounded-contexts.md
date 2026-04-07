# Bounded Contexts — NegotiationCoach AI

> Classification legend: **Observed** | **Inferred** | **Missing** | **Proposed**
> Last audit: 2026-03-27

---

## Overview

The system contains six meaningful bounded contexts. Each context has a canonical owner, a primary datastore, and defined write/read paths. Where a context spans multiple runtimes without a clear owner, this is marked as a **violation**.

---

## BC-01 · Identity & Auth

**Canonical Owner:** Supabase Auth
**Primary Datastore:** Supabase Auth schema (not PostgreSQL tables)
**Business Logic Owner:** Supabase + Railway middleware

### Write Path
- Sign-up / sign-in / password reset → `supabase.auth.*` calls from frontend `useAuth.tsx`
- Session token stored in browser `localStorage` automatically by Supabase JS
- Tier metadata written to `user_metadata` / `app_metadata` on JWT — **Inferred** written by Stripe webhooks

### Read Path
- Frontend: `useAuth().user` from `onAuthStateChange` listener
- Railway backend: `supabase.auth.getUser(token)` in `authMiddleware.ts`
- Edge Functions: Supabase JWT verification (built-in)

### Sync / Projection Rule
JWT carries tier as `user.user_metadata.tier` or `user.app_metadata.tier`. Railway reads this on every request. No caching.

### Auth / Permission Owner
Supabase Auth (issuance) + Railway `authMiddleware` (validation)

### Violations / Ambiguities
- **RESOLVED 2026-04-03 — fd68e1e:** 401 enforced for missing/invalid tokens. `AUTH_REQUIRED=false` provides explicit dev bypass. Default tier for tokens with no metadata: `'free'`.
- **Missing:** Stripe webhook → `user_metadata.tier` update path is not visible in either repo. Mechanism assumed but unverified.
- **Observed:** Frontend calls `supabase.auth.getSession()` in 6 different files to extract Bearer token rather than using a centralized accessor.

---

## BC-02 · Negotiation Analysis Engine

**Canonical Owner:** Railway backend (`negotiationcoach-backend`)
**Primary Datastore:** `negotiation_sessions` table (layer1_result, layer2_result columns)
**Business Logic Owner:** `src/layer1/` (algorithms), `src/layer2/` (enrichment)

### Write Path
- Frontend → `POST /api/analyze-full` → Layer 1 algorithms → Layer 2 enrichment → `negotiation_sessions` INSERT/UPDATE via service-role key
- Optionally via `/api/analyze` (Layer 1 only) + `/api/enrich` (Layer 2 only)

### Read Path
- Frontend ← `GET /api/sessions/:id` ← `negotiation_sessions` SELECT
- Results also held in `AnalysisContext` (localStorage) for in-session display

### Sync / Projection Rule
Analysis results are computed on-demand. The `negotiation_sessions` record is created at `/api/analyze` and updated (layer2_result) at `/api/enrich`. AnalysisContext mirrors the last result in localStorage.

### Auth / Permission Owner
Railway `authMiddleware` + `requireTier('kmu')` gate on `/api/enrich`

### Violations / Ambiguities
- **CRITICAL:** Layer 1 algorithms (ZOPA, Nash Bargaining, Monte Carlo, Deadline Effect, Strategy Score) are **duplicated** in:
  - `src/layer1/` — Express path, uses `own_target / own_minimum / opponent_estimated_max / opponent_estimated_min`
  - `supabase/functions/_shared/engine/` — Edge Function path, uses `user_goal / user_walkaway / counterpart_goal / counterpart_walkaway`
  - These schemas are **incompatible**. Any algorithm change must be applied in both locations. No mechanism enforces this. (Observed)
- **Observed:** Tests in `tests/layer1/` reference the Edge Function schema (stale). Tests are broken and should not be trusted.

---

## BC-03 · Chat & Input Extraction

**Canonical Owner:** Supabase Edge Function `/chat`
**Primary Datastore:** `session_messages` table
**Business Logic Owner:** Shared — Edge Function (streaming, tag extraction) + `chatHelpers.ts` in Railway (fallback, non-streaming)

### Write Path
- Frontend `useChat.ts` → SSE POST to `supabase/functions/v1/chat` → streams tokens back
- Frontend `useSessionManager.ts` → `supabase.from('session_messages').insert()` directly (no API intermediary)

### Read Path
- Resume: `useSessionManager.ts` → `supabase.from('session_messages').select()` last 50 messages
- Real-time: streamed directly from Edge Function

### Sync / Projection Rule
`AnalysisContext.messages[]` holds in-session chat history. `session_messages` table holds persisted history. Frontend syncs both on save (fire-and-forget with 2 retries).

### Auth / Permission Owner
Supabase anon key (for Edge Function call), Supabase RLS (inferred via `owns_session()` function in DB schema)

### Violations / Ambiguities
- **HIGH:** `session_messages.insert()` is called fire-and-forget from the browser. PARTIAL: toast surfaced on failure (2026-04-03). Write path ownership moves to Railway in RFB-004. (Observed)
- **Observed:** Railway also has a `/api/chat` endpoint (non-streaming fallback) using a hardcoded `claude-haiku` model, not `modelRouter`. The relationship between this fallback and the Edge Function primary path is undocumented.
- **Inferred:** The Railway `/api/chat` is the original implementation; the Edge Function `/chat` is a later addition. The fallback may be dead code.

---

## BC-04 · Market Intelligence

**Canonical Owner:** Railway backend Layer 2 (`src/layer2/`)
**Primary Datastore:** `knowledge_graph` table (7-day TTL cache)
**Business Logic Owner:** `marketDataResolver.ts`, `webSearch.ts`, `knowledgeGraph.ts`

### Write Path
- Railway Layer 2 → `webSearch.ts` (Claude tool_use with training-data market values) → `knowledge_graph` INSERT with `valid_until = now() + 7 days`

### Read Path
- Railway Layer 2 → `knowledge_graph` SELECT WHERE `valid_until > now()` → cache hit returns cached data
- Cache miss → `webSearch.ts` → store → return

### Sync / Projection Rule
Cache-first, 7-day TTL. No invalidation mechanism exists.

### Auth / Permission Owner
Tier gate: privat/free receive no market data. kmu/profi access Layer 2 enrichment.

### Violations / Ambiguities
- **Inferred:** Despite the name `webSearch.ts`, no external web search API is called. Claude's training-data knowledge is used as the "web search" result. Market data may be stale for rapidly changing markets (e.g., rent prices). Naming is misleading.
- **Missing:** No mechanism to invalidate stale knowledge_graph entries before TTL expires (e.g., after a market shock).

---

## BC-05 · Team Management

**Canonical Owner:** Frontend (`TeamDashboard.tsx`) — **VIOLATION**
**Primary Datastore:** `teams`, `team_members`, `team_training_tasks` tables
**Business Logic Owner:** Railway backend (Phase A complete — commit 0b10d9c)

### Write Path (Phase A complete — Railway endpoints live)
- `POST /api/teams` — Team erstellen, Aufrufer wird admin_user_id
- `POST /api/teams/:id/members` — Mitglied hinzufügen (admin only)
- `DELETE /api/teams/:id/members/:userId` — Mitglied entfernen (admin only)
- `PATCH /api/teams/:id/tasks/:taskId` — Task aktualisieren (admin only)
- **Phase B pending:** TeamDashboard.tsx ruft Supabase noch direkt — Migration folgt

### Read Path
- Frontend `TeamDashboard.tsx` → direct Supabase SDK reads

### Sync / Projection Rule
No server-side projection. All state is read directly from Supabase.

### Auth / Permission Owner
**Observed:** Admin authorization is enforced in frontend React code (`TeamDashboard.tsx ~line 69`) as a UI guard. Supabase RLS now independently enforces admin authorization at the DB layer via migration `20260403120000` — 10 snake_case policies across all three team tables. Any direct SDK call bypassing the React UI is blocked by RLS.

### Violations / Ambiguities
- **Resolved (RFB-002):** RLS now enforced at DB level. Frontend React check remains as redundant UI guard (acceptable). (Observed → Verified)
- **Missing:** Team invite via email does not exist — only link copy. No notification system.
- **Missing:** No audit log for team membership changes.

---

## BC-06 · User Profile & Preferences

**Canonical Owner:** Supabase DB (`user_profiles` table)
**Primary Datastore:** `user_profiles` + `localStorage` (synced copy)
**Business Logic Owner:** Frontend `Profile.tsx`

### Write Path
- Frontend `Profile.tsx` → `supabase.from('user_profiles').update()` → then syncs to localStorage
- No INSERT observed — profile assumed to be auto-created on sign-up (Missing: creation trigger not visible)

### Read Path
- Frontend → `supabase.from('user_profiles').select()` on mount
- Persona type also read from localStorage for fast access

### Sync / Projection Rule
localStorage is written after every successful Supabase update. No TTL. Risk of stale localStorage if update fails partially.

### Auth / Permission Owner
Supabase RLS (inferred — user_profiles likely scoped to `auth.uid()`)

### Violations / Ambiguities
- **RESOLVED 2026-04-03 — RFB-012:** `on_auth_user_created` trigger created on `auth.users`. `handle_new_user()` inserts a default `user_profiles` row (persona_type='private', subscription_tier='free', experience_level=1) on every new sign-up. Backfill not required — 4 existing rows already present.
- **Observed:** The `persona_type` enum (`pro | kmu | private`) does not map to the Railway tier system (`free | privat | kmu | profi`). No translation layer exists in either repo.
- **Observed:** `subscription_tier` sent in chat persona is hardcoded as `"free"` in `useChat.ts`. Actual user tier is not propagated to the Edge Function.

---

## Cross-Context Issues

| Issue | Affected Contexts | Classification |
|-------|------------------|----------------|
| Two incompatible NegotiationInputs type schemas | BC-02, BC-03 | Observed |
| Two incompatible tier enumerations | BC-01, BC-02, BC-06 | Observed |
| Frontend directly writes to DB in BC-03, BC-05, BC-06 without Railway mediation | BC-03, BC-05, BC-06 | Observed |
| ~~Team admin authorization frontend-only~~ **RLS enforced at DB layer — RFB-002** | BC-05 | Resolved |
| Knowledge candidate pipeline broken (extracted, never submitted) | BC-03, BC-04 | Observed |
| `subscription_tier` in chat hardcoded "free" | BC-01, BC-03 | Observed |
