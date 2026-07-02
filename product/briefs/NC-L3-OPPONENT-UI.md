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
  oder manuell eingegeben werden muss → **ENTSCHIEDEN:** Auswertungs-Screen
  zeigt ein Zahlen-Input vorbelegt mit 0, Nutzer trägt das letzte Angebot ein.
  Kein NLP-Extraction aus dem Turn-Text (zu komplex, out of scope).

---

## Plan

**Erstellt:** 2026-07-02 — Frontend-Plan, TARGET REPO negotiation-buddy
**Status:** PLANNED — wartet auf GO

### 1. Reihenfolge

Typen → apiClient → OpponentSimulator.tsx → Routing (App.tsx + BottomTabBar + SessionSidebar + Landing)

### 2. Dateiliste (vollständige Pfade)

| Datei | Art | Änderung |
|---|---|---|
| `../negotiation-buddy/src/lib/types.ts` | erweitert | Additive Typen am Ende der Datei |
| `../negotiation-buddy/src/lib/apiClient.ts` | erweitert | 3 neue Funktionen am Ende |
| `../negotiation-buddy/src/pages/OpponentSimulator.tsx` | neu | Vollständige neue Komponente |
| `../negotiation-buddy/src/App.tsx` | erweitert | Import + Route unter `/app` |
| `../negotiation-buddy/src/components/BottomTabBar.tsx` | erweitert | Neuer Eintrag + TOOL_ROUTES |
| `../negotiation-buddy/src/components/SessionSidebar.tsx` | erweitert | Neuer Eintrag |
| `../negotiation-buddy/src/pages/Landing.tsx` | erweitert | Neuer Tool-Eintrag |

### 3. Typ-Erweiterungen (src/lib/types.ts)

Additiv am Ende der Datei, keine bestehenden Typen anfassen:

```typescript
// ─── NC-L3-OPPONENT: Opponent Simulation ─────────────────────────────────────

export type OpponentStyle = 'kooperativ' | 'hart' | 'manipulativ' | 'sachlich';
export type ScenarioDifficulty = 'einfach' | 'mittel' | 'schwer';

export interface StartOpponentSimulationBody {
  negotiation_type:       NegotiationType;
  opponent_style:         OpponentStyle;
  scenario_difficulty:    ScenarioDifficulty;
  own_target:             number;
  own_minimum:            number;
  opponent_estimated_max: number;
  opponent_estimated_min: number;
  negotiation_session_id?: string;
}

export interface StartOpponentSimulationResponse {
  simulation_session_id: string;
  status:                string;
  max_turns:             number;
  opening_message:       string;
}

export interface TurnOpponentSimulationResponse {
  assistant_message?: string;
  turn_count:         number;
  max_turns:          number;
  finished:           boolean;
  idempotent?:        boolean;
  reason?:            string;
}

export interface OpponentSimulationEvaluation {
  final_outcome:      number;
  own_zopa_min:       number;
  own_zopa_max:       number;
  nash_solution:      number;
  outcome_vs_nash:    number;
  outcome_percentile: number;
  tactic_assessment:  string;
}

export interface FinishOpponentSimulationResponse {
  evaluation:                  OpponentSimulationEvaluation;
  hidden_opponent_minimum:     number;
  hidden_opponent_target:      number;
}
```

### 4. API-Funktionen (src/lib/apiClient.ts)

Additiv am Ende der Datei, Pattern identisch zu bestehenden Funktionen
(`analyzeOnly`, `enrich` etc. — alle rufen `apiCall<T>` auf):

```typescript
export function startOpponentSimulation(
  body: StartOpponentSimulationBody,
  token: string,
) {
  return apiCall<StartOpponentSimulationResponse>('/opponent-simulation/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
}

export function sendOpponentTurn(
  simulationSessionId: string,
  body: { content: string; client_turn_id: string },
  token: string,
) {
  return apiCall<TurnOpponentSimulationResponse>(
    `/opponent-simulation/${simulationSessionId}/turn`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(body),
    },
  );
}

export function finishOpponentSimulation(
  simulationSessionId: string,
  body: { final_offer: number },
  token: string,
) {
  return apiCall<FinishOpponentSimulationResponse>(
    `/opponent-simulation/${simulationSessionId}/finish`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(body),
    },
  );
}
```

### 5. OpponentSimulator.tsx — Struktur

Drei Phasen via lokalen State `phase: 'setup' | 'playing' | 'evaluation'`.
Pattern von `WhatIfSimulator.tsx`: `useAnalysis()` für extractedInputs, `trackEvent`,
`useNavigate`, Supabase-Session für Token, `toast` für Fehler.

