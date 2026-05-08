# Current Release

## Release ID
R-2026-09

## Release status
Planned

## Release goal
Kernfunktionen reparieren: Verhandlungsplan-Trigger und Market-Data-Anzeige.
Beides ist für Nutzer aktuell nicht funktionierend — P1-Fixes vor NC-ONBOARDING.

## In scope
- NC-PLAN-FIX (P1 — NEU): Verhandlungsplan-Trigger anpassen
  Symptom: Plan wird nie generiert weil "gegenseite"-Felder nie aus Chat
  extrahiert werden. Fix: Trigger-Logik anpassen.
  Brief: product/briefs/NC-PLAN-FIX.md

- NC-L2-UI (P1 — NEU): Market Data anzeigen + /api/enrich einbinden
  Symptom: Layer-2-Ergebnisse (Marktmedian, Reality Score) nirgends sichtbar.
  Fix: /api/enrich aufrufen + Werte im UI anzeigen.
  Brief: product/briefs/NC-L2-UI.md

## Blocked / Open items
- NC-ONBOARDING: BLOCKED — wartet auf PostHog-Baseline (frühestens Mitte Mai 2026)
- AR-032 Stripe Webhook: BLOCKED EXTERN — wartet auf Stripe go-live

## Affected repos
- negotiation-buddy (NC-PLAN-FIX, NC-L2-UI — Frontend)
- negotiationcoach-backend (NC-L2-UI — /api/enrich bereits vorhanden)

## Exit criteria
- Verhandlungsplan erscheint nach vollständigem Chat-Flow ✅
- Market-Data-Werte (Marktmedian, Reality Score) im UI sichtbar ✅
- TypeCheck negotiation-buddy: 0 Fehler ✅

## Open decisions
- NC-PLAN-FIX: Welche der 6 Fortschrittspunkte sind Pflicht für Plan-Trigger?
- NC-L2-UI: Wo genau werden Market Data angezeigt (Strategy Report, eigene Sektion)?
