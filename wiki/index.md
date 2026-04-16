# NegotiationCoach AI — Wiki Index

Navigation layer for the NegotiationCoach AI system — links to all major architecture documents, tracks open refactor items, and provides session history.

---

## Architecture & Decisions

→ [architecture.md](architecture.md) — System boundaries, AI provider split, engine layers, auth flow, tier system, and all ADR decisions in one place.

---

## Active Backlog

Full backlog: [../docs/audits/refactor-backlog.md](../docs/audits/refactor-backlog.md) — Structured refactor registry with body entries, dependency graph, and Summary Index.

### Currently Open Items

| ID | Title | Priority | Blocker |
|----|-------|----------|---------|
| RFB-006 | Unify dual Layer 1 implementations (Railway vs Edge Function engine) | P1 | VG-06 (dual Layer 1 architecture decision unresolved) |
| RFB-016 | Complete or remove knowledge candidate pipeline | P2 | None (deferred to feature backlog pending ADR) |
| RFB-026 | Repair broken claudeClient import in `batnaDetector.ts` (Edge Function) | P2 | RFB-006 |
| RFB-032 | Implement Stripe webhook handler — `POST /api/webhooks/stripe` | P0 | Stripe not yet live in production; RFB-036 must complete first |

---

## Session Log

→ [session-log.md](session-log.md) — Append-only log of every Control Tower session: what changed, what was decided, what comes next.

---

## Key Documents

| Document | Description |
|----------|-------------|
| [docs/system-overview.md](../docs/system-overview.md) | System architecture, runtime map, and data flows |
| [docs/bounded-contexts.md](../docs/bounded-contexts.md) | Six bounded contexts with canonical ownership and violations |
| [docs/source-of-truth-matrix.md](../docs/source-of-truth-matrix.md) | Canonical owner and access rules for every core entity |
| [docs/auth-permission-map.md](../docs/auth-permission-map.md) | Auth flows, tier gates, permission violations, and resolution history |
| [docs/contracts/frontend-backend.md](../docs/contracts/frontend-backend.md) | API contracts, transport table, request/response shapes, type drift |
| [docs/audits/current-state-report.md](../docs/audits/current-state-report.md) | Full finding registry (CRIT / HIGH / MED / LOW) |
| [docs/audits/refactor-backlog.md](../docs/audits/refactor-backlog.md) | Refactor item registry with body entries, Summary Index, and dependency graph |
| [docs/decision-log/ADR-001-system-boundaries.md](../docs/decision-log/ADR-001-system-boundaries.md) | Where code belongs: browser vs Railway vs Supabase |
| [docs/decision-log/ADR-002-data-ownership.md](../docs/decision-log/ADR-002-data-ownership.md) | Who writes which tables and the write path rules |
| [docs/decision-log/ADR-003-ai-provider-strategy.md](../docs/decision-log/ADR-003-ai-provider-strategy.md) | Two-provider split: Lovable/Gemini for EFs, Anthropic for Railway |
| [docs/decision-log/ADR-004-chat-path-routing.md](../docs/decision-log/ADR-004-chat-path-routing.md) | Edge Function is canonical chat path for all tiers; tier enforcement inside EF |
| [docs/decision-log/ADR-005-plan-generation-path.md](../docs/decision-log/ADR-005-plan-generation-path.md) | Railway `/api/plan` is canonical long-term path; `generate-plan` EF is temporary |
| [docs/decision-log/ADR-006-tier-mapping.md](../docs/decision-log/ADR-006-tier-mapping.md) | `subscription_tier` DB enum migrated to Railway Tier labels (ADR-006 Option A) |

---

*LLM-maintained — do not edit manually. Updated by Claude Code.*
