# Current Release

## Release ID
R-2026-05

## Release status
In Progress

## Release goal
Layer 2 Market Data diagnostizieren und reparieren.
Single-focus release. AR-006 und AR-026 sind nicht in scope.

## In scope
- NC-L2-FIX: Layer 2 Market Data Diagnose und Reparatur

## Released items
- NC-L2-FIX: Released 2026-04-21 — verified

## Conditional — not in this release
- AR-026: batnaDetector-Reparatur — removed from R-2026-05 scope. Depends on AR-006 (ADR-007), which is Paused. Candidate for next release after AR-006 is resolved.

## Out of scope
- AR-006: ADR-007 (VG-06 Dual Layer 1) — Paused, requires separate architectural slot
- Layer 3 Simulation Engine
- Scenario Marketplace UI
- PDF Export
- Stripe Webhook Handler
- Knowledge Pipeline
- Neue Frontend-Screens
- Jedes Item, das nicht explizit in "In scope" steht

## Affected repos
- negotiationcoach-backend (NC-L2-FIX)

## Dependencies
- none (single-item release)

## Exit criteria
- Layer 2 Market Data liefert korrekte Ergebnisse (manuell verifiziert)
- NC-L2-FIX hat einen Brief
- TypeCheck backend: 0 Fehler

## Open risks
- Layer-2-Fehlerursache noch nicht diagnostiziert — Diagnose ist erster Schritt

## Open decisions
- VG-06: Dual Layer 1 — welche Implementierung bleibt kanonisch? (ADR-007, deferred to next release)
