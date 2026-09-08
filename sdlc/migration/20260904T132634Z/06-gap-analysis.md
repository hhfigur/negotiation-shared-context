# Stage 2 — Gap Analysis

Compares the Stage 1 inventory against `02-target-operating-model.md` and the migration kit's overlays, organized by the 12 gap-analysis requirements in the master prompt.

## Delta review — actual gaps vs. stale-documentation gaps (owner-confirmed, 2026-09-04)

The owner's three corrections (Supabase single-instance intent, Lovable retirement, Railway retirement) let this analysis now separate what was previously bundled together: **items that are real architectural/process gaps requiring new work**, vs. **items that are purely stale documentation requiring a correction, with no underlying architecture problem at all.** This distinction changes how items 5 and 9 below should be read:

| Item | Was framed as | Now classified as | Why |
|---|---|---|---|
| #5 (concise root `CLAUDE.md`) — Supabase hard-constraint wording | Blocking decision needed | **Stale-documentation gap only — decision RESOLVED, no longer blocking** | The owner has settled that frontend/backend intentionally share one Supabase project. The kit template's proposed hard-constraint line ("do not assume the backend/frontend Supabase instance shares schema... with the other") must simply **not** be adopted verbatim — it is factually wrong for this project. See `10-conflicts-and-decisions.md` C2 RESOLVED and `04-supabase-boundary-map.md`'s new governance section for the affirmative wording to use instead. |
| #9 (Controller repositioning) — Lovable Plan Mode as an Audit Controller invocation path | Not previously flagged as a decision point | **Real correction needed before adoption, newly surfaced** | `05-instruction-and-skill-map.md`'s delta review found the target `AUDIT_REFACTORING_CONTROLLER.md` template's invocation list still names "Lovable Plan Mode" as a live venue. This is not a documentation-debt item to leave for later — it must be corrected before Phase D lands the new Controller docs, since pasting it as-is into a live Claude.ai Project would hand an operator a dead invocation path. |
| Railway naming sweep (Phase E, `08-migration-plan.md`) | Previously "misdirects any agent that reads these before code" (a suspected/likely-but-unconfirmed risk) | **Confirmed-stale documentation, no architectural gap underneath** | The owner has confirmed Render.com is current and Railway is retired — there was never a live Railway/Render.com dual-hosting question, only outdated prose. No governance or architecture work is needed here beyond the mechanical grep-and-replace already scoped in Phase E. |
| Lovable-as-active-frontend-dev-tool references (`docs/lovable-*-knowledge.md`, `.lovable/plan.md`, README boilerplate) | Not separately called out | **Confirmed-stale documentation, no architectural gap underneath** | Same reasoning as Railway — the owner's correction resolves this as a pure documentation-currency issue. `lovable-tagger` remaining as a build dependency (see `01-current-inventory.md` delta review) is the one item here that is not purely documentational and may warrant a separate, later cleanup decision (not part of this migration). |

Every other gap-analysis item (1-4, 6-8, 10-12) is unaffected by the owner's corrections and stands as originally analyzed below, **except** item 7/8 (plugin consolidation, "install plugin, compare with existing Skills"): a direct re-read of the kit's Skill source files this pass found the kit's own `assess-supabase` Skill contains an instruction that directly contradicts owner decision C2 (`"Never assume the frontend and backend Supabase projects share identity, schema, data, or lifecycle"`), plus four smaller Lovable-assumption lines across `create-plan`, `assess-ux`, and two `frontend` overlay templates. See `10-conflicts-and-decisions.md`'s new "Kit Skill/template corrections required before adoption" table for the full list — these must be corrected at install time, not adopted verbatim, which item 7's original "install-only addition" framing did not anticipate.

## 1. Shared-context/sdlc/ as cross-repository artifact home

**Gap**: does not exist yet. `shared-context` has no `sdlc/` directory outside of this analysis's own report folder (`sdlc/migration/`, created by this process, not project content).
**Target**: `shared-context-overlay/sdlc/` ships `README.md`, `registry.yaml`, `changes/` (empty, `.gitkeep`), `policies/` (6 draft policy templates + README), `templates/` (10 artifact templates), `scripts/` (`new_change.py`, `validate_change.py`).
**Mechanism**: additive copy of `shared-context-overlay/sdlc/*` into `shared-context/sdlc/`, alongside (not replacing) the existing `sdlc/migration/` this process created. No existing shared-context content collides with this path — clean addition.

