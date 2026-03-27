# Audit Dashboard — NegotiationCoach AI

> **Source of truth:** git-tracked markdown in repos.
> Knowledge Items (Notion, Lovable IDE) are **not** authoritative.
> Last updated: 2026-03-27

---

## Legend

| Status | Meaning |
|--------|---------|
| ✅ Done | Artifact produced, committed, actionable |
| 🔄 In Progress | Work started, not complete or not committed |
| ⚠️ Blocked | Cannot advance without external action |
| 🔲 Not Started | Identified but no work done |

---

## Workstream 1 — Backend Audit

| Field | Value |
|-------|-------|
| **Status** | 🔄 In Progress |
| **Owner / Tool** | Claude Code (general-purpose agent) |
| **Branch** | `main` — 2 commits ahead of `origin/main` (not pushed) |

### Outputs

| Artifact | Path | Committed |
|----------|------|-----------|
| Repo map | `negotiationcoach-backend/docs/repo-map.md` | ✅ yes |
| API catalog | `negotiationcoach-backend/docs/api-catalog.md` | ✅ yes |
| DB map | `negotiationcoach-backend/docs/db-map.md` | ✅ yes |
| Service catalog | `negotiationcoach-backend/docs/service-catalog.md` | ✅ yes |
| Audit findings | `negotiationcoach-backend/docs/audit-findings.md` | ✅ yes |
| Dead code candidates | `negotiationcoach-backend/docs/dead-code-candidates.md` | ✅ yes |
| Redundancy register | `negotiationcoach-backend/docs/redundancy-register.md` | ✅ yes |
| Agent nav guide | `negotiationcoach-backend/AGENTS.md` | ✅ yes |

### Key Findings (from `audit-findings.md`)

| ID | Severity | Summary |
|----|----------|---------|
| CRIT-01 | Critical | Dual Layer 1 implementations with incompatible type schemas (`own_target` vs `user_goal`) |
| CRIT-03 | Critical | `authMiddleware` never returns 401 — Railway is fully public |
| HIGH-01 | High | Model router (`selectModel()`) not used by `/api/chat` or `/api/plan` endpoints |
| A03 | High | Wildcard CORS header (`*`) overrides allowlist — accepts all origins |
| A04 | High | No rate limiting on Claude API calls — cost exposure risk |
| S02 | Medium | `webSearch.ts` uses Claude tool_use, not real web search — misleading name |
| E01 | Medium | Node.js backend and Edge Function `negotiate/` overlap with no delegation |

### Blockers

- `tasks/todo.md` and `tasks/lessons.md` are empty — no action items derived from findings yet
- 2 local commits (`AGENTS.md`, audit docs) not pushed to remote

### Next Step

1. `git push` the 2 pending commits in `negotiationcoach-backend`
2. Populate `tasks/todo.md` with actionable items derived from `audit-findings.md`
3. Fix CRIT-03 (auth enforcement) for production hardening
4. Fix A03 (remove wildcard CORS header)

---

## Workstream 2 — Frontend Audit

| Field | Value |
|-------|-------|
| **Status** | 🔄 In Progress |
| **Owner / Tool** | Claude Code (general-purpose agent) |
| **Branch** | `main` — up-to-date with remote; docs untracked |

### Outputs

| Artifact | Path | Committed |
|----------|------|-----------|
| Repo map | `negotiation-buddy/docs/repo-map.md` | ⚠️ untracked |
| Feature catalog | `negotiation-buddy/docs/feature-catalog.md` | ⚠️ untracked |
| Data access map | `negotiation-buddy/docs/data-access-map.md` | ⚠️ untracked |
| Audit findings | `negotiation-buddy/docs/audit-findings.md` | ⚠️ untracked |
| Dead code candidates | `negotiation-buddy/docs/dead-code-candidates.md` | ⚠️ untracked |
| Redundancy register | `negotiation-buddy/docs/redundancy-register.md` | ⚠️ untracked |
| Agent nav guide | `negotiation-buddy/AGENTS.md` | ⚠️ untracked |
| CLAUDE.md | `negotiation-buddy/CLAUDE.md` | ⚠️ untracked |

### Key Findings (from `audit-findings.md`)

| ID | Severity | Summary |
|----|----------|---------|
| CRIT-02 | Critical | Team admin authorization is UI-only — no verified RLS enforcement on `teams` / `team_members` |
| HIGH-01 | High | Direct Supabase SDK writes from browser for 6 tables (sessions, messages, teams, profile) without Railway mediation |
| HIGH-02 | High | Session message persistence is fire-and-forget; failures silently lost |
| F-003 | Medium | `AnalysisContext` persists to localStorage with no TTL, schema version, or logout-clear |
| F-004 | Medium | Knowledge candidates accumulate in localStorage without cleanup |
| F-005 | Low | No code splitting — all 13 pages in initial bundle |

### Blockers

