# Brief: NC-TELEMETRY — Telemetrie-Setup

**Status:** Released
**Release:** R-2026-08 (Wave 2 — Tier 3)
**Typ:** Feature
**Priorität:** P1 — alle Metriken sind UNKNOWN ohne Telemetrie
**Erstellt:** 2026-04-29
**Abgeschlossen:** 2026-04-30

**Status: DONE**
Verification: Spec-Review 17/17 ✓ | Code-Quality APPROVED ✓ | tsc --noEmit clean ✓
Teil A: POST /api/analyze (negotiationcoach-backend) loggt `{event, tier, negotiation_type, layer2_used, success}`
Teil B: `src/lib/telemetry.ts` (negotiation-buddy) — `logTelemetry()` — 3 Events instrumentiert,
  Commit: `5b66bfc`
Open: Kein Capture-Layer — Baselines in metrics.md bleiben UNKNOWN bis NC-TELEMETRY-C.
Follow-ups: useRef-Guard bei Backend-Migration (FU-01), TeamDashboard Grenzfall (FU-02).
Docs updated: product/metrics.md, docs/delivery/follow-ups/telemetry-followups.md

---

## Lagebeurteilung

Alle Metriken in `product/metrics.md` haben Baseline: UNKNOWN. Es gibt
kein produktives Telemetrie-Setup. Datengetriebene Entscheidungen über
Conversion, Tier-Upgrades, Session-Abschlüsse und Layer-2-Fehler sind
nicht möglich.

---

## Ziel / Outcome

Basistelemetrie für die wichtigsten Produktentscheidungen:
- Wie viele Sessions werden abgeschlossen?
- Welche Tiers nutzen das Produkt aktiv?
- Wo brechen Nutzer den Chat-Flow ab?
- Wie oft wird Layer 2 genutzt (kmu/profi)?

---

## Problem

- North Star Metric (vollständige Analysen/Monat) ist UNKNOWN
- Layer-2-Fehlerrate ist UNKNOWN (obwohl Layer 2 gefixt wurde)
- Kein Tracking von Tier-Upgrades oder Conversion
- Kein Nachweis für Hypothesen in strategy.md

---

## Affected Repos

- `negotiationcoach-backend` (Railway: Logging-Endpunkte oder Render-Logs)
- `negotiation-buddy` (Frontend: Event-Tracking)
- `shared-context` (Metriken-Update: `product/metrics.md`)

---

## Scope

**Minimal-Scope (empfohlen für Kickoff):**

1. **Railway-Logs strukturieren** (negotiationcoach-backend):
   - POST /api/analyze → Log: `{tier, negotiation_type, layer2_used, success}`
   - POST /api/chat (input extraction) → Log: `{tier, inputs_complete}`

2. **Frontend-Events** (negotiation-buddy):
   - Session gestartet
   - Chat-Flow abgeschlossen (Tone Selected)
   - Tool geöffnet (WhatIf, ZOPA, Strategy)
   - Session verlassen ohne Abschluss

3. **Metriken-Baselines erheben** (shared-context):
   - `product/metrics.md` Baselines befüllen nach 2 Wochen Datenerfassung

**Out-of-Scope für Minimal-MVP:**
- Externes Analytics-Tool (PostHog, Amplitude etc.)
- Custom Dashboard
- A/B-Testing

---

## Non-Goals

- Vollständiges Analytics-Setup mit Drittanbieter
- DSGVO-Consent-Management (sofern keine PII geloggt)
- Real-time Dashboard

---

## Acceptance Criteria

1. POST /api/analyze loggt tier + layer2_used pro Request (Render-Logs)
2. Mindestens 3 Frontend-Events werden strukturiert geloggt
3. Nach 14 Tagen: `product/metrics.md` Baselines befüllt (nicht UNKNOWN)
4. TypeCheck: 0 Fehler in beiden Repos nach Änderungen

---

## Telemetry / Measurement

Dieser Brief IST das Telemetrie-Setup. Erfolg gemessen an:
- Baselines in metrics.md sind nicht UNKNOWN nach 14 Tagen

---

## Risks / Open Questions

| Risiko | Bewertung |
|---|---|
| DSGVO: werden PII in Logs geschrieben? | Zu prüfen — keine user_id in Logs, nur Tier + Event-Typ |
| Render-Logs sind ephemer (kein persistentes Log-Storage) | Medium — ggf. externe Log-Aggregation nötig für Langzeitdaten |
| ADR erforderlich? | Möglicherweise wenn externes Tool gewählt wird |
