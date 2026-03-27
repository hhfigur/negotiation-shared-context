# NegotiationCoach AI — Shared Context

This repository contains system-level documentation that spans both the frontend (`negotiation-buddy`) and backend (`negotiationcoach-backend`) repos.

**It is read-only documentation.** No application code lives here.

---

## What This Repository Contains

```
shared-context/
└── docs/
    ├── system-overview.md          System architecture, runtime map, data flows
    ├── bounded-contexts.md         Six bounded contexts with ownership and violations
    ├── source-of-truth-matrix.md   Canonical owner for every entity + verification gaps
    ├── auth-permission-map.md      Auth flows, tier gates, permission violations
    ├── contracts/
    │   └── frontend-backend.md     API contracts, type shapes, known drift
    ├── audits/
    │   └── current-state-report.md Full finding registry (CRIT/HIGH/MED/LOW)
    └── decision-log/
        ├── ADR-001-system-boundaries.md   Where code belongs (browser vs Railway vs Supabase)
        └── ADR-002-data-ownership.md      Who writes which tables, write path rules
```

---

## Classification Convention

Every finding is marked as one of:

| Label | Meaning |
|-------|---------|
| **Observed** | Directly verified in source code |
| **Inferred** | Logically deduced, not directly confirmed |
| **Missing** | Expected but not found anywhere |
| **Proposed** | Recommended change, not yet implemented |

---

## System in One Paragraph

NegotiationCoach AI is a React SPA (`negotiation-buddy`) backed by two services: a Railway Express API (`negotiationcoach-backend`) for LLM orchestration and analysis, and Supabase for auth, storage, and streaming Edge Functions. The analysis engine implements ZOPA, Nash Bargaining, and Monte Carlo simulation in TypeScript. Market data enrichment adds benchmarks for kmu/profi tier users. The frontend has significant historical direct-Supabase-write patterns (sessions, messages, teams) that predate the Railway API and represent the primary architectural debt.

---

## Critical Issues (Quick Reference)

| ID | Severity | Summary |
|----|----------|---------|
| CRIT-01 | Critical | Layer 1 algorithms duplicated in Railway AND Supabase Edge Function with incompatible schemas |
| CRIT-02 | Critical | Team admin check is frontend React code only — no server-side enforcement verified |
| CRIT-03 | Critical | Railway authMiddleware never returns 401 — all endpoints publicly accessible |
| HIGH-01 | High | Frontend writes negotiation_sessions, session_messages, teams directly (no API mediation) |
| HIGH-02 | High | Message saves are fire-and-forget — silent data loss possible |
| HIGH-03 | High | Three incompatible tier systems: Railway, Supabase persona_type, Edge Function hardcoded "free" |
| MED-01 | Medium | modelRouter bypassed in /api/chat and /api/plan — cost optimization and tier routing absent |
| MED-02 | Medium | CORS wildcard header overrides allowlist in Railway backend |

Full details: `docs/audits/current-state-report.md`

---

## Do Not

- Modify application source code from this repo
- Create implementation files here
- Use this repo for task tracking (use `tasks/` in the relevant repo instead)

## Do

- Read these docs before making architectural decisions
- Update docs when boundary decisions change
- Mark findings with the correct classification label
- Add new ADRs for decisions that affect both repos

---

## Repo Pointers

| Repo | Path | Role |
|------|------|------|
| Frontend | `/Users/maikfigur/app-workspace/negotiation-buddy/` | React SPA, Supabase Edge Functions |
| Backend | `/Users/maikfigur/app-workspace/negotiationcoach-backend/` | Railway Express API, Layer 1/2 algorithms |
| Shared context | `/Users/maikfigur/app-workspace/shared-context/` | This repo — documentation only |

---

## Verification Gaps (Must Be Resolved Before Scale)

| VG-ID | Question | Risk |
|-------|----------|------|
| VG-01 | Do Supabase RLS policies on `teams` and `team_members` enforce `admin_user_id = auth.uid()`? | Critical |
| VG-02 | Does Supabase RLS on `negotiation_sessions` prevent cross-user reads with anon_key? | High |
| VG-03 | Where does Stripe webhook update `user_metadata.tier`? Is it active in production? | High |
| VG-04 | What creates the initial `user_profiles` row on signup? | Medium |
| VG-05 | Does Edge Function `/chat` read actual user tier from JWT or use the hardcoded "free"? | Medium |
