# NegotiationCoach AI — Architecture Overview

---

## System Boundaries

Three repositories, two Supabase instances (Inferred), two AI providers:

| Component | Repo / Service | Role |
|-----------|---------------|------|
| React SPA | `negotiation-buddy` | Frontend — coaching UI, auth, session display |
| Express API | `negotiationcoach-backend` | Railway — LLM orchestration, analysis engine, business rules |
| Edge Functions | `negotiation-buddy/supabase/functions/` | Supabase — SSE streaming chat, plan generation, session summarization |
| Shared Docs | `shared-context` | Documentation only — architecture, contracts, ADRs |

**Boundary rules (ADR-001):**
- Browser: auth operations, reading own data, `user_profiles` preference updates, streaming chat via Edge Function
- Railway: all business entity mutations (sessions, messages, teams), all LLM calls, algorithm execution, tier enforcement
- Supabase: identity/JWT issuance, raw storage, RLS enforcement, streaming via Edge Functions
- No algorithm logic in Edge Functions or frontend (non-negotiable from ADR-001)

---

## AI Provider Split

Source: ADR-003 (Accepted — 2026-03-31)

| Path | Provider | Model | Cost |
|------|----------|-------|------|
| Supabase Edge Functions (`generate-plan`, `chat`) | Lovable AI Gateway | Gemini 2.5 Flash | Free (Lovable plan) |
| Railway backend (`/api/chat`, `/api/plan`, `/api/analyze`) | Anthropic Claude | Haiku / Sonnet / Opus | Pay per token |

The two-provider split is intentional and accepted. The `generate-plan` Edge Function remains on Lovable's Gemini gateway until a deliberate migration decision is made. Railway handles all structured AI output and algorithm orchestration via Anthropic Claude.

---

## Engine Layers

Source: `negotiationcoach-backend/docs/service-catalog.md`

| Layer | Responsibility | Key Files |
|-------|---------------|-----------|
| Layer 0 | Infrastructure — Supabase client (SERVICE_ROLE_KEY, bypasses RLS) | `src/layer0/supabaseClient.ts` |
| Layer 1 | Core mathematical analysis — ZOPA, Nash Bargaining, Monte Carlo (10k iterations), Deadline Effect, Strategy Score, BATNA detection | `src/layer1/` |
| Layer 2 | Market data enrichment — cache-first (7-day TTL), Claude tool_use for training-data market values, reality score | `src/layer2/` |
| Layer 3 (API) | Express routes — authMiddleware, requireTier(), model routing, session/message/team CRUD | `src/api/` |

**Layer 2 tier gate:** `free` and `privat` tiers skip enrichment entirely — `src/layer2/index.ts` early return with `market_data_source: 'none'`.

**Note:** Layer 1 algorithms are also duplicated in `supabase/functions/_shared/engine/` with an incompatible type schema (`user_goal / user_walkaway` vs `own_target / own_minimum`). This is CRIT-01 — tracked under RFB-006.

---

## Auth Flow

Source: `docs/auth-permission-map.md`

```
Browser (useAuth.tsx)
  └─ supabase.auth.signIn/signUp → JWT issued by Supabase Auth
        │
        ├─ Bearer token → Railway authMiddleware
        │     → supabase.auth.getUser(token)
        │     → req.user = { id, tier }
        │     → tier: app_metadata.tier || user_metadata.tier || 'free'
        │     → requireTier(minTier) on gated endpoints
        │
        ├─ Anon key + RLS → Supabase direct (user_profiles reads/writes)
        │
        └─ Bearer token → Supabase Edge Functions
              → supabase.auth.getUser(jwtToken) inside EF
              → user_profiles lookup for persona_type → tier resolution
```

**Key resolved violations:**
- AUTH-01: Railway authMiddleware now enforces 401 — resolved `fd68e1e` 2026-04-03
- AUTH-09: `generate-plan` EF now has JWT guard + user_id ownership filters — resolved RFB-033 2026-04-11
- All remaining EF calls in `Index.tsx` now send user JWT — resolved RFB-035A/B 2026-04-11/13

