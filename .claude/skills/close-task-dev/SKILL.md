---
name: close-task-dev
description: Run automatically at the end of every Template 2-DEV implementation.
  Enforces verification, API/DB artifact hygiene, and atomic two-location stamping
  in both the Wave Scope / Refactor Backlog and the Feature Register.
trigger: Automatically invoked by Template 2-DEV. Also callable manually before
  marking any feature or bug item complete.
basis: Extends close-task skill — same step structure, additional Wave Scope stamping
  and API/DB artifact checks.
---

# Close Task Dev — /close-task-dev

Run at the end of every Template 2-DEV / Template 2b-DEV implementation, or
before declaring any feature/bug item complete. Enforces verification,
documentation hygiene, and atomic two-location backlog stamping.

Supports two backlog file formats — detected automatically in Step A:
- **Backlog format** (`docs/audits/refactor-backlog.md`, `RFB-` items):
  `### <ITEM_ID>` entry-body headings + a separate `## Summary Index` table.
- **Register format** (`product/feature-register.md`, `NC-` and other items):
  a single flat `## Register` table (`| ID | Title | Type | Status | Affected Repos | Target Release | Notes |`),
  no per-item headings, no separate summary index.

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

## Step A — Identify the backlog file and format

Determine which file contains the item:
- If ITEM_ID starts with `RFB-`: use `shared-context/docs/audits/refactor-backlog.md` → **Backlog format**
- If ITEM_ID starts with `NC-` or any other prefix: use `shared-context/product/feature-register.md` → **Register format**

Read the identified file in full.

Do not assume format from the prefix alone if the file's actual structure
disagrees — confirm by checking for `### <ITEM_ID>` (Backlog format) vs a
`| <ITEM_ID> |` row inside a `## Register` table (Register format). If
neither is present, treat as "not found" (see Step B / Step B2).

---

## Step A2 — Multi-Phase Completeness Gate (PFLICHT, beide Formate)

`/close-task-dev` marks an item as fully **DONE / Released**. Many feature
items ship in multiple phases (see the item's Brief in `product/briefs/<ITEM_ID>.md`
if one exists, and/or its design doc).

