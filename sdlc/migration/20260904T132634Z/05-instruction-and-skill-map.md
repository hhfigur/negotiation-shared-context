# Stage 1 — Instruction and Skill Map

## Delta review — Lovable/Railway removed from target-state assumptions (owner-confirmed, 2026-09-04)

The owner has confirmed Lovable is no longer used for active frontend development and Railway is no longer used for hosting. Applying this to the Skill/Controller map below:

- **Audit and Refactoring Controller invocation** (table row below): its "Manual prompt-pasting... into Claude.ai / Claude Code / Lovable Plan Mode / optionally Antigravity" invocation path names Lovable Plan Mode as a live venue. **This must be removed from the target-state Controller instructions** (`shared-context-overlay/controllers/AUDIT_REFACTORING_CONTROLLER.md`, per `08-migration-plan.md` Phase D) before that document is adopted or pasted into a live Claude.ai Project — Lovable Plan Mode is not an available invocation path anymore. This is now a confirmed correction, not a staleness suspicion.
- **Currency notes** ("describes Railway hosting... Lovable/Gemini two-provider AI split") for both Controllers, below, are confirmed-stale facts (not merely aged) — see `06-gap-analysis.md` delta review for how this reclassifies items 5 and 9's severity.
- No Skill file inventoried below (`session-start`, `impact-check`, `contract-check`, `cleanup-audit`, `close-task`, the PM skills) was found to *itself* invoke Lovable or Railway as part of its instructions — the staleness is confined to the Controller docs and the `docs/`-level content already tracked in `08-migration-plan.md` Phase E, not to Skill logic. No Skill needs functional modification from this correction alone; only the Controller docs (Phase D) and any CLAUDE.md proposal text (`09-proposed-file-diffs.md`) do.

## Controllers (full detail — see also `01-current-inventory.md` § shared-context)

Neither controller is a Claude Code command, Skill, agent, or hook anywhere in any of the three repos. Both are **human-operated Claude.ai Projects**, activated by pasting markdown instructions from shared-context into a Project's instructions field.

| Controller | Instruction source(s) | Invocation | State/handoff files | Currency |
|---|---|---|---|---|
| Development Controller | `shared-context/docs/governance/delivery-controller-setup.md` (English, detailed) + `delivery-controller-grundinstruktion.md` (German, leaner, largely overlapping) | Manual paste into a Claude.ai Project; dispatches by telling the human to run Claude Code sessions per repo with pasted task briefs | `docs/wiki/index.md`, `docs/wiki/session-log.md`, `docs/audits/refactor-backlog.md` | Stale — describes Railway hosting, ADR-003-active two-provider AI split, "Layer 3 not started"; superseded by ADR-012 (2026-07-18) and the shipped Layer 3 work |
| Audit and Refactoring Controller | Workflow only: `docs/governance/GOV-01-audit-runbook.md` (canonical) + near-duplicate `README-AUDIT.md`; prompt texts in `docs/governance/ALL-PROMPTS-AUDIT.md`. **No dedicated project-instruction file exists for this controller** (unlike the Development Controller) — only its name ("App Governance & Audit") and workflow are documented. | Manual prompt-pasting per the GOV-01 prompt matrix, into Claude.ai / Claude Code / Lovable Plan Mode / optionally Antigravity, depending on step | `docs/audit-dashboard.md` (self-labeled Legacy), `docs/audits/refactor-backlog.md`, `docs/audits/current-state-report.md` (drifted since Apr 17) | Stale — same Railway/generic-folder-name staleness as the Development Controller docs |

Neither controller currently provides a formal independence guarantee between implementer and reviewer — both rely on the same Claude Code sessions doing both roles, with independence achieved only informally via ad hoc "Task-Review"/"Critic-Pass" practices noted in shared-context's `tasks/lessons.md`. This is the central gap the target operating model's Independent Verifier/Reviewer roles are meant to close.

Frontend and backend participate in this controller ecosystem asymmetrically:
- **Backend** has real symlinks: `.claude/skills/{pm-normalize-state,pm-plan-release,pm-prepare-delivery,pm-release-review,pm-sync-status}` → `../../../shared-context/.claude/skills/*`.
- **Frontend** has no such symlinks; `CLAUDE.md`'s "Delivery Workflow" section references `shared-context/docs/delivery/claude-code-prompt-templates-dev.md` and a `/close-task-dev` skill by path, but that skill is not present locally in the frontend repo (only in shared-context) and the frontend maintains its own, independently-written `close-task` skill instead.

## Skills / commands / agents inventory by repository

