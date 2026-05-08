# Brief: NC-PLAN-FIX — Verhandlungsplan-Trigger reparieren

**Status:** In Delivery
**Release:** R-2026-09
**Typ:** Bug
**Priorität:** P1 — Kernfunktion nicht nutzbar
**Erstellt:** 2026-05-08

---

## Lagebeurteilung

Der Verhandlungsplan-Modal zeigt "Noch kein Verhandlungsplan vorhanden"
auch nach vollständigem Chat-Flow. Bestätigt per Screenshot 2026-05-08.

Der Plan wird in `Index.tsx` nur generiert wenn `allDone = true`:
```typescript
const keys = ["situation", "ziel", "gegenseite", "batna", "macht", "strategie"];
const allDone = keys.every((k) => progressStatus[k]?.completed);
```

Der Fortschrittspunkt "gegenseite" erfordert `opponent_estimated_max`
oder `opponent_estimated_min`. Bei Gehaltsverhandlungen werden diese
Felder vom Chat nie erfragt und vom Gemini-Extraktor nie gefunden →
`gegenseite = false` → `allDone = false` → kein Plan.

---

## Ziel / Outcome

Der Verhandlungsplan wird generiert sobald die wesentlichen Felder
vorliegen — ohne dass "gegenseite" als Pflicht-Gate gilt.

---

## Problem

- "gegenseite" ist konzeptuell sinnvoll, aber für Gehaltsverhandlungen
  strukturell nicht extrahierbar (Arbeitgeber nennt sein Limit nicht)
- Alle anderen 5 Punkte können grün sein — Plan erscheint trotzdem nie
- Nutzer sieht "Noch kein Verhandlungsplan vorhanden" und weiß nicht warum

---

## Affected Repos

- `negotiation-buddy` (Index.tsx — Plan-Trigger-Logik)

---

## Scope

**Option A (empfohlen):** Plan-Trigger auslösen wenn mindestens 4 von 6
Punkten completed sind (statt alle 6).

**Option B:** "gegenseite" aus dem Pflicht-Gate entfernen — Plan wird
generiert wenn situation, ziel, batna, macht, strategie grün sind.

**Option C:** Separater Trigger: wenn `extractedInputs.own_target` und
`extractedInputs.negotiation_type` gesetzt sind → Plan generieren
unabhängig von progressStatus.

Implementierungsort: `Index.tsx` — Plan-Generierungs-useEffect
(ca. Zeile 354-396 im aktuellen Stand).

---

## Non-Goals

- Kein neuer Progress-Punkt
- Kein Interface-Change an generate-plan EF
- Keine Änderung an der Fortschrittsanzeige selbst

---

## Acceptance Criteria

1. Nach vollständigem Gehaltverhandlungs-Chat erscheint der Verhandlungsplan
2. Plan enthält sinnvolle Inhalte (nicht leer)
3. TypeCheck negotiation-buddy: 0 Fehler
4. Keine Regression bei anderen Verhandlungstypen (Miete, Auto)

---

## Telemetry / Measurement

NC-TELEMETRY: `chat_flow_completed` Event feuert → plan wird generiert.
Direkte Messung nach Fix möglich über PostHog.

---

## Risks / Open Questions

| Risiko | Bewertung |
|---|---|
| Option A könnte Plan zu früh triggern | Low — 4/6 ist konservativ genug |
| generate-plan EF braucht vollständige Daten | Medium — Brief senden mit vorhandenen extractedInputs |
| Lovable-Deployment nötig | Bekannt — Frontend-Only |

**Offene Entscheidung:** Option A, B oder C? → Entscheid vor GO.