- All frontend docs are **untracked** (not committed) — not yet source-of-truth
- TypeScript strictness is off (`noImplicitAny: false`, `strictNullChecks: false`) — limits static analysis reliability
- Recent git history shows 2 reverts — unstable baseline

### Next Step

1. `git add docs/ AGENTS.md CLAUDE.md && git commit` in `negotiation-buddy`
2. Verify RLS policies on `teams` and `team_members` tables (VG-01 — unresolved verification gap)
3. Derive action items from findings into a `tasks/todo.md`

---

## Workstream 3 — Cross-Repo Synthesis

| Field | Value |
|-------|-------|
| **Status** | 🔄 In Progress |
| **Owner / Tool** | Claude Code (general-purpose agent) |
| **Branch** | `shared-context/main` — all docs untracked |

### Outputs

| Artifact | Path | Committed |
|----------|------|-----------|
| System overview | `shared-context/docs/system-overview.md` | ⚠️ untracked |
| Auth & permission map | `shared-context/docs/auth-permission-map.md` | ⚠️ untracked |
| Bounded contexts | `shared-context/docs/bounded-contexts.md` | ⚠️ untracked |
| Source of truth matrix | `shared-context/docs/source-of-truth-matrix.md` | ⚠️ untracked |
| Current state report | `shared-context/docs/audits/current-state-report.md` | ⚠️ untracked |
| Frontend-backend contract | `shared-context/docs/contracts/frontend-backend.md` | ⚠️ untracked |
| ADR-001 System boundaries | `shared-context/docs/decision-log/ADR-001-system-boundaries.md` | ⚠️ untracked |
| ADR-002 Data ownership | `shared-context/docs/decision-log/ADR-002-data-ownership.md` | ⚠️ untracked |
| **This dashboard** | `shared-context/docs/audit-dashboard.md` | ⚠️ untracked |

### Key Cross-Cutting Issues

| Issue | Repos Affected | Finding ID |
|-------|---------------|------------|
| Dual Layer 1 implementations with incompatible schemas | backend | CRIT-01 |
| Three incompatible `Tier` type definitions | backend + frontend + edge functions | CRIT-04 |
| JWT token fetching duplicated in 6+ frontend files | frontend | HIGH-03 |
| Model router implemented but unused by LLM endpoints | backend | HIGH-01 |
| Two competing chat paths (Railway `/api/chat` vs Edge Function `/chat`) | both | ADR-001 |
| Direct DB writes from browser bypass Railway business logic | frontend + backend | HIGH-01 |

### Blockers

- **All artifacts are untracked** — synthesis work has no git-tracked source of truth yet
- CRIT-01 resolution requires an agreed canonical schema before any refactor can begin
- ADR-001 (system boundary decisions) is drafted but not accepted/recorded formally

### Next Step

1. Commit all `shared-context/docs/` artifacts: `git add docs/ && git commit`
2. Accept ADR-001 and ADR-002 as binding decisions
3. Pick CRIT-01 as the first cross-repo remediation: agree canonical schema, deprecate Edge Function layer1

---

## Workstream 4 — Lovable Knowledge Sync

| Field | Value |
|-------|-------|
| **Status** | 🔄 In Progress |
| **Owner / Tool** | Manual / Claude Code assist |
| **Branch** | `negotiation-buddy/main` — docs untracked |

### Outputs

| Artifact | Path | Committed |
|----------|------|-----------|
| Lovable project knowledge | `negotiation-buddy/docs/lovable-project-knowledge.md` | ⚠️ untracked |
| Lovable workspace knowledge | `negotiation-buddy/docs/lovable-workspace-knowledge.md` | ⚠️ untracked |

### Purpose

These files capture the state of the Lovable IDE's project knowledge so that:
- Claude Code agents have context when working on the frontend repo
- Lovable-generated changes can be diff'd against the canonical architectural decisions
- Drift between Lovable's internal model and actual code can be detected

### Blockers

- Files not committed — cannot be treated as source of truth
- No formal sync mechanism: Lovable may overwrite files or generate code inconsistent with ADR-001/ADR-002
- Scope of Lovable's write access to component files is not bounded

### Next Step

1. Commit `lovable-project-knowledge.md` and `lovable-workspace-knowledge.md`
2. Define what Lovable is and is not allowed to modify (component scope boundary)
3. Add a `CLAUDE.md` boundary note: Lovable owns UI components only; `src/lib/`, `src/hooks/`, `src/integrations/` require Claude Code review

---

## Workstream 5 — Cleanup Backlog

| Field | Value |
|-------|-------|
| **Status** | 🔲 Not Started |
| **Owner / Tool** | Claude Code (to be assigned) |

### Identified Candidates

**Backend** (`negotiationcoach-backend/docs/dead-code-candidates.md`):

