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

## Now (R-2026-09 — Planned)
- NC-TELEMETRY-C: Capture-Layer-Entscheidung (PostHog / Sentry / Custom)
  → Blocking: metrics.md Baselines bleiben UNKNOWN ohne dieses Item
- NC-ONBOARDING: BLOCKED — wartet auf 14-Tage Telemetrie-Baseline (frühestens Mitte Mai)

## Next
- AR-032: Stripe Webhook Handler (extern blockiert — wartet auf Stripe go-live)
- NC-ONBOARDING: nach Telemetrie-Baseline-Erhebung

## Later (Wave 3+)
- NC-L3: Layer 3 Simulation Engine
- NC-MARKETPLACE: Scenario Marketplace UI
- NC-PDF: PDF Export

## Holding (extern blockiert)
- AR-032: Stripe Webhook Handler — Stripe nicht live; Aktivierungscheckliste in RFB-032 dokumentiert

## Notes
- Wave 1 vollständig abgeschlossen (R-2026-05 bis R-2026-08)
- ADR-007 entschieden + dokumentiert (Option A, Retire)
- Layer 0–2 stabil. Layer 3 erst nach Wave-2-Abschluss
- NC-ONBOARDING ist von NC-TELEMETRY-C-Baseline (min. 2 Wochen Daten) abhängig
- NC-TELEMETRY-C ist der nächste strategische Entscheidungspunkt
