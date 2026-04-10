# ADR-002: Data Ownership & Write Path Decisions — NegotiationCoach AI

**Status:** Observed (reconstructed) | Proposed (canonical rules)
**Date Reconstructed:** 2026-03-27
**Classification:** Observed | Proposed

---

## Context

Data ownership is ambiguous across the system because multiple runtimes write to the same Supabase tables using different access mechanisms (service role key via Railway, anon key via frontend). This ADR establishes canonical ownership for each table and write path, identifies current violations, and proposes the target state.

---

## Canonical Ownership Rules

### Rule 1: One Writer Per Business Entity

Each business entity should have exactly one canonical writer responsible for enforcing business rules. Multiple writers to the same table are acceptable only when:
- Each writer is scoped to different columns (e.g., Railway writes `layer1_result`, frontend writes `session_mode`)
- Or one writer is authoritative and the other is read-only projection

**Current Violation:** `negotiation_sessions` is written by both Railway (analysis results) and frontend (session metadata). Business rules for the session live in two places.

---

### Rule 2: Service Role Key = API Layer Only

The Supabase SERVICE_ROLE_KEY bypasses all RLS policies. Its use must be strictly controlled:

**Allowed:** Railway backend only (where user_id validation is enforced in application code)
**Not Allowed:** Frontend, Edge Functions, or any browser-accessible environment

**Current State (Observed):** Correctly used in Railway only.

---

### Rule 3: Anon Key = Read + RLS-Gated Writes Only

The Supabase anon key (VITE_SUPABASE_PUBLISHABLE_KEY) is intentionally public. Any write that uses this key must be protected by a Supabase RLS policy that enforces row ownership.

**Implication:** Every table writable from the frontend MUST have a tested, verified RLS policy. Frontend-only auth checks (React conditionals) are insufficient.

---

## Table Ownership Map

### `negotiation_sessions`

| Property | Current | Proposed |
|----------|---------|---------|
| **Canonical Writer** | Ambiguous (Railway + Frontend) | Railway only |
| **Railway writes** | `layer1_result`, `layer2_result`, `task_type`, `model_used`, `model_degraded`, `user_id` | Same |
| **Frontend writes** | `id`, `user_id`, `title`, `mode`, `persona_type` via `useSessionManager.ts` | **RETIRED** — `useSessionManager.ts` now calls Railway `POST /api/sessions` + `PATCH /api/sessions/:id` via `apiClient.ts`. Migration complete `2415f72` (2026-04-08). |
| **Read** | Frontend direct select + Railway GET /api/sessions/:id | Both acceptable |
| **RLS** | Inferred (owns_session() function exists) | Verify + enforce |
| **Access Control** | Railway: code-enforced `.eq('user_id')` | Unchanged |

**Migration Path:** Add `title`, `mode`, `persona_type` fields to Railway `/api/analyze` and `/api/analyze-full` request bodies. Railway creates the complete session record.

---

### `session_history`

| Property | Current | Proposed |
|----------|---------|---------|
| **Canonical Writer** | Frontend (`useSessionManager.ts`) | Railway |
| **Frontend writes** | All message inserts (fire-and-forget) | **RETIRED** — `useSessionManager.ts` now calls Railway `POST /api/sessions/:id/messages` via `apiClient.ts`. Migration complete `2415f72` (2026-04-08). |
| **Business rules** | Retry logic (2x, 1500ms), load limit (50) in frontend | **MIGRATED** — 50-message limit and ownership enforced server-side. Retry logic removed from frontend. |
| **Read** | Frontend direct select (last 50) | `GET /api/sessions/:id/messages` with server-side pagination |
| **RLS** | Inferred | Verify + enforce |

**Migration Path:** Railway endpoint `POST /api/sessions/:id/messages` validates ownership, enforces limits, and handles persistence. Frontend fires and awaits acknowledgment.

---

### `teams`

| Property | Current | Proposed |
|----------|---------|---------|
| **Canonical Writer** | Frontend (`TeamDashboard.tsx`) | Railway |
| **Frontend writes** | INSERT (create team) | **RETIRED** — `POST /api/teams` |
| **Business rules** | Admin assignment, team naming | Move to Railway |
| **Admin validation** | Frontend React conditional only (**CRITICAL GAP**) | Server-side: `admin_user_id = req.user.id` check |
| **RLS** | Unknown — **MUST VERIFY** | Enforce `admin_user_id = auth.uid()` for mutations |

---

### `team_members`

| Property | Current | Proposed |
|----------|---------|---------|
| **Canonical Writer** | Frontend (`TeamDashboard.tsx`) | Railway |
| **Frontend writes** | INSERT, DELETE | **RETIRED** — `POST/DELETE /api/teams/:id/members` |
| **Admin validation** | Frontend-only (**CRITICAL GAP**) | Server-side |
| **RLS** | Unknown — **MUST VERIFY** | Enforce team admin ownership |

