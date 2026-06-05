# BUG-20260521-slow-return-from-tool

**Erstellt:** 2026-05-21
**Status:** DONE
**Risiko:** P2
**TARGET REPO:** negotiation-buddy
**Layer:** Layer 0 — Frontend State / Performance
**Bug-Typ:** UI-Bug (Memory / Re-render)
**Betroffene Tiers:** Alle
**ADR-Constraints:** ADR-001 (Backend kanonisch — kein direkter Supabase-Call im Frontend)

## Symptom
Nach dem Aufruf eines Tools (z. B. ZOPA-Rechner, Marktdaten) und der Rückkehr in den Chat reagiert die App ungewöhnlich langsam (mehrere Sekunden). Deutet auf ein Memory- oder State-Management-Problem hin.

## Ort
- `src/pages/Index.tsx` — Remount nach Route-Wechsel
- `src/contexts/AnalysisContext.tsx` — shared State, re-rendert bei Rückkehr
- `src/hooks/useSessionManager.ts` — mögliche parallele API-Calls beim Remount

## Reproduktion
1. Chat-Session starten, einige Nachrichten senden
2. Zu ZOPA-Rechner oder Marktdaten navigieren
3. Über "← Zurück" in den Chat zurückkehren
4. Beobachten: App reagiert für mehrere Sekunden nicht oder sehr langsam

## Logs / Fehlermeldungen
- R-002 dokumentiert mehrfache isLoading-State-Instanzen in verschiedenen Komponenten
- Safari hat in dieser Session einen zwangsweisen Page-Reload wegen Memory-Druck ausgelöst
- analyze-progress wird bei jedem AI-Response getriggert (vor Throttling-Fix jede Antwort, jetzt jede 3.)

## Verdacht
- AnalysisContext oder useSessionManager hält großen State und re-rendert beim Route-Wechsel komplett (Inferred)
- Mehrfache parallele API-Calls werden beim Remount der Chat-Komponente ausgelöst (Inferred)
- Möglicher Memory-Leak durch nicht gecleante Subscriptions / Event-Listener beim Unmount (Inferred)

## Diagnose-Fragen (vor Fix zu beantworten)
1. Wie viele API-Calls werden beim Remount von ChatInterface ausgelöst? (Browser Network Tab — Observed/Missing)
2. Gibt es useEffect-Hooks ohne Cleanup-Return in ChatInterface oder useSessionManager? (Observed/Missing)
3. Wird AnalysisContext beim Navigation-Wechsel neu initialisiert? (Inferred — verifizieren)
4. Klassifiziere jeden Befund als: Observed / Inferred / Missing

## Plan
Diagnosis Report: `shared-context/docs/delivery/BUG-20260521-batna-lost-after-nav-diagnosis-report.md`
Root cause: 14 useEffects in Index.tsx ohne Cleanup-Return. Effect Z. 318-398 startet
2 API-Calls ohne AbortController → race conditions + stale state updates nach Navigation.

## Implement
`src/pages/Index.tsx` — AbortController zu Effect Z. 318-398:
- `controller = new AbortController()` nach early-return guards
- `signal: controller.signal` für beide fetch-Calls
- AbortError-Guard in beiden catch-Blöcken
- `return () => controller.abort()` als Cleanup

## Abschluss

**Status:** DONE
Commit: `81e65d9` (negotiation-buddy) — 2026-05-21 (original fix)
Verified: tsc --noEmit clean ✓ | Spec-Review PASS_WITH_NOTES | Code-Quality APPROVED_WITH_DEBT
Debt-1: `finally` fires `setIsAnalyzingProgress(false)` even on abort (benign)
Debt-2: `extractedInputs` stale closure in dep array (pre-existing, low severity)
Docs: `BUG-20260521-batna-lost-after-nav-diagnosis-report.md`

## Regression — 2026-06-04

**Ursache:** `d1485f7` (perf: auto-restore last active session) enthielt einen Effect-Ordering-Bug.
Effect 1 (`setLastActiveSessionId`) und Effect 2 (auto-restore) feuerten im selben Render-Zyklus.
Effect 1 (zuerst deklariert) überschrieb `_lastActiveSessionId` auf `null`, bevor Effect 2 sie lesen konnte.
Auto-Restore feuerte nie → User musste manuell klicken → `handleSelectSession` → `summarize-session` → 3–10s Freeze.

**Fix 1:** `5436ad5` (negotiation-buddy) — 2026-06-04
`lastActiveIdAtMount = useRef(_lastActiveSessionId)` bei Component-Init (vor allen Effects).
Effect 2 liest `lastActiveIdAtMount.current` statt `_lastActiveSessionId`.

**Regression 2 — 2026-06-05 — verbleibender Delay (~550ms)**
Ursache: `loadSessions` servierte `_sessionCache` erst NACH dem Supabase-DB-Query.
- `hasFreshCache` Bedingung war mit `>= 0` immer true → Spinner nie gesetzt
- ABER `setSessions` wurde trotzdem erst nach dem DB-Round-Trip (200–500ms) aufgerufen
- `useState`-Initializer für sessions konnte den Cache nie nutzen (auth async → `currentUserId = null` bei Mount)
- Auto-Restore wartete auf `sessions.length > 0`, das erst nach dem DB-Query kam

**Fix 2:** `22414cd` (negotiation-buddy) — 2026-06-05
`loadSessions`: `setSessions(_sessionCache)` + `setIsLoadingSessions(false)` sofort wenn `hasFreshCache`.
DB-Query läuft als stiller Background-Refresh. Delay: ~50ms statt ~550ms.
tsc --noEmit clean ✓

## Abschluss

**Status:** DONE
Commits: `5436ad5` + `22414cd` (negotiation-buddy)
Verified: tsc --noEmit clean ✓ | beide Fixes deployed via Render.com auto-deploy
