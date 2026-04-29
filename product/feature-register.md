# Feature Register

## Scope
Alle operativen Items: Features, Bugs, Enabler, Refactors, Research.
Mapping: AR-xxx Einträge entsprechen den RFB-xxx Items im Audit-Backlog.

## Status and type rules
- exactly one Type per item
- exactly one Status per item
- every active item must list affected repos
- every delivery-bound item must link to a brief
- every released item references the release where it shipped

## Register
| ID | Title | Type | Status | Affected Repos | Target Release | Notes |
|---|---|---|---|---|---|---|
| NC-WAVE2 | Wave 2 Scope-Dokument erstellen | Enabler | In Delivery | shared-context | R-2026-07 | Brief: product/briefs/NC-WAVE2.md |
| NC-SEC-01 | VG-01/VG-02: RLS-Audit in Produktion (teams, negotiation_sessions) | Enabler | Qualified | shared-context, negotiationcoach-backend | TBD (Wave 2) | Brief: product/briefs/NC-SEC-01.md. P0 security — Critical/High aus Wave-1-Audit. |
| NC-SEC-02 | VG-05-A: JWT-Auth-Hardening in Edge Functions (Tier-Enforcement) | Enabler | Qualified | negotiation-buddy | TBD (Wave 2) | Brief: product/briefs/NC-SEC-02.md. ADR-004 umsetzen. |
| NC-TIER-01 | Stripe-Readiness-Check — was fehlt bis Stripe live? | Research | Qualified | shared-context | TBD (Wave 2) | Brief: product/briefs/NC-TIER-01.md. Prerequisite für AR-032. |
| NC-TELEMETRY | Telemetrie-Setup — Konversions- und Nutzungsdaten | Feature | Qualified | negotiationcoach-backend, negotiation-buddy | TBD (Wave 2) | Brief: product/briefs/NC-TELEMETRY.md. Alle Metriken UNKNOWN ohne dieses Item. |
| NC-ONBOARDING | Guest Mode / Free-Tier Onboarding-Optimierung | Feature | Qualified | negotiation-buddy | TBD (Wave 2) | Brief: product/briefs/NC-ONBOARDING.md. Blocked by NC-TELEMETRY (braucht Baseline-Daten). |
| AR-006 | ADR-007 schreiben (VG-06 Dual Layer 1) | Enabler | Released | shared-context | R-2026-06 | ADR-007 DECIDED Option A 2026-04-21, Commit 9c6f1f2. Brief: product/briefs/AR-006.md. |
| NC-L2-FIX | Layer 2 Market Data Diagnose + Reparatur | Bug | Released | negotiationcoach-backend | R-2026-05 | Released 2026-04-21. Verified locally via two-run cache test. Brief: product/briefs/NC-L2-FIX.md |
| AR-020b | Extract useGuidedFlow hook from Index.tsx | Refactor | Released | negotiation-buddy | — | DONE `64b7432` — bereits in technischem Backlog RFB-020b. |
| AR-020c | Extract useProgressEngine hook from Index.tsx | Refactor | Released | negotiation-buddy | — | DONE — bereits in technischem Backlog RFB-020c. |
| AR-026 | batnaDetector Edge Function reparieren | Bug | Dropped | negotiationcoach-backend | — | Superseded by ADR-007-A (RFB-006 Commit 9c6f1f2). _shared/engine/ gelöscht 2026-04-21. |
| AR-032 | Stripe Webhook Handler | Feature | Paused | negotiationcoach-backend | TBD | Stripe nicht live. Unblocked nach NC-TIER-01. |
| AR-016a | Knowledge Pipeline | Enabler | Dropped | negotiationcoach-backend, shared-context | — | Done via Option B — extraction code removed from useChat.ts and systemPrompt.ts, commit a647d5a, 2026-04-16. |
| NC-L3 | Layer 3 Simulation Engine | Feature | Idea | negotiationcoach-backend, negotiation-buddy | TBD | Wave 3 |
| NC-MARKETPLACE | Scenario Marketplace UI | Feature | Idea | negotiation-buddy | TBD | DB vorhanden |
| NC-PDF | PDF Export | Feature | Idea | negotiationcoach-backend, negotiation-buddy | TBD | Wave 4 |