---

### `team_training_tasks`

| Property | Current | Proposed |
|----------|---------|---------|
| **Canonical Writer** | Frontend (`TeamDashboard.tsx`) | Railway |
| **Frontend writes** | INSERT, UPDATE | **RETIRED** — Railway team task endpoints |
| **RLS** | Unknown | Enforce |

---

### `user_profiles`

| Property | Current | Proposed |
|----------|---------|---------|
| **Canonical Writer** | Frontend (`Profile.tsx`) | Shared (frontend for preferences, Railway for tier sync) |
| **Frontend writes** | UPDATE (persona_type, experience_level, preferred_frameworks) | Acceptable — user-scoped, RLS enforces |
| **Initial INSERT** | **Missing** — creation mechanism not found | Supabase trigger on auth.users insert (standard pattern) |
| **RLS** | Inferred | Verify: `user_id = auth.uid()` for all mutations |
| **Tier field** | Not present — persona_type is a separate concept | **Proposed:** Add `tier` column synced from JWT metadata |

---

### `knowledge_graph`

| Property | Current | Proposed |
|----------|---------|---------|
| **Canonical Writer** | Railway Layer 2 only | Unchanged |
| **Frontend writes** | None | Unchanged |
| **Read** | Railway Layer 2 only | Unchanged |
| **TTL** | 7 days (valid_until column) | Consider shorter TTL for volatile markets |

---

### `knowledge_base` (read-only)

| Property | Current | Proposed |
|----------|---------|---------|
| **Canonical Writer** | Inferred: admin/seeded data | Unchanged |
| **Frontend access** | SELECT only (inferred) | Acceptable via RLS |

---

### `knowledge_queue`

| Property | Current | Proposed |
|----------|---------|---------|
| **Canonical Writer** | **Missing** — infrastructure exists (table + Edge Function tag extraction) but no submission path | Frontend write via Edge Function submission endpoint |
| **Frontend writes** | None (candidates accumulate in localStorage only) | `POST /functions/v1/submit-knowledge` |
| **Review flow** | None | Proposed: admin review before promotion to knowledge_base |

---

## Tier System Ownership

**Current State (Critical Gap):** Three incompatible representations exist:

| Representation | Location | Values |
|----------------|----------|--------|
| JWT user_metadata.tier | Supabase Auth | `free \| privat \| kmu \| profi` (inferred) |
| Railway Tier type | src/types/index.ts | `free \| privat \| kmu \| profi` |
| DB persona_type enum | Supabase schema | `pro \| kmu \| private` |
| Edge Function chat | useChat.ts line | `"free"` (hardcoded) |

**Proposed Canonical Rule:**
- **Single Source of Truth:** JWT `app_metadata.tier` with values `free | privat | kmu | profi` (Railway definition)
- **persona_type** is renamed to **ui_persona** and decoupled from subscription tier
- **subscription_tier** in Edge Function chat payload is populated from `supabase.auth.getSession().data.session.user.app_metadata.tier`
- **user_profiles** gains a `current_tier` column (read-only, synced from JWT by webhook)
- Frontend reads tier from `useAuth().user.app_metadata.tier`, not from persona_type

---

## Write Path Decision Tree (Proposed)

```
Is the write a user auth operation?
  └─ YES → useAuth.tsx → supabase.auth.* methods (only)

Is the write updating a user's own preferences (profile, persona)?
  └─ YES → Direct SDK write acceptable IF RLS verified → supabase.from('user_profiles').update()

Is the write a business entity mutation (session, message, team)?
  └─ YES → MUST go through Railway API
           → railway.POST('/api/...') with Bearer JWT
           → Railway validates ownership, enforces rules, writes with SERVICE_ROLE_KEY

Is the write streaming chat?
  └─ YES → Edge Function /chat (SSE) — no DB writes from frontend

Is the write a new table with no existing pattern?
  └─ DEFAULT: Railway API endpoint required
  └─ Must have RLS policy before any direct frontend access is considered
```

---

## Consequences of These Rules

### Short-term (accepted inconsistencies during migration)
- Frontend direct writes to negotiation_sessions, session_history, teams remain until Railway CRUD endpoints are built
- persona_type and tier remain separate systems until a migration is planned

### Medium-term (target state)
- All business entity writes flow through Railway
- Team admin authorization is server-enforced
- Single tier enum across all runtimes

### Long-term
- Frontend is a pure view layer with no business rules in hooks
- All data persistence rules are testable via Railway API tests
- RLS policies serve as a defense-in-depth layer, not the primary access control
