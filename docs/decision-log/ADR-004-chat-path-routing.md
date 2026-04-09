# ADR-004 — Chat Path Routing by User Tier

**Status:** Accepted
**Date:** 2026-04-09
**Deciders:** Maik Figur
**Supersedes:** Nothing — amends ADR-003 (adds tier routing assignment that ADR-003 left open)

## Context

VG-07 investigation (2026-04-09) confirmed:

1. The Supabase Edge Function `/functions/v1/chat` is the only active chat path — Railway `/api/chat` has never been called from the frontend.
2. Response shapes are structurally incompatible:
   - Edge Function: SSE stream, OpenAI delta format
   - Railway: synchronous JSON `{message, extractedInputs, isComplete}`
3. ADR-003 named the Edge Function as the chat path but left tier-based routing unassigned.
4. The Edge Function has no tier enforcement — `subscription_tier` is injected as decorative prompt text only (VG-05, 2026-04-09).
5. Railway `/api/chat` already has `modelRouter` wired (`routes.ts:71`) and returns structured `extractedInputs` — architecturally valuable but for a different purpose (analysis triggering, not chat streaming).

## Decision

The Supabase Edge Function `/functions/v1/chat` remains the canonical chat path for **ALL** user tiers (free, privat, kmu, profi).

Tier enforcement is added **inside** the Edge Function:
- Read the authenticated user's tier from the Supabase JWT via `supabase.auth.getUser()` (server-side, not from request body)
- Select the appropriate Gemini model via Lovable AI Gateway `model` parameter based on resolved tier
- Apply tier-appropriate system prompt behaviour (response depth, market data inclusion, etc.)

Railway `/api/chat` remains available for:
- Internal backend use (e.g., triggered by analysis pipeline)
- Future structured extraction flows where `extractedInputs` is consumed
- **NOT** for direct frontend chat streaming

## Rationale

- **Option A (this decision)** isolates all tier enforcement changes to a single file (`supabase/functions/chat/index.ts`) without touching `useChat.ts` or the Railway backend
- Resolving Options B or C would require simultaneously fixing four blocking compatibility gaps (transport, response shape, auth header, `extractedInputs` consumer) with no prior production validation
- ADR-003 explicitly assigned the Edge Function as the chat path; this decision extends rather than contradicts it
- Lovable AI Gateway free-tier cost advantage is preserved for the high-volume chat path
- Railway `/api/chat`'s structured output (`extractedInputs`, `isComplete`) serves analysis triggering — a distinct use case that should not be conflated with the coaching chat stream

## Consequences

**Positive:**
- Single change surface for tier enforcement
- No frontend regression risk
- ADR-003 alignment maintained
- `modelRouter` tier logic in Railway remains valid for analysis paths

**Negative:**
- Gemini remains the model for all chat tiers — Claude is not used in the chat stream even for profi users (accepted trade-off per ADR-003 two-provider split)
- Edge Function must now perform JWT validation (new Deno dependency on `supabase.auth.getUser()`)
- Lovable AI Gateway model switching capability must be verified before implementation (prerequisite for RFB-009)

## Dependencies

- **RFB-007 Step B:** wire `personaTypeToTier()` into Edge Function (now confirmed as the correct target file)
- **RFB-009 (revised scope):** add JWT read + model switching inside `supabase/functions/chat/index.ts`
- **Prerequisite check:** verify Lovable AI Gateway supports `model` parameter switching (must be confirmed before RFB-009 implementation)