## 2. `sdlc/changes/<change-id>/` per change

**Gap**: no per-change lifecycle folder convention currently exists. The closest analogues are `product/briefs/*.md` (one-off delivery briefs, not full lifecycle artifacts), `docs/delivery/*` (planning/session-dump docs), and `docs/delivery/bugs/*` (defect docs) — all real, all valuable, none matching the intent→spec→plan→verify→review→release→outcome structure.
**Target**: the kit's `templates/{intent,spec,plan,debug-evidence,verification,review,release,outcome,incident}.md` + `traceability.yaml` template, instantiated per change via `sdlc/scripts/new_change.py`.
**Mechanism**: no existing file is superseded by this — it's a genuinely new practice. Migration principle #3 ("one authoritative home per information class") means `product/briefs/*` and `docs/delivery/*` should be **linked from**, not replaced by, future `sdlc/changes/<id>/` folders — see `08-migration-plan.md` Phase A and `10-conflicts-and-decisions.md` for how existing briefs relate to future changes.

## 3. Bidirectional traceability

**Gap**: traceability today is one-directional and file-specific — `product/feature-register.md` (PM-facing status), `docs/audits/refactor-backlog.md` (technical backlog), `docs/wiki/index.md`/`session-log.md` (open items log) each carry partial state, cross-referenced by convention, not by a shared schema. No file links a requirement → implementation path → test → evidence → release → outcome in one record.
**Target**: `templates/traceability.yaml` (kit) defines `FR-###`/`NFR-###`/`AC-###`/`R-###`/`E-###`/`H-###`/`F-###` ID conventions and one traceability record per change.
**Mechanism**: additive — new changes get a `traceability.yaml`; retrofitting old items is out of scope for this migration (per "discover before designing" and "do not invent... approvals," retroactive traceability for already-shipped items would require guessing history).

## 4. Convert or link existing requirements/plans rather than copying blindly

**Gap**: `product/roadmap.md`, `product/strategy.md`, `product/feature-register.md`, `product/briefs/*`, and `docs/features/*` already constitute real product-intent and specification material — none of it should be duplicated into `sdlc/changes/`.
**Target**: per `05-source-of-truth.yaml`'s `copy_rule` ("Link to canonical artifacts. Copy only when a verified tool limitation requires it..."), new `intent.md`/`spec.md` files for *new* changes should **link to** relevant existing `product/` and `docs/features/` material rather than restating it.
**Mechanism**: no file moves; a documentation convention only — captured in the refactored shared-context `CLAUDE.md`/`AGENTS.md` orientation, not a structural change.

## 5. Refactor each root `CLAUDE.md` into a concise orientation + verification contract

**Gap** (per-repo, from Stage 1):
- Frontend `CLAUDE.md`: currently mixes root operating rules with a "Delivery Workflow" section that itself has an internal conflict (references `/close-task-dev`, which isn't present locally, while the repo also ships its own independent `close-task` skill).
- Backend `CLAUDE.md`: similar shape — operating rules + delivery workflow triggers, generally cleaner but not yet split into orientation vs. path-scoped rules.
- Shared-context `CLAUDE.md`: already imports `AGENTS.md` + `product/*` via `@import` — closest of the three to the target's "root = orientation, detail = elsewhere" model already.
**Target**: `repo-overlays/{frontend,backend}/CLAUDE.md.template` — read in full this pass — define exactly this shape: repository role (1 paragraph), session-start resolution steps (`.sdlc/config.yaml` → active change → accepted intent/spec/plan → git status → path-scoped rules), a **verified-commands block with explicit `<DISCOVER>`/`<DISCOVER_OR_NOT_AVAILABLE>` placeholders** (never invented — to be filled from `03-command-and-toolchain-evidence.md`), an architecture-orientation section that **links out** rather than inlines detail, hard constraints, and a completion contract. **RESOLVED 2026-09-04** (was: "do not assume the backend/frontend Supabase instance shares schema... with the other" pending an owner decision — see `10-conflicts-and-decisions.md` C2): the owner has confirmed the instance **is** intentionally shared, so this line must **not** be adopted verbatim. Use instead the affirmative governance wording from `04-supabase-boundary-map.md`'s "Governance implications of the shared instance" section (migration-coordination rule, per-table ownership map, VG-01/VG-02 as a precondition, service-role-stays-backend-only).
**Mechanism**: **merge, not replace.** The template's session-start/verified-commands/hard-constraints/completion-contract sections are additive structure; the *existing* repository-specific content Stage 1 found (Lovable conventions, layer architecture, protected-file lists, etc.) stays — largely already externalized into `.claude/rules/*` and `docs/*` in both repos, which is precisely the target shape. This migration proposes restructuring, not a wholesale rewrite; the literal merged text is Stage 3 work requiring a full read of the current file (Stage 1's agents summarized but did not return complete file text) — see `09-proposed-file-diffs.md`.