No repository in this project has a `.claude/agents/` directory or any Claude Code subagent definitions — "agents" in the current setup means Claude.ai Project personas (the two Controllers above) and Skills, not repo-native subagents. (The migration kit itself, separately, ships 8 read-only assurance agents — those are new/proposed, not part of the current operating system being inventoried here.)

### Shared-context — `.claude/commands/` and `.claude/skills/` (19 total)

| Name | Purpose | Mutating vs. advisory | Reusable vs. repo-specific |
|---|---|---|---|
| `/update-diagrams` (command) | Regenerate `docs/ARCHITECTURE.md` sections from `git diff --name-only HEAD` | Mutating (writes docs) | Repo-specific |
| `adr-create` | Structured ADR creation with forced options-analysis | Mutating (writes decision-log) | Reusable pattern, repo-specific paths |
| `bug-fix` | Structured diagnose-first bug-fix workflow, forces lessons entry | Mutating (code + docs) | Reusable pattern |
| `bug-report` | Structured bug capture into `docs/delivery/bugs/BUG-*.md` | Mutating (docs only) | Reusable pattern, repo-specific path |
| `cleanup-audit` | Read-only dead-code/duplication audit in a target repo, writes findings to shared-context | Read-only in target repo / mutating in shared-context | Cross-repo, reusable |
| `close-task-dev` | Auto-invoked at end of Template 2-DEV; verification + two-location stamping | Mutating | Repo-specific, has known format gaps (feature-register.md flat-table mismatch) |
| `close-task` | Manual task-closure gate: verification, contract hygiene, two-location backlog stamping | Mutating | Repo-specific, has a known unfixed path bug (`wiki/index.md` vs actual `docs/wiki/index.md`) |
| `contract-check` | Checks a target repo against `docs/contracts/` for drift before merge/ship | Advisory/read-only | Cross-repo, reusable |
| `feature-implement` | Post-GO implementation workflow, enforces typecheck + close-task-dev | Mutating (code) | Reusable pattern |
| `feature-plan` | Pre-implementation planning workflow, enforces impact-check + ADR-check | Advisory (produces plan doc) | Reusable pattern |
| `impact-check` | Cross-repo impact assessment before shared-state/API/DB changes | Advisory/read-only | Cross-repo, reusable |
| `pm-normalize-state` | Sync repo/product state before a new release cycle | Advisory (produces mismatch list) | Repo-specific (product/ paths) |
| `pm-plan-release` | Define/update next release scope | Mutating (writes `current.md`) | Repo-specific |
| `pm-prepare-delivery` | Create/update a delivery brief for an item | Mutating (writes brief) | Repo-specific |
| `pm-release-review` | Post-release review creation | Mutating (writes release-review) | Repo-specific |
| `pm-sync-status` | Update item status in feature-register after delivery/QA | Mutating | Repo-specific |
| `release-check` | Checks release readiness (open bugs, gate status) | Read-only/advisory | Repo-specific |
| `session-end` | End-of-session: update MEMORY.md, lessons check, session-dump | Mutating | Reusable pattern |
| `session-start` | Start-of-session orientation | Read-only/advisory | Reusable pattern, cross-repo |
| `verify-loop` | Defines mandatory-vs-advisory inner verification loop (SOFT-LAUNCH per ADR-011, not yet a hard gate) | Advisory | Reusable pattern |

### negotiation-buddy (frontend) — `.claude/skills/` (6) + hooks (4)

| Name | Purpose | Lifecycle-changing vs. read-only | Reusable vs. frontend-specific |
|---|---|---|---|
| `session-start` | Orientation checklist (references missing `tasks/todo.md`) | Read-only/advisory | Reusable pattern, frontend instance |
| `impact-check` | Blast-radius assessment before editing shared state/hooks/APIs | Read-only/advisory | Frontend-specific |
| `contract-check` | Gate for API/Edge Function contract changes | Read-only/advisory | Frontend-specific but structurally reusable |
| `cleanup-audit` | Read-only dead-code investigation, paired with `audit-block.sh` | Strictly read-only | Reusable pattern |
| `close-task` | Cross-repo task-closing: stamps shared-context backlog+wiki | Lifecycle-changing | Frontend-specific invocation; overlaps/conflicts with `CLAUDE.md`'s referenced `/close-task-dev` |
| `.claude/hooks/audit-block.sh` | Blocks Edit/Write/destructive Bash under `src/`/`supabase/` during audit sessions | Lifecycle-changing (hard block) | Frontend-specific paths, generic mechanism |
| `.claude/hooks/protected-file-warn.sh` | Hard-blocks edits to `types.ts`, `client.ts`, `config.toml`, `settings.local.json` | Lifecycle-changing (hard block) | Frontend-specific paths |
| `.claude/hooks/impact-check-warn.sh` | Non-blocking warning on high-impact file edits | Advisory | Frontend-specific paths |
| `.claude/hooks/stop-reminder.sh` | Stop-hook checklist reminder | Advisory | Frontend-specific; references missing `tasks/todo.md` |

