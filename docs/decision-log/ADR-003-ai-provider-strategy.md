# ADR-003 — AI Provider Strategy

**Status:** Accepted — 2026-03-31
**Supersedes:** MIG01 (Migration Lovable Gateway Gemini → Anthropic)
**Owner:** Refactor Control Tower

---

## Context

MIG01 planned to migrate the `generate-plan` Supabase Edge Function from
Lovable's AI Gateway (Gemini 2.5 Flash) to Anthropic Claude. This migration
was never executed. Inspection of `supabase/functions/generate-plan/index.ts`
on 2026-03-31 confirmed it still calls `https://ai.gateway.lovable.dev` with
`LOVABLE_API_KEY` and model `google/gemini-2.5-flash`. No `modelRouter` or
`selectModel()` call exists in that file.

A separate assumption — that Lovable's Gemini model was available as a
runtime provider for the app's own code — was found to be incorrect.
Lovable's Gemini is their internal platform tooling, not a runtime API
available to application code.

---

## Decision

The current two-provider split is intentional and accepted:

| Path | Provider | Model | Cost |
|------|----------|-------|------|
| Supabase Edge Function (`generate-plan`, `chat`) | Lovable AI Gateway | Gemini 2.5 Flash | Free (Lovable plan) |
| Railway backend (`/api/chat`, `/api/plan`, `/api/analyze`) | Anthropic Claude | Haiku / Sonnet | Pay per token |

MIG01 is superseded. The `generate-plan` Edge Function will continue to use
Lovable's Gemini gateway until a deliberate decision is made to migrate.

---

## Cost optimisation within Railway

`modelRouter.ts` handles cost optimisation within the Anthropic tier:
- Haiku — cheap tasks (validate, classify, summarise)
- Sonnet — standard tasks (strategy, coaching, analysis)
- Opus — Profi tier only (what-if, simulation)

No further provider abstraction is needed now.

---

## Future provider toggle

If a runtime provider toggle becomes necessary (e.g. Lovable gateway
unavailable, quality gap confirmed by user data, or cost pressure), the
correct implementation path is:

1. Obtain a Gemini API key independently of Lovable
2. Build a `aiProvider.ts` abstraction layer in the backend
3. Add `AI_PROVIDER=anthropic|gemini` environment variable
4. Wire `modelRouter` to delegate to the correct client

Do not build this until there is a concrete trigger. Premature abstraction
here adds maintenance cost with no current benefit.

---

## Consequences

- `executive_summary` TaskType in `modelRouter.ts` has zero callers and is
  confirmed dead code. DCC-BE-01 proceeds.
- MIG01 document (`shared-context/docs/` or project knowledge) is superseded
  by this ADR.
- No code changes are required as a result of this decision.
```

---

### File 2 — `negotiationcoach-backend/docs/dead-code-candidates.md`

Find the `DCC-BE-01` entry. Locate the line that reads:
```
**Status:** Confirmed dead config — safe to remove after contract doc update.