## 6. Move path-specific instructions into `.claude/rules/` only after validating actual path patterns

**Gap**: both frontend and backend **already** use `.claude/rules/*.md` for path-scoped guardrails (`architecture.md`, `data-access.md`, `db-boundaries.md`, `ui-boundaries.md`, `protected-files.md`, `api-contracts.md` in each) — this part of the target model is **already substantially implemented**, ahead of the kit's own overlay in maturity (the kit's `.claude/rules/frontend-ui.md`/`backend-tests.md`/etc. use YAML frontmatter `paths:` globs; the existing repo rules do not use frontmatter path-scoping at all — they're always-loaded prose files).
**Target**: kit overlay rules (`00-sdlc-contract.md` cross-cutting + `frontend-ui.md`/`frontend-tests.md` or `backend-tests.md`/`supabase-data.md`/`backend-api-domain.md`, each with a `paths:` frontmatter block) explicitly say "retain only path patterns that exist in this repository" — i.e., the glob lists in the templates (`src/**/*.ts`, `supabase/**/*`, etc.) must be checked against each repo's real structure before adoption, not pasted verbatim.
**Mechanism**: additive new rule files (`00-sdlc-contract.md` + 2 domain rule files per repo) alongside the existing rule files, which are KEPT (per artifact map, all `KEEP` except the two flagged `SUPERSEDE_LATER`/`MERGE` for stale content). No existing rule file is replaced by this step.

## 7. Consolidate reusable lifecycle workflows into the `negotiation-ai-sdlc` plugin

**Gap**: the same conceptual Skills (`session-start`, `impact-check`, `contract-check`, `cleanup-audit`, `close-task`) exist **independently and with independently-drifted content in all three repos** (see `05-instruction-and-skill-map.md` § Cross-repo Skill/command observations). This is the clearest, highest-value consolidation opportunity found.
**Target**: the kit ships a fully-built plugin at `shared-context-overlay/tooling/claude-marketplace/plugins/negotiation-ai-sdlc/` — 10 manual lifecycle Skills (`capture-intent`, `create-spec`, `create-plan`, `implement-change`, `diagnose-bug`, `fix-diagnosed-bug`, `verify-change`, `review-change`, `close-change`, `incident-to-intent`), 6 advisory policy-assessment Skills (`assess-{security,privacy,architecture,ux,supabase,ai-quality}`), and 8 read-only assurance agents (`change-reviewer`, `codebase-researcher`, `plan-critic`, `policy-auditor`, `root-cause-analyst`, `spec-critic`, `traceability-auditor`, `verifier`), installed once via a local marketplace and available to all three repo windows without copying.
**Mechanism**: install-only addition (`/plugin marketplace add` + `/plugin install`, per `tooling/claude-marketplace/README.md`, read in full this pass). This is **new lifecycle machinery**, not a replacement for the existing repo-native Skills — see item 8.

## 8. Preserve project-specific Skills locally when not reusable

