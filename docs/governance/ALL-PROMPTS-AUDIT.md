# All Prompts — Audit, Governance, Refactoring

This file consolidates all prompts from the full workflow.

## How to use this file

- Replace these placeholders before use:
  - `negotiationcoach`
  - `negotiation-buddy`
  - `negotiationcoach-backend`
- Use each prompt only in the tool and mode listed in the matrix below.
- `Terminal` commands are not prompts; they are listed where needed.
- Step 2, the instruction layer setup, is mostly manual and does **not** use a large audit prompt.

---

## Prompt matrix

| Prompt ID | Step / Purpose | Enter in | Mode | Status |
|---|---|---|---|---|
| `MASTER-ARCH-01` | One-shot master prompt to install the overall operating system | Claude Code | normal | optional / broad setup |
| `CAI-01` | Set up the control tower | Claude.ai Project Chat | normal | current |
| `CAI-02` | Review phase output and define the next step | Claude.ai Project Chat | normal | current |
| `CC-BE-01` | Backend audit and documentation | Claude Code in `backend/` | normal or first `plan` | current |
| `CC-FE-01` | Frontend audit and documentation | Claude Code in `frontend/` | normal or first `plan` | current |
| `CC-XR-01` | Cross-repo synthesis and shared-context docs | Claude Code in `shared-context/` | normal or first `plan` | current |
| `LOV-01` | Lovable knowledge and boundary sync | Lovable | Plan Mode | current |
| `LOV-02` | Risky frontend change investigation before coding | Lovable | Plan Mode | optional / recurring |
| `ANT-01` | Audit dashboard / orchestration board | Antigravity Agent Chat | normal | optional |
| `CC-BL-01` | Build the refactor backlog | Claude Code in `shared-context/` | normal or first `plan` | current |
| `CC-GR-01` | Install rules, skills, and hook spec | Claude Code in `frontend/` and `backend/` | normal | current |
| `CC-RP-01` | Plan a single refactor backlog item | Claude Code in target repo | `plan` | current |
| `CC-RI-01` | Implement a single approved refactor item | Claude Code or Lovable | normal | current |

---

## Step map

### Step 0 — Start the program
1. Run `CAI-01` in **Claude.ai**.
2. Create the repos / folders and baseline branches in **Terminal**.

### Step 1 — Set up the instruction layer
This step is **manual**.
- Create and fill:
  - `shared-context/AGENTS.md`
  - `shared-context/CLAUDE.md`
  - `shared-context/docs/source-of-truth-matrix.md`
  - `shared-context/docs/contracts/frontend-backend.md`
  - `frontend/AGENTS.md`
  - `frontend/CLAUDE.md`
  - `backend/AGENTS.md`
  - `backend/CLAUDE.md`
- Then verify with `/memory` in Claude Code.

### Step 2 — Backend audit
Run `CC-BE-01` in **Claude Code** inside `backend/`.

### Step 3 — Frontend audit
Run `CC-FE-01` in **Claude Code** inside `frontend/`.

### Step 4 — Cross-repo synthesis
Run `CC-XR-01` in **Claude Code** inside `shared-context/` with `--add-dir ../frontend --add-dir ../backend`.

### Step 5 — Lovable sync
Run `LOV-01` in **Lovable Plan Mode**.

### Step 6 — Cleanup / refactor backlog
Run `CC-BL-01` in **Claude Code** inside `shared-context/`.

### Step 7 — Guardrails
Run `CC-GR-01` once in **`frontend/`** and once in **`backend/`** using Claude Code.

### Step 8 — Refactor execution
For each backlog item:
1. Run `CC-RP-01` in Claude Code Plan Mode.
2. Run `CC-RI-01` in Claude Code or Lovable, depending on where the approved change belongs.

### Review checkpoints
Run `CAI-02` in **Claude.ai** after:
- backend audit
- frontend audit
- cross-repo synthesis
- lovable sync
- light audit
- full audit

---

# Prompts

## `MASTER-ARCH-01`

**Use when:** You want Claude to propose the whole governance system in one broad pass. This is useful at the very beginning, but the prompt pack above is the more controlled operating mode.

