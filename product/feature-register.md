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
| AR-006 | ADR-007 schreiben (VG-06 Dual Layer 1) | Enabler | Released | shared-context | R-2026-06 | ADR-007 DECIDED Option A 2026-04-21, Commit 9c6f1f2. Brief: product/briefs/AR-006.md. |
| NC-L2-FIX | Layer 2 Market Data Diagnose + Reparatur | Bug | Released | negotiationcoach-backend | R-2026-05 | Released 2026-04-21. Verified locally via two-run cache test. Run 1: web_search. Run 2: knowledge_graph. reality_score: 25%, non-NaN. market_context_summary: non-empty. Brief: product/briefs/NC-L2-FIX.md |
| AR-026 | batnaDetector Edge Function reparieren | Bug | Dropped | negotiationcoach-backend | — | Superseded by ADR-007-A (RFB-006 Commit 9c6f1f2). _shared/engine/ gelöscht 2026-04-21 — kein Repair mehr erforderlich. |
| AR-032 | Stripe Webhook Handler | Feature | Paused | negotiationcoach-backend | TBD | Stripe nicht live |
| AR-016a | Knowledge Pipeline | Enabler | Dropped | negotiationcoach-backend, shared-context | — | Done via Option B — extraction code removed from useChat.ts and systemPrompt.ts, commit a647d5a, 2026-04-16. |
| AR-020b | Extract useGuidedFlow hook from Index.tsx | Refactor | Qualified | negotiation-buddy | TBD | Requires test plan before implementation. Not blocking R-2026-05. |
| AR-020c | Extract useProgressEngine hook from Index.tsx | Refactor | Qualified | negotiation-buddy | TBD | Requires test plan before implementation. Not blocking R-2026-05. |
| NC-L3 | Layer 3 Simulation Engine | Feature | Idea | negotiationcoach-backend, negotiation-buddy | TBD | Wave 3 |
| NC-MARKETPLACE | Scenario Marketplace UI | Feature | Idea | negotiation-buddy | TBD | DB vorhanden |
| NC-PDF | PDF Export | Feature | Idea | negotiationcoach-backend, negotiation-buddy | TBD | Wave 4 |
