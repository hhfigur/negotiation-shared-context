# Stage 1 — Current Operating System Inventory

Produced from three parallel, read-only discovery passes (one per repository). Raw per-file content was not copied into synthesis; only structured findings were merged. Full per-repository detail (all inventory rows, toolchain evidence, Supabase boundary, skills/agents) is preserved in this file and in `02-existing-artifact-map.yaml` / `03-command-and-toolchain-evidence.md` / `04-supabase-boundary-map.md` / `05-instruction-and-skill-map.md`.

## Delta review — owner-confirmed corrections (2026-09-04)

The project owner has issued three authoritative current-state corrections that override any conflicting assumption in the migration kit or in stale repository documentation. These are **facts, not proposals**, and are recorded here as the decision basis; full detail and disposition are in `10-conflicts-and-decisions.md` (C2 and C4, both RESOLVED):

1. **Supabase**: exactly ONE active Supabase project (`gpllrgkuozytyrmpfwbb`) for the whole system. Frontend and backend sharing it is **intentional**, not accidental coupling to be migrated away from. Cross-repo summary item 2 below is updated accordingly — this is no longer an open question about intent, only a question of what governance the shared model needs (see `04-supabase-boundary-map.md`).
2. **Frontend development**: Lovable is no longer used for active frontend development. `negotiation-buddy` is developed directly by Claude Code in the local repo. Lovable-specific assumptions must be removed from *target-state* proposals (Controllers, Skills, CLAUDE.md templates) — historical documentation may keep Lovable references where historically accurate (e.g. describing why `lovable-tagger` is still a build-time Vite dependency, or why past migrations exist).
3. **Hosting**: Railway is no longer used. Render.com is the current, owner-confirmed hosting/deployment platform. Railway references must be removed from active target-state instructions, Skills, controller logic, and deployment assumptions; kept only for historical traceability. Render.com usage is corroborated by both repos' `MEMORY.md` (prose, not a codified deploy artifact — see `03-command-and-toolchain-evidence.md`, which still correctly flags that no in-repo deploy config exists for either code repo). Where repository evidence cannot independently verify a Render.com claim, that is marked explicitly below rather than silently upgraded to "confirmed."

**Effect on this file**: cross-repo summary items 2 and 3 (immediately below) are updated in place; item 6 (Supabase MCP wrong-project wiring) is unchanged — the owner's corrections settle *intent*, not the separate, still-open question of which project this environment's MCP tool actually reaches (validation item 1 in `10-conflicts-and-decisions.md`, still open).