**Enter in:** Claude Code

**Mode:** normal

```text
You are acting as a Principal Architect, Codebase Governor, and AI Workflow Designer.

Your first job is NOT to build features.
Your first job is to install a durable system that prevents architectural drift, duplicate logic, dead code, forgotten decisions, and cross-repo side effects.

## Environment
- Frontend repo: [FRONTEND_REPO_NAME], built with Lovable, synced with GitHub.
- Backend repo: [BACKEND_REPO_NAME], developed with Claude Code.
- Frontend currently uses a Lovable-managed Supabase.
- Backend uses a separate Supabase instance.
- Frontend development started before backend.
- Architecture decisions exist in Notion, but they are not reliably available to the coding agent during implementation.
- Duplicate functions, dead code, and forgotten architecture decisions are already suspected.

## Primary objective
Create a file-based, versioned, AI-readable operating system for this product.

The system must:
1. Separate shared cross-repo context from repo-local context.
2. Turn architecture decisions into durable rules, contracts, and checklists.
3. Detect and track duplicate logic, dead-code candidates, and risky coupling.
4. Create a repeatable workflow for future tasks.
5. Minimize context noise and avoid long monolithic instructions.

## Non-negotiable rules
- Do not invent facts about code you cannot see.
- Classify every statement as one of: Observed, Inferred, Missing, Proposed.
- Do not implement business features before the governance system exists.
- Keep top-level memory files concise and directive.
- Prefer focused docs and rules over one giant context file.
- Never create a new utility/service/module until you have searched for an existing equivalent.
- Every cross-repo or data-flow change must update the relevant contract and decision log.
- Treat Notion as a mirror, not the execution-time source of truth. The operational source of truth must live in git-tracked markdown.

## Work in phases

### Phase 1 — Audit
Map the current codebase and produce a current-state report that includes:
- architecture overview
- modules, services, utilities, routes, data flows, auth flows, integrations, and Supabase touchpoints
- duplicate logic candidates
- dead code candidates
- missing contracts
- missing documentation
- risky side effects / hidden coupling

For every candidate, include evidence:
- file paths
- imports / call sites
- why it may be duplicate or dead
- confidence level
- what must be verified before removal or consolidation

### Phase 2 — Design the operating system
Propose a minimal but durable structure using:

Shared context:
- [SHARED_CONTEXT_PATH]/CLAUDE.md
- [SHARED_CONTEXT_PATH]/docs/system-overview.md
- [SHARED_CONTEXT_PATH]/docs/source-of-truth-matrix.md
- [SHARED_CONTEXT_PATH]/docs/bounded-contexts.md
- [SHARED_CONTEXT_PATH]/docs/contracts/
- [SHARED_CONTEXT_PATH]/docs/decision-log/

Frontend repo:
- [FRONTEND_PATH]/CLAUDE.md
- [FRONTEND_PATH]/.claude/rules/
- [FRONTEND_PATH]/.claude/skills/
- [FRONTEND_PATH]/docs/repo-map.md
- [FRONTEND_PATH]/docs/feature-catalog.md
- [FRONTEND_PATH]/docs/redundancy-register.md
- [FRONTEND_PATH]/docs/dead-code-candidates.md
- [FRONTEND_PATH]/docs/lovable-project-knowledge.md

Backend repo:
- [BACKEND_PATH]/CLAUDE.md
- [BACKEND_PATH]/.claude/rules/
- [BACKEND_PATH]/.claude/skills/
- [BACKEND_PATH]/docs/repo-map.md
- [BACKEND_PATH]/docs/service-catalog.md
- [BACKEND_PATH]/docs/redundancy-register.md
- [BACKEND_PATH]/docs/dead-code-candidates.md

Explain exactly:
- what belongs in shared context
- what belongs only in frontend
- what belongs only in backend
- what must be mirrored into Lovable knowledge
- what must stay out of high-level context to reduce noise

### Phase 3 — Create scaffolding
Create the files and write useful first-pass content based on the visible code.
Use TODO only where the information is genuinely missing.
Do not leave empty shells unless the code truly does not provide enough evidence.

### Phase 4 — Install workflow commands
Create project skills / slash commands for:
- /session-start
- /impact-check
- /contract-check
- /cleanup-audit
- /close-task

Each skill must define:
- when to use it
- required inputs
- analysis steps
- output template
- docs/files that must be checked
- explicit “do not code yet” behavior where relevant

### Phase 5 — Guardrails
Recommend lightweight hooks and repo checks for:
- protected files / generated files
- contract-change reminders
- test and lint reminders
- completion verification before task closure

### Phase 6 — Cleanup backlog
Generate a prioritized backlog with:
- item
- repo
- evidence
- confidence
- risk of removal/change
- recommended action
- docs/contracts to update

## Output format
1. Executive summary
2. Current-state findings
3. Proposed folder tree
4. File-by-file content plan
5. Draft file contents
6. Skills / hooks proposal
7. Cleanup backlog
8. First 5 concrete actions to execute now

## Important behavior
- If only one repo is visible, do not guess the other repo. Instead create an external-interface contract and a verification gap list.
- For dead code, use the statuses: suspected / likely / verified-safe-to-remove.
- For duplicate logic, nominate one canonical owner and one migration path.
- For every architectural rule, explain the failure mode it prevents.
```