---

## Tier System

Source: `docs/source-of-truth-matrix.md`, `docs/auth-permission-map.md`

**Four canonical tiers** (Railway definition, post-ADR-006):

| Tier | Price | Access |
|------|-------|--------|
| `free` | €0 | Basic analysis only, no market enrichment |
| `privat` | €12 | Standard analysis, no market enrichment |
| `kmu` | €49 | Analysis + Layer 2 market enrichment |
| `profi` | €99 | Full access including Opus model for what-if/simulation |

**Two-column tier structure in `user_profiles`:**

| Column | Values | Purpose |
|--------|--------|---------|
| `persona_type` | `pro \| kmu \| private` | UI coaching persona — tone, prompt depth, feature visibility |
| `subscription_tier` | `free \| starter \| professional \| expert \| team` → post-ADR-006: `free \| privat \| kmu \| profi` | Billing tier (RFB-036 migration pending) |

`personaTypeToTier()` bridges `persona_type` → Railway `Tier` at call boundaries. After RFB-036, `subscription_tier` will use Railway values directly and need no translation.

**Model routing by tier** (`modelRouter.ts` — wired into all Railway handlers post-RFB-011):

| Task | free | privat | kmu | profi |
|------|------|--------|-----|-------|
| validate_input | Haiku | Haiku | Haiku | Haiku |
| strategy_coaching | Haiku | Sonnet | Sonnet | Sonnet |
| what_if_analysis | Haiku | Sonnet | Sonnet | **Opus** |
| opponent_simulation | Haiku | Sonnet | Sonnet | **Opus** |
| executive_summary | Haiku | Sonnet | Sonnet | **Opus** |

---

## Key Architectural Decisions

Source: `docs/decision-log/`

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](../docs/decision-log/ADR-001-system-boundaries.md) | System boundary rules — browser vs Railway vs Supabase | Active |
| [ADR-002](../docs/decision-log/ADR-002-data-ownership.md) | Data ownership — one canonical writer per business entity | Active |
| [ADR-003](../docs/decision-log/ADR-003-ai-provider-strategy.md) | Two-provider AI split — Lovable/Gemini for EFs, Anthropic for Railway | Active |
| [ADR-004](../docs/decision-log/ADR-004-chat-path-routing.md) | Edge Function `/chat` is canonical chat path for all tiers; tier enforcement inside EF | Active |
| [ADR-005](../docs/decision-log/ADR-005-plan-generation-path.md) | Railway `/api/plan` is canonical long-term plan path; `generate-plan` EF is temporary | Active |
| [ADR-006](../docs/decision-log/ADR-006-tier-mapping.md) | `subscription_tier` enum migrated to Railway Tier labels; enables Stripe webhook (RFB-032) | Active — migration pending (RFB-036) |

---

## Open Architecture Questions

| Item | Question | Tracks |
|------|----------|--------|
| CRIT-01 / RFB-006 | Dual Layer 1 implementations — Railway `src/layer1/` and `supabase/functions/_shared/engine/` use incompatible type schemas. Which is retired? | [RFB-006](../docs/audits/refactor-backlog.md) |
| RFB-036 | `subscription_tier` DB enum still uses Lovable scaffold values (`starter`, `professional`, `expert`, `team`). Migration to Railway values (`privat`, `kmu`, `profi`) pending. Blocks RFB-032 (Stripe webhook). | [RFB-036](../docs/audits/refactor-backlog.md) |
| VG-04 | What creates the initial `user_profiles` row on sign-up? (Inferred: `on_auth_user_created` trigger — RFB-012 created it 2026-04-03, but creation mechanism pre-RFB-012 was missing) | Resolved by RFB-012 |

---

*LLM-maintained — do not edit manually. Updated by Claude Code.*
