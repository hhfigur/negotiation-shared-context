# Skill: close-task

Run before declaring any task complete. Enforces verification, contract hygiene,
and atomic two-location backlog stamping.

---

## /close-task Command

Accepts four required parameters:

```
/close-task ITEM_ID=<e.g. RFB-018> COMMIT=<e.g. 675cc21> REPO=<e.g. negotiationcoach-backend> DATE=<e.g. 2026-04-02>
```

When invoked, execute Steps A–J below **in order**. Do not skip steps.

**Prerequisite:** Claude Code must be running with shared-context visible.
Launch from the backend repo with:
```bash
claude --add-dir ../shared-context
```
Or from within shared-context with `--add-dir ../negotiationcoach-backend`.
If `shared-context/docs/audits/refactor-backlog.md` is not readable, **HALT — report "shared-context not accessible."**

### Step A — Read the backlog

Read `shared-context/docs/audits/refactor-backlog.md` in full.

### Step B — Locate the entry body

Find the section heading `### <ITEM_ID>` in the backlog.
If not found:
- Check the Tooling/Infra Exemption below.
- If the exemption does NOT apply: **HALT — report "ITEM_ID not found in backlog".**
- If the exemption DOES apply: skip Steps C–J entirely and run the
  Exemption Path instead (see below) — this is not a skip, it is the
  regular closure path for this case.

---

### Step B — Tooling/Infra Exemption (no RFB-/NC-ID)

Some deliveries are cross-cutting tooling/governance/infra work that was
never meant to get an RFB-/NC-ID — not "not yet entered," but structurally
outside the product backlog's scope. This has already happened five times
in practice (Loop-Coding-Integration PROMPT 1/2/3, the `verify-harness`
telemetry fix, and `DCC-EF-02`) via an ad hoc version of exactly this path
— this section formalizes it for `/close-task` itself, it does not invent
new behavior.

**The exemption applies when Step B's HALT triggers AND at least one of:**
1. No RFB-/NC-ID was ever assigned to this delivery — there is no pending
   backlog entry to find, because none was ever meant to exist for this
   kind of work.
2. The changed files are predominantly under one or more of: `scripts/`,
   `.claude/skills/`, `docs/contracts/`, `docs/decision-log/`,
   `docs/dead-code-candidates.md`, or a `docs/features/*.md` file that
   already has a "Delivery Log" section.
3. The originating task explicitly framed this as a governance/tooling/
   infra delivery (e.g. Template 2-DEV with no ITEM_ID parameter at all, or
   a 2b-DEV harness/skill-repair delivery) rather than a product feature or
   bug fix.

If none of these apply, the exemption does not apply — fall through to the
normal HALT.

**Exemption Path (replaces Steps C–J):**

a) Check whether an existing internal ID scheme fits:
   - `DCC-[EF|BE]-[NN]` in `docs/dead-code-candidates.md` for dead-code
     findings — stamp there using that document's own existing DONE/Status
     convention.
   - No other scheme currently exists. If none fits, use a generic
     `TOOL-[YYYYMMDD]-[kurzname-kebab-case]` identifier (mirrors the
     `BUG-[YYYYMMDD]-[kurzname]` convention from `/bug-report`) **only if**
     a durable, standalone tracking entry is actually warranted — for a
     one-off skill/doc fix that's fully captured by its own commit message
     plus a lessons.md entry, minting an ID just to have one is unnecessary
     ceremony. Default to (b) unless a specific reason favors a tracked ID.