**Setup-Phase:**
- `negotiation_type`: Dropdown vorbelegt aus `extractedInputs?.negotiation_type ?? 'gehalt'`
- `opponent_style`: Dropdown (kooperativ/hart/manipulativ/sachlich)
- `scenario_difficulty`: Dropdown (einfach/mittel/schwer)
- `own_target`/`own_minimum`/`opponent_estimated_max`/`opponent_estimated_min`:
  aus `extractedInputs` vorbelegt, Inputs falls null
- Start-Button → `startOpponentSimulation(...)` → setzt `simSessionId` + `messages[0]`
  → Wechsel zu `'playing'`
- Wenn `subscription_tier !== 'profi'`: Upgrade-Hinweis statt Setup-Formular (AC-1)

**Playing-Phase:**
- Messages-Liste (alternierend user/assistant)
- Textarea + "Senden"-Button
- Beim Senden: `client_turn_id = crypto.randomUUID()` (AC-3)
- Turn-Counter "Runde {turn_count} von {max_turns}"
- Bei `finished: true` → direkt `phase = 'evaluation'` nach Bestätigung von
  `final_offer` (kleines Modal/Inline-Input)
- "Beenden"-Button → zeigt `final_offer`-Input → `finishOpponentSimulation(...)`
  → Wechsel zu `'evaluation'`

**Evaluation-Phase:**
- `evaluation.tactic_assessment` prominent
- `outcome_vs_nash` mit Vorzeichen (`+` = gut)
- `own_zopa_min`–`own_zopa_max` Balken
- Erst hier: `hidden_opponent_minimum` + `hidden_opponent_target` sichtbar (AC-5)
- "Neue Runde"-Button → `phase = 'setup'`, State leeren
- `trackEvent('tool_opened', { tool: 'opponent_simulator' })` beim Mount

### 6. Routing

**App.tsx:** Import + neue Child-Route:
```typescript
import OpponentSimulator from './pages/OpponentSimulator';
// unter <Route path="/app" ...>:
<Route path="opponent" element={<OpponentSimulator />} />
```

**BottomTabBar.tsx:**
- Neuer Eintrag: `{ marker: "06", label: "KI-Gegner", route: "/app/opponent", badge: "Profi" }`
- `/app/opponent` zu `TOOL_ROUTES` hinzufügen

**SessionSidebar.tsx:**
- Neuer Eintrag: `{ marker: "06", label: "KI-Gegner", route: "/app/opponent", badge: "Profi" }`

**Landing.tsx:**
- Neuer Eintrag in Tool-Liste mit `route: "/app/opponent"`

### 7. Side-Effect-Check

a) `grep -r '"/app/opponent"' src/` vor Commit — erwartet: genau in App.tsx,
   BottomTabBar.tsx, SessionSidebar.tsx, Landing.tsx, OpponentSimulator.tsx (useNavigate-Calls).
   Falls eine Datei fehlt → nachpflegen (Lesson BUG-20260630).

b) Neue apiClient-Funktionen sind additiv — kein bestehender Caller betroffen.
   `apiCall<T>` wird unverändert wiederverwendet, kein Eingriff.

c) Loop-Risiko in OpponentSimulator.tsx: kein `useContext`-Wert aus AnalysisContext
   als `useEffect`-Dep nutzen — nur stabile Werte (`extractedInputs` beim Init
   einmalig lesen, nicht als reaktive Dep). Pattern wie WhatIfSimulator.tsx.

d) Keine DB-Änderung.

e) API-Contract: `docs/contracts/frontend-backend.md` bereits aktuell — kein Update nötig.

### 8. Tests

- `npx tsc --noEmit` — 0 Fehler (Pflicht)
- Manueller Full-Flow lokal mit profi-Test-Account:
  Setup → Start (Eröffnungsnachricht erscheint) → 2+ Turns → Finish → Auswertung sichtbar
- Nicht-profi-Account: Upgrade-Hinweis statt Formular (AC-1)
- Tool in BottomTabBar sichtbar + Navigation zu `/app/opponent` funktioniert ohne 404

### 9. Rollback

Reine Frontend-Änderung, keine DB-Migration. Rollback:
- `src/pages/OpponentSimulator.tsx` löschen
- Route-Einträge in App.tsx, BottomTabBar.tsx, SessionSidebar.tsx, Landing.tsx entfernen
- apiClient.ts + types.ts — additive Abschnitte entfernen

### 10. Git-Commit

```
cd ../negotiation-buddy
git add src/lib/types.ts src/lib/apiClient.ts \
        src/pages/OpponentSimulator.tsx \
        src/App.tsx \
        src/components/BottomTabBar.tsx \
        src/components/SessionSidebar.tsx \
        src/pages/Landing.tsx
git commit -m "feat(layer3): OpponentSimulator UI — /app/opponent, 3 API-Funktionen, Routing (NC-L3-OPPONENT-UI)"
```
