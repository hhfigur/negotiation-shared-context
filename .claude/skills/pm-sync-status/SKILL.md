# Skill: pm-sync-status

## Purpose
Update item status after delivery or QA completion.
Usage: `/pm-sync-status <ITEM-ID>`

## Steps
1. Read the brief in `product/briefs/<ITEM-ID>.md`
2. Verify acceptance criteria — ask for evidence (test output, log, manual check)
3. Update status in `product/feature-register.md`
4. Update `product/releases/current.md` if all in-scope items are done
5. If released: update `product/audit/refactor-backlog.md` if applicable
6. Output: status change summary

## Rules
- "Code complete" is not "Released"
- "Released" is not "Verified"
- require explicit evidence before status change to Verified