b) If no scheme fits (the common case for pure governance/process
   deliveries): run the already-established replacement path — this
   **is** the regular closure for this case, not a fallback:
   - A delivery-log entry in `shared-context/tasks/lessons.md`, and/or the
     "Delivery Log" section of the relevant `docs/features/*.md` file if
     this delivery continues one.
   - Confirmation that every relevant commit (target repo(s) + shared-context)
     is actually pushed — `git log <remote>/main..HEAD` empty for each
     affected repo.
   - Output (replaces Step H):
     ```
     close-task: [no RFB-/NC-ID — Tooling/Infra Exemption]
     ────────────────────────────────────────
     Exemption reason:      <which of the 3 conditions above applies>
     Internal ID scheme:    <DCC-*/TOOL-*/none applicable>
     Delivery-log entry:    DONE (<path>)
     Commits pushed:        DONE (<repo>: <range>)
     ────────────────────────────────────────
     Status: DONE (via Exemption Path)
     ```
   Steps I/J (git commands, wiki update) do not apply here — there is no
   backlog entry needing a wiki cross-reference — but the underlying
   two-location rule (target repo + shared-context both committed and
   pushed) still holds and is confirmed in the output above.

**Example (dry run — no real task, illustrates the path only):**

```
/close-task ITEM_ID=none COMMIT=a1b2c3d REPO=shared-context DATE=2026-07-20
```
Step B: no `### none` heading exists (there never will be — this is a
docs-only skill-repair delivery, never meant to carry an RFB-ID).
Exemption check: condition 1 applies (no ID was ever assigned) and
condition 2 applies (changed files are `.claude/skills/close-task/SKILL.md`
and `.claude/skills/close-task-dev/SKILL.md`). Exemption path (b) runs —
no existing ID scheme fits a skill repair, and minting a `TOOL-*` ID for a
single self-contained doc fix isn't warranted here.
```
close-task: [no RFB-/NC-ID — Tooling/Infra Exemption]
────────────────────────────────────────
Exemption reason:      No RFB-/NC-ID ever assigned; changed files under .claude/skills/
Internal ID scheme:    none applicable — one-off skill fix, commit + lessons entry is sufficient
Delivery-log entry:    DONE (tasks/lessons.md)
Commits pushed:        DONE (shared-context: <range>)
────────────────────────────────────────
Status: DONE (via Exemption Path)
```

---

### Step C — Check for existing DONE stamp in entry body

Scan the entry body for `**Status:** DONE`.
If already present: **HALT — report "Entry body already stamped DONE. Skipping."**

### Step D — Stamp the entry body

Append this exact block to the end of the entry body (before the next `---`):

```
**Status:** DONE
Commit: `<COMMIT>` (<REPO>) — <DATE>
Verified: <one-line summary of what was confirmed clean, e.g. "tsc --noEmit clean ✓ | grep confirms 0 references ✓">
Docs updated: <list docs updated, or "none">
```

Fill in `<COMMIT>`, `<REPO>`, `<DATE>` from the parameters.
Write the Verified line based on what was actually checked during the task.

### Step E — Locate the Summary Index row

Find the line in the `## Summary Index` table that begins with `| <ITEM_ID> |`.
If not found: **HALT — report "Summary Index row for ITEM_ID not found. Index may be out of sync — fix manually before closing."**

### Step F — Check for existing ✅ in summary row

If the row already contains `✅`: **HALT — report "Summary Index row already stamped. Skipping."**

### Step G — Stamp the Summary Index row

In the Title cell of that row, append ` — ✅ DONE \`<COMMIT>\`` to the existing title text.
Do not change the Priority, Repo, or Category cells.

Before:
```
| RFB-018 | Rename webSearch.ts to reflect actual behaviour | P3 | backend | contract-gap |
```
After:
```
| RFB-018 | Rename webSearch.ts to reflect actual behaviour — ✅ DONE `675cc21` | P3 | backend | contract-gap |
```

### Step H — Output results

```
close-task: <ITEM_ID>
────────────────────────────────────────
Entry body update:    DONE / SKIPPED (<reason>)
Summary index update: DONE / SKIPPED (<reason>)
────────────────────────────────────────
```

### Step I — Output git commands (do NOT commit automatically)

```bash
# Two commits required — one per repo:

# 1. Implementation repo (negotiationcoach-backend or negotiation-buddy):
git add <changed files>
git commit -m "<implementation commit message>"

# 2. shared-context (backlog + wiki):
cd ../shared-context
git add docs/audits/refactor-backlog.md
git add wiki/index.md
git add wiki/session-log.md
git commit -m "docs(backlog): close <ITEM_ID> — <short title> <COMMIT>"
```

