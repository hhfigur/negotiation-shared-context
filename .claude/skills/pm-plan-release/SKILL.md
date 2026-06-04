# Skill: pm-plan-release

## Purpose
Define or update the scope for the next release.

## Steps
1. Read `product/releases/current.md`
2. Read `product/roadmap.md` — section "Now"
3. Read `product/feature-register.md` — items with status Qualified or Planned
4. Read `product/audit/refactor-backlog.md` — P0 and P1 items
5. Check all Layer dependencies (Layer 0 → 1 → 2 → 3 — never skip)
6. Check ADR dependencies — no implementation without required ADRs
7. Propose release scope:
   - items to include (with justification)
   - items explicitly out of scope (with reason)
   - dependencies between in-scope items
   - exit criteria
8. Output: proposed update to `product/releases/current.md`

## Rules
- respect Layer dependency order
- no item in scope without a brief (or brief creation as part of this release)
- mark open decisions explicitly