---

## `CAI-01`

**Enter in:** Claude.ai Project Chat

**Mode:** normal

```text
You are the audit control tower for a two-repo application.

Context:
- App name: [APP_NAME]
- Frontend repo: [FRONTEND_REPO_NAME]
- Backend repo: [BACKEND_REPO_NAME]
- Frontend is built with Lovable and synced with GitHub.
- Backend is developed with Claude Code.
- Frontend currently uses a Lovable-managed Supabase instance.
- Backend uses a separate Supabase instance.
- Frontend development started before backend.
- The goals are:
  1. eliminate architectural drift
  2. identify duplicate logic
  3. identify dead code candidates
  4. document the real architecture
  5. create a safe refactoring backlog
  6. keep git-tracked markdown as the operational source of truth

Your role:
- Maintain one coherent runbook for the audit.
- Review outputs from each phase.
- Detect contradictions, missing artifacts, and hidden risks.
- Generate tool-specific next steps only when I ask.
- Never act as a generic prompt factory.

Rules:
- Git-tracked markdown is the operational source of truth.
- Notion is a mirror, not the execution-time source of truth.
- Never assume unseen code.
- Classify conclusions as:
  - Observed
  - Inferred
  - Missing
  - Proposed
- Never generate one generic prompt for all tools.
- Keep outputs practical, concise, and execution-ready.
- Refactoring must follow audit and documentation, not precede it.

Whenever I say:
PREPARE NEXT STEP

you must return:
1. Goal
2. Required inputs / artifacts
3. Exact tool and mode
4. Copy-paste prompt
5. Expected files / outputs
6. Stop conditions
7. Recommended git commit message
8. Main risks to watch

Whenever I upload or paste outputs from Claude Code or Lovable, you must return:
1. What is now established as Observed
2. What remains Inferred
3. What is still Missing
4. Contradictions across repos or docs
5. The exact next action

Start now by giving me:
1. the current runbook state
2. the required artifact checklist
3. the exact first action
```

---

## `CAI-02`

**Enter in:** Claude.ai Project Chat

**Mode:** normal

**Use after:** backend audit, frontend audit, cross-repo synthesis, lovable sync, light audit, or full audit.

```text
I completed the following phase:
[PASTE PHASE NAME HERE]

Here are the produced artifacts and findings:
[PASTE OR UPLOAD THE RELEVANT DOCS / SUMMARIES HERE]

Review them as the audit control tower.

Return:
1. What is now Observed
2. What remains Inferred
3. What is still Missing
4. Contradictions or drift risks
5. Whether the phase is complete or not complete
6. The exact next action
7. The exact next tool to use
8. The exact docs that must exist before refactoring starts
```

---

## `CC-BE-01`

**Enter in:** Claude Code inside `app-workspace/backend`

**Mode:** normal or first `--permission-mode plan`

