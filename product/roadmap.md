# Roadmap

## Prioritization rules
1. Stabiles Produkt vor neuen Features
2. Layer-Abhängigkeiten einhalten: 0 → 1 → 2 → 3
3. Sicherheit vor Tier-Wertversprechen vor neuen Features
4. ADR-Entscheidungen vor Implementierung
5. Dependency-Druck und Risikoreduktion

## Now (Wave 2 — Tier 1: Sicherheit)
- NC-WAVE2: Wave 2 Scope-Dokument — **IN DELIVERY** (R-2026-07)
- NC-SEC-01: VG-01/VG-02 RLS-Audit in Produktion (Critical/High Risk)
- NC-SEC-02: VG-05-A JWT-Auth-Hardening in Edge Functions (ADR-004 umsetzen)

## Next (Wave 2 — Tier 2/3: Observability + Revenue)
- NC-TELEMETRY: Telemetrie-Setup (nach NC-SEC-01/02)
- NC-TIER-01: Stripe-Readiness-Check (parallel zu NC-TELEMETRY möglich)
- NC-ONBOARDING: Guest Mode / Free-Tier Onboarding (nach NC-TELEMETRY-Baseline)
- AR-032: Stripe Webhook Handler (nach NC-TIER-01 + Stripe go-live)

## Later (Wave 3+)
- NC-L3: Layer 3 Simulation Engine
- NC-MARKETPLACE: Scenario Marketplace UI
- NC-PDF: PDF Export

## Holding (extern blockiert)
- AR-032: Stripe Webhook Handler — Stripe nicht live; Unblocked nach NC-TIER-01 + Stripe go-live
- AR-016a: Knowledge Pipeline — Dropped (Option B umgesetzt)

## Notes
- Wave 1 vollständig abgeschlossen (R-2026-05, R-2026-06) — alle P0/P1 Items DONE
- ADR-007 entschieden (Option A) — Dual Layer 1 aufgelöst
- Layer 0–2 stabil. Layer 3 erst nach Wave-2-Abschluss
- NC-ONBOARDING ist von NC-TELEMETRY-Baseline (min. 2 Wochen Daten) abhängig
