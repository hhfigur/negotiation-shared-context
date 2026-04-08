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
| Write Path | **Missing** — Stripe webhook → Supabase user update (mechanism not visible in either repo) |
| Read Path | Railway: `user.user_metadata.tier \|\| user.app_metadata.tier` in `authMiddleware.ts`; defaults to `'privat'` |
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
| Write Path (create) | Railway `POST /api/analyze` → `supabase.from('negotiation_sessions').insert()` with SERVICE_ROLE_KEY |
| Write Path (update) | Railway `POST /api/enrich` → `.update({layer2_result})` with SERVICE_ROLE_KEY |
| Write Path (frontend) | `useSessionManager.ts` → direct SDK insert/update — **VIOLATION** |
| Read Path | Railway `GET /api/sessions/:id` (owner-scoped) or `useSessionManager.ts` direct select |
| Sync Rule | AnalysisContext (localStorage) mirrors in-session result. DB is written asynchronously (fire-and-forget in session manager). |
| Business Logic Owner | Railway Layer 1/2 (analysis); Frontend useSessionManager (session metadata, title, mode) |
| Auth Owner | Railway: `.eq('user_id', req.user.id)` code-enforced (SERVICE_ROLE_KEY bypasses RLS) |
| Violations | Frontend bypasses API and writes directly to `negotiation_sessions`. Session title truncation (40 chars) and message load limit (50) are business rules enforced only in frontend. |

---

### 4. Session Messages

| Property | Value |
|----------|-------|
| Canonical Owner | **Ambiguous** — Supabase DB schema owns the record, frontend writes it |
| Primary Datastore | `session_messages` table |
| Write Path | `useSessionManager.ts` → direct `supabase.from('session_messages').insert()` — fire-and-forget, 2 retries |
| Read Path | `useSessionManager.ts` → direct select, last 50 messages |
| Sync Rule | In-session: `AnalysisContext.messages[]`; Persisted: `session_messages` table. Sync is eventually consistent (fire-and-forget). |
| Business Logic Owner | Frontend — message save retry logic, message count limit (50), truncation |
| Auth Owner | Supabase RLS (inferred via `owns_session()` function) |
| Violations | No Railway API mediates these writes. Message persistence business rules live in browser JavaScript. Silent failure on message save does not surface to user. |

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
| VG-02 | Supabase RLS on `negotiation_sessions` — is there overlap with Railway's code-enforced user_id check? | High |
| VG-03 | Stripe webhook handler — how is `user_metadata.tier` updated on subscription change? | High |
| VG-04 | Profile creation on sign-up — what creates the initial `user_profiles` row? | Medium |
| VG-05 | Edge Function `/chat` actual tier enforcement — does it read subscription_tier from JWT or use the hardcoded "free"? | Medium |
| VG-06 | Edge Function `generate-plan` — is this actively used, or has Railway `/api/plan` superseded it? | Low |