**Gap/decision**: several existing Skills are genuinely repo-specific and should stay put (`update-diagrams` in shared-context; the hooks in frontend/backend). Others (`session-start`, `impact-check`, `contract-check`, `cleanup-audit`, `close-task`/`close-task-dev`) conceptually overlap with the new plugin's lifecycle Skills but are **not identical** — the plugin's Skills operate on `sdlc/changes/<id>/` artifacts; the existing Skills operate on `product/feature-register.md`, `docs/audits/refactor-backlog.md`, and repo-local docs. These are not simple duplicates to delete; per migration principle #3 and constraint #1, comparison and an explicit decision are required before any merge. See `10-conflicts-and-decisions.md`.
**Target**: kit's `close-change`/`verify-change`/`review-change` Skills vs. existing `close-task`/`verify-loop`/informal review practice.
**Mechanism**: no action in this ANALYZE_ONLY pass beyond recording the comparison — Stage 3 would require the owner to decide per-Skill: keep both running in parallel during a transition, retire the old one after the new one is proven on the pilot change, or keep the old one permanently for its current non-lifecycle-artifact use case (e.g. `close-task`'s stamping of `product/feature-register.md`, which the new plugin does not touch at all).

**RESOLVED for `close-task`/`close-task-dev` specifically, 2026-09-04 (C3, `10-conflicts-and-decisions.md`)**: the owner decided directly rather than leaving it for Stage 3 — `/negotiation-ai-sdlc:close-change` is canonical for new SDLC-managed work, all four existing close-task variants are LEGACY (marked, not deleted, not merged). `session-start`/`impact-check`/`contract-check`/`cleanup-audit` remain open per the original framing above — no owner ruling was given for those, and they don't have a 1:1 kit-Skill counterpart the way close-task does (the kit's advisory policy Skills `assess-*` are a different shape: read-only, forked, policy-scoped, not general pre-work checklists).

## 9. Reposition Development Controller as orchestrator; Audit/Refactoring Controller as independent assurance

