# Frontend ↔ Backend Contract — NegotiationCoach AI

> Classification legend: **Observed** | **Inferred** | **Missing** | **Proposed**
> Last audit: 2026-03-27
> **Reduced 2026-09-04** (owner decision C1, `sdlc/migration/20260904T132634Z/10-conflicts-and-decisions.md`):
> the full REST API contract (§2) is no longer maintained here — it is relocated to the canonical
> `NegotiationCoach-backend/docs/api-catalog.md`. This document retains transport overview, Supabase
> Edge Function contracts, type drift register, error contract, and known contract violations —
> genuinely cross-repo audit/reference content, not the REST contract itself.

This document defines the cross-repository contracts between the React SPA (`negotiation-buddy`) and backend services; the REST API shapes themselves live in the canonical backend contract (§2). This file covers transport, authentication, Edge Function contracts, error handling, and known drift.

---

## 1. Transport Overview

| Channel | From | To | Protocol | Auth |
|---------|------|----|----------|------|
| Backend API | Browser | Express Backend (Render.com) (negotiationcoach-backend) | HTTPS + JSON | `Authorization: Bearer <JWT>` |
| Supabase Edge Function /chat | Browser | Supabase Edge | HTTPS + SSE | `Authorization: Bearer <anon_key>` |
| Supabase JS SDK | Browser | Supabase PostgreSQL | HTTPS | Anon key + RLS |
| Supabase Edge Function /generate-plan | Browser | Supabase Edge | HTTPS + JSON | `Authorization: Bearer <JWT>` (user token) — RFB-033 |

**Note (Observed):** Two different Authorization schemes are used:
- Backend API calls: user's JWT (access_token from `supabase.auth.getSession()`)
- Edge Function calls: Supabase anon/publishable key (not user JWT)
**Partial fix (RFB-033, 2026-04-11):** `generate-plan` now requires user JWT.
`/chat` EF still uses anon key. Three other EF calls in Index.tsx (lines 287,
431, 565) still use anon key — tracked as RFB-034.

---

## 2. Backend REST API

**Canonical contract:** `NegotiationCoach-backend/docs/api-catalog.md` (owner decision, 2026-09-04 —
shared-context references the canonical contract, it does not maintain a competing one). This
section previously duplicated the full REST API contract here; that content has been relocated to
the canonical file (see its "Simulation Endpoints" section, added 2026-09-04, for the
`/api/simulate/*`/`/api/opponent-simulation/*` routes that existed only in this document before
the relocation — confirmed present in the canonical file before this reduction was applied).

**Base URL:** `VITE_API_URL` env var, falling back to `https://negotiationcoach-backend.onrender.com`
(hardcoded in `src/lib/apiClient.ts`). **Client:** `src/lib/apiClient.ts`.

---

## 3. Supabase Edge Function Contract

**Canonical contract:** `NegotiationCoach-backend/docs/api-catalog.md` § "Supabase Edge Function API
Routes" (owner decision, C1 Edge Function scope, 2026-09-04 — shared-context references the
canonical catalog, it does not maintain a competing copy). This section previously duplicated the
`chat` and `generate-plan` Edge Function contracts in full here; that content has been relocated to
the canonical file, which also now documents the remaining five Edge Functions
(`analyze-progress`, `analyze-document`, `summarize-session`, `send-password-reset`,
`verify-reset-token`) that this document never covered.

**Provider/model history preserved for reference, not relocated** (audit-trail content, not
contract shape): the `chat` EF's tier-dependent model selection was originally documented assuming
Google Gemini; ADR-012 (2026-07-18) corrected the provider to Anthropic-only, and
`docs/audits/provider-drift-diagnosis.md` found the currently deployed function hardcodes
`claude-haiku-4-5-20251001` for all tiers rather than the originally-documented tier-dependent
selection — see that diagnosis doc and ADR-012 for the full history. VG-05/VG-05-A/VG-06-A/VG-07
findings (JWT enforcement, tier resolution, canonical chat-path decision) are RESOLVED per ADR-004
and the RFB-009/RFB-033 commits referenced there — see git history for exact commits if needed.

---

## 4. Type Drift Register

| Type | Frontend Definition | Backend Definition | Status |
|------|--------------------|--------------------|--------|
| `NegotiationInputs` | `src/lib/types.ts` | `src/types/index.ts` | Consistent (Observed) |
| `AnalysisResult` | `src/lib/types.ts` | `src/types/index.ts` | Consistent (Observed) |
| `ExtractedInputs` | `src/lib/types.ts` | `src/lib/types.ts` | Maintained in parallel — no shared package |
| `ChatMessage` | `src/lib/types.ts` | `src/lib/types.ts` | Maintained in parallel |
| `NegotiationType` | `src/lib/types.ts` | `src/types/index.ts` | Consistent enum values |
| `Tier` | Not defined in frontend | `'free' \| 'privat' \| 'kmu' \| 'profi'` | **Drift** — frontend uses persona_type instead |
| `subscription_tier` DB enum | ~~`free \| starter \| professional \| expert \| team`~~ → `free \| privat \| kmu \| profi` | `free \| privat \| kmu \| profi` | ✅ **RESOLVED RFB-036 `a28d28c` 2026-04-16** — DB enum now aligned to backend Tier values per ADR-006-tier-mapping.md |
| `persona_type` DB enum | `'pro' \| 'kmu' \| 'private'` | Mapped via `personaTypeToTier()` in `src/utils/tierUtils.ts` | **Partial resolution (RFB-007 Step B)** — wired at `POST /api/sessions`; EF boundary pending Step C (VG-06) |
| Edge Function inputs | ~~`user_goal / user_walkaway`~~ | `own_target / own_minimum` | ~~**CRITICAL DRIFT**~~ **RESOLVED — ADR-007-A 2026-04-21.** `_shared/engine/` retired. EF-Schema-Konflikt obsolet. Verified 2026-04-30. |

