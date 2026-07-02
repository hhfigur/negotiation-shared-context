# Delivery Brief: NC-L3-OPPONENT-UI
## OpponentSimulator — Frontend-Implementierung (KI-Gegner-Rollenspiel)

**Release:** TBD (Wave 3)
**Status:** Qualified
**Affected repos:** negotiation-buddy (primary), shared-context (docs)
**Tier impact:** profi only
**Created:** 2026-07-02
**Priority:** P2 — Backend live, Feature ohne UI nicht nutzbar
**Depends on:** NC-L3-OPPONENT (Released `d6b39b6`) — Backend-Endpoints live
**ADR:** ADR-009 (Backend-Routing), ADR-001/002 (keine Logik/Supabase-Calls im Frontend)

---

## Goal / Outcome

Profi-Nutzer können das KI-Gegner-Rollenspiel über eine eigene Seite `/app/opponent`
starten und spielen. Die Seite folgt dem Muster von `WhatIfSimulator.tsx`: eigene
Route, ruft ausschließlich Backend-API auf (keine direkten Supabase-Calls), zeigt
eine eigene Auswertung am Ende.

---

## Architektur

- Neue Seite `src/pages/OpponentSimulator.tsx`
- Route `/app/opponent` als Child-Route unter `/app` (Nested-Routing-Pattern,
  konsistent mit anderen Tools seit BUG-20260630-Fix)
- 3 neue API-Funktionen in `src/lib/apiClient.ts`
- Profi-Badge in BottomTabBar + SessionSidebar, `/app/opponent` in `TOOL_ROUTES`
- Kein direkter Supabase-Call — alle Datenzugriffe via Backend-API
- Tier-Check: `subscription_tier === 'profi'` aus localStorage
  (`negotiation_coach_persona`-Key), Pattern identisch zu WhatIfSimulator

---

## UI-Phasen

### Phase 1 — Setup-Screen
Nach Laden der Seite (oder wenn keine aktive Runde):
- Verhandlungstyp: vorbefüllt aus AnalysisContext (`extractedInputs.negotiation_type`)
  oder Dropdown-Auswahl falls kein Context
- Gegner-Stil: Auswahl 'kooperativ' | 'hart' | 'manipulativ' | 'sachlich'
- Schwierigkeitsgrad: Auswahl 'einfach' | 'mittel' | 'schwer'
- "Simulation starten"-Button → POST /api/opponent-simulation/start

### Phase 2 — Turn-UI (Chat-ähnlich)
- Zeigt Eröffnungs-Nachricht der KI-Gegenseite
- Texteingabe für Nutzer-Angebot/Nachricht
- "Senden"-Button → POST /api/opponent-simulation/:id/turn
- Turn-Zähler: "Runde X von 12" sichtbar
- "Verhandlung beenden"-Button → POST /api/opponent-simulation/:id/finish
- Bei `finished: true` (Rundenlimit) → automatisch zu Phase 3

### Phase 3 — Auswertungs-Screen
- Ergebnis vs. Nash-Optimum anzeigen (`outcome_vs_nash`, `tactic_assessment`)
- Eigene ZOPA-Range sichtbar (`own_zopa_min`/`own_zopa_max`)
- Jetzt erst: versteckte Gegenseiten-Werte anzeigen
  (`hidden_opponent_minimum`, `hidden_opponent_target`)
- "Neue Runde"-Button → zurück zu Phase 1
- "Zurück zum Chat"-Button → `/app`

---

## API-Funktionen (neu in apiClient.ts)

```typescript
export function startOpponentSimulation(
  body: StartOpponentSimulationBody,
  token: string,
): Promise<StartOpponentSimulationResponse>

export function sendOpponentTurn(
  simulationSessionId: string,
  body: { content: string; client_turn_id: string },
  token: string,
): Promise<TurnOpponentSimulationResponse>

export function finishOpponentSimulation(
  simulationSessionId: string,
  body: { final_offer: number },
  token: string,
): Promise<FinishOpponentSimulationResponse>
```

Typen sind in `src/lib/types.ts` anzulegen (analog zu `NegotiationInputs`, `AnalysisResult`).

---

## Dateien

| Datei | Art |
|---|---|
| `src/pages/OpponentSimulator.tsx` | neu |
| `src/lib/apiClient.ts` | erweitert — 3 neue Funktionen (additiv) |
| `src/lib/types.ts` | erweitert — Response-Typen für Opponent-Simulation |
| `src/App.tsx` | erweitert — Import + Route `path="opponent"` unter `/app` |
| `src/components/BottomTabBar.tsx` | erweitert — neuer Eintrag + TOOL_ROUTES |
| `src/components/SessionSidebar.tsx` | erweitert — neuer Eintrag |
| `src/pages/Landing.tsx` | erweitert — neuer Tool-Eintrag in Tool-Liste |

**Pflicht:** Nach jeder Route-Addition `grep -r '"/app/opponent"' src/` über ALLE
Dateien laufen, um sicherzustellen dass kein Eintrag fehlt (Lesson BUG-20260630).

---

## Nicht in Scope

- Turn-History persistiert anzeigen (nur aktive Runde sichtbar)
- Integration in DebriefDashboard
- Offline-Fallback / Skeleton-Loading über was WhatIfSimulator schon hat
- NC-L3-SCENARIO (separate Initiative)

---

## Acceptance Criteria

- AC-1: Nicht-profi-Nutzer sehen auf `/app/opponent` eine "Profi-Feature"-Meldung
  statt der Simulation (kein 403-Toast)
- AC-2: Setup → Start → mindestens 2 Turns → Finish funktioniert vollständig
  im lokalen Testflow mit profi-Test-Account
- AC-3: `client_turn_id` wird per `crypto.randomUUID()` generiert (kein manuelles Random)
- AC-4: Rundenzähler stimmt mit Backend-Response (`turn_count`/`max_turns`) überein
- AC-5: `hidden_opponent_minimum` und `hidden_opponent_target` sind NUR in Phase 3
  sichtbar, niemals in Phase 1 oder 2
- AC-6: `/app/opponent` in `TOOL_ROUTES` in BottomTabBar.tsx eingetragen
- AC-7: TypeCheck negotiation-buddy: `npx tsc --noEmit` 0 Fehler

---

## Open Decisions

- Ob `final_offer` aus dem letzten Nutzer-Turn automatisch befüllt wird,
  oder manuell eingegeben werden muss (Implementierungsdetail)