**Gap**: today, both Controllers exist only as stale (Railway-era) Claude.ai Project instruction documents (`docs/governance/delivery-controller-{setup,grundinstruktion}.md`, and — for the Audit Controller — only a workflow doc with no dedicated instruction file at all). Neither has a built-in independence mechanism; the same session that implements typically also "audits" via ad hoc practices.
**Target**: `shared-context-overlay/controllers/DEVELOPMENT_CONTROLLER.md` (read in full) — a complete, file-backed state machine over `sdlc/changes/<id>/`, with an explicit stage table (`No change record → capture-intent`, ... `Released → close-change`, `Production incident → incident-to-intent`), a source-of-truth contract, plan-deviation handling, traceability-update duty, and a mandatory session handoff via `SESSION_HANDOFF_TEMPLATE.md`. `AUDIT_REFACTORING_CONTROLLER.md` (read in full) — 10 independent review passes (gate integrity, intent alignment, requirements coverage, correctness, architecture, security/privacy, **Supabase and data boundary** [Pass 7 explicitly requires verifying "which project owns data and migrations... cross-project flows" — directly actionable against this analysis's Supabase finding], UX/accessibility, AI quality, release/outcome readiness), a structured finding format (`F-###`/severity/evidence/disposition), and hard independence rules ("Do not use the implementation session's completion statement as evidence... Do not edit code, tests, or lifecycle artifacts while acting as the independent auditor").
**Mechanism**: additive new files at `shared-context/sdlc/../controllers/` (or wherever Stage 3 places them — see `07-target-file-tree.md`); the *old* Controller docs are not deleted (`ALLOW_DELETIONS_OR_RENAMES: false`) but proposed `SUPERSEDE_LATER` once the new ones are validated in the pilot — see `10-conflicts-and-decisions.md` for the reactivation risk if the old docs are pasted into a fresh Claude.ai Project as-is (they'd reintroduce the Railway/ADR-003 staleness).

## 10. Root-cause lane separating diagnosis from implementation

**Gap**: partially present today — shared-context's `bug-fix` Skill is explicitly "diagnose-first," and `docs/delivery/bugs/*` capture diagnosis docs — but nothing enforces the separation as a hard gate (a session can go straight to editing code), and there's no dedicated read-only root-cause agent.
**Target**: kit's `diagnose-bug` Skill (produces `debug-evidence.md` only, no code edits) + `fix-diagnosed-bug` Skill (requires `fix_authorized: true` in the diagnosis record before it will proceed) + `root-cause-analyst` read-only agent (no Write/Edit tool, per acceptance criteria).
**Mechanism**: additive Skills/agent; the existing `bug-fix`/`bug-report` Skills are not replaced (`KEEP` per artifact map) — they can coexist during a transition, with the new gate applied to the pilot change specifically.

## 11. Candidate hooks defined but inactive

**Gap**: frontend and backend already run **active, hard-blocking** hooks in production (`audit-block.sh`/`protected-file-warn.sh` in frontend, `audit-guard.sh` in backend) — these are proven, working, and out of scope for the "stay inactive" caution, since they're not candidates, they're operating controls.
**Target**: `tooling/hook-design/HOOK_CANDIDATES.md` (read in full) proposes 5 **new** candidate hooks (lifecycle-artifact validation post-write, formatter/linter post-edit, secret/local-file protection pre-commit, implementation-gate check pre-edit, stop/completion-evidence check) — explicitly "No hook in this migration kit is active," with 8 named activation criteria and a one-at-a-time rollout rule.
**Mechanism**: documentation-only addition in this pass (the candidates file itself); no hook is wired into any repo's `settings.json` by this migration, consistent with constraint #10.

## 12. Support independent frontend/backend sessions while Shared-context remains authoritative

**Gap**: today, "cross-repo awareness" is implemented ad hoc — `additionalDirectories` pointing at `../shared-context` in both frontend and backend's `.claude/settings.json`, plus path references in `CLAUDE.md`/skills. This mostly works today (both repos can already read shared-context) but has no explicit, versioned local-path-resolution contract, and the two repos resolve it inconsistently (backend via symlinks, frontend via bare paths).
**Target**: `.sdlc/config.yaml` (tracked, logical identity) + `.sdlc/config.local.yaml` (gitignored, absolute path to Shared-context) + `.sdlc/active-change.yaml` (optional, real pilot only) — both templates read in full this pass; `.gitignore.additions` (`.sdlc/config.local.yaml`) confirmed as the exact line to add.
**Mechanism**: additive new `.sdlc/` directory per code repo; does not touch the existing `additionalDirectories` mechanism, which can coexist.

## Summary table

| # | Target requirement | Current gap severity | Migration mechanism | Blocking decision needed? |
|---|---|---|---|---|
| 1 | `sdlc/` home | Missing entirely | Additive copy | No |
| 2 | Per-change folders | Missing entirely | New convention + scripts | No |
| 3 | Bidirectional traceability | Partial, file-specific | New `traceability.yaml` per change | No |
| 4 | Link don't copy | Mostly N/A (no changes exist yet) | Documentation convention | No |
| 5 | Concise root CLAUDE.md | Present but mixed with workflow detail | Merge with kit template | ~~Yes~~ **No — RESOLVED 2026-09-04.** Supabase-sharing wording corrected per owner decision C2 (see `10-conflicts-and-decisions.md`); use affirmative governance wording, not a "don't assume sharing" constraint |
| 6 | Path-scoped rules | Already substantially implemented | Additive new rule files, validate globs | No |
| 7 | Plugin consolidation | High duplication across repos | Install plugin, compare with existing Skills | Partial — ~~Yes~~ **close-task/close-task-dev RESOLVED 2026-09-04 (C3): LEGACY, `close-change` canonical.** `session-start`/`impact-check`/`contract-check`/`cleanup-audit` still open |
| 8 | Preserve local Skills | N/A until item 7 decided | — | Same as above |
| 9 | Controller repositioning | Both Controllers stale and non-independent | Additive new controller docs | Yes — old docs' disposition (Development Controller doc also needs one addition: canonical API contract source-of-truth line, per C1 RESOLVED 2026-09-04) |
| 10 | Root-cause lane | Partially present | Additive Skill + agent | No |
| 11 | Inactive hook candidates | N/A (existing hooks already active/proven) | Documentation only | No |
| 12 | Dual-window support | Ad hoc, inconsistent | Additive `.sdlc/` config | No |
