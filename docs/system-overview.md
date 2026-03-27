# System Overview — NegotiationCoach AI

> Classification legend: **Observed** | **Inferred** | **Missing** | **Proposed**
> Last audit: 2026-03-27

---

## 1. Purpose

NegotiationCoach AI is a web application that guides users through professional negotiations (salary, rent, supplier, M&A) using AI-powered analysis. It combines structured input extraction via chat, quantitative negotiation algorithms (ZOPA, Nash Bargaining, Monte Carlo), market data enrichment, and PDF export of negotiation plans.

---

## 2. System Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Browser                                                                     │
│  React SPA (negotiation-buddy)                                              │
│                                                                             │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────┐                  │
│  │ AnalysisCtx │   │ useSessionMgr│   │  useAuth.tsx   │                  │
│  │ localStorage│   │ (direct DB)  │   │  (Supabase JS) │                  │
│  └──────┬──────┘   └──────┬───────┘   └───────┬────────┘                  │
│         │                 │                    │                            │
└─────────┼─────────────────┼────────────────────┼────────────────────────────┘
          │                 │                    │
          │ Railway REST     │ Supabase JS SDK    │ Supabase Auth
          ▼                 ▼                    ▼
┌──────────────────┐  ┌─────────────────────────────────────────────────────┐
│ Railway           │  │ Supabase (PostgreSQL + Auth + Edge Functions)       │
│ negotiationcoach- │  │                                                     │
│ backend           │  │  ┌──────────────────┐  ┌────────────────────────┐  │
│                   │  │  │ Auth             │  │ Edge Function: /chat   │  │
│  Express API      │  │  │ (JWT, sessions)  │  │ (SSE streaming,        │  │
│  ─────────────    │  │  └──────────────────┘  │  Deno, duplicates L1)  │  │
│  Layer 3: API     │  │                         └────────────────────────┘  │
│  Layer 2: Market  │  │  ┌──────────────────────────────────────────────┐  │
│  Layer 1: Algos   │  │  │ Tables                                        │  │
│  Layer 0: DB      │  │  │  negotiation_sessions   knowledge_graph       │  │
│                   │  │  │  session_messages        user_profiles         │  │
│  SERVICE_ROLE_KEY │  │  │  teams  team_members     team_training_tasks   │  │
│  bypasses RLS     │  │  └──────────────────────────────────────────────┘  │
└──────────────────┘  └─────────────────────────────────────────────────────┘
          │
          ▼
  Anthropic Claude API
  (haiku / sonnet / opus
   per modelRouter.ts)
```

---

## 3. Runtimes

| Runtime | Repo | Language | Host | Role |
|---------|------|----------|------|------|
| React SPA | negotiation-buddy | TypeScript/TSX | Browser | UI, state orchestration |
| Express API | negotiationcoach-backend | TypeScript | Railway | Analysis, market data, LLM orchestration |
| Edge Function: chat | negotiation-buddy/supabase/functions/chat | TypeScript (Deno) | Supabase | SSE chat streaming |
| Edge Function: generate-plan | negotiation-buddy/supabase/functions/generate-plan | TypeScript (Deno) | Supabase | Plan generation (inferred, may be unused) |
| Edge Function: negotiate | negotiationcoach-backend/supabase/functions/negotiate | TypeScript (Deno) | Supabase | **Duplicates Layer 1 algorithms** (Observed) |

**Note (Observed):** Two parallel backend runtimes exist — the Railway Express API and a Supabase Edge Function (`negotiate`) that independently implement ZOPA, Nash, Monte Carlo, and strategy scoring with a different input schema. These are NOT in sync.

---

## 4. External Services

| Service | Purpose | Who Uses It |
|---------|---------|------------|
| Anthropic Claude API | LLM inference (haiku/sonnet/opus) | Railway backend only |
| Supabase Auth | JWT issuance, email verification, password reset | Frontend + Railway middleware |
| Supabase PostgreSQL | Primary datastore | Frontend (direct) + Railway backend |
| Supabase Edge Functions | SSE chat, password reset emails | Frontend |
| HaveIBeenPwned API | Password breach check (k-anonymity) | Frontend only |
| Stripe | Subscription billing, tier updates | Inferred — webhooks update `user_tier` in Supabase |

---

## 5. Data Flow Paths

### 5.1 Chat / Input Extraction
```
User types → useChat.ts → Supabase Edge Function /chat (SSE)
  → Streams tokens back → stripInternalTags() extracts [KNOWLEDGE_CANDIDATE]
  → AnalysisContext stores messages + extractedInputs
  → useSessionManager.ts writes session + messages DIRECTLY to Supabase DB
```

### 5.2 Structured Analysis (Canvas)
```
User fills form → NegotiationCanvas.tsx → Railway POST /api/analyze-full
  → authMiddleware (optional, dev mode) → Layer 1 (ZOPA, Nash, MC, strategy)
  → Layer 2 (market enrichment, kmu+ only)
  → Result stored in AnalysisContext + negotiation_sessions table
```

### 5.3 Plan Generation
```
AnalysisContext → Railway POST /api/plan
  → Claude (hardcoded sonnet, NOT modelRouter) generates JSON plan
  → Plan stored in AnalysisContext.cachedPlan (localStorage)
  → PDF export via browser print dialog
```

### 5.4 Session Persistence
```
useSessionManager.ts → Supabase SDK direct writes
  → negotiation_sessions (INSERT/UPDATE)
  → session_messages (INSERT, fire-and-forget with 2 retries)
  [No Railway API intermediary — frontend writes DB directly]
```

---

## 6. Tier System

**VIOLATION — Observed:** Two incompatible tier enumerations exist in the same system.

| Source | Tier Values |
|--------|-------------|
| Railway backend (src/types/index.ts) | `free \| privat \| kmu \| profi` |
| Supabase DB (persona_type enum) | `pro \| kmu \| private` |
| Frontend chat persona (useChat.ts) | `"free"` (hardcoded string) |

The backend enforces feature gating via the `free/privat/kmu/profi` hierarchy. The frontend uses `persona_type` (pro/kmu/private) for UI mode selection. These systems do not share a canonical tier definition. **Missing:** A unified tier contract.

---

## 7. Critical System-Level Risks

| ID | Risk | Severity | Classification |
|----|------|----------|----------------|
| SYS-01 | Dual Layer 1 implementations (Railway src/ vs Edge Function negotiate/) with divergent type schemas and no sync mechanism | Critical | Observed |
| SYS-02 | Team admin authorization is frontend-only (no RLS enforcement verified) | High | Observed |
| SYS-03 | Railway authMiddleware never rejects — no 401 issued in dev mode | High | Observed |
| SYS-04 | Frontend writes negotiation_sessions, session_messages, teams, team_members, user_profiles directly (no API mediation) | High | Observed |
| SYS-05 | CORS wildcard header overrides allowlist in Railway backend | Medium | Observed |
| SYS-06 | Two incompatible tier/subscription enumerations across frontend and backend | Medium | Observed |
| SYS-07 | AnalysisContext stored in localStorage with no TTL, no versioning, no size limit | Medium | Observed |
| SYS-08 | modelRouter.ts not used by /api/chat and /api/plan — cost optimization bypassed | Low | Observed |
| SYS-09 | Knowledge candidates extracted by Edge Function and stored in localStorage but never submitted | Low | Observed |
