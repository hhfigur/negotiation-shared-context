# Metrics

## Planning horizon
- Horizon: next 90 days
- Product goal: Layer 2 stabilisieren, Wave 2 scope-ready
- Notes: Baselines sind UNKNOWN bis erstes Telemetrie-Setup

## North Star
| Name | Definition | Baseline | Target | Source | Status |
|---|---|---:|---:|---|---|
| Vollständige Analysen pro Monat | Sessions mit isComplete=true und Layer-1-Ergebnis | UNKNOWN | TBD | Railway logs | Draft |

## Primary release metrics
| Metric | Why it matters | Baseline | Target | Source | Owner |
|---|---|---:|---:|---|---|
| Layer-2-Fehlerrate | Market Data broken = kein KMU-Wert | UNKNOWN | <5% | Railway logs | Backend |
| realityScore Genauigkeit | Kernversprechen Layer 2 | UNKNOWN | TBD | manual review | Product |

## Guardrails
| Metric | Risk guarded against | Current | Limit | Source |
|---|---|---:|---:|---|
| TypeCheck-Fehler im Backend | Regressions durch Layer-2-Fix | 0 | 0 | npx tsc --noEmit |

## Telemetrie-Baseline (Stand 2026-04-30)

**Status:** UNKNOWN — Instrumentierung deployed, kein Aggregations-Layer aktiv.

Events instrumentiert (NC-TELEMETRY Released):
- `analyze_completed` — Backend (POST /api/analyze): tier, negotiation_type, layer2_used, success
- `session_started` — Frontend: 2 Trigger (handleUseCaseStart, handleNewSession)
- `chat_flow_completed` — Frontend: wenn alle 6 Progress-Punkte abgeschlossen
- `tool_opened` — Frontend: ZopaCalculator, WhatIfSimulator, StrategyGenerator, NegotiationCanvas, DebriefDashboard

Baseline-Erhebung möglich erst nach **NC-TELEMETRY-C** (Capture-Layer-Entscheidung).
Ohne Aggregations-Layer (PostHog, Sentry o.ä.) bleiben alle Baselines UNKNOWN,
da `console.log` ephemer ist und nicht automatisch aggregiert wird.

## Telemetry gaps
- UNKNOWN: kein Aggregations-Layer — NC-TELEMETRY-C entscheidet ob/welches Tool
- UNKNOWN: kein Tracking von Tier-Upgrades oder Conversion-Pfaden
- UNKNOWN: keine Session-ID in Events — Funnel-Analyse nicht möglich ohne Identifier

## Rules
- use `UNKNOWN` instead of guessing numbers
- no release item should move into delivery without at least one success metric or an explicit telemetry-gap note
