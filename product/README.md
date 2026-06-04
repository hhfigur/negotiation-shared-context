# Product Operations

## Purpose
`product/` is the operational source of truth for:
- product planning and release planning
- delivery briefs
- product decisions
- audit and refactor prioritization
- release reviews

## Boundary
`product/` holds the current operational state.
`wiki/` and `docs/` are reference-only for architecture, ADRs, deep analysis, and background context.

## Read order for planning work
1. `product/releases/current.md`
2. `product/roadmap.md`
3. `product/strategy.md`
4. `product/metrics.md`
5. `product/feature-register.md`
6. `product/audit/refactor-backlog.md`

## Read order for delivery work
1. `product/releases/current.md`
2. relevant brief in `product/briefs/<ITEM-ID>.md`
3. `product/feature-register.md` entry for the item
4. use `docs/` only if deeper technical context is needed

## Naming guidance
- Product items use prefix `NC-` (NegotiationCoach)
- Audit and refactor items use prefix `AR-` (maps to existing RFB-xxx items)
- Release IDs use format `R-YYYY-MM`

## Operating rules
- `product/` is authoritative for current product and release state
- `docs/` and ADRs are authoritative for architecture decisions
- no delivery work starts without a brief in `product/briefs/`
- code complete is not the same as `Released`
- `Released` is not the same as `Verified`
- every active item must have exactly one item type and one status
- every active item must list affected repos
- unknowns must be marked explicitly as `UNKNOWN`

## Standard item types
- Feature
- Bug
- Enabler
- Refactor
- Research

## Standard status values
- Idea | Qualified | Planned | In Delivery | Ready for Release | Released | Verified | Paused | Dropped
