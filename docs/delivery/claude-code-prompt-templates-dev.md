# Claude Code Prompt Templates — Feature Delivery Controller

**Location:** `shared-context/docs/delivery/claude-code-prompt-templates-dev.md`
**Owner:** Feature Delivery Controller (Claude)
**Basis:** Extends `docs/claude-code-prompt-templates.md` (Refactor Templates)
**Status:** Active
**Last updated:** 2026-04-24

---

## Purpose

These are the two canonical prompt templates used by the Feature Delivery Controller
when generating Claude Code prompts for feature development and bug fixes in the
`negotiationcoach` project.

- **Template 1-DEV — Plan** is used for every planning step before any code is touched.
- **Template 2-DEV — Implement** is used only after a plan has been reviewed and
  a GO decision has been issued by the Delivery Controller.

Relationship to refactor templates:
- Template 1-DEV extends Template 1 (Refactor) with feature-specific fields:
  Layer scope, Tier scope, ADR gate, API delta, DB delta.
- Template 2-DEV extends Template 2 (Refactor) with: architecture constraint guards,
  DB migration rules, and an automatic `/close-task-dev` invocation at the end.
- `/close-task-dev` extends `/close-task` with Wave-Scope stamping and API/DB
  artifact tracking.

Never skip Template 1-DEV. Never use Template 2-DEV without a reviewed and
approved plan. Never invoke `/close-task-dev` manually if Template 2-DEV ran —
it is invoked automatically at the end of Template 2-DEV.

---

## Template 1-DEV — Claude Code Plan (Feature / Bug)

> Trigger: `PLAN ITEM [ITEM_ID]` from the Feature Delivery Controller

```
PLAN ONLY. DO NOT CHANGE CODE YET.

Context:
  App: negotiationcoach
  Repo: [TARGET_REPO]
  Item ID: [ITEM_ID]
  Item title: [ITEM_TITLE]
  Type: [bug | feature | arch]
  Layer: [0 | 1 | 2 | 3 | cross-cutting]
  Tier scope: [free | privat | kmu | profi | all]

Primary goal:
Produce the smallest safe implementation plan for this item.

Read first:
  repo-level CLAUDE.md and AGENTS.md
  relevant .claude/rules/*
  relevant repo docs under docs/**
  if available and relevant:
    ../shared-context/docs/adr/ADR-001-system-boundaries.md
    ../shared-context/docs/adr/ADR-002-data-ownership.md
    ../shared-context/docs/adr/ADR-003-ai-provider-strategy.md
    ../shared-context/docs/adr/ADR-006-tier-mapping.md
    ../shared-context/docs/adr/ADR-007-dual-layer1.md
    ../shared-context/docs/contracts/frontend-backend.md
    ../shared-context/docs/source-of-truth-matrix.md
    ../shared-context/docs/audits/refactor-backlog.md

Rules:
  Do not implement anything yet.
  Do not change files.
  Classify all statements as Observed, Inferred, Missing, or Proposed.
  Check Layer dependency order: the layer below this item's layer must be stable.
  Layer 0 → 1 → 2 → 3. Do not plan work that skips a broken layer.
  Check ADR-001: is this on the Railway execution path or Edge Function path?
  All new business logic must go to Railway Backend, not Edge Functions.
  Check ADR-002: does this introduce a new DB write? Who is the canonical writer?
  Service role key is only used by Railway. Frontend never writes directly.
  Check ADR-003: which AI provider is required?
  Railway Backend → Anthropic Claude. Edge Functions → Gemini via Lovable AI Gateway.
  Check ADR-007: does this item depend on the Dual Layer-1 decision?
  If yes and ADR-007 is not yet decided, stop and mark BACK TO DOCS.
  If tier gating is involved: confirm the check is serverside, never clientside only.
  Prefer existing modules, services, hooks, utilities, components, and validators
  over introducing new ones.
  If ownership, contract, auth, permission, write path, or datastore
  responsibility is unclear, stop and mark BACK TO DOCS.

Analyze:
  Exact goal and expected behavior after this item is complete
  Affected modules and files (new and existing)
  API contract changes (new endpoints, changed shapes, new error codes)
  DB/schema changes required (new tables, columns, migrations, RLS policies)
  Tier gating implications — which tiers are affected, where is the gate enforced?
  Layer dependency — is the layer below this item stable?
  Cross-repo impact (frontend + backend + shared-context)
  Hidden coupling risks
  Tests currently covering this area (if any)
  ADR required — yes / no, and if yes: new ADR or amend existing?
  Required docs/contracts updates (before and after implementation)

Return exactly:
  Item summary
  Observed (what exists today relevant to this item)
  Missing (what does not exist yet)
  ADR required: yes / no — if yes: which decision, new or amend existing ADR
  Decision recommendation (GO / HOLD / SPLIT / BACK TO DOCS)
  Smallest safe scope
  New files to create
  Existing files likely to change
  Files that must NOT change unless explicitly approved
  API contract delta (new/changed endpoints, shapes, error codes — or "none")
  DB delta (migrations, new tables, RLS policies needed — or "none")
  Risks and side effects
  Required tests and checks
  Required doc updates before and after implementation
  Proposed implementation sequence
  Rollback strategy
  Suggested commit message for the implementation step
```