**Suggested start command:**

```bash
cd app-workspace/backend
claude
```

```text
AUDIT AND DOCUMENTATION ONLY.

Context:
- App name: [APP_NAME]
- Repo role: backend
- Frontend repo exists separately and is not the execution target of this session.
- Shared governance docs exist in a separate shared-context workspace.

Allowed changes:
- create or update markdown files only under:
  - AGENTS.md
  - CLAUDE.md
  - docs/**

Forbidden changes:
- do NOT modify application source code
- do NOT modify tests
- do NOT modify SQL migrations
- do NOT modify config files
- do NOT modify package files
- do NOT modify environment files
- do NOT refactor
- do NOT rename
- do NOT delete code

Classify every finding as:
- Observed
- Inferred
- Missing
- Proposed

If information is missing:
- create a verification gap
- continue the audit
- do not stop for open-ended questions unless absolutely necessary

Audit scope:
- entrypoints
- API routes/controllers
- services/use-cases
- validators
- auth and permission checks
- Supabase access points
- jobs/queues/cron
- shared utilities
- test coverage gaps
- duplicate logic candidates
- dead code candidates
- boundaries that appear to conflict with expected frontend/backend ownership

Create or update:
1. docs/repo-map.md
2. docs/service-catalog.md
3. docs/api-catalog.md
4. docs/db-map.md
5. docs/redundancy-register.md
6. docs/dead-code-candidates.md
7. docs/audit-findings.md
8. AGENTS.md
9. CLAUDE.md

Requirements for duplicate logic candidates:
- file paths
- call sites or references
- evidence
- why it looks duplicated
- likely canonical owner
- confidence level
- migration note
- verification needed before consolidation

Requirements for dead code candidates:
- file path
- evidence
- references or lack of references
- why it appears unused
- confidence level
- status using only:
  - suspected
  - likely
  - verified-safe-to-remove
- verification needed before removal

Documentation quality rules:
- document ownership, boundaries, flows, contracts, risks, and hotspots
- do not document trivial code line by line
- keep docs practical and operational

At the end:
1. summarize what was created or updated
2. list the highest-risk findings
3. list verification gaps
4. list files changed
5. stop
```

---

## `CC-FE-01`

**Enter in:** Claude Code inside `app-workspace/frontend`

**Mode:** normal or first `--permission-mode plan`

**Suggested start command:**

```bash
cd app-workspace/frontend
claude
```

```text
AUDIT AND DOCUMENTATION ONLY.

Context:
- App name: [APP_NAME]
- Repo role: frontend
- This frontend is built with Lovable and synced with GitHub.
- The backend exists in a separate repo and is not the execution target of this session.
- Shared governance docs exist in a separate shared-context workspace.

Allowed changes:
- create or update markdown files only under:
  - AGENTS.md
  - CLAUDE.md
  - docs/**

Forbidden changes:
- do NOT modify application source code
- do NOT modify tests
- do NOT modify package files
- do NOT modify config files
- do NOT modify environment files
- do NOT refactor
- do NOT rename
- do NOT delete code

Classify every finding as:
- Observed
- Inferred
- Missing
- Proposed

If information is missing:
- create a verification gap
- continue the audit
- do not stop for open-ended questions unless absolutely necessary

Audit scope:
- routes/pages
- layouts
- shared components
- feature components
- hooks
- stores/state
- direct Supabase access points
- API clients
- role and permission gates
- duplicated business logic
- potential dead code
- places where frontend appears to own logic that should likely belong to backend
- historical workarounds from the frontend-first phase

Create or update:
1. docs/repo-map.md
2. docs/feature-catalog.md
3. docs/data-access-map.md
4. docs/redundancy-register.md
5. docs/dead-code-candidates.md
6. docs/audit-findings.md
7. docs/lovable-project-knowledge.md
8. docs/lovable-workspace-knowledge.md
9. AGENTS.md
10. CLAUDE.md

Requirements for duplicate logic candidates:
- file paths
- call sites or references
- evidence
- why it looks duplicated
- likely canonical owner
- confidence level
- migration note
- verification needed before consolidation

Requirements for dead code candidates:
- file path
- evidence
- references or lack of references
- why it appears unused
- confidence level
- status using only:
  - suspected
  - likely
  - verified-safe-to-remove
- verification needed before removal

Additional frontend-specific requirements:
- identify all direct Lovable Supabase usage
- identify UI checks that may duplicate authorization or business rules
- identify frontend validations that may conflict with backend validation
- identify high-risk shared files and shared components
- prepare docs/lovable-project-knowledge.md and docs/lovable-workspace-knowledge.md as concise copy-ready knowledge text

Documentation quality rules:
- document ownership, boundaries, flows, contracts, risks, and hotspots
- do not document trivial code line by line
- keep docs practical and operational

At the end:
1. summarize what was created or updated
2. list the highest-risk findings
3. list verification gaps
4. list files changed
5. stop
```

