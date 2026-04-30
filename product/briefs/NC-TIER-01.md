# NC-TIER-01 — Stripe-Readiness-Audit

**Status:** Released
**Typ:** Audit / Architecture Prep
**Datum:** 2026-04-30
**Release:** R-2026-08

## Ziel
Alle UNKNOWN-Lücken im Stripe→Tier-Pfad identifizieren und entscheiden,
sodass RFB-032 ohne weitere Analyse direkt implementiert werden kann
wenn Stripe live geht.

## Ergebnis
Audit abgeschlossen. Zwei P0-Entscheidungen getroffen.
RFB-032 bleibt DEFERRED — Aktivierung ist bewusste Produktentscheidung.

## Entscheidungen

| Entscheidung | Gewählt |
|---|---|
| Write-Target | app_metadata.tier (Admin-Write via Stripe Webhook) |
| Middleware-Fix | app_metadata-first bei Aktivierung (1-Zeilen-Fix middleware.ts:112) |
| Token-Refresh | Automatisch via Supabase JS — akzeptable Latenz |
| Customer-ID-Lookup | Option A — Stripe Metadata (supabase_user_id bei Checkout setzen) |
| Checkout-Flow | Voraussetzung — eigenes Item bei Aktivierung |

## Offene Punkte (extern / deferred)
- Stripe-Konto + Preise: UNKNOWN (extern, nicht von uns kontrolliert)
- Checkout-Flow (POST /api/checkout): nicht gebaut — bewusst deferred
- Stripe-Live-Datum: UNKNOWN

## Neue Artefakte

- `negotiationcoach-backend/.env.example` — angelegt mit Stripe-Variablen (kommentiert)
- `docs/audits/refactor-backlog.md` RFB-032 — Architekturentscheidungen + Aktivierungscheckliste ergänzt

## Verweise
- RFB-032 (refactor-backlog.md) — aktualisiert 2026-04-30
- ADR-006 (tier-mapping)
- negotiationcoach-backend/.env.example (neu)