---

## Template 2-DEV — Claude Code Implementation (Feature / Bug)

> Trigger: `REVIEW PLAN` → GO decision issued by Feature Delivery Controller

```
IMPLEMENT THE APPROVED PLAN ONLY.

Context:
  App: negotiationcoach
  Repo: [TARGET_REPO]
  Item ID: [ITEM_ID]
  Item title: [ITEM_TITLE]
  Type: [bug | feature | arch]
  Approved plan summary: [PASTE_SHORT_APPROVED_PLAN]
  ADR required: [yes — ADR-XXX to be created / amended | no]

Constraints:
  Implement exactly what was approved. Nothing more.
  Stay within the approved scope.
  Reuse existing modules, services, hooks, utilities, and validators before
  introducing new ones.
  Do not touch unrelated code.
  Do not change ownership, contract, auth, permission, or datastore boundaries
  unless the approved plan explicitly includes it.
  All tier checks must be serverside — never clientside only.
  All LLM calls must go via Railway Backend using Anthropic Claude.
  Never add LLM calls to Edge Functions.
  No new DB writes from Frontend without a documented ADR reference.
  All new DB tables must have an RLS policy in the same migration file.
  Schema changes via migration files only — never via Supabase Dashboard.

Before changing code:
  Read repo CLAUDE.md and AGENTS.md
  Read relevant .claude/rules/*
  Read the approved plan
  Run impact-check skill if any cross-repo impact is present

Implementation rules:
  Prefer consolidation over reinvention.
  Preserve existing public behavior unless the approved plan explicitly changes it.
  If you discover a blocker that invalidates the approved plan, STOP and report
  it — do not improvise or broaden scope.
  If a required doc update is part of this change, make it in the same commit.
  If a migration is needed: create the migration file, include RLS policies,
  do NOT apply via dashboard.
  If an ADR is required: create or amend it before or alongside the implementation
  — not after.
  Keep the diff as small and reviewable as possible.

Required output at the end:
  What changed (per file — one line each)
  Files changed (list)
  New files created (list, or "none")
  API contract delta (changed/new endpoints, shapes, error codes — or "none")
  DB delta (migration file name, tables, RLS policies — or "none")
  Tests run or still required
  Docs updated (list, or "none")
  ADR created or amended (file name and decision — or "none required")
  Remaining risks or follow-up items

After producing this output, immediately run:
/close-task-dev ITEM_ID=[ITEM_ID] COMMIT=[COMMIT_HASH] REPO=[TARGET_REPO] DATE=[DATE]
```

---

## Field Reference

| Field | Content |
|---|---|
| `[TARGET_REPO]` | `negotiation-buddy` or `negotiationcoach-backend` |
| `[ITEM_ID]` | Item ID from wave2-scope.md or refactor-backlog.md (e.g. NC-014, RFB-026) |
| `[ITEM_TITLE]` | Exact title from the backlog or wave scope |
| `[TYPE]` | `bug`, `feature`, or `arch` |
| `[LAYER]` | `0`, `1`, `2`, `3`, or `cross-cutting` |
| `[TIER_SCOPE]` | `free`, `privat`, `kmu`, `profi`, or `all` |
| `[PASTE_SHORT_APPROVED_PLAN]` | 3–5 sentence summary of the reviewed plan |
| `[COMMIT_HASH]` | Short git commit hash after implementation commit |
| `[DATE]` | ISO date of implementation (e.g. 2026-04-24) |

---

## Rules for the Feature Delivery Controller

- Template 1-DEV is always used before Template 2-DEV. No exceptions.
- Template 2-DEV is only issued after a GO decision in a `REVIEW PLAN` response.
- If an ADR is required and not yet decided, the next output is an ADR task —
  not an implementation prompt.
- If Layer N-1 is unstable, no Template 1-DEV or 2-DEV is issued for Layer N.
- Cross-repo items require an explicit impact assessment before Template 1-DEV.
- `/close-task-dev` is always invoked automatically at the end of Template 2-DEV.
  Never wait for the user to trigger it.
