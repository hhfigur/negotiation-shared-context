# BUG-20260521-session-save-retry-loop

**Erstellt:** 2026-05-21
**Status:** DONE
**Risiko:** P1
**TARGET REPO:** negotiation-buddy (primary), negotiationcoach-backend (secondary)
**Layer:** Layer 0 (Session Persistence / Data Foundation)
**Bug-Typ:** Data-Bug
**Betroffene Tiers:** Alle
**ADR-Constraints:** ADR-001 (Railway kanonisch für Session-Writes), ADR-002 (Data Ownership)

## Symptom

Bei einer neuen Verhandlungssession erscheint der Toast "Sitzung konnte nicht gespeichert werden"
wiederholt und kontinuierlich — auch ohne weitere Nutzereingabe. Die App belastet die
Systemressourcen so stark, dass der Computer zum Stehen kommt (CPU/Memory-Erschöpfung).

**Soll-Verhalten:** Session einmalig speichern. Bei Fehler: Toast einmalig anzeigen, kein
weiterer automatischer Retry-Loop ohne User-Aktion.

## Ort

- `negotiation-buddy/src/hooks/useSessionManager.ts` — Retry-Mechanismus bei POST /api/sessions
- `negotiation-buddy/src/context/AnalysisContext.tsx` — F-003 localStorage-Write auf State-Change
- API-Endpunkt: `POST /api/sessions` (Railway/Render Express Backend)
- Layer 0: Session Persistence

## Reproduktion

Neue Verhandlungssession starten → POST /api/sessions schlägt fehl (5xx oder Supabase insert error)
→ Toast erscheint kontinuierlich, App friert ein.

Exakte Reproduktionsschritte noch nicht verifiziert (Inferred). Mögliche Voraussetzung:
dauerhafter Backend-Fehler (z. B. DB-Verbindungsfehler) oder RFB-004-Phase-B-Zustand
(useSessionManager noch direkter Supabase-Write statt Railway-Weiterleitung).

## Logs / Fehlermeldungen

- Toast: `"Sitzung konnte nicht gespeichert werden"` (wiederholt)
- Error-Code: `SESSION_CREATE_ERROR` — dokumentiert in `docs/contracts/frontend-backend.md`
  als Response bei POST /api/sessions Supabase insert failure

## Verdacht

**Hypothese A — Retry-Loop ohne Abbruchbedingung (Inferred):**
`useSessionManager.ts` implementiert 2 Retries mit 1500ms Delay (RFB-014-Beobachtung).
Falls POST /api/sessions einen dauerhaften Fehler (5xx) zurückgibt und der Retry-Mechanismus
bei jedem Fehler erneut getriggert wird (z. B. durch useEffect ohne korrekte Cleanup-Logik),
entsteht ein Endlos-Loop. Jeder Retry-Cycle hält Ressourcen (Promises, Fetch-Instanzen)
ohne AbortController-Cleanup → Memory-Leak.

**Hypothese B — AnalysisContext-Write-Loop (Inferred):**
`AnalysisContext.tsx` serialisiert gesamten State bei jeder Änderung in localStorage (F-003).
Falls ein Session-Save-Fehler den State verändert, der wiederum einen erneuten Save triggert:
`Error → State-Update → localStorage-Write → Re-render → erneuter Save-Versuch` → Schreib-Loop.

**Offene Diagnose-Fragen:**
1. Ist `useSessionManager.ts` vollständig auf Railway migriert (RFB-004 Phase B) oder
   schreibt er noch direkt nach Supabase?
2. Hat der Retry-Mechanismus eine harte Abbruchbedingung nach N Versuchen?
3. Gibt es einen AbortController oder Cleanup in den Retry-Calls?
4. Welcher useEffect in AnalysisContext.tsx triggert localStorage-Writes — hat er
   eine Dependency-Array-Schranke die Loops verhindert?

**Verwandte Items:**
- RFB-014 (fire-and-forget Fix — war der Fix vollständig?)
- RFB-004 Phase B (useSessionManager Railway-Migration — Status klären)
- RFB-015 (localStorage TTL — noch offen)
- BUG-20260521-slow-return-from-tool (App-Freeze — möglicherweise gleiche Ursache)

## Plan

Root Cause via Diagnose-Report (commit `0fcffc8`):
- Hypothese A (Retry-Loop in useSessionManager): ausgeschlossen — kein Retry, single try/catch, return null
- Hypothese B (AnalysisContext-Write-Loop): ausgeschlossen — saveToStorage ist synchrones localStorage
- **Hypothese C (Caller-Fan-Out in Index.tsx): bestätigt**
  Ein useEffect ruft `createSession` bei jeder neuen Nachricht erneut auf, solange
  `activeSessionId === null`. Nach Fehler bleibt activeSessionId null → jeder SSE-Chunk
  triggert erneuten Call → N Toasts + N offene Fetch-Promises → Resource-Exhaustion.

Fix-Scope: nur `src/pages/Index.tsx`
- Guard-Flag `isCreatingSession: useRef<boolean>` — verhindert concurrent Creates
- Error-Flag `sessionCreateFailed: useRef<boolean>` — verhindert Retry nach Fehler
- AbortController `createSessionAbortRef` — Cleanup bei Unmount

## Implement

Commit: `967475d` (negotiation-buddy) — 2026-05-21
Datei: `src/pages/Index.tsx` — 30 Insertions, 1 Deletion

Implementierte Änderungen (Zeilen):
- Z.268: `const isCreatingSession = useRef<boolean>(false);`
- Z.269: `const sessionCreateFailed = useRef<boolean>(false);`
- Z.270: `const createSessionAbortRef = useRef<AbortController | null>(null);`
- Z.273–277: useEffect-Cleanup → `createSessionAbortRef.current?.abort()`
- Z.607: Guard `if (isCreatingSession.current || sessionCreateFailed.current) return;`
- Z.609: `isCreatingSession.current = true;` vor createSession-Call
- Z.614: `await createSession(title)`
- Z.615–617: `if (result === null) { sessionCreateFailed.current = true; }`
- Z.618–620: `finally { isCreatingSession.current = false; }`
- Z.293 (handleUseCaseStart) + Z.656 (handleNewSession): Reset `sessionCreateFailed.current = false`

Spec-Review: PASS_WITH_NOTES
Code-Quality-Review: APPROVED_WITH_DEBT

Debt dokumentiert (nicht blockierend):
- AbortController signal nicht an createSessionApi durchgereicht → abort() auf Unmount ist inert für HTTP-Cancellation
- Silent return bei sessionCreateFailed gibt keinen User-Feedback auf Retry-Versuche nach Fehler

## Abschluss

**Status:** DONE
Commit: `967475d` (negotiation-buddy) — 2026-05-21
Verified: `npx tsc --noEmit` exit 0 ✓ | Spec-Review: PASS_WITH_NOTES | Code-Quality: APPROVED_WITH_DEBT
API contract updated: no
DB delta: none
ADR created/amended: none
Docs updated: BUG-20260521-session-save-retry-loop-diagnosis-report.md (`0fcffc8`), BUG-20260521-session-save-retry-loop.md (this file)
