# Product Strategy

## Planning horizon
- Horizon: next 90 days
- Status: Updated 2026-04-29 (nach Wave-1-Abschluss und R-2026-06)
- Last updated: 2026-04-29

## Product goal
- Erstes zahlungsfähiges Tier (kmu/profi) aktivieren: Stripe live, Tier-Enforcement gesichert, Telemetrie vorhanden

## Target users
- Primary: KMU-Verhandlungsführer (tier: kmu, profi)
- Secondary: Privatpersonen mit konkretem Verhandlungsbedarf (tier: privat)

## Core problem
- Verhandler gehen ohne strukturierte Vorbereitung und ohne Kenntnis der Marktlage in wichtige Verhandlungen

## Value proposition
- KI-gestützte Analyse von ZOPA, BATNA, Marktdaten und Strategie in Minuten statt Stunden

## Strategic focus for the next 90 days
- Focus 1: Sicherheit absichern — VG-01/VG-02 RLS-Audit, VG-05-A JWT-Hardening (NC-SEC-01, NC-SEC-02)
- Focus 2: Observability aufbauen — Telemetrie-Setup für datengetriebene Entscheidungen (NC-TELEMETRY)
- Focus 3: Tier-Conversion-Pfad vorbereiten — Stripe-Readiness-Check + Onboarding-Optimierung (NC-TIER-01, NC-ONBOARDING)

## Resolved since last update (2026-04-20)
- Layer 2 Market Data: ✅ repariert und verifiziert (R-2026-05)
- ADR-007 Dual Layer 1: ✅ entschieden Option A, umgesetzt (R-2026-06)
- RFB-006 / RFB-026: ✅ geschlossen
- Diverse Bugs (RFB-039, 040, 043, 044): ✅ gefixt und deployed

## Not a focus right now
- Layer 3 Simulation Engine (kein Tier-Druck, keine Layer-2-Voraussetzung verletzt)
- Scenario Marketplace UI (kein aktiver Nutzer-Bedarf belegt)
- PDF Export (Stripe nicht live — kein bezahlter Tier aktiv)
- AR-032 Stripe Webhook (extern blockiert bis Stripe live)

## Assumptions to validate
- KMU-Nutzer sind bereit 49€/Monat zu zahlen, wenn Tier-Enforcement sichtbar und Marktdaten verlässlich sind
- Der Chat-first Einstieg reduziert Onboarding-Friction gegenüber dem Canvas (→ validieren via NC-TELEMETRY)

## Dependencies and constraints
- Stripe nicht live → NC-TIER-01 klärt Vorbedingungen, AR-032 wartet auf Stripe-Go-Live
- NC-ONBOARDING hängt von NC-TELEMETRY-Daten ab (min. 2 Wochen Baseline)
- VG-05-A (NC-SEC-02): Lovable-managed EF — Deployment-Prozess einschränkend

## Deep-dive references
- `docs/decision-log/ADR-006-tier-mapping.md` — Tier-Definitionen
- `docs/decision-log/ADR-003-ai-provider-strategy.md` — AI-Provider-Split
- `docs/decision-log/ADR-004-chat-path-routing.md` — EF-Tier-Enforcement
- `docs/audits/wave1-completion-gate.md` — Wave-1-Abschluss + Post-Gate-Actions
- `docs/audits/refactor-backlog.md` — technische Schulden