---

## `CC-XR-01`

**Enter in:** Claude Code inside `app-workspace/shared-context`

**Mode:** normal or first `--permission-mode plan`

**Suggested start command:**

```bash
cd app-workspace/shared-context
claude --add-dir ../frontend --add-dir ../backend
```

```text
AUDIT AND DOCUMENTATION ONLY.

Context:
- App name: [APP_NAME]
- Frontend repo: [FRONTEND_REPO_NAME]
- Backend repo: [BACKEND_REPO_NAME]
- Current working directory is shared-context.
- Additional readable directories are:
  - ../frontend
  - ../backend
- Frontend uses a Lovable-managed Supabase instance.
- Backend uses a separate Supabase instance.
- Frontend development started before backend.

Allowed changes:
- create or update markdown files only under the current shared-context repository:
  - AGENTS.md
  - CLAUDE.md
  - docs/**

Forbidden changes:
- do NOT modify application source code in any repo
- do NOT modify tests
- do NOT modify SQL migrations
- do NOT modify configs
- do NOT modify package files
- do NOT modify environment files
- do NOT refactor
- do NOT rename
- do NOT delete code
- do NOT write to ../frontend or ../backend

Classify every finding as:
- Observed
- Inferred
- Missing
- Proposed

If information is missing:
- create a verification gap
- continue the synthesis
- do not stop for open-ended questions unless absolutely necessary

Read and synthesize from:
- ./AGENTS.md
- ./CLAUDE.md
- ./docs/**
- ../frontend/AGENTS.md
- ../frontend/CLAUDE.md
- ../frontend/docs/**
- ../backend/AGENTS.md
- ../backend/CLAUDE.md
- ../backend/docs/**

Create or update:
1. docs/system-overview.md
2. docs/bounded-contexts.md
3. docs/source-of-truth-matrix.md
4. docs/auth-permission-map.md
5. docs/contracts/frontend-backend.md
6. docs/audits/current-state-report.md
7. docs/decision-log/ADR-001-system-boundaries.md
8. docs/decision-log/ADR-002-data-ownership.md
9. AGENTS.md
10. CLAUDE.md

For every core entity or capability identify:
- canonical owner
- primary datastore
- write path
- read path
- sync/projection rule
- business logic owner
- auth/permission owner
- current violations or ambiguities

Special focus:
- dual Supabase responsibilities
- direct frontend writes that should likely be mediated by backend
- duplicated auth or permission checks
- duplicated validation logic
- historical frontend-first workarounds that should now be retired
- places where repo docs contradict each other

Documentation quality rules:
- document boundaries, contracts, ownership, data flows, side effects, and risks
- do not document every function
- when evidence is missing, mark Missing and create a verification gap

At the end:
1. summarize what was created or updated
2. list the top architectural violations or ambiguities
3. list the biggest verification gaps
4. list files changed
5. stop
```

---

## `LOV-01`

**Enter in:** Lovable

**Mode:** Plan Mode

**Important:** Before running this prompt, paste the relevant excerpts from:
- `shared-context/docs/source-of-truth-matrix.md`
- `shared-context/docs/contracts/frontend-backend.md`
- optionally `shared-context/docs/auth-permission-map.md`

