# Current Release

## Release ID
R-2026-06

## Release status
Planned

## Release goal
ADR-007 entscheiden (Dual Layer 1 — VG-06) und AR-026 (batnaDetector
Edge Function) unmittelbar danach umsetzen. Zwei sequenzielle Items,
minimaler Scope, so schnell wie möglich.

## In scope
- AR-006: ADR-007 schreiben — VG-06 Dual Layer 1 Entscheidung
- AR-026: batnaDetector Edge Function reparieren (abhängig von AR-006)

## Out of scope
- Layer 3 Simulation Engine
- Wave 2 neue Features (noch nicht briefed)
- Stripe Webhook Handler (nicht live)
- Knowledge Pipeline (ADR ausstehend)
- AR-020b / AR-020c (Index.tsx Refactors — kein Release-Druck)
- Jedes Item das nicht explizit in "In scope" steht

## Affected repos
- shared-context (ADR-007 — AR-006)
- negotiation-buddy (AR-026 — EF batnaDetector)
- negotiationcoach-backend (AR-026 — falls Layer-1-Anpassung nötig)

## Dependencies
- AR-026 ist hart geblockt durch AR-006
- Reihenfolge: AR-006 → AR-026
- Kein paralleles Delivery möglich

## Exit criteria
- ADR-007 geschrieben, reviewed und committed (AR-006 DONE)
- batnaDetector Edge Function liefert korrekte Ergebnisse (AR-026 DONE)
- TypeCheck negotiation-buddy: 0 Fehler
- TypeCheck negotiationcoach-backend: 0 Fehler

## Open decisions
- VG-06: Welche Layer-1-Implementierung bleibt kanonisch?
  Option A: Railway `src/layer1/` (EF-Engine löschen)
  Option B: EF `supabase/functions/_shared/engine/` (Railway delegiert)
  Option C: Beide aktiv mit explizitem Routing
  → Entscheidung ist der Kern von AR-006 / ADR-007

## Briefs
- AR-006: Brief muss erstellt werden (einfach — nur ADR schreiben)
- AR-026: Brief erst nach AR-006-Entscheidung möglich (Scope hängt von Option ab)

## Open risks
- ADR-007-Entscheidung kann technische Analyse erfordern (Beides lesen,
  Divergenzen dokumentieren) — Aufwand noch nicht geschätzt
- AR-026-Scope ist unbekannt bis ADR-007 entschieden
