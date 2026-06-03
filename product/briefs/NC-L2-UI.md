# Brief: NC-L2-UI — Market Data anzeigen + /api/enrich einbinden

**Status:** Released
**Release:** R-2026-09
**Typ:** Bug / Missing Feature
**Priorität:** P1 — Layer-2-Mehrwert komplett unsichtbar
**Erstellt:** 2026-05-08

---

## Lagebeurteilung

Layer 2 (Market Data Enrichment) ist im Backend implementiert und
repariert (RFB-037, RFB-045). Der Endpunkt `/api/enrich` existiert
und liefert `market_median`, `reality_score`, `market_context_summary` etc.

**Problem:** Das Frontend ruft `/api/enrich` nie auf. Es gibt keine
Komponente die Layer-2-Daten darstellt. Die Enrichment-Daten verschwinden
im Backend ohne je angezeigt zu werden.

**Tier-Gate:** `/api/enrich` erfordert `requireTier('kmu')` — nur kmu/profi-
Nutzer sehen Marktdaten. Das ist korrekt und soll so bleiben.

---

## Ziel / Outcome

kmu/profi-Nutzer sehen nach der Analyse Marktdaten:
- Marktmedian (z.B. "72.000 € / Jahr")
- Reality Score (z.B. "+25% über Markt")
- Marktlage-Zusammenfassung (1-2 Sätze)

---

## Problem

- `/api/enrich` wird nie aufgerufen → Layer-2-Mehrwert = 0
- Der Verhandlungsplan (generate-plan EF) enthält keine Marktdaten
- Der Strategy-Tab zeigt keine Marktkontext-Information
- Nutzer zahlender Tiers (kmu/profi) sehen keinen Unterschied zu free

---

## Affected Repos

- `negotiation-buddy` (Frontend — Call + Darstellung)
- `negotiationcoach-backend` (Backend — `/api/enrich` bereits vorhanden)

---

## Scope

### Phase 1 — /api/enrich aufrufen

In `negotiation-buddy`, nach erfolgreichem `/api/analyze`-Call
(oder nach Chat-Flow-Abschluss wenn `sessionId` vorliegt):

```typescript
// Nur für kmu/profi Tier
if (tier === 'kmu' || tier === 'profi') {
  const enriched = await apiClient.enrich(sessionId, extractedInputs);
  setEnrichedData(enriched);
}
```

`/api/enrich` Request: `{ sessionId: string, inputs: NegotiationInputs }`
`/api/enrich` Response: `EnrichedAnalysisResult` (market_median, reality_score, etc.)

### Phase 2 — Marktdaten anzeigen

Neue Sektion im Strategy-Tab oder Fortschritts-Panel:
- "Marktlage" Card mit: Median-Wert, Quartil-Range, Reality Score, Zusammenfassung
- Nur sichtbar wenn `enrichedData !== null` (automatisch für kmu/profi)
- Für free/privat: ausblenden oder Upgrade-CTA

---

## Non-Goals

- Kein neuer Endpunkt (bestehend nutzen)
- Kein Change an Layer-2-Logik
- Keine Änderung am Tier-Gate
- Kein eigener Screen — Integration in bestehende UI

---

## Acceptance Criteria

1. kmu-Nutzer sieht nach Chat-Flow Marktmedian und Reality Score
2. free/privat-Nutzer sieht diese Daten nicht
3. `/api/enrich` wird mit korrekter JWT aufgerufen (kein 401, kein 403)
4. TypeCheck negotiation-buddy: 0 Fehler
5. Bei `source: 'none'` (Tier zu niedrig oder Fehler): kein Crash, keine leere Sektion

---

## Telemetry / Measurement

NC-TELEMETRY: neues Event `market_data_shown` (tier, source) nach Implementierung.
Baseline nach 14 Tagen: wie oft wird Layer 2 genutzt?

---

## Risks / Open Questions

| Risiko | Bewertung |
|---|---|
| sessionId fehlt wenn kein Session-Feature aktiv (privat/free) | Medium — Guard nötig |
| /api/enrich kann Sekunden dauern (Claude-Call) | Medium — Loading-State nötig |
| Lovable-Deployment für Frontend | Bekannt |
| ADR erforderlich? | Nein — bestehender Endpunkt |

**Entschieden:** Market-Data-Card in Index.tsx (bereits vorhanden, jetzt befüllt).

---

**Status: DONE**
Commit: `8a5b38d` (negotiationcoach-backend) + `f276041` (negotiation-buddy) — 2026-06-02
Verified: tsc --noEmit clean ✓ (both repos) | backend chat-flow path in routes.ts ✓
API contract updated: yes — docs/contracts/frontend-backend.md (inputs optional, chat-flow path documented)
DB delta: none
ADR created/amended: none
Docs updated: product/briefs/NC-L2-UI.md, product/feature-register.md, docs/contracts/frontend-backend.md
