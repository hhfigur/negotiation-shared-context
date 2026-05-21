# BUG-20260521-session-save-retry-loop

**Erstellt:** 2026-05-21
**Status:** OPEN
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
_Wird durch Template 1-DEV befüllt._

## Implement
_Wird durch Template 2-DEV befüllt._

## Abschluss
_Wird durch /close-task befüllt._
