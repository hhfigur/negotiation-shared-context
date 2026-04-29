# Current Release

## Release ID
R-2026-07

## Release status
Planned

## Release goal
Wave 2 Scope finalisieren: alle Wave-2-Items identifizieren, mit IDs
versehen, Briefs erstellen und Feature Register auf Stand bringen.
Kein Code-Delivery — reine Planung und Housekeeping.

## In scope
- NC-WAVE2: Wave 2 Scope-Dokument erstellen (Enabler)
  Deliverable: product/feature-register.md mit vollständigen Wave-2-Items
  (ID, Typ, Status Qualified, Brief, Affected Repos)
- CLEANUP-001: Feature Register bereinigen
  AR-020b → Released, AR-020c → Released (bereits in technischem Backlog DONE)
- CLEANUP-002: Strategy.md aktualisieren
  Stale Constraints entfernen (ADR-007 resolved, Layer 2 done)
  Neuen Fokus setzen (Wave 2 + Tier-Conversion)
- CLEANUP-003: Roadmap "Now" auf Wave-2-Items aktualisieren

## Out of scope
- Implementierung von Wave-2-Features (erst nach NC-WAVE2)
- Layer 3 Simulation Engine
- Stripe Webhook Handler (nicht live)
- NC-TELEMETRY (Idea — braucht Wave-2-Scope zuerst)
- NC-ONBOARDING (Idea — braucht Wave-2-Scope zuerst)
- Jedes Code-Delivery-Item

## Affected repos
- shared-context (alle Änderungen — Docs only)

## Dependencies
- Keine blocking Dependencies
- NC-WAVE2 muss vor CLEANUP-003 fertig sein
  (Roadmap erst aktualisieren wenn Scope klar)

## Exit criteria
- product/feature-register.md: Wave-2-Items vollständig mit ID + Brief + Status
- AR-020b, AR-020c: Status = Released in Feature Register
- Strategy.md: aktuell (keine stale Constraints, neuer Fokus)
- Roadmap "Now" enthält konkrete Wave-2-Delivery-Items

## Open decisions
- Was sind die Wave-2-Items? (Kern von NC-WAVE2)
  Kandidaten aus Strategy: Tier-Conversion-Pfad, Telemetrie, Onboarding
  → Entscheidung ist Teil des NC-WAVE2-Deliverables

## Open risks
- Wave-2-Scope könnte ADRs erfordern bevor Delivery beginnt
  (insbes. Tier-Enforcement-Pfad — VG-05-A noch offen)
