# ADR-001: System Boundary Decisions — NegotiationCoach AI

**Status:** Observed (reconstructed from codebase)
**Date Reconstructed:** 2026-03-27
**Classification:** Observed (existing decisions) | Proposed (recommended boundaries)

---

## Context

This ADR reconstructs the implicit system boundary decisions made during development and proposes the canonical boundaries going forward. The system evolved from a Lovable-generated React frontend with direct Supabase access into a two-service architecture (Railway + Supabase). Boundaries were established incrementally and contain inconsistencies.

---

## Observed Boundary Decisions

### Decision 1: Supabase as Identity and Storage Layer

**What was decided:** Supabase handles all auth (JWT issuance, email verification, password reset) and serves as the primary PostgreSQL datastore. Both the React frontend and the Railway backend read from and write to Supabase.

**Rationale (Inferred):** Lovable generates Supabase-integrated frontends by default. Auth and DB were the natural Supabase responsibilities from project inception.

**Current State:** Correct in principle. Implementation has violations:
- Railway uses SERVICE_ROLE_KEY (bypasses RLS) — access control is code-enforced
- Frontend uses anon key with RLS — access control is schema-enforced
- These two access patterns are not coordinated

**Proposed Canonical Rule:**
- Supabase = identity provider and datastore only
- Railway = exclusive write path for all business entity mutations (analysis results, session records, messages)
- Frontend direct writes = allowed ONLY for user-scoped profile updates and where RLS is verified to enforce ownership

---

### Decision 2: Railway as LLM Orchestration Backend

**What was decided:** A separate Express backend on Railway handles all Claude API calls, multi-step algorithm orchestration (Layer 1 + Layer 2), and stateful analysis results.

**Rationale (Inferred):** Claude API calls cannot be made from the browser (API key exposure). A server is required for LLM inference, market data caching, and model routing logic.

**Current State:** Correct. Railway is the canonical owner of analysis computation.

**Violation:** Supabase Edge Function `negotiate/` independently implements the same Layer 1 algorithms (ZOPA, Nash, Monte Carlo) with a different type schema. This creates two competing analysis paths.

**Proposed Canonical Rule:**
- Railway = canonical Layer 1 and Layer 2 analysis owner
- Edge Function `negotiate/` = to be deprecated or refactored to delegate to Railway
- No algorithm code shall exist in Edge Functions; Edge Functions may orchestrate but not compute

---

### Decision 3: Edge Functions for Streaming Chat

**What was decided:** The Supabase Edge Function `/chat` handles real-time SSE streaming for the coaching chat interface.

**Rationale (Inferred):** Railway does not natively support SSE streaming in a cost-effective way from Lovable. Supabase Edge Functions support SSE and are co-located with the database, reducing latency for session persistence.

**Current State:** Functioning. The Edge Function `/chat` is the primary chat path. Railway `/api/chat` is a non-streaming fallback.

**Proposed Canonical Rule:**
- Edge Functions = streaming I/O and thin orchestration only (no algorithm logic)
- Knowledge candidate extraction and tag parsing = Edge Function responsibility (already implemented)
- Knowledge candidate submission = Edge Function responsibility (currently missing)

---

### Decision 4: Frontend-Direct Supabase Writes (Historical Workaround)

**What was decided:** (Inferred — not an explicit decision) During Lovable-first development, session persistence, message saves, team CRUD, and profile updates were implemented as direct Supabase SDK calls from the React frontend.

**Rationale (Inferred):** Lovable code generation pattern. No Railway API existed for these operations when they were first implemented. Direct Supabase writes are the fastest path in Lovable.

**Current State:** Multiple business rules now live in browser JavaScript:
- Session title truncation (40 chars) in `useSessionManager.ts`
- Message load limit (50) in `useSessionManager.ts`
- Retry logic (2 retries, 1500ms) in `useSessionManager.ts`
- Team admin check in `TeamDashboard.tsx`

**Proposed Canonical Rule (Going Forward):**
- Frontend direct writes are acceptable ONLY for:
  - User profile preferences (user-scoped, RLS-enforced)
  - Reading data where Railway API has no endpoint
- All business entity mutations (sessions, messages, teams) should be mediated by Railway API endpoints
- Business rules (limits, titles, retry logic) must live in server-side code

---

### Decision 5: Client-Side Session State in localStorage

**What was decided:** `AnalysisContext` persists the full in-session negotiation state (messages, analysis results, ZOPA, plan, acceptance curves) to `localStorage` for cross-page navigation and browser refresh survival.

**Rationale (Inferred):** Eliminates the need for re-fetching analysis results on navigation. Fast local access.

**Current State:** Working but risky:
- No TTL — stale state persists across weeks
- No versioning — schema changes silently corrupt deserialized state
- No size limit — large Monte Carlo acceptance curves accumulate
- `knowledge_candidates` key grows without bound

**Proposed Canonical Rule:**
- AnalysisContext localStorage = ephemeral session cache only (cleared on new session start)
- Add schema version key to AnalysisContext — clear on version mismatch
- Add TTL (24 hours) to negotiationcoach_session localStorage entry
- Remove knowledge_candidates localStorage accumulation until submission pipeline exists

---

## Proposed Boundary Map

```
┌─────────────────────────────────────────────────────────────┐
│ BROWSER (React SPA)                                         │
│  Allowed:                                                   │
│   - Auth operations (signIn, signUp, resetPassword)        │
│   - Reading own session data (via Railway API)             │
│   - user_profiles update (own row, RLS-enforced)           │
│   - AnalysisContext as ephemeral session cache             │
│   - Streaming chat via Edge Function /chat                 │
│  NOT Allowed:                                               │
│   - negotiation_sessions writes (→ use Railway API)        │
│   - session_history writes (→ use Railway API)            │
│   - teams / team_members writes (→ use Railway API)        │
│   - Any business logic (limits, titles, retries)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
              ┌────────────────┴───────────────┐
              ▼                                 ▼
┌────────────────────────┐       ┌─────────────────────────────┐
│ RAILWAY (Express API)  │       │ SUPABASE                    │
│  Canonical owner:      │       │  Canonical owner:           │
│   - All analysis       │       │   - Identity / JWT          │
│   - All LLM calls      │       │   - Auth session tokens     │
│   - Session CRUD       │       │   - Streaming (Edge Fns)    │
│   - Message CRUD       │       │   - Raw storage             │
│   - Team CRUD          │       │   - RLS enforcement         │
│   - Tier enforcement   │       │  NOT responsible for:       │
│   - Model routing      │       │   - Business logic          │
│   - Market data cache  │       │   - Algorithm computation   │
└────────────────────────┘       └─────────────────────────────┘
```

---

## Consequences

### Accepted Violations (To Be Resolved)
- Frontend direct session/message writes remain until Railway CRUD endpoints are built
- Team management remains frontend-direct until Railway team endpoints are built
- Edge Function `negotiate/` remains until deprecation path is agreed

### Non-Negotiable From Now On
- No new algorithm logic in Edge Functions or frontend
- No new business rules in frontend hooks/components
- All new database tables require RLS policies before frontend access is permitted
- Any new frontend DB write requires documented justification referencing this ADR