---

### 4.1 Canonical Tier Mapping Function

**File:** `src/utils/tierUtils.ts` — added RFB-007 Step A (2026-04-09)

| DB `persona_type` | Backend `Tier` |
|---|---|
| `'pro'` | `'profi'` |
| `'kmu'` | `'kmu'` |
| `'private'` | `'privat'` |
| `null` / `undefined` / unknown | `'free'` |

**Function:** `personaTypeToTier(personaType: string | null | undefined): Tier`
**Import:** `import { personaTypeToTier } from '../utils/tierUtils';`
**Purpose:** Pure mapping — no side effects, no DB calls, no external dependencies.
**Status:** Function exists. Call sites not yet wired — pending RFB-007 Steps B/C.

---

## 5. Error Contract

**Backend errors follow AppError shape:**
```typescript
{
  error: {
    code: string;       // e.g., "AUTH_ERROR", "TIER_ERROR", "VALIDATION_ERROR"
    message: string;    // human-readable message
    statusCode: number; // HTTP status code
  }
}
```

**Validation error (400):** `VALIDATION_ERROR` — returned when Zod schema parse fails on request body (wired in RFB-021).
Field-level detail is included in `error.message` as a comma-separated string of `field: reason` pairs.
Example:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "negotiation_type: Invalid enum value, own_target: Required",
    "statusCode": 400
  }
}
```
Routes covered: Backend `/api/analyze`, `/api/chat`, `/api/plan`, `/api/enrich`, `/api/analyze-full`

**Frontend error handling:** Each page/hook independently catches errors and displays a toast. No centralized error boundary. Pattern repeated in 4+ locations (redundancy R-002 in frontend audit).

**Tier gate error (403):** `requireTier('kmu')` returns 403 with `TierError` for `/api/enrich` when tier insufficient. Frontend does not handle this with a dedicated upgrade prompt — generic error toast shown (Inferred).

**`POST /api/chat` parse error (500):** `CHAT_PARSE_ERROR` — returned when `parseChatResponse()` cannot extract a valid JSON block from the Claude API response. The frontend `sendChatMessage()` call site (`Index.tsx:398`) catches this silently — `extractedInputs` remains at its previous value. Fixed in REF-BE-02, commit `fe961ee`.

**Session endpoint errors (RFB-004 Phase A):**
- `SESSION_NOT_FOUND` (404) — session does not exist or caller does not own it. Returned by `assertSessionOwner()` for both cases — does not reveal resource existence.
- `MESSAGE_LIMIT_REACHED` (400) — session already has 50 messages. Returned by `POST /api/sessions/:id/messages` before insert.
- `SESSION_CREATE_ERROR` (500) — Supabase insert failure on `POST /api/sessions`.
- `SESSION_UPDATE_ERROR` (500) — Supabase update failure on `PATCH /api/sessions/:id`.
- `MESSAGE_SAVE_ERROR` (500) — Supabase count or insert failure on `POST /api/sessions/:id/messages`.

---

## 6. Known Contract Violations

| ID | Violation | Impact |
|----|-----------|--------|
| CON-01 | ~~`subscription_tier` always "free" in Edge Function chat request~~ **RESOLVED RFB-009 `d90d5c0`** — tier now resolved server-side via JWT; `subscription_tier` in body ignored | — |
| CON-02 | persona_type enum (pro/kmu/private) mapped via `personaTypeToTier()` — **PARTIAL RESOLVED RFB-007 Step B `6ba5710`** | Wired at Backend `POST /api/sessions` boundary; EF boundary (Step C) pending VG-06 |
| CON-03 | Edge Function `negotiate` has completely different NegotiationInputs schema than Backend `/api/analyze` | Parallel analysis paths produce incomparable results |
| CON-04 | Types maintained in parallel (no shared package) — frontend and backend can silently drift | Runtime errors on schema mismatch |
| CON-05 | Render.com URL hardcoded in apiClient.ts as production URL | `VITE_API_URL` env var ignored if not set — dev vs prod confusion |
| CON-06 | ~~backend authMiddleware never returns 401~~ **RESOLVED RFB-001** — 401 enforced, `AUTH_REQUIRED=false` dev-bypass via env flag. `middleware.ts` confirmed. | — |
