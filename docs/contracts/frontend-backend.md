# Frontend ↔ Backend Contract — NegotiationCoach AI

> Classification legend: **Observed** | **Inferred** | **Missing** | **Proposed**
> Last audit: 2026-03-27

This document defines the contracts between the React SPA (`negotiation-buddy`) and all backend services. It covers request/response shapes, authentication, error handling, and known drift.

---

## 1. Transport Overview

| Channel | From | To | Protocol | Auth |
|---------|------|----|----------|------|
| Railway REST API | Browser | Railway (negotiationcoach-backend) | HTTPS + JSON | `Authorization: Bearer <JWT>` |
| Supabase Edge Function /chat | Browser | Supabase Edge | HTTPS + SSE | `Authorization: Bearer <anon_key>` |
| Supabase JS SDK | Browser | Supabase PostgreSQL | HTTPS | Anon key + RLS |

**Note (Observed):** Two different Authorization schemes are used:
- Railway calls: user's JWT (access_token from `supabase.auth.getSession()`)
- Edge Function calls: Supabase anon/publishable key (not user JWT)

---

## 2. Railway REST API

**Base URL:** `VITE_API_URL` env var, falling back to `https://negotiationcoach-backend-production.up.railway.app` (hardcoded in `src/lib/apiClient.ts`)

**Client:** `src/lib/apiClient.ts`

---

### `POST /api/chat`

**Purpose:** Multi-turn conversation for negotiation input extraction (non-streaming fallback)

**Status:** Inferred as secondary/fallback path. Primary chat is Supabase Edge Function `/chat` (SSE).

**Request:**
```typescript
{
  messages: ChatMessage[];         // { role: 'user' | 'assistant', content: string }[]
  scenario?: string;               // optional scenario context
  previousInputs?: ExtractedInputs; // partial inputs from prior turns
}
```

**Response:**
```typescript
{
  message: string;                 // assistant reply text
  extractedInputs: ExtractedInputs; // parsed negotiation parameters
  isComplete: boolean;             // all required fields captured
}
```

**Auth:** Bearer JWT (optional in backend — never rejects)
**Tier Gate:** None explicit. Tier read and used for system prompt tone.
**Model:** Hardcoded `claude-haiku-4-5-20251001` — does NOT use modelRouter

**Type Drift:** `ExtractedInputs` is defined in both `src/lib/types.ts` (frontend) and `src/lib/types.ts` (backend). Shape appears consistent but is maintained in parallel — no shared package.

---

## POST /api/plan — Plan Generation Contract

> Status: Verified 2026-03-30 | Classification: Observed
> Canonical owner: negotiationcoach-backend (`src/api/planHelpers.ts`)

### Request (frontend → backend)
```typescript
{
  messages?: ChatMessage[];        // optional: chat history
  extractedInputs: ExtractedInputs;
  zopaResult?: object;             // optional: ZOPA calculation output
  analysis?: object;               // optional: analyze-full result
}
```

### Response (backend → frontend)
```typescript
{
  summary: string;
  situationAnalysis: string;
  opening: string;
  objections: Array<{ title: string; objection: string; response: string }>;
  recommendations: string[];
  nextStep: string;
}
```

### Type declarations
| Side | File | Interface name |
|---|---|---|
| Backend | `src/api/planHelpers.ts:69–76` | `PlanResponse` |
| Frontend | `src/lib/apiClient.ts:76–83` | `PlanResponse` (local) |

⚠️ No shared canonical type file. PlanResponse is declared independently in
both repos. They are currently aligned but not enforced by a shared schema.

### Legacy fields (deprecated — frontend only)
The following fields exist in `StrategyDialog.tsx NegotiationPlan` interface
as optional fallbacks. They are never populated by either the Railway backend
or the Edge Function. They are dead code candidates.

| Field | Status |
|---|---|
| `executive_summary?` | Dead — legacy fallback |
| `situation_analysis?` | Dead — legacy fallback |
| `opening_script?` | Dead — legacy fallback |
| `numbers?` | Dead — legacy fallback |

### Active architectural gap
The frontend does NOT currently call `POST /api/plan` on Railway.
`StrategyDialog` receives plan data as a prop from `Index.tsx` via `BottomBar`,
sourced from a Supabase Edge Function. The Railway endpoint is deployed but
unused. Decision required before Release 1: deprecate Railway `/api/plan` or
migrate Edge Function call to Railway.

---

### `POST /api/analyze`

**Purpose:** Layer 1 analysis — ZOPA, Nash Bargaining, Monte Carlo, strategy score

**Request:**
```typescript
// NegotiationInputs (shared type)
{
  negotiation_type: 'gehalt' | 'miete' | 'lieferant' | 'm_a' | 'sonstige';
  own_target: number;
  own_minimum: number;
  opponent_estimated_max: number;
  opponent_estimated_min: number;
  batna_description?: string;
  deadline_days?: number;
  context_notes?: string;
  tier?: 'free' | 'privat' | 'kmu' | 'profi';
}
```

**Response:**
```typescript
{
  sessionId: string;               // UUID of created negotiation_sessions record
  zopa_exists: boolean;
  zopa_min: number;
  zopa_max: number;
  nash_solution: number;
  monte_carlo_p50: number;
  monte_carlo_p90: number;
  strategy_score: number;          // 0-100
  acceptance_curve: Array<{ offer: number; probability: number }>;
  recommendations: string[];       // 3 strategic recommendations from Claude
  missing_inputs: string[];        // fields that would improve analysis
}
```

