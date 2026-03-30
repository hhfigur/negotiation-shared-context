# Claude Code Prompt Templates — Refactor Control Tower

**Location:** `shared-context/docs/claude-code-prompt-templates.md`  
**Owner:** Refactor Control Tower (Claude)  
**Status:** Active  
**Last updated:** 2026-03-31

---

## Purpose

These are the two canonical prompt templates used by the Refactor Control Tower
when generating Claude Code prompts for the `negotiationcoach` project.

- **Template 1 — Plan** is used for every planning step before any code is touched.
- **Template 2 — Implementation** is used only after a plan has been reviewed and
  a GO decision has been issued.

Never skip Template 1. Never use Template 2 without a reviewed and approved plan.

---

## Template 1 — Claude Code Plan

> Trigger: `START NEXT REFACTOR` or `PLAN ITEM [ITEM_ID]`

```
PLAN ONLY. DO NOT CHANGE CODE YET.

Context:
- App: negotiationcoach
- Repo: [TARGET_REPO]
- Backlog item ID: [ITEM_ID]
- Backlog item title: [ITEM_TITLE]
- Category: [CATEGORY]
- Canonical owner (if known): [CANONICAL_OWNER_OR_TBD]

Primary goal:
Produce the smallest safe implementation plan for this backlog item.

Read first:
- repo-level CLAUDE.md and AGENTS.md
- relevant .claude/rules/*
- relevant repo docs under docs/**
- if available and relevant:
  - ../shared-context/docs/audits/refactor-backlog.md
  - ../shared-context/docs/source-of-truth-matrix.md
  - ../shared-context/docs/contracts/frontend-backend.md
  - ../shared-context/docs/auth-permission-map.md

Rules:
- Do not implement anything yet.
- Do not change files.
- Do not rename, delete, or refactor code in this step.
- Do not invent behavior you cannot verify from the code or docs.
- Classify statements as Observed, Inferred, Missing, or Proposed.
- Prefer existing modules, services, hooks, utilities, components, queries,
  and validators over introducing new ones.
- If ownership, contract, auth, permission, write path, or datastore
  responsibility is unclear, stop and mark BACK TO DOCS.

Analyze:
1. exact current behavior
2. canonical owner and competing implementations
3. files and modules involved
4. call sites and side effects
5. hidden coupling risks
6. tests currently covering this area
7. required docs/contracts/ADR updates
8. rollback considerations

Return exactly:
1. Item summary
2. Observed
3. Missing
4. Decision recommendation
   - GO
   - HOLD
   - SPLIT
   - BACK TO DOCS
5. Smallest safe scope
6. Exact files likely to change
7. Exact files that must NOT change unless explicitly approved
8. Risks and side effects
9. Required tests and checks
10. Required doc updates before and after implementation
11. Proposed implementation sequence
12. Rollback strategy
13. Suggested commit message for the implementation step
```

---

## Template 2 — Claude Code Implementation

> Trigger: `REVIEW PLAN` → GO decision issued by Control Tower

```
IMPLEMENT THE APPROVED PLAN ONLY.

Context:
- App: negotiationcoach
- Repo: [TARGET_REPO]
- Backlog item ID: [ITEM_ID]
- Backlog item title: [ITEM_TITLE]
- Approved plan summary: [PASTE_SHORT_APPROVED_PLAN]

Constraints:
- Minimal change only.
- Stay within the approved scope.
- Reuse existing code before introducing anything new.
- Do not broaden the refactor.
- Do not touch unrelated shared logic.
- Do not change ownership, contract, auth, permission, or datastore boundaries
  unless the approved plan explicitly includes it.

Before changing code:
- read repo CLAUDE.md and AGENTS.md
- read relevant docs and rules
- read the approved plan

Implementation rules:
- Prefer consolidation over reinvention.
- Preserve public behavior unless the approved plan explicitly changes it.
- If you discover a blocker that invalidates the approved plan, stop and report
  it instead of improvising.
- If a required doc update is needed as part of the same change, make it.
- Keep the diff as small and reviewable as possible.

Required output at the end:
1. What changed
2. Files changed
3. Tests/checks run or still required
4. Docs updated
5. Remaining risks or follow-up items
6. Suggested backlog status update
```

---

## Workflow sequence

```
START NEXT REFACTOR
        │
        ▼
 Template 1 → Claude Code (Plan)
        │
        ▼
REVIEW PLAN
        │
   ┌────┴────────────────┐
   ▼                     ▼
  GO               HOLD / SPLIT /
   │               BACK TO DOCS
   ▼
 Template 2 → Claude Code (Implementation)
        │
        ▼
REVIEW RESULT
        │
        ▼
 Backlog update + next item
```

---

## Field reference

| Field                    | Description                                              |
|--------------------------|----------------------------------------------------------|
| `[TARGET_REPO]`          | `negotiation-buddy` or `negotiationcoach-backend`        |
| `[ITEM_ID]`              | Backlog item ID from `refactor-backlog.md`               |
| `[ITEM_TITLE]`           | Exact title from the backlog                             |
| `[CATEGORY]`             | e.g. dead-code, duplicate-logic, contract, auth, schema  |
| `[CANONICAL_OWNER_OR_TBD]` | Named file/module, or TBD if unknown                   |
| `[PASTE_SHORT_APPROVED_PLAN]` | 3–5 sentence summary of the reviewed plan          |

---

## Rules for the Control Tower

- Template 1 is always used before Template 2. No exceptions.
- Template 2 is only issued after a GO decision in a `REVIEW PLAN` response.
- If a docs or contract gap is found during planning, the next output is a
  prerequisite task — not an implementation prompt.
- Cross-repo items are never recommended first unless no safer single-repo
  option exists in the backlog.
