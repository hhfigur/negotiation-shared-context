# BUG-20260619-canvas-fetch-aborted

**Erstellt:** 2026-06-19
**Status:** OPEN
**Risiko:** P2
**TARGET REPO:** negotiation-buddy
**Layer:** Frontend (useSessionManager hook)
**Bug-Typ:** UI-Bug
**Betroffene Tiers:** unbekannt
**ADR-Constraints:** keine erkennbar

## Symptom

Beim Öffnen von Canvas (Sidebar-Navigation) und anschließender Rückkehr in den Chat erscheint ein roter Fehler-Toast: "Fetch is aborted". Das sollte nicht passieren — Navigation zwischen Tools soll keine Fehlertoasts erzeugen.

## Ort

- `negotiation-buddy/src/hooks/useSessionManager.ts` — Zeile 138 (createSession / AbortController)
- `negotiation-buddy/src/components/SessionSidebar.tsx` — Zeile 107:33 und 149:52 (DOM-Nesting-Warning, separates Problem)

## Reproduktion

Nicht konsistent reproduzierbar. Bisher aufgetreten bei:
1. Chat führen (vollständiger Flow inkl. Datenextraktion — "Daten vollständig — Tools verfügbar" Badge aktiv)
2. Canvas (Direkteingabe) aus der Sidebar öffnen
3. Zurück in den Chat navigieren
4. Fehler-Toast erscheint: "Fetch is aborted"

Erneuter Aufruf von Canvas reproduziert den Fehler nicht zuverlässig. Wahrscheinlich Race Condition.

## Logs / Fehlermeldungen

**Console-Error:**
```
Failed to create session: AbortError: Fetch is aborted
  (anonyme Funktion) — useSessionManager.ts:138
```

**Console-Warning (separat, kein Zusammenhang mit Abort-Error):**
```
Warning: validateDOMNesting(...): <button> cannot appear as a descendant of <button>.
  NavRow @ SessionSidebar.tsx:107:33
  SessionSidebar @ SessionSidebar.tsx:149:52
```

## Verdacht

Der AbortController aus dem BUG-20260521 Regression-3-Fix (loadSessions/createSession mit 6s-Timeout) wird beim Canvas-Navigations-Zyklus getriggert und bricht einen in-flight `createSession`-Fetch ab. Mögliche Ursachen:

- Canvas-Navigation verursacht unmount/remount von Index.tsx oder useSessionManager
- Der beim Remount neu erstellte AbortController ruft `.abort()` auf den vorherigen Call
- `createSession` (nicht `loadSessions`) ist betroffen — Zeile 138 ist im createSession-Pfad

Nebenrisiko: Wenn Session-Create abgebrochen wird, könnte die Konversation nicht persistiert werden ("Sitzung konnte nicht gespeichert werden" — bekanntes separates Problem).

## Plan

_Wird durch Template 1-DEV befüllt._

## Implement

_Wird durch Template 2-DEV befüllt._

## Abschluss

_Wird durch /close-task befüllt._