**Auth:** Bearer JWT (optional — anonymous gets 'privat' tier)
**Tier Gate:** None explicit

---

### `POST /api/enrich`

**Purpose:** Layer 2 market data enrichment — adds market median, reality score, context

**Request:**
```typescript
{
  sessionId: string;               // from /api/analyze response
  inputs: NegotiationInputs;       // same as /api/analyze
}
```

**Response:**
```typescript
// Extends AnalysisResult:
{
  // ...all AnalysisResult fields...
  market_data_source: 'web_search' | 'knowledge_graph' | 'none';
  market_median: number;
  market_range_min: number;
  market_range_max: number;
  reality_score: number;           // % deviation from market median, clamped [-100, 100]
  market_context_summary: string;  // 2-3 sentence Claude-generated context
}
```

**Auth:** Bearer JWT (optional)
**Tier Gate:** `requireTier('kmu')` — explicit middleware gate, returns 403 for free/privat

---

### `POST /api/analyze-full`

**Purpose:** Combined Layer 1 + optional Layer 2 in a single call

**Request:** Same as `POST /api/analyze` (`NegotiationInputs`)

**Response:** Combined `AnalysisResult` + optional `EnrichedData` fields (Layer 2 skipped if tier < kmu)

**Auth:** Bearer JWT (optional)
**Tier Gate:** Layer 2 implicitly skipped for free/privat; no 403 thrown

---

### `GET /api/sessions/:id`

**Purpose:** Retrieve stored session by ID

**Response:**
```typescript
{
  id: string;
  user_id: string;
  created_at: string;
  layer1_result: AnalysisResult;
  layer2_result?: EnrichedAnalysisResult;
  task_type?: string;
  model_used?: string;
  model_degraded?: boolean;
}
```

**Auth:** Bearer JWT. Access enforced via `.eq('user_id', req.user.id)` code-side (SERVICE_ROLE_KEY bypasses RLS).

---

## 3. Supabase Edge Function Contract

### `POST /functions/v1/chat` (SSE)

**Client:** `src/hooks/useChat.ts`
**Protocol:** Server-Sent Events (streaming)

**Request:**
```typescript
{
  messages: Array<{ role: 'user' | 'assistant'; content: string }>;
  persona: {
    type: 'pro' | 'kmu' | 'private';   // persona_type enum
    mode: 'analyse' | 'strategie' | 'sparring' | 'quick';
    experience_level: number;           // 1-5
    subscription_tier: string;          // hardcoded "free" in useChat.ts — VIOLATION
    preferred_frameworks: string[];
    negotiation_tone: string;
  };
}
```

**Response:** SSE stream of text chunks

**Special Tags in Stream:**
- `[KNOWLEDGE_CANDIDATE] <content>` — extracted negotiation knowledge; written to localStorage
- `[SYSTEM: <note>]` — internal system notes; logged to console, stripped from display

**Auth:** `Authorization: Bearer ${VITE_SUPABASE_PUBLISHABLE_KEY}` (anon key, not user JWT)

**Type Violation (Observed):**
- `persona.type` uses `persona_type` enum values (`pro | kmu | private`)
- `persona.subscription_tier` is always `"free"` regardless of actual user subscription
- Railway backend uses different tier values (`free | privat | kmu | profi`)
- Edge Function cannot enforce tier-based features without the correct tier value

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
| `persona_type` DB enum | `'pro' \| 'kmu' \| 'private'` | Not defined | **Drift** — no backend mapping |
| Edge Function inputs | `user_goal / user_walkaway` | `own_target / own_minimum` | **CRITICAL DRIFT** — incompatible schemas |

---

## 5. Error Contract

**Railway errors follow AppError shape:**
```typescript
{
  error: string;     // error.code (e.g., "AUTH_ERROR", "TIER_ERROR", "VALIDATION_ERROR")
  message: string;   // human-readable message
  status: number;    // HTTP status code
}
```

**Frontend error handling:** Each page/hook independently catches errors and displays a toast. No centralized error boundary. Pattern repeated in 4+ locations (redundancy R-002 in frontend audit).

**Tier gate error (403):** `requireTier('kmu')` returns 403 with `TierError` for `/api/enrich` when tier insufficient. Frontend does not handle this with a dedicated upgrade prompt — generic error toast shown (Inferred).

---

## 6. Known Contract Violations

| ID | Violation | Impact |
|----|-----------|--------|
| CON-01 | `subscription_tier` always "free" in Edge Function chat request | Edge Function cannot apply tier-based behavior |
| CON-02 | persona_type enum (pro/kmu/private) has no mapping to Railway tier (free/privat/kmu/profi) | Feature gating inconsistent between chat and analysis paths |
| CON-03 | Edge Function `negotiate` has completely different NegotiationInputs schema than Railway `/api/analyze` | Parallel analysis paths produce incomparable results |
| CON-04 | Types maintained in parallel (no shared package) — frontend and backend can silently drift | Runtime errors on schema mismatch |
| CON-05 | Railway URL hardcoded in apiClient.ts as production URL | `VITE_API_URL` env var ignored if not set — dev vs prod confusion |
| CON-06 | Railway authMiddleware never returns 401 | Frontend receives 200 even on invalid/expired token |
