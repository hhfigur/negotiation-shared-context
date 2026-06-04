# Skill: pm-prepare-delivery

## Purpose
Create or update a delivery brief for a specific item before implementation starts.
Usage: `/pm-prepare-delivery <ITEM-ID>`

## Steps
1. Read the item entry in `product/feature-register.md`
2. Read `product/releases/current.md` — confirm item is in scope
3. Read relevant ADRs and architecture docs
4. Check if a brief already exists in `product/briefs/<ITEM-ID>.md`
5. Create or update the brief with:
   - Goal / Outcome
   - Problem (what breaks or what is missing)
   - Affected Repos
   - Scope (exactly what will change)
   - Non-goals (explicitly what will NOT change)
   - Acceptance Criteria (testable, concrete)
   - Telemetry / Measurement (or explicit gap note)
   - Risks / Open Questions
6. Update item status to "In Delivery" in `product/feature-register.md`
7. Output: brief file path and summary

## Rules
- acceptance criteria must be concrete and verifiable
- if telemetry cannot be measured, document the gap explicitly
- do not start delivery on items with open blocking decisions
