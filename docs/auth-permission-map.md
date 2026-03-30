# Auth & Permission Map — NegotiationCoach AI

> Classification legend: **Observed** | **Inferred** | **Missing** | **Proposed**
> Last audit: 2026-03-27

---

## 1. Auth Architecture

```
Browser
  └─ useAuth.tsx
       ├─ supabase.auth.signUp(email, password) ──────────────────┐
       ├─ supabase.auth.signIn(email, password)                   │
       ├─ supabase.auth.resetPasswordForEmail(email)              │
       └─ supabase.auth.updateUser({password})                    │
                                                                   ▼
                                                         Supabase Auth
                                                         (JWT issued)
                                                               │
                               ┌───────────────────────────────┘
                               │ JWT (Bearer token)
              ┌────────────────┼────────────────────────┐
              ▼                ▼                         ▼
    Railway Express       Supabase SDK            Supabase Edge
    authMiddleware        (anon key)              Functions
    (validates JWT)       (for direct DB          (JWT-validated
                          writes from frontend)    by runtime)
```

---

## 2. Token Flow

### 2.1 Browser-to-Railway
- Frontend obtains JWT access token via `supabase.auth.getSession().data.session.access_token`
- Sends as `Authorization: Bearer <token>` header to Railway API
- Railway validates token via `supabase.auth.getUser(token)` in `authMiddleware.ts`

**Duplication (Observed):** Token fetching via `supabase.auth.getSession()` is repeated in at least 6 files:
- `useSessionManager.ts`
- `NegotiationCanvas.tsx`
- `DebriefDashboard.tsx`
- `ZopaCalculator.tsx` (inferred)
- `WhatIfSimulator.tsx` (inferred)
- `ChatInterface.tsx` (inferred)

No central `getToken()` accessor exists in `useAuth.tsx`.

### 2.2 Browser-to-Supabase Direct
- Supabase client initialized with **anon key** (VITE_SUPABASE_PUBLISHABLE_KEY)
- Auth session in localStorage provides user context to Supabase JS SDK
- RLS policies on Supabase tables filter results by `auth.uid()`
- Direct writes from browser are subject to RLS only (no Railway validation layer)

### 2.3 Browser-to-Edge-Function
- `useChat.ts` calls Supabase Edge Function `/functions/v1/chat` with the anon key as Authorization header
- Edge Function runtime validates JWT internally (Supabase Deno runtime)

---

## 3. Railway Backend: Auth Middleware

**File:** `src/api/middleware.ts`

```
Request received
  → Extract Bearer token from Authorization header
  → If no token OR validation fails:
       → fallback: req.user = { id: 'anonymous', tier: 'privat' }  ← NEVER REJECTS
  → If valid token:
       → req.user = { id: user.id, tier: from JWT metadata || 'privat' }
  → next()
```

**CRITICAL (Observed):** `authMiddleware` **never returns 401**. Any request — with or without a valid token — proceeds. The anonymous user gets `tier: 'privat'`, which grants access to Layer 1 analysis. This is documented as intentional dev-mode behavior pending production hardening.

**Consequence:** The Railway API has no auth enforcement in its current state. Tier gating is the only access control that functions.

---

## 4. Tier Hierarchy & Feature Gates

### 4.1 Tier Hierarchy (Railway)
```
free (0) < privat (1) < kmu (2) < profi (3)
```

### 4.2 Feature Gate Map

| Endpoint / Feature | Min Tier | Gate Type | Enforced By |
|-------------------|----------|-----------|-------------|
| `GET /api/health` | none | none | — |
| `POST /api/chat` | none | implicit | tier read, not gated |
| `POST /api/plan` | none | implicit | tier read, not gated |
| `POST /api/analyze` | none | implicit | tier read for model routing |
| `POST /api/enrich` | kmu | **explicit** | `requireTier('kmu')` middleware |
| `POST /api/analyze-full` | none (auto-skips L2 for free/privat) | implicit | `layer2/index.ts` tier check |
| `GET /api/sessions/:id` | none | user_id check | `.eq('user_id', req.user.id)` |
| Layer 2 market data | kmu | implicit | `layer2/index.ts` early return |
| Opus model (what_if) | profi | implicit | `modelRouter.ts` — but `/api/chat` and `/api/plan` bypass modelRouter |
| Team operations | none | **frontend-only** | `admin_user_id === user.id` in React |