### negotiationcoach-backend — `.claude/skills/` (5 local + 5 symlinked) + hooks (2)

| Name | Purpose | Lifecycle-changing vs. read-only | Reusable vs. backend-specific |
|---|---|---|---|
| `cleanup-audit` | Dead-code/redundancy/staleness scan | Read-only/advisory | Backend-specific |
| `close-task` | Verification + backlog stamping (local-backlog variant) | Lifecycle-changing | Backend-specific but structurally reusable |
| `contract-check` | API/DB/type contract sync verification | Read-only/advisory | Backend-specific |
| `impact-check` | Blast-radius/dependency-trace before changes | Read-only/advisory | Backend-specific |
| `session-start` | Session bootstrap checklist | Read-only/advisory | Reusable pattern, backend content; MCP step is misleading per L-004 |
| `pm-normalize-state`, `pm-plan-release`, `pm-prepare-delivery`, `pm-release-review`, `pm-sync-status` (symlinked to shared-context) | Shared PM/delivery-controller workflow | Lifecycle-changing (release/delivery state) | Cross-repo/reusable — the actual controller surface this repo touches |
| `.claude/hooks/audit-guard.sh` | Blocks Edit/Write outside `docs`/`tasks` during audit session marker | Lifecycle-changing (blocking) | Backend-specific but generic mechanism |
| `.claude/hooks/contract-reminder.sh` | Prints contract-sync checklist on Stop if contract files changed | Advisory only | Backend-specific but generic mechanism |

## Cross-repo Skill/command observations

- The same conceptual Skills (`session-start`, `impact-check`, `contract-check`, `cleanup-audit`, `close-task`) exist **independently, with independently-drifted content, in all three repos** rather than as one canonical reusable implementation referenced from each repo. This is the central "consolidate into a plugin" opportunity the target operating model calls for (Stage 2 §7) — but consolidation must resolve real content differences (e.g. frontend's `close-task` targets nonexistent `docs/api-catalog.md`; backend's targets its own real files; shared-context's targets `docs/wiki/*` with a known path bug), not just deduplicate file names.
- Backend is the only repo with a working symlink-based sharing mechanism today (`pm-*` skills); frontend and shared-context both rely on manual/path-reference sharing, which is where staleness and mismatches accumulate.
- Two hooks are hard-blocking today (frontend's `audit-block.sh`/`protected-file-warn.sh`, backend's `audit-guard.sh`); per the target model and migration principle #10, any *new* hook candidates proposed in Stage 2 must stay inactive until commands, matchers, and rollback are proven — these three existing ones are already proven in production use and are out of scope for that caution (they're not "candidate" hooks, they're operating ones).
- No policy file anywhere in any of the three repos carries explicit `status: approved` frontmatter — under the kit's policy model, **nothing currently in any repo qualifies as an enforceable policy**; everything found is an operative convention, rule file, or draft at best.

## Delta review — C3 canonical closure RESOLVED (2026-09-04)

All four `close-task`/`close-task-dev` variants discussed above (shared-context ×2, backend, frontend) are now formally **LEGACY** by owner decision (`10-conflicts-and-decisions.md` C3): `/negotiation-ai-sdlc:close-change` is canonical for all new SDLC-managed work; none of the four is deleted, all four are marked (see `09-proposed-file-diffs.md` Diff 8) and preserved for traceability/rollback of already-closed items. This resolves the "consolidation must resolve real content differences" caution in the first bullet above for *new* work — the four variants' individual bugs (frontend's nonexistent-path targets, shared-context's `wiki/` path bug) no longer need fixing to unblock consolidation, since they're retired rather than merged. They remain real bugs *if* the legacy Skills are ever invoked for old-style (non-SDLC) tasks, which the owner's decision does not prohibit. Separately, a direct read of `close-change/SKILL.md` found it implements only the post-release outcome-measurement stage, not the broader pre-release closure gate (intent/spec/plan accepted, verification passes, review approved, no open CRITICAL/HIGH) the owner described — an unresolved design question, not a Stage-1-discoverable fact, so not previously listed here. See `10-conflicts-and-decisions.md` C3 for the two possible readings.
