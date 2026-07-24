# Roadmap

## Prioritization rules
1. Stabiles Produkt vor neuen Features
2. Layer-Abhängigkeiten einhalten: 0 → 1 → 2 → 3
3. Sicherheit vor Tier-Wertversprechen vor neuen Features
4. ADR-Entscheidungen vor Implementierung
5. Dependency-Druck und Risikoreduktion

## Released (Wave 2 — Tier 1 + 2)
- R-2026-05: NC-L2-FIX — Layer 2 Market Data ✅
- R-2026-06: AR-006 — ADR-007 formal geschlossen ✅
- R-2026-07: NC-WAVE2 — Wave 2 Scope-Dokument ✅
- R-2026-08: NC-SEC-01, NC-SEC-02, NC-TIER-01, NC-TELEMETRY A+B ✅
- R-2026-09: NC-PLAN-FIX, NC-L2-UI, NC-CONTEXT, NC-TELEMETRY-C ✅

## Released (Wave 3 — vorgezogen, vor formalem Wave-3-Start qualifiziert)
- NC-L3-OPPONENT — KI-Gegner-Rollenspiel, Backend (`d6b39b6`) ✅ — profi only
- NC-L3-OPPONENT-UI — OpponentSimulator Frontend (`78ff4fb`) ✅ — profi only, depends on NC-L3-OPPONENT
- NC-L3-SIM-REALISM — Simulation-Realismus-Fix (`690851c`) ✅
- NC-NAV — Navigation & Tier-Struktur Redesign, Phasen A–E vollständig (`847aa79`…`42c6fc7`) ✅
  TBD (R-2026-10) — code-complete, noch keinem offiziellen Release zugeordnet.
- NC-L3-SIM — Layer 3 Simulation Engine — Redesign (L1/L2-geerdeter Gegner, dynamischer
  Intake, Debrief) ✅ `886d3e8` — alle Phasen abgeschlossen 2026-07-24 (Backend Phase 1-3
  `c00e719`/`2f163c8`/`007a6ee`+`b5bf2d7`; Frontend Phase 6 "Substance Activation A-3"
  `1bad815`..`886d3e8`). Ersetzt NICHT NC-L3-OPPONENT — `/api/opponent-simulation/*` bleibt
  deployt, Frontend ruft aber nur noch `/api/simulate/*` auf (Entscheidung P-3, DCC-FE-03/
  DCC-BE-03). Brief: product/briefs/NC-L3-SIM.md. TBD (R-2026-10) — code-complete, noch
  keinem offiziellen Release zugeordnet.

## Now
- NC-ONBOARDING: BLOCKED — wartet auf 14-Tage PostHog-Baseline ab VITE_POSTHOG_API_KEY-Aktivierung
  (frühestens Mitte Mai 2026). Unblockiert sobald metrics.md Baselines vorliegen.

## Next
- FEATURE-GUIDED-CONTEXT (Qualified, P2): Guided Flows erfassen Kontextfelder für belastbare
  Marktdaten. Infrastruktur bereit (FEATURE-L2-CONTEXT `858c0c4`). Pflichtfelder pro Type
  (gehalt/miete/lieferant/m_a/autokauf) definiert. Optionen A (UI-Form) / B (Chat-Extraktion) /
  C (Hybrid) zu entscheiden. Offene Fragen: ARCH02-Konformität, autokauf-Type,
  NC-CONTEXT-Abhängigkeit (NC-CONTEXT selbst bereits released). Nächster Schritt: Spec-Prompt
  (Template 2-DEV Docs-only).

## Later (Wave 3+, noch nicht qualifiziert)
- NC-L3-SCENARIO: Sub-Item von NC-L3, noch nicht qualifiziert
- NC-MARKETPLACE: Scenario Marketplace UI
- NC-PDF: PDF Export

## Holding (extern blockiert)
- AR-032: Stripe Webhook Handler — Paused, Stripe nicht live. NC-TIER-01 (Vorbedingung) ist
  bereits released; wartet nur noch auf Stripe go-live. Aktivierungscheckliste in RFB-032
  dokumentiert.

## Notes
- Wave 1 vollständig abgeschlossen (R-2026-05 bis R-2026-08)
- Wave 2 (R-2026-09) abgeschlossen: NC-PLAN-FIX, NC-L2-UI, NC-CONTEXT, NC-TELEMETRY-C
- ADR-007 entschieden + dokumentiert (Option A, Retire)
- Wave 3 ist trotz "Later"-Planung bereits mit vier released Teilstücken gestartet
  (NC-L3-OPPONENT + UI, NC-L3-SIM-REALISM, NC-L3-SIM Redesign — vollständig Released
  2026-07-24, alle Phasen inkl. Frontend abgeschlossen)
- NC-ONBOARDING ist von NC-TELEMETRY-C-Baseline (min. 2 Wochen Daten) abhängig —
  NC-TELEMETRY-C ist selbst bereits released (R-2026-09), die Baseline-Uhr läuft entsprechend
- NC-TELEMETRY-C ist der nächste strategische Entscheidungspunkt (Aggregations-Layer,
  siehe metrics.md)