| Candidate | Risk |
|-----------|------|
| `src/utils/claudeClient.ts` re-exports (deprecated `CLAUDE_MODEL`) | Low — internal only |
| Edge Function `negotiate/` Layer 1 implementation | High — CRIT-01 resolution required first |
| Unused `SimulationTurn` interface in `src/types/index.ts` | Low |
| `src/layer2/webSearch.ts` rename (misleading name) | Low |
| Dead imports in `src/api/routes.ts` | Low |
| `tsconfig.test.json` coverage if tests are rebuilt | Medium |

**Frontend** (`negotiation-buddy/docs/dead-code-candidates.md`):

| Candidate | Risk |
|-----------|------|
| Duplicate token-fetch calls in 6+ components | Medium — requires `useAuth` refactor |
| Unused shadcn/ui primitives | Low |
| `public/version.json` update mechanism (if superseded) | Low |
| `src/test/` (minimal, unused) | Low |
| Orphaned page components from reverted features | Medium — verify before deleting |
| Mock data files (if any remain from Lovable scaffolding) | Low |

### Blockers

- CRIT-01 must be resolved before Edge Function cleanup
- Recent reverts in frontend make dead code determination risky without re-testing

### Next Step

1. After CRIT-01 decision: deprecate and remove Edge Function Layer 1 implementation
2. Refactor `useAuth.tsx` to expose central `getToken()` — removes 6 duplicate call sites
3. Remove deprecated `CLAUDE_MODEL` export from `claudeClient.ts`

---

## Workstream 6 — Guardrails Installation

| Field | Value |
|-------|-------|
| **Status** | 🔲 Not Started |
| **Owner / Tool** | Claude Code (to be assigned) |

### Required Guardrails (derived from audit findings)

| Guardrail | Finding | Location | Priority |
|-----------|---------|----------|----------|
| Remove wildcard CORS header | A03 | `negotiationcoach-backend/src/api/routes.ts:29` | P0 |
| Enforce auth (return 401) in production | CRIT-03 | `negotiationcoach-backend/src/api/middleware.ts:80` | P0 |
| Rate limiting on Claude API endpoints | A04 | `negotiationcoach-backend/src/api/routes.ts` | P1 |
| Verify RLS on `teams` / `team_members` | CRIT-02 | Supabase schema | P0 |
| Add `getToken()` to `useAuth.tsx` | HIGH-03 | `negotiation-buddy/src/hooks/useAuth.tsx` | P1 |
| localStorage schema versioning for AnalysisContext | F-003 | `negotiation-buddy/src/contexts/AnalysisContext.tsx` | P2 |
| Clear localStorage on logout | F-003 | `negotiation-buddy/src/hooks/useAuth.tsx` | P1 |
| Pre-commit hook: `npx tsc --noEmit` (backend) | general | `negotiationcoach-backend/.husky/` | P2 |
| Environment variable guard: reject placeholder keys in prod | CRIT-03 | `negotiationcoach-backend/src/api/middleware.ts` | P1 |

### Blockers

- No CI/CD lint or type-check gate exists in either repo
- Production deployment (Railway) is currently running without auth enforcement
- P0 guardrails require careful staging to avoid breaking the anonymous dev-mode fallback

### Next Step

1. **P0 immediately:** Remove wildcard CORS from `routes.ts` line 30 — safe fix, no logic change
2. **P0 immediately:** Add `supabase inspect db --lint` or equivalent to verify RLS on `teams`
3. **P1 — production gate:** Add env var guard in middleware: if `NODE_ENV=production` and `SUPABASE_URL` contains `placeholder`, crash-exit at startup rather than silently accepting all requests
4. Install `husky` in backend with `pre-commit: tsc --noEmit`

---

## Summary Table

| # | Workstream | Status | Critical Blocker | Next Action |
|---|-----------|--------|-----------------|-------------|
| 1 | Backend Audit | 🔄 In Progress | 2 unpushed commits | `git push` + populate `tasks/todo.md` |
| 2 | Frontend Audit | 🔄 In Progress | All docs untracked | `git commit` frontend docs |
| 3 | Cross-Repo Synthesis | 🔄 In Progress | All docs untracked | `git commit` shared-context docs; accept ADRs |
| 4 | Lovable Knowledge Sync | 🔄 In Progress | Docs untracked, no scope boundary | Commit docs + define Lovable write boundary |
| 5 | Cleanup Backlog | 🔲 Not Started | CRIT-01 must be resolved first | Resolve CRIT-01, then remove Edge Function Layer 1 |
| 6 | Guardrails Installation | 🔲 Not Started | Auth enforcement needs staging plan | Remove wildcard CORS (P0, safe) immediately |

---

## Priority Queue (Immediate Actions)

1. **Commit all untracked docs** across all three repos — nothing is source-of-truth until committed
2. **Remove wildcard CORS** (`routes.ts:30`) — zero-risk fix
3. **Verify RLS on `teams` / `team_members`** — Supabase MCP `execute_sql` or `get_advisors`
4. **Accept ADR-001 and ADR-002** — unblock CRIT-01 remediation plan
5. **Add auth enforcement guard for `NODE_ENV=production`** — close CRIT-03 for production
