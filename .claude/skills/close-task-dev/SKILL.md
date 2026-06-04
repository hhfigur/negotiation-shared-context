---
name: close-task-dev
description: Run automatically at the end of every Template 2-DEV implementation.
  Enforces verification, API/DB artifact hygiene, and atomic two-location stamping
  in both the Wave Scope and the Refactor Backlog.
trigger: Automatically invoked by Template 2-DEV. Also callable manually before
  marking any feature or bug item complete.
basis: Extends close-task skill — same step structure, additional Wave Scope stamping
  and API/DB artifact checks.
---

# Close Task Dev — /close-task-dev

Run at the end of every Template 2-DEV implementation, or before declaring any
feature/bug item complete. Enforces verification, documentation hygiene, and
atomic two-location backlog stamping.

---

## Command Syntax

```
/close-task-dev ITEM_ID=<e.g. NC-014> COMMIT=<e.g. a3f9c12> REPO=<e.g. negotiationcoach-backend> DATE=<e.g. 2026-04-24>
```

All four parameters are required. Execute Steps A–J in order. Do not skip steps.

**Prerequisite:** Claude Code must be running with shared-context visible.
Launch from the backend or frontend repo with:
```bash
claude --add-dir ../shared-context
```
Or from within shared-context with `--add-dir ../negotiationcoach-backend` or
`--add-dir ../negotiation-buddy`.

If `shared-context` is not readable, HALT — report "shared-context not accessible."

---

## Step A — Identify the backlog file

Determine which file contains the item:
- If ITEM_ID starts with `RFB-`: use `shared-context/docs/audits/refactor-backlog.md`
- If ITEM_ID starts with `NC-` or any other prefix: use `shared-context/product/feature-register.md`

Read the identified file in full.

---

## Step B — Locate the entry body

Find the section heading `### <ITEM_ID>` in the identified file.
If not found: HALT — report "ITEM_ID not found in [filename]."

---

## Step C — Check for existing DONE stamp

Scan the entry body for `**Status: DONE**`.
If already present: HALT — report "Entry already stamped DONE. Skipping."

---

## Step D — Run verification

Before stamping, confirm at least one of the following was run during this session:

- [ ] `npx tsc --noEmit` — no new errors
- [ ] `npm test` — no new failures
- [ ] API smoke test — describe endpoint called and result observed
- [ ] Manual dev server check — describe what was verified

If none of the above can be confirmed, append a verification note to the stamp
marked as "UNVERIFIED — <reason why verification was not possible>".

---

## Step E — Stamp the entry body

Append this exact block to the end of the entry body (before the next `---`):

```
**Status: DONE**
Commit: `<COMMIT>` (<REPO>) — <DATE>
Verified: <one-line summary: e.g. "tsc --noEmit clean ✓ | API /api/enrich smoke test ✓">
API contract updated: <yes — docs/api-catalog.md updated | no>
DB delta: <migration file name + tables + RLS | none>
ADR created/amended: <ADR-XXX — one-line decision | none>
Docs updated: <list of updated files, or "none">
```

---

## Step F — Locate the Summary Index row

Find the line in the `## Summary Index` table that begins with `| <ITEM_ID> |`.
If not found: HALT — report "Summary Index row not found. Fix manually before closing."

---

## Step G — Check for existing ✅ in summary row

If the row already contains `✅`: HALT — report "Summary Index row already stamped. Skipping."

---

## Step H — Stamp the Summary Index row

In the Title cell of that row, append ` — ✅ DONE \`<COMMIT>\`` to the existing title text.
Do not change Priority, Repo, Category, or any other cells.

Before:
```
| NC-014 | Layer 2 marketDataResolver fix | P1 | backend | bug |
```
After:
```
| NC-014 | Layer 2 marketDataResolver fix — ✅ DONE `a3f9c12` | P1 | backend | bug |
```

---

## Step I — Output results

```
close-task-dev: <ITEM_ID>
────────────────────────────────────────────────
Backlog file:         <filename>
Entry body update:    DONE / SKIPPED (<reason>)
Summary index update: DONE / SKIPPED (<reason>)
Verification:         <method used or UNVERIFIED>
API contract:         updated / no change
DB delta:             <migration file or none>
ADR:                  <ADR-XXX or none>
Docs:                 <list or none>
────────────────────────────────────────────────
```

---

## Step J — Output git commands

Output the exact commands to commit. Do NOT commit automatically — wait for user.

```bash
# Stage the backlog file that was stamped:
git add shared-context/docs/audits/refactor-backlog.md        # if RFB- item
# OR:
git add shared-context/product/feature-register.md            # if NC- or other item

# Stage any docs that were updated in this task:
# git add shared-context/docs/api-catalog.md                  # if API contract updated
# git add shared-context/docs/decision-log/ADR-XXX.md         # if ADR created/amended

git commit -m "docs(backlog): close <ITEM_ID> — <short title> <COMMIT>"
```

Wait for user to run the commands.

---

## Standard Verification Steps

Run before invoking /close-task-dev:

```bash
# Type check
npx tsc --noEmit

# Tests
npm test 2>&1 | tail -20

# API smoke test — example for a changed endpoint:
curl -s -X POST http://localhost:3001/api/enrich \
  -H "Authorization: Bearer $TEST_JWT" \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "test"}' | jq '.status'
```

If verification cannot be run (e.g., missing env vars), state why explicitly.
Mark as "UNVERIFIED" in the stamp rather than skipping the step.

---

## Contract Check

Before stamping, confirm:
- If any endpoint was added or changed: `docs/api-catalog.md` is updated
- If schema changed: migration file exists, types regenerated, RLS policies included
- TypeScript types reflect any shape changes
- If new frontend-backend contract exists: `docs/contracts/frontend-backend.md` updated

---

## Lessons Update

If anything went wrong or required a correction:
- Update `tasks/lessons.md` with a rule that prevents recurrence
- Format: what was the mistake, what is the rule going forward

---

## Staff Engineer Gate

Before stamping, ask: "Would a staff engineer approve this diff as-is?"

If no, or uncertain:
- List what would need to change
- Either fix it now or document it explicitly as known debt in `docs/audit-findings.md`

---

## Example Invocation

```
/close-task-dev ITEM_ID=NC-014 COMMIT=a3f9c12 REPO=negotiationcoach-backend DATE=2026-04-24
```

Expected entry body stamp:
```
**Status: DONE**
Commit: `a3f9c12` (negotiationcoach-backend) — 2026-04-24
Verified: tsc --noEmit clean ✓ | API /api/enrich smoke test returns 200 ✓
API contract updated: yes — docs/api-catalog.md updated (EnrichedAnalysisResult shape)
DB delta: none
ADR created/amended: none
Docs updated: docs/api-catalog.md
```

Expected summary index row after:
```
| NC-014 | Layer 2 marketDataResolver fix — ✅ DONE `a3f9c12` | P1 | backend | bug |
```