```text
Plan mode only. Do not implement.

Context:
- App name: [APP_NAME]
- This project is the frontend repo.
- The backend exists in a separate repo.
- The frontend currently uses a Lovable-managed Supabase instance.
- The backend uses a separate Supabase instance.
- The purpose of this session is to align frontend knowledge and frontend boundaries with the audited architecture.

Read:
- current project knowledge
- current workspace knowledge
- repository instruction files
- docs/repo-map.md
- docs/feature-catalog.md
- docs/data-access-map.md
- docs/lovable-project-knowledge.md
- docs/lovable-workspace-knowledge.md

Also use this shared-context excerpt as architecture truth:

=== SHARED CONTEXT EXCERPT START ===
[PASTE HERE THE RELEVANT SECTIONS FROM:
- shared-context/docs/source-of-truth-matrix.md
- shared-context/docs/contracts/frontend-backend.md
- optionally shared-context/docs/auth-permission-map.md
]
=== SHARED CONTEXT EXCERPT END ===

Return exactly:

1. Current frontend boundary summary
2. Outdated or missing knowledge
3. Direct frontend data access that conflicts with the current architecture
4. Role or permission logic that may be duplicated or misplaced
5. Files or shared components that should not be touched casually
6. A copy-ready Workspace Knowledge proposal
7. A copy-ready Project Knowledge proposal
8. A minimal-change plan for future frontend work

Rules:
- Do not write code.
- Do not invent missing architecture.
- Respect backend ownership for authorization, server-side validation, and durable business logic unless explicitly documented otherwise.
- Keep the final knowledge concise, directive, and operational.
- If something is still unclear, label it as Missing instead of guessing.
```

---

## `LOV-02`

**Use when:** A frontend change looks risky and you want Lovable to investigate before writing code.

**Enter in:** Lovable

**Mode:** Plan Mode

```text
Investigate only. Do not write code yet.

Read current project knowledge and inspect the existing implementation for [ROUTE / FEATURE].

Then provide:
1. Current behavior summary
2. Existing components, hooks, services, and utilities that already implement similar logic
3. Files that are likely impacted
4. Files that must not be touched unless explicitly approved
5. Whether this change affects:
   - role logic
   - Lovable Supabase access
   - backend API contracts
   - shared auth/session behavior
6. A minimal-change plan
7. The docs/contracts that must be updated if implementation proceeds

Rules:
- Do not create new utilities or services before checking for an existing equivalent.
- Do not edit shared layout, auth, or data-access infrastructure unless necessary.
- If the change crosses a boundary, stop and propose the contract/doc update first.
```

---

## `ANT-01`

**Enter in:** Antigravity Agent Chat

**Mode:** normal

```text
Planning and orchestration only.

Create a task-oriented audit board for a two-repo application:
- frontend
- backend
- shared-context

Track these workstreams:
1. Backend audit
2. Frontend audit
3. Cross-repo synthesis
4. Lovable knowledge sync
5. Cleanup backlog
6. Guardrails installation

Rules:
- Do not treat Knowledge Items as the source of truth.
- The source of truth is git-tracked markdown in the repos.
- Summarize status, blockers, next actions, and produced artifacts.
- Create one artifact called audit-dashboard.md with:
  - workstream
  - status
  - owner/tool
  - outputs
  - blockers
  - next step
```

---

## `CC-BL-01`

**Enter in:** Claude Code inside `app-workspace/shared-context`

**Mode:** normal or first `--permission-mode plan`

**Suggested start command:**

```bash
cd app-workspace/shared-context
claude --add-dir ../frontend --add-dir ../backend
```

```text
DOCUMENTATION ONLY. DO NOT CHANGE APPLICATION CODE.

Using the current audit docs, create:
- docs/audits/refactor-backlog.md

Structure each backlog item as:
- ID
- title
- repo
- category (duplicate-logic / dead-code / boundary-violation / contract-gap)
- evidence
- confidence
- risk
- canonical owner
- recommended action
- required docs/contracts to update
- required tests to run
- dependency on other backlog items

Prioritize as:
- P0: auth, permissions, duplicate writes, security, data ownership
- P1: duplicated business logic, conflicting validation, contract mismatches
- P2: redundant hooks, components, services, utilities
- P3: naming, folder cleanup, cosmetic structure improvements
```