**Second delta pass (2026-09-04)**: cross-repo summary item 4 (the API-contract source-of-truth conflict) is now **RESOLVED**, not open — `10-conflicts-and-decisions.md` C1: `negotiationcoach-backend/docs/api-catalog.md` is the confirmed canonical location (owner decision), pending a completion migration (see `09-proposed-file-diffs.md` Diff 5). Cross-repo summary item 7 (task-closing has "at least three coexisting mechanisms") is also now RESOLVED — `10-conflicts-and-decisions.md` C3: `/negotiation-ai-sdlc:close-change` is canonical for new work; all four existing variants (this made it four, not three, once `negotiationcoach-backend`'s local variant was counted alongside shared-context's two and the frontend's one) are LEGACY, not deleted.

## Cross-repository summary (read this first)

1. **Neither "Development Controller" nor "Audit and Refactoring Controller" is a repo-native artifact anywhere.** Both are human-operated Claude.ai Projects whose *instructions* live as markdown in `shared-context/docs/governance/` (`delivery-controller-setup.md`, `delivery-controller-grundinstruktion.md` for the Development Controller; `GOV-01-audit-runbook.md` + `ALL-PROMPTS-AUDIT.md` for the Audit/Refactoring Controller — no dedicated instruction file for the latter was found at all, only its workflow). The backend repo participates via **symlinked** `pm-*` skills into `shared-context/.claude/skills/`; the frontend repo participates via **plain path references** in `CLAUDE.md` and its own independent (non-symlinked) `close-task` skill. Both Controller instruction documents are ~4-5 months stale (Railway hosting, Lovable/Gemini two-provider AI split, "Layer 3 not started" — all superseded by ADR-012 and shipped Layer 3 work).
2. **Frontend and backend Supabase projects are, right now, the *same* project** (`gpllrgkuozytyrmpfwbb`), not separate instances as `04-repository-registry.yaml` assumes. Both repos' migration histories contain files explicitly reconciling schema with "the backend"/"the frontend," confirming intentional coupling, not an accident. **Owner-confirmed (2026-09-04): this is the correct, intended architecture going forward** — not a defect and not a candidate for a split-instance migration. The remaining work is governance (access control, ownership, migration coordination, security boundaries for the shared model), not separation. See `04-supabase-boundary-map.md` for full detail.
3. **"Railway" naming/URL staleness is systemic**, appearing in governance docs in shared-context, rule docs in the backend, and rule docs in the frontend — all describing a hosting/provider topology (Railway + Lovable/Gemini split) that `MEMORY.md` in both code repos and ADR-012 confirm was replaced by Render.com + Anthropic-only months ago, in one documented cleanup pass that evidently did not reach `.claude/rules/*` or `docs/governance/*`. **Owner-confirmed (2026-09-04): Render.com is the current platform and Lovable is no longer used for active frontend development; Railway and "Lovable as active dev tool" are historical-only facts.** Every occurrence listed in `08-migration-plan.md` Phase E's naming-sweep row is now a confirmed-stale-documentation gap, not a merely-suspected one — see `06-gap-analysis.md`'s delta review for the actual-gap-vs-stale-doc split this enables.
4. **The frontend/backend API contract has two competing "source of truth" files, and both are wrong/incomplete in different ways**: frontend's `.claude/rules/api-contracts.md` has the *old Railway base URL* and is missing `/api/enrich` and `/api/simulate/*`; backend's `docs/api-catalog.md` is missing the entire `/api/simulate/*` and `/api/opponent-simulation/*` route families. Per migration principle #9 / constraint, this is a **source-of-truth conflict** requiring an explicit decision in Stage 2, not a silent merge.
5. **No repository has a CI workflow.** All three are on `main` with no `.github/workflows/` (or equivalent) anywhere. Verification (`scripts/verify.sh` in both frontend and backend) is a well-built local/manual oracle that nothing invokes automatically.
6. **The backend's Supabase MCP tool is reported (in its own `tasks/lessons.md`, entry L-004) to be permanently connected to a third, unused Supabase project** (`ivrfsjxdfzxrimexvoft`), distinct from the real active project both repos actually use. This analysis did not invoke any Supabase MCP tool to re-verify — flagged as unconfirmed but load-bearing if true: any future migration tooling that trusts MCP `list_tables`/`execute_sql` without checking the project ref first could be misled.
7. **Task-closing has at least three coexisting mechanisms**: shared-context's own `/close-task` and `/close-task-dev`, backend's local `/close-task` (symlinks to shared-context PM skills but has its own close-task variant), and frontend's local, independently-written `/close-task` (different from all of the above, targets `docs/api-catalog.md`/`docs/db-map.md` paths that don't exist in the frontend repo — likely copy-pasted from the backend's convention without adaptation).
8. **Working-tree state at time of inventory:** shared-context has one untracked bug-diagnosis doc (real, pre-existing); frontend has four real modified source files (`useSessionManager.ts`, `apiClient.ts`, `Index.tsx`, `NegotiationCanvas.tsx` — notably the exact files flagged as "high impact" by the frontend's own `impact-check-warn.sh` hook) plus harmless Supabase CLI cache diffs; backend is clean. None of this was read or touched as committed state.

---

## Repository: Shared-context

`/Volumes/MF_extern/app-workspace/shared-context` — branch `main`, 9 commits ahead of `origin/main` (unpushed at scan time), working tree dirty only via `.DS_Store` + one untracked file.

### Controllers (full detail)

**Development Controller** — realized as a Claude.ai Project, not a repo command/skill/hook.
- Instruction sources: `docs/governance/delivery-controller-setup.md` (English, detailed: role, system landscape, tier model, "Grundinstruktion" paste block, task-brief/ADR-request/session-log templates) and `docs/governance/delivery-controller-grundinstruktion.md` (German, leaner variant of the same role, created same era, largely overlapping).
- Invocation: manual — a human pastes the Grundinstruktion into a Claude.ai Project's instructions; it then tells the user to run Claude Code sessions per-repo and paste task briefs.
- State/handoff: `docs/wiki/index.md` (open items, "Legacy" self-labeled but confirmed still live), `docs/wiki/session-log.md` (append-only), `docs/audits/refactor-backlog.md` (canonical technical backlog).
- Gap vs. target: functions today purely as an orchestrator/dispatcher; independent assurance is not built into it — that's scattered across `contract-check`/`impact-check`/`verify-loop` skills and informal "Task-Review"/"Critic-Pass" practices noted in `tasks/lessons.md`.
- Currency: describes an April-2026 world (Railway, ADR-003-active two-provider AI split, "Layer 3 not started") superseded by ADR-012 (2026-07-18) and the Render.com move. Would misdirect a reactivation as-is.

**Audit and Refactoring Controller** — also a Claude.ai Project ("App Governance & Audit"), referenced by name in the Development Controller's own instructions and in `GOV-01-audit-runbook.md`/`README-AUDIT.md`, but **no project-instruction file for it exists in the repo** — only its workflow (steps, tool routing, prompt matrix) is captured in `docs/governance/GOV-01-audit-runbook.md` (canonical) and its near-duplicate `README-AUDIT.md` (German, undated, `600`-permission file). The actual prompt texts operators paste live in `docs/governance/ALL-PROMPTS-AUDIT.md`.
- Invocation: manual prompt-pasting into whichever tool the prompt matrix specifies (Claude.ai for control, Claude Code CLI for repo-level audit/refactor, Lovable Plan Mode for frontend sync).
- State/handoff: `docs/audit-dashboard.md` (explicitly "Legacy" per the wiki index), `docs/audits/refactor-backlog.md`, `docs/audits/current-state-report.md` (last touched Apr 17, drifted since — see finding below).
- Gap vs. target: an orchestration/prompt-dispatch playbook, not a built-in independent-assurance mechanism — the same Claude Code sessions that implement also audit, with independence achieved only informally.

### Full artifact inventory, skills, and findings

See the complete per-artifact table (60+ rows: `.claude/` commands/skills/settings, `CLAUDE.md`/`AGENTS.md`/`MEMORY.md`, all of `docs/` including ADR-001..012, governance, audits, wiki, delivery, and all of `product/` including strategy/roadmap/releases/briefs/feature-register, plus `tasks/`) in `02-existing-artifact-map.yaml` (machine-readable) and `05-instruction-and-skill-map.md` (skills/commands detail). Key standalone findings not already covered in the cross-repo summary:

- `docs/infrastructure/supabase-instances.md` **names the wrong production Supabase project** — labels `ujnyioggxipvuxxxcivr` as production/JWT-authority; both code repos' `MEMORY.md` and `tasks/lessons.md` confirm the real active project is `gpllrgkuozytyrmpfwbb`, and that `ujnyioggxipvuxxxcivr` was a legacy footgun once accidentally committed to `.env`. **Highest-risk single document found in this entire inventory** — a future session or automation trusting this file could target the wrong Supabase project. Never modified since 2026-04-21.
- The `docs/wiki/WIKI---*.md` bundle (9 files, mostly dated Apr 17-18) and `docs/wiki/architecture.md` describe the same superseded Railway/Lovable-Gemini world; `WIKI---Index.md` also links to a file that doesn't exist (`WIKI---Repo-Profile-negotiation-buddy.md`).
- `GOV-01-audit-runbook.md` and `README-AUDIT.md` are near-duplicate content with no stated precedence between them.
- Two parallel bug-doc conventions exist: `docs/delivery/bug-reports/` (older, has its own `ARCHIVED.md`, not read this pass) vs. `docs/delivery/bugs/` (current, per its own `README.md`, actively used by the bug-report/bug-fix/close-task skills).
- `close-task/SKILL.md` still references `wiki/index.md`/`wiki/session-log.md` (no `docs/` prefix) — a known, previously-diagnosed-but-unfixed path bug (`tasks/lessons.md`, 2026-07-16/18 entries); real files live at `docs/wiki/*`.
- `close-task`/`close-task-dev` assume `docs/audits/refactor-backlog.md`'s per-item-heading format, but `product/feature-register.md` (where NC-/AR- items actually live) is a flat single table — a real, only partially-mitigated format mismatch per `tasks/lessons.md` (2026-07-08).
- `.claude/worktrees/quizzical-poitras-6b3676/` is an orphaned, gitignored, locked worktree holding a stale fork of `docs/`/`product/` — housekeeping noise, not canonical content.
- `tasks/lessons.md` is the single richest process-history artifact found across all three repos — extensive, append-only, documents multiple still-open skill bugs.
- No file in this repo carries explicit `status: approved` policy frontmatter anywhere; per the kit's own policy model, **nothing here currently qualifies as an enforceable policy** — everything is an operative convention at best.

---

## Repository: negotiation-buddy (Frontend)

`/Volumes/MF_extern/app-workspace/negotiation-buddy` — branch `main`, in sync with `origin/main`, working tree dirty (4 real files + 2 harmless Supabase CLI cache files, see above).

Originally Lovable-generated (via `lovable-tagger` Vite plugin, build-time only — no static markers found in source). **Owner-confirmed (2026-09-04): Lovable is no longer used for active development at all** — Claude Code, working directly in this local repo, is the sole current development path. `lovable-tagger` remaining in `package.json`/`vite.config.ts` is a leftover build-time dependency, not evidence of an active Lovable workflow; whether it is still needed or safe to remove is a Stage 3 cleanup candidate, not addressed by this migration. Stack: Vite + React + TypeScript, ESLint (flat config, `no-unused-vars` off), Vitest + Testing Library + jsdom for unit tests, **no e2e/visual/browser test tooling** (no Playwright/Cypress/Percy found).

### Toolchain (verbatim from `package.json` / `scripts/verify.sh` — see `03-command-and-toolchain-evidence.md` for full table)
`vite` (dev), `vite build` (build), `vite build --mode development` (build:dev), `eslint .` (lint), `vitest run` (test), `vitest` (test:watch), `vite preview`. `scripts/verify.sh` runs tsc→vitest→build as hard gates, contract-check/smoke as explicitly skipped, lint as warn-only (54 pre-existing problems tolerated). No CI invokes this. No deploy config in-repo (Render.com static site, per `MEMORY.md` prose only, not codified as a repo artifact).

### Full artifact inventory, Supabase boundary, and findings
Full per-artifact table (`.claude/rules`/`hooks`/`skills`, all of `docs/`, `.lovable/plan.md`, `tasks/`, `.superpowers/sdd/`, `scripts/`) in `02-existing-artifact-map.yaml`. Supabase detail in `04-supabase-boundary-map.md`. Standalone findings not already in the cross-repo summary:

- **Triple lockfile**: `package-lock.json`, `bun.lock`, and legacy binary `bun.lockb` coexist; timestamps don't cleanly indicate which is canonical for the real Render.com build pipeline.
- `docs/repo-map.md` (dated 2026-03-27) has a stale route map (routes now nested under `/app/*`, missing `OpponentSimulator.tsx`/`/app/opponent`) and still lists `useProgressEngine.ts` as active (deleted, commit `1eebf3b`).
- `tasks/todo.md` is referenced by `CLAUDE.md`, the `close-task` skill, and `stop-reminder.sh` hook, but **does not exist** in this repo — a dangling reference that would fail silently for an agent following it literally.
- `.env.local` contains an undocumented variable, `VITE_DEV_TIER_MOCK`, absent from `.env.example`, `AGENTS.md`, and `docs/repo-map.md`.
- `README.md` is largely unmodified Lovable scaffold boilerplate with an unfilled `REPLACE_WITH_PROJECT_ID` placeholder.
- Two independent Claude Code hooks (`audit-block.sh`, `protected-file-warn.sh`) hard-block (exit 2); two are advisory only (`impact-check-warn.sh`, `stop-reminder.sh`) — `stop-reminder.sh` references `tasks/todo.md` (missing, see above).

---

## Repository: negotiationcoach-backend (Backend)

`/Volumes/MF_extern/app-workspace/negotiationcoach-backend` — branch `main`, in sync with `origin/main`, clean working tree.

Claude Code is the stated primary implementation environment (confirmed — no Lovable involvement found). Stack: Express 5, TypeScript strict/CommonJS, `tsc` build, hand-rolled `console.assert`-based tests run sequentially via `ts-node` (no Jest/Mocha installed despite one stale audit doc claiming Jest). **No lint or format command exists** (no ESLint/Prettier config anywhere in the repo — a real, confirmed gap, not an oversight in discovery). Four-layer architecture (`layer0` Supabase client, `layer1` pure negotiation math, `layer2` market-data enrichment, `layer3` negotiation simulation), enforced by convention/docs, not tooling.

### Toolchain (verbatim from `package.json` / `scripts/verify.sh` — see `03-command-and-toolchain-evidence.md` for full table)
`nodemon --exec ts-node src/api/routes.ts` (dev), `tsc` (build), `node dist/api/routes.js` (start), `tsc --noEmit` (typecheck), a chained sequence of 10 `ts-node`-run test files (test). Lint/format: `NOT_FOUND`. Deploy: `NOT_FOUND` in-repo (Render.com auto-deploy from `main`, configured outside the repo per `MEMORY.md`). No CI anywhere (`.github/` doesn't exist).

### Full artifact inventory, Supabase boundary, and findings
Full per-artifact table (`.claude/rules`/`hooks`/`skills` including 5 symlinked `pm-*` skills into shared-context, `docs/*`, `.superpowers/sdd/`, `tasks/`, `scripts/`) in `02-existing-artifact-map.yaml`. Supabase detail in `04-supabase-boundary-map.md`. Standalone findings not already in the cross-repo summary:

- `docs/api-catalog.md` is the single most consequential contract-doc gap found: entirely missing `/api/simulate/*` and `/api/opponent-simulation/*` (6 routes total), despite the repo's own `.claude/rules/api-contracts.md` mandating it be kept in sync in the same commit/PR as any route change.
- `docs/audit-findings.md` self-contradicts other current docs — e.g. its CORS-wildcard finding (FINDING-A03) is already resolved per `docs/api-catalog.md`'s own "Fixed (RFB-005)" note and the actual `routes.ts` code.
- `AGENTS.md`'s "authMiddleware never rejects" finding (ARCH-01) is stale — current `middleware.ts` code returns 401 (comment references "RFB-001 — 401 enforced" superseding it), but `MEMORY.md`'s "Nicht anfassen" note and `session-start`'s known-issues list still assume the old behavior.
- `.claude/rules/db-boundaries.md` references a nonexistent path, `src/engine/simulationEngine.ts` (real logic lives in `src/layer1/*`/`src/layer3/*`) — likely unadapted boilerplate.
- `scripts/verify.sh` references `.claude/skills/verify-loop/SKILL.md`, which does not exist in this repo.
- Local `docs/audits/refactor-backlog.md` (near-empty, 1 entry) duplicates the name of shared-context's canonical 2317-line backlog, where the vast majority of RFB-xxx items this repo's own docs cite actually live.
- `tasks/lessons.md` entry L-004: the Supabase MCP tool available to this environment is documented as permanently connected to an unused, wrong project (`ivrfsjxdfzxrimexvoft`) — not independently reconfirmed this pass (out of scope for read-only discovery); see cross-repo summary item 6.

## Outcome

Stage 1 complete. Proceeding to Stage 2 gap analysis against the target operating model and kit overlays.
