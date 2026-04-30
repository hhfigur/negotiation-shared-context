# NC-TELEMETRY Follow-ups

Registriert: 2026-04-30
Quelle: Code-Quality-Review NC-TELEMETRY Teil B (5b66bfc)

---

## FU-01: useRef-Guard in Tool-Page-Effects

**Kontext:** Bei Migration auf Backend-Calls (fetch in useEffect) kann
React Strict-Mode doppelte Mounts triggern — `useRef`-Guard nötig.
Aktuell kein Problem: `console.log` ist ephemer, Strict-Mode-Double-Fire
verfälscht keine produktiven Metriken.

**Trigger:** Wenn NC-TELEMETRY-C auf Backend-Events (fetch/HTTP) migriert.

**Umsetzung:** In allen 5 Tool-Pages `useEffect` mit `useRef`-Guard wrappen:
```typescript
const loggedRef = useRef(false);
useEffect(() => {
  if (loggedRef.current) return;
  loggedRef.current = true;
  logTelemetry({ event: "tool_opened", tool_name: "..." });
}, []);
```

**Priorität:** Low — kein Defekt in aktueller console.log-Implementierung.

---

## FU-02: TeamDashboard tool_opened

**Kontext:** `TeamDashboard.tsx` hat kein `tool_opened`-Event.
Alle anderen analytischen Tools (ZOPA, WhatIf, Strategy, Canvas, Debrief) sind abgedeckt.

**Entscheidung nötig:** Ist TeamDashboard ein "Tool" im Telemetrie-Sinne?
- Wenn ja: `logTelemetry({ event: "tool_opened", tool_name: "team_dashboard" })` ergänzen
- Wenn nein: Kein Action nötig

**Trigger:** NC-TELEMETRY-C Scope-Definition.

**Priorität:** Low — kein Defekt.
