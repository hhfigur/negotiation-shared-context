# Current Release

## Release ID
R-2026-08

## Release status
Released & Verified

## Release goal
Wave 2 — Tier 1 + 2: Security, Telemetrie und Stripe-Readiness.
Alle P0-Sicherheitslücken aus Wave-1-Audit behoben,
Telemetrie instrumentiert, Stripe-Architekturentscheidungen dokumentiert.

## Released items
- NC-SEC-01: Released — RLS-Audit abgeschlossen, VG-01/VG-02 RESOLVED (61dfb5d)
- NC-SEC-02: Released — JWT-Hardening verifiziert, VG-05-A RESOLVED (244e6de)
- NC-TIER-01: Released — Stripe-Readiness-Audit, Architekturentscheidungen dokumentiert (23cbae9)
- NC-TELEMETRY Teil A: Released — console.log in POST /api/analyze (e6401ca)
- NC-TELEMETRY Teil B: Released — Frontend logTelemetry(), 3 Events (5b66bfc)
- ADR-007 Docs-Rückstand: Released — Retire vollständig dokumentiert (ea39735)

## Blocked / Open items
- NC-TELEMETRY-C: OPEN — Capture-Layer (PostHog/Sentry): strategische Entscheidung ausstehend
- NC-ONBOARDING: BLOCKED — wartet auf 14-Tage Telemetrie-Baseline (frühestens Mitte Mai 2026)
- AR-032 Stripe Webhook: BLOCKED EXTERN — wartet auf Stripe go-live

## Affected repos
- negotiationcoach-backend (NC-SEC-01, NC-TIER-01, NC-TELEMETRY Teil A, ADR-007 Docs)
- negotiation-buddy (NC-TELEMETRY Teil B)
- shared-context (alle Docs)

## Exit criteria (alle erfüllt)
- VG-01/VG-02 RESOLVED ✅
- VG-05-A RESOLVED ✅
- ADR-007 DECIDED + dokumentiert ✅
- NC-TELEMETRY Teil A + B committed ✅
- TypeCheck negotiationcoach-backend: 0 Fehler ✅

## Open decisions
- NC-TELEMETRY-C: welches Capture-Layer-Tool?
- NC-ONBOARDING Scope: nach Baseline-Daten definieren