Wait for user to run the commands.

### Step J — Update wiki/index.md

Read shared-context/wiki/index.md.

In the "Active Backlog — Open Items" table:
- Find the row for <ITEM_ID>
- If found: remove the entire row from the table
- If not found: report "ITEM_ID not in wiki open items — already removed or was never open. No action needed."

Then append a one-line entry to the session-log section of
shared-context/wiki/session-log.md under today's date:
- If today's date heading already exists: append bullet under it
- If not: create new heading `## [<DATE>] refactor | <ITEM_ID> closed`
  and add bullet: `- <ITEM_ID> closed — <short title>, commit <COMMIT>`

---

## Standard Verification Steps

Run before invoking /close-task:

```bash
# Type check
npx tsc --noEmit

# Tests (note: layer1/layer2 tests are currently broken — document if still broken)
npm test 2>&1 | tail -20

# If an API endpoint was changed, show a curl or test call result
```

If verification cannot be run (e.g., missing env vars), state why explicitly.

---

## Contract Check

Run the `contract-check` skill. Confirm:
- `docs/api-catalog.md` is current
- `docs/db-map.md` is current (if schema changed)
- TypeScript types are regenerated (if migration applied)
- RLS policies exist for any new tables

---

## Lessons Update

If anything went wrong or required a correction during this task:
- Update `tasks/lessons.md` with a rule that prevents recurrence
- Be specific: what was the mistake, what's the rule

---

## Task File Update

Update `tasks/todo.md`:
- Mark completed items with `[x]`
- Add a brief review section at the bottom noting what was done and any remaining follow-ups

---

## Commit Hygiene

Before committing:
- No `.env` files staged
- No temporary debug logs committed
- No `// TODO: fix later` without an issue reference
- Commit message describes the "why", not just the "what"

---

## Staff Engineer Question

Before marking done, ask: **"Would a staff engineer approve this as-is?"**

If the answer is no, or uncertain:
- List what would need to change
- Either fix it or explicitly document it as known debt in `docs/audit-findings.md`

---

## Full Output Format

```
CLOSE TASK — <ITEM_ID>: <title>
────────────────────────────────────────
TypeCheck:            [pass / fail — output]
Tests:                [pass / fail / broken-known]
Contracts:            [all current / [updated items]]
Lessons:              [none / updated tasks/lessons.md with: ...]
Todo:                 [tasks/todo.md updated]
Staff Check:          [approved / debt documented: ...]
────────────────────────────────────────
Entry body update:    DONE / SKIPPED (<reason>)
Summary index update: DONE / SKIPPED (<reason>)
Wiki index update:    DONE (row removed) / SKIPPED (<reason>)
Wiki session log:     DONE (entry appended) / SKIPPED (<reason>)
────────────────────────────────────────
Git commands:
  # Implementation repo:
  git add <changed files>
  git commit -m "<implementation commit message>"
  # shared-context:
  cd ../shared-context
  git add docs/audits/refactor-backlog.md
  git add wiki/index.md
  git add wiki/session-log.md
  git commit -m "docs(backlog): close <ITEM_ID> — <short title> <COMMIT>"
────────────────────────────────────────
Status: DONE / BLOCKED BY: [reason]
```

---

## Example Invocation

```
/close-task ITEM_ID=RFB-019 COMMIT=056e672 REPO=negotiation-buddy DATE=2026-04-01
```

Expected entry body stamp appended:
```
**Status:** DONE
Commit: `056e672` (negotiation-buddy) — 2026-04-01
Verified: tsc --noEmit clean ✓ | useToast imports → 0 remaining ✓
Docs updated: docs/redundancy-register.md (R-007 Resolved)
```

Expected summary index row after:
```
| RFB-019 | Consolidate dual toast systems — ✅ DONE `056e672` | P3 | frontend | dead-code |
```
