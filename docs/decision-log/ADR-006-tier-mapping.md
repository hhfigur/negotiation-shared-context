# ADR-006 — Canonical Subscription Tier Mapping

**Date:** 2026-04-13
**Status:** Decided
**Decider:** Maik

## Decision

The `subscription_tier` DB enum in the Lovable-managed Supabase instance
is migrated to use Railway Tier values as the single canonical representation.

## Canonical Mapping

| Old DB value  | New DB value | Railway Tier | Price  | Notes                        |
|---------------|--------------|--------------|--------|------------------------------|
| `free`        | `free`       | `free`       | €0     | Unchanged                    |
| `starter`     | `privat`     | `privat`     | €12    | Renamed                      |
| `professional`| `kmu`        | `kmu`        | €49    | Renamed                      |
| `expert`      | `profi`      | `profi`      | €99    | Renamed                      |
| `team`        | `profi`      | `profi`      | €99    | Merged into profi (Option A) |

## Consequence

- Supabase `subscription_tier` enum values are renamed via migration
- All existing `user_profiles` rows are backfilled atomically in the migration
- `src/integrations/supabase/types.ts` is regenerated after migration
- Any frontend code comparing `subscription_tier` values directly must be
  updated to use new values
- `personaTypeToTier()` in `tierUtils.ts` remains valid for mapping
  `persona_type` → Railway Tier (separate concern — UI persona)
- Railway `authMiddleware.ts` Tier type (`free | privat | kmu | profi`)
  is unchanged — DB now aligns to it
- Stripe webhook (RFB-032) will write Railway Tier values directly to
  `subscription_tier` once Stripe goes live

## Items Affected

- RFB-036 (re-opened, re-scoped): DB enum migration + frontend value updates
- RFB-032: Stripe webhook now has a clear write target and value set
- source-of-truth-matrix.md: Entity 2 update required