---

## `CC-GR-01`

**Enter in:** Claude Code in `frontend/`, then again in `backend/`

**Mode:** normal

```text
GUARDRAILS ONLY.

You may create or update:
- CLAUDE.md
- AGENTS.md
- .claude/rules/**
- .claude/skills/**
- docs/hook-spec.md

Do NOT modify application source code.

Create a durable repo operating system.

Required outputs:
1. CLAUDE.md that imports AGENTS.md and stays concise
2. .claude/rules/architecture.md
3. .claude/rules/protected-files.md
4. Repo-specific rules:
   - frontend: ui-boundaries.md, data-access.md
   - backend: api-contracts.md, db-boundaries.md
5. Skills:
   - .claude/skills/session-start/SKILL.md
   - .claude/skills/impact-check/SKILL.md
   - .claude/skills/contract-check/SKILL.md
   - .claude/skills/cleanup-audit/SKILL.md
   - .claude/skills/close-task/SKILL.md
6. docs/hook-spec.md containing exact recommended PreToolUse and Stop hook behaviors for later setup via /hooks

Rules:
- Keep CLAUDE.md concise.
- Put durable always-on rules in CLAUDE.md or .claude/rules.
- Put repeatable workflows in skills.
- Hook spec must enforce:
  - no risky edits during audit sessions
  - reminder to update contracts/ADRs/docs before closing a task
```

---

## `CC-RP-01`

**Enter in:** Claude Code inside the repo where the backlog item belongs

**Mode:** `--permission-mode plan`

```text
Plan only. Do not write code yet.

Backlog item: [ITEM_ID]

Read:
- shared-context/docs/audits/refactor-backlog.md
- relevant repo docs
- relevant contracts
- relevant ADRs

Return:
1. Smallest safe refactor scope
2. Exact files impacted
3. Side effects to watch
4. Tests to run
5. Docs/contracts to update
6. Rollback strategy
7. Whether this should be implemented in Claude Code or Lovable
```

---

## `CC-RI-01`

**Enter in:** Claude Code or Lovable, depending on the approved target tool

**Mode:** normal

```text
Implement only the approved plan for backlog item [ITEM_ID].

Rules:
- Minimal change only
- Reuse existing code before creating new utilities/services/components
- Update contracts/docs if boundaries change
- Do not touch unrelated shared logic
- After implementation, provide:
  1. changed files
  2. tests run
  3. docs updated
  4. remaining risks
```

---

# Terminal commands that belong to the flow

## Verify `CLAUDE.md` is loaded
Run inside each repo in Claude Code:

```text
/memory
```

## Backend audit start

```bash
cd app-workspace/backend
claude
```

## Frontend audit start

```bash
cd app-workspace/frontend
claude
```

## Cross-repo synthesis start

```bash
cd app-workspace/shared-context
claude --add-dir ../frontend --add-dir ../backend
```

## Backend audit commit

```bash
cd app-workspace/backend
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): initial backend audit baseline"
```

## Frontend audit commit

```bash
cd app-workspace/frontend
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): initial frontend audit baseline"
```

## Cross-repo audit commit

```bash
cd app-workspace/shared-context
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): initial cross-repo architecture baseline"
```

## Lovable knowledge sync commit

```bash
cd app-workspace/frontend
git add docs/lovable-workspace-knowledge.md docs/lovable-project-knowledge.md
git commit -m "docs(lovable): sync workspace and project knowledge"
```

---

# Minimal execution order

1. `CAI-01`
2. Manual instruction layer setup
3. `/memory` checks
4. `CC-BE-01`
5. `CAI-02`
6. `CC-FE-01`
7. `CAI-02`
8. `CC-XR-01`
9. `CAI-02`
10. `LOV-01`
11. `CAI-02`
12. `CC-BL-01`
13. `CC-GR-01` in `frontend/`
14. `CC-GR-01` in `backend/`
15. per backlog item: `CC-RP-01` -> `CC-RI-01`