### 4.3 Model Routing by Tier (modelRouter.ts — partially bypassed)
| Task | free | privat | kmu | profi |
|------|------|--------|-----|-------|
| validate_input | haiku | haiku | haiku | haiku |
| strategy_coaching | haiku | sonnet | sonnet | sonnet |
| what_if_analysis | haiku | sonnet | sonnet | **opus** |
| opponent_simulation | haiku | sonnet | sonnet | **opus** |
| executive_summary | haiku | sonnet | sonnet | **opus** |

**Bypass (Observed):** `/api/chat` hardcodes `claude-haiku-4-5-20251001`. `/api/plan` hardcodes `claude-sonnet-4-6`. Neither calls `modelRouter.selectModel()`. Tier-based model degradation does not apply to these endpoints.

---

## 5. Database Access Control

### 5.1 Railway Backend (SERVICE_ROLE_KEY)
**Observed:** All Railway Supabase queries use `SUPABASE_SERVICE_KEY` which **bypasses RLS**. Access control is enforced in code:
- All session reads/writes include `.eq('user_id', req.user.id)` or `.eq('user_id', userId)`
- Risk: If `req.user.id` resolves to `'anonymous'` (the fallback), sessions for anonymous users could collide or be exposed if the user_id check is omitted

### 5.2 Frontend (Anon Key + RLS)
**Observed:** Frontend Supabase client uses the anon key. RLS policies are the only access control for frontend-direct DB writes.

| Table | Frontend Writes | RLS Enforcement | Verified |
|-------|----------------|-----------------|---------|
| `negotiation_sessions` | INSERT, UPDATE | Inferred (`owns_session()`) | No |
| `session_messages` | INSERT | Inferred | No |
| `teams` | INSERT, SELECT | Inferred — CRITICAL: admin check frontend-only | No |
| `team_members` | INSERT, SELECT, DELETE | Inferred — CRITICAL: admin check frontend-only | No |
| `team_training_tasks` | INSERT, SELECT, UPDATE | Inferred | No |
| `user_profiles` | SELECT, UPDATE | Inferred (user-scoped) | No |

**All RLS enforcement is inferred, not verified in this audit.** See VG-01 and VG-02 in source-of-truth-matrix.md.

---

## 6. Permission Violation Summary

| ID | Violation | Severity | Classification |
|----|-----------|----------|----------------|
| AUTH-01 | Railway authMiddleware never rejects — no 401 enforced | Critical | Observed |
| AUTH-02 | Team admin check is React UI code only — no server-side enforcement verified | Critical | Observed |
| AUTH-03 | Frontend direct DB writes to teams/team_members bypass all API auth layers | High | Observed |
| AUTH-04 | Token fetching duplicated in 6 frontend files — no centralized accessor | Medium | Observed |
| AUTH-05 | modelRouter bypassed in /api/chat and /api/plan — tier-based model control absent | Medium | Observed |
| AUTH-06 | subscription_tier hardcoded as "free" in Edge Function chat persona | Medium | Observed |
| AUTH-07 | CORS wildcard header overrides allowlist in Railway backend | Medium | Resolved — fixed in `fix(rfb-005)`: wildcard middleware removed, `ngrok-skip-browser-warning` moved to `cors()` `allowedHeaders` |
| AUTH-08 | Railway anon fallback assigns 'privat' tier — free-tier users get privat access without a token | Low | Observed |

---

## 7. Password Security

**Observed:** Password validation implements 5 requirements (8+ chars, upper, lower, digit, special character) across 3 locations:
1. `src/lib/passwordValidation.ts` — canonical definition
2. `Auth.tsx` inline checks — duplication
3. `PasswordStrengthIndicator.tsx` — display duplication

HaveIBeenPwned integration uses k-anonymity (SHA-1 prefix only). Silent failure if HIBP API is down — signup proceeds regardless of breach status.

---

## 8. Proposed Hardening (Not Implemented)

| Priority | Action | Affected Component |
|----------|--------|-------------------|
| P0 | Verify and harden Supabase RLS on teams/team_members | Supabase migrations |
| P0 | Return 401 from Railway authMiddleware on invalid/missing token | middleware.ts |
| P1 | Move team CRUD to Railway API endpoints with server-side admin validation | New Railway routes |
| P1 | Centralize token accessor in useAuth.tsx | Frontend |
| P2 | Integrate modelRouter into /api/chat and /api/plan | chatHelpers.ts, planHelpers.ts, routes.ts |
| P2 | Fix CORS: remove wildcard header or apply after allowlist check | routes.ts |
| P3 | Propagate actual user tier to Edge Function chat persona | useChat.ts |