Check: does the Brief or design doc describe this item as having multiple
phases (e.g. "Phase X von Y", an explicit phase/sequence list, or a Brief
`## Implement` section that only covers part of the item's `## Scope`)?

- **If multi-phase AND not all phases are complete:**
  HALT — do not stamp DONE/Released. Report:
  ```
  close-task-dev: <ITEM_ID> — HALTED (incomplete, multi-phase item)
  Phase status: <X of Y complete, per <source>>
  Correct action instead: update product/briefs/<ITEM_ID>.md `## Implement`
  section with this phase's result, and update the Register row's Notes
  cell / Backlog entry body with the phase status. Do NOT change Status to
  Released/DONE until all phases are complete.
  ```
  This mirrors how partial progress is already tracked (see
  `product/briefs/NC-L3-SIM.md` for the reference pattern: Status stays
  `IN PROGRESS`, `## Implement` documents each phase as it lands).

- **If single-phase, or this is confirmed to be the final phase:**
  proceed to Step B (Backlog format) or Step B2 (Register format).

---

## Backlog Format (`docs/audits/refactor-backlog.md`, `RFB-` items)

### Step B — Locate the entry body

Find the section heading `### <ITEM_ID>` in the identified file.
If not found: HALT — report "ITEM_ID not found in [filename]."

### Step C — Check for existing DONE stamp

Scan the entry body for `**Status:** DONE`.
If already present: HALT — report "Entry already stamped DONE. Skipping."

### Step E — Stamp the entry body

Append this exact block to the end of the entry body (before the next `---`):

```
**Status:** DONE
Commit: `<COMMIT>` (<REPO>) — <DATE>
Verified: <one-line summary: e.g. "tsc --noEmit clean ✓ | API /api/enrich smoke test ✓">
API contract updated: <yes — docs/api-catalog.md updated | no>
DB delta: <migration file name + tables + RLS | none>
ADR created/amended: <ADR-XXX — one-line decision | none>
Docs updated: <list of updated files, or "none">
```

### Step F — Locate the Summary Index row

Find the line in the `## Summary Index` table that begins with `| <ITEM_ID> |`.
If not found: HALT — report "Summary Index row not found. Fix manually before closing."

### Step G — Check for existing ✅ in summary row

If the row already contains `✅`: HALT — report "Summary Index row already stamped. Skipping."

### Step H — Stamp the Summary Index row

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

## Register Format (`product/feature-register.md`, `NC-` and other items)

The Register has no per-item entry body and no separate summary index — one
row carries both the status stamp and the summary. Status values are the
`product/README.md` Standard status values (`Idea | Qualified | Planned |
In Delivery | Ready for Release | Released | Verified | Paused | Dropped`).
`/close-task-dev` maps its DONE-stamp to **`Released`** — `Verified` is a
distinct, later confirmation and is never set by this skill (per
`product/README.md`: "`Released` is not the same as `Verified`").

### Step B2 — Locate the Register row

Find the line in the `## Register` table that begins with `| <ITEM_ID> |`.
If not found: HALT — report "ITEM_ID not found in feature-register.md."

### Step C2 — Check for existing Released/Verified stamp

Read the row's `Status` cell.
If it already reads `Released` or `Verified`: HALT — report
"Row already stamped <Status>. Skipping."

### Step E2 — Stamp the Register row

Update three cells of the row, leave `Type`, `Affected Repos`, and
`Target Release` untouched unless the task explicitly changed them:

1. **Title cell:** append ` — ✅ DONE \`<COMMIT>\`` to the existing title
   text (same mechanic as Backlog-format Step H).
2. **Status cell:** set to `Released`.
3. **Notes cell:** append (do not delete existing notes — prepend a `·`
   separator if the cell is non-empty) a condensed one-line stamp:
   ```
   Verified: <summary>. API contract: <yes/no>. DB delta: <delta/none>. ADR: <ref/none>. Docs: <list/none>. Commit `<COMMIT>` (<REPO>) — <DATE>.
   ```

Before:
```
| NC-014 | Layer 2 marketDataResolver fix | Bug | In Delivery | negotiationcoach-backend | R-2026-05 | Brief: product/briefs/NC-014.md |
```
After:
```
| NC-014 | Layer 2 marketDataResolver fix — ✅ DONE `a3f9c12` | Bug | Released | negotiationcoach-backend | R-2026-05 | Brief: product/briefs/NC-014.md · Verified: tsc clean, API smoke test ✓. API contract: no. DB delta: none. ADR: none. Docs: none. Commit `a3f9c12` (negotiationcoach-backend) — 2026-04-24. |
```

If the item has a Brief (`product/briefs/<ITEM_ID>.md`), also update its
`**Status:**` header field to `Released` and add/confirm a closing note in
its `## Implement` section — the Brief and the Register row must agree.

---

## Step D — Run verification (shared, both formats)

Before stamping, confirm at least one of the following was run during this session:

- [ ] `npx tsc --noEmit` — no new errors
- [ ] `npm test` — no new failures
- [ ] API smoke test — describe endpoint called and result observed
- [ ] Manual dev server check — describe what was verified

If none of the above can be confirmed, append a verification note to the stamp
marked as "UNVERIFIED — <reason why verification was not possible>".

Run this before stamping (Step E or Step E2), regardless of format.

---

## Step I — Output results

```
close-task-dev: <ITEM_ID>
────────────────────────────────────────────────
Format:                <Backlog (### + Summary Index) | Register (flat table)>
Backlog file:          <filename>
Entry/Row update:      DONE / SKIPPED (<reason>)
Summary index update:  DONE / SKIPPED (<reason>) / N/A (Register format)
Brief updated:         <yes — product/briefs/<ITEM_ID>.md | no Brief exists>
Verification:          <method used or UNVERIFIED>
API contract:          updated / no change
DB delta:              <migration file or none>
ADR:                   <ADR-XXX or none>
Docs:                  <list or none>
────────────────────────────────────────────────
```

---

## Step J — Output git commands

Output the exact commands to commit. Do NOT commit automatically — wait for user.

```bash
# Stage the backlog file that was stamped:
git add shared-context/docs/audits/refactor-backlog.md        # if RFB- item (Backlog format)
# OR:
git add shared-context/product/feature-register.md            # if NC- or other item (Register format)

# If a Brief was updated (Register format):
# git add shared-context/product/briefs/<ITEM_ID>.md

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

## Example Invocation — Backlog format

```
/close-task-dev ITEM_ID=RFB-014 COMMIT=a3f9c12 REPO=negotiationcoach-backend DATE=2026-04-24
```

Expected entry body stamp:
```
**Status:** DONE
Commit: `a3f9c12` (negotiationcoach-backend) — 2026-04-24
Verified: tsc --noEmit clean ✓ | API /api/enrich smoke test returns 200 ✓
API contract updated: yes — docs/api-catalog.md updated (EnrichedAnalysisResult shape)
DB delta: none
ADR created/amended: none
Docs updated: docs/api-catalog.md
```

Expected summary index row after:
```
| RFB-014 | Layer 2 marketDataResolver fix — ✅ DONE `a3f9c12` | P1 | backend | bug |
```

## Example Invocation — Register format (single-phase item)

```
/close-task-dev ITEM_ID=NC-L2-UI COMMIT=8a5b38d REPO=negotiationcoach-backend DATE=2026-05-29
```

Expected Register row after (Status → Released, Title stamped, Notes appended):
```
| NC-L2-UI | Market Data anzeigen + /api/enrich einbinden — ✅ DONE `8a5b38d` | Bug | Released | negotiation-buddy, negotiationcoach-backend | R-2026-09 | Brief: product/briefs/NC-L2-UI.md. Released 2026-05-29. Backend 8a5b38d (chat-flow enrich path), Frontend f276041 (enrich useEffect after plan generation). · Verified: tsc clean, API /api/enrich smoke test ✓. API contract: no. DB delta: none. ADR: none. Docs: none. Commit `8a5b38d` (negotiationcoach-backend) — 2026-05-29. |
```

## Example Invocation — Register format, multi-phase item (Step A2 halts)

```
/close-task-dev ITEM_ID=NC-L3-SIM COMMIT=c00e719 REPO=negotiationcoach-backend DATE=2026-07-08
```

Expected output (per Step A2 — Phase 1 of 7, not the final phase):
```
close-task-dev: NC-L3-SIM — HALTED (incomplete, multi-phase item)
Phase status: 1 of 7 complete, per docs/features/layer3-simulation.md Abschnitt 11
Correct action instead: update product/briefs/NC-L3-SIM.md `## Implement`
section with this phase's result, and update the Register row's Notes
cell with the phase status. Do NOT change Status to Released/DONE until
all phases are complete.
```
