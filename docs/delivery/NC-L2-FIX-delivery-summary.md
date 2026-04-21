# NC-L2-FIX — Delivery Summary

**Released:** 2026-04-21
**Release:** R-2026-05
**Brief:** product/briefs/NC-L2-FIX.md

## Root Causes Found (Diagnosis Step A)

| # | Finding | Confidence | File |
|---|---|---|---|
| 1 | knowledge_graph missing in production Supabase instance | High | infrastructure |
| 2 | saveMarketData swallowed insert errors silently | High | knowledgeGraph.ts |
| 3 | Cache region filter: no IS NULL guard for undefined region | High | knowledgeGraph.ts |
| 4 | data_type key format: 'market_gehalt' vs 'gehalt' mismatch | Medium | marketDataResolver.ts |
| 5 | realityScore NaN risk on undefined/invalid median | Medium | realityScore.ts |
| 6 | Unit mismatch risk: annual vs monthly not enforced | Medium | marketDataInterpreter.ts |
| 7 | Tier gate inconsistency on /api/analyze-full | Low | routes.ts |

## Fixes Applied (Step B)

| File | Change |
|---|---|
| knowledgeGraph.ts | saveMarketData throws on insert failure with console.error |
| knowledgeGraph.ts | region filter: .is('region', null) when region undefined |
| marketDataResolver.ts | cacheKey: negotiationType (bare, no prefix) |
| realityScore.ts | NaN/undefined/negative guard on marketMedian |
| marketDataInterpreter.ts | Unit context added to Claude tool prompt |
| routes.ts | Explicit tier ?? 'privat' fallback on /api/analyze-full |
| layer2/index.ts | generateMarketContextSummary throws on empty response |

## Infrastructure Fix

knowledge_graph table created in Lovable Supabase instance
(ujnyioggxipvuxxxcivr) via SQL Editor.
RLS policies: service_role INSERT, authenticated SELECT.

## Verification

- Run 1: market_data_source=web_search, reality_score=25%,
  market_context_summary non-empty
- Run 2: market_data_source=knowledge_graph (cache hit confirmed)
- TypeCheck: 0 errors

## Remaining Known Limitations

- Unit mismatch (annual/monthly) mitigated by prompt wording,
  not enforced at runtime — documented in code comments
- tests/layer2/layer2.test.ts has no assertions (RFB-027)
- ivrfsjxdfzxrimexvoft (local dev instance) is empty and
  unused — can be archived (separate decision)
