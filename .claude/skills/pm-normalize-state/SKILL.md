# Skill: pm-normalize-state

## Purpose
Synchronize the current state of all repos with `product/`.
Run once before a new release cycle to establish a clean baseline.

## Steps
1. Read `product/releases/current.md` — note the release goal and in-scope items
2. Read `product/feature-register.md` — check every item's status
3. Read `docs/audits/refactor-backlog.md` — check for items that should be in the register
4. For each item:
   - confirm status is accurate
   - confirm affected repos are correct
   - confirm a brief exists if status is "In Delivery" or later
5. Identify mismatches and list them
6. Propose corrections — do NOT apply them without explicit confirmation
7. Output: normalization report with proposed changes

## Rules
- do not change status without evidence
- mark UNKNOWN where status cannot be determined
- do not infer release approval from code completion

---
**OUTPUT-SIGNAL:**
> NORMALIZE COMPLETE — [DATUM]
> Vorgeschlagene Korrekturen: [Anzahl]
> Warte auf Bestätigung vom User bevor Änderungen geschrieben werden.
