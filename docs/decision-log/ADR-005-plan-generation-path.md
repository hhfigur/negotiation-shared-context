# ADR-005 — Plan Generation Path: Railway as Canonical Target

**Date:** 2026-04-11
**Status:** Decided
**Decider:** Maik

## Decision

Railway `POST /api/plan` is the canonical long-term path for plan generation.
The Supabase Edge Function `generate-plan` is a temporary active path.

## Consequence

- `POST /api/plan` (Railway) must NOT be removed.
- `planHelpers.ts` must NOT be removed.
- `generate-plan` Edge Function will be retired when the frontend migrates
  to Railway `/api/plan` (scoped under RFB-004 or a successor item).
- `apiClient.ts generatePlan()` wrapper is dead code today but is the
  correct future call site — do not remove; add a comment marking it
  as the migration target.

## Rationale

Consistent with the Railway-first boundary established in RFB-001, RFB-003,
and RFB-004. All business logic, auth, and AI orchestration belong on Railway.
Edge Functions are Gemini/SSE paths, not the permanent home for structured
AI output generation.

## Items Affected

- DCC-BE-02: status changes from "do not remove" to "preserve as migration target"
- RFB-034: re-scope from "remove" to "document + preserve + mark migration target"
- RFB-004: plan generation frontend migration added as a Phase C scope item