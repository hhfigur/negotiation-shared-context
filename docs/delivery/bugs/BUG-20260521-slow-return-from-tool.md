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

**Regression 3 — 2026-06-08 — App friert komplett ein (15–60s)**
Ursache: Supabase PostgREST killt `loadSessions`-Queries nach 30s Timeout.
Supabase JS Client retried automatisch → zweite 30s-Hang. Gleichzeitig:
React StrictMode (Dev) und rapid dep-changes triggern 2 simultane `loadSessions`-Calls,
beide hängen je 30s. Kein AbortController → kein vorzeitiger Abbruch → UI eingefroren.
PostgREST Log: "Thread killed by timeout manager" in 30s-Abstand (observed).

**Fix 3:** `dee7096` (negotiation-buddy) — 2026-06-08
AbortController mit 6s Timeout + Concurrent-Call-Guard in `loadSessions`.
Vorherigen in-flight Call abbrechen wenn neuer startet. Auto-abort nach 6s.
UI zeigt Cache sofort (aus Fix 2) — DB-Query bricht nach 6s ab statt 30s.
PostgREST sieht keine hängenden Threads mehr. tsc --noEmit clean ✓

## Abschluss

**Status:** DONE
Commits: `5436ad5` + `22414cd` + `dee7096` (negotiation-buddy)
Verified: tsc --noEmit clean ✓ | alle drei Fixes deployed via Render.com auto-deploy

---

## Infrastruktur-Grundursache — 2026-06-08

Nach den drei Frontend-Regressionsfixes blieb die Verzögerung in Produktion
bestehen (~15s, App eingefroren). MCP-Diagnose (nach Korrektur des falschen
`project_ref` und Re-Auth) ergab die eigentliche Grundursache:

**Fehlender Index:** `negotiation_sessions` hatte keinen Index auf
`(user_id, status, updated_at)`. Jede `loadSessions`-Query führte einen
Sequential Scan mit Per-Row-RLS-Auswertung durch — PostgREST killt Threads
nach 30s ("Thread killed by timeout manager"), der Supabase JS Client
retried automatisch → zweite 30s-Hänger (erklärt die exakt 30s auseinander
liegenden Fehlerpaare in den Logs).

**Tabellengröße:** `negotiation_sessions` hatte zum Diagnosezeitpunkt
1.130 Zeilen — **1.126 davon für einen einzigen User** (hhfigur@gmx.net,
das eigene Test-Konto). Ohne Index degradiert die Performance mit
wachsender Tabellengröße — das erklärt, warum der "gefixte" Bug nach
einigen Wochen zurückkam (Tabelle wuchs über die Schwelle, ab der
Sequential Scans den 30s-Timeout überschreiten).

**Migration:** `20260608120000_add_negotiation_sessions_index.sql`
```sql
CREATE INDEX IF NOT EXISTS idx_negotiation_sessions_user_status_updated
  ON public.negotiation_sessions (user_id, status, updated_at DESC);
```
Verifiziert via `EXPLAIN ANALYZE`: Query-Zeit für den betroffenen User sank
von Sequential-Scan-Timeout auf **5,2ms** (Index Scan, 1.126 Zeilen).

Commit: migration in `negotiation-buddy` (in `7686703` enthalten),
`supabase db push` gegen Projekt `gpllrgkuozytyrmpfwbb` ausgeführt.

---

## Folge-Bug entdeckt — BUG-20260608-empty-session-accumulation

Bei der Analyse der 1.126 Sessions des Test-Accounts: **1.115 davon waren
leere Platzhalter mit Titel "Neue Verhandlung"** (1.112 ganz ohne
Nachrichten), **985 davon an einem einzigen Tag (2026-06-03, 15:27–17:49 Uhr)**
erstellt — in Bursts von 5–10 innerhalb von Sekunden, mit Pausen von
20–75 Minuten dazwischen (~1 Session alle 9s im Schnitt über 2,5h).

**Root Cause:** `createSession` wird beim ersten Senden einer Nachricht
aufgerufen — bevor irgendeine Antwort vorliegt. Während des UI-Freezes
(siehe oben) wirkten Sende-Versuche wie "nichts passiert" → User versuchte
es erneut (ggf. über "Neue Verhandlung"-Button, der `sessionCreatedForConvo`
zurücksetzt) → jeder Versuch erzeugte eine neue leere DB-Zeile → Tabelle
wuchs → Queries wurden langsamer → noch mehr Retry-Versuche. Ein
sich selbst verstärkender Teufelskreis.

**Fix (2026-06-08):** `POST /sessions` in `negotiationcoach-backend` —
Reuse-Logik: kürzlich erstellte (≤10 Min) leere Session wird wiederverwendet
statt eine neue Zeile anzulegen; zusätzlich 3s-Cooldown als Race-Condition-
Backstop gegen parallele Retry-Requests.
Commit: `d3edf36` (negotiationcoach-backend).

**Cleanup durchgeführt:** 1.112 leere Sessions gelöscht, 5 älteste reale
Sessions archiviert (Test-Account von 1.126 auf 9 aktive Sessions reduziert
— unter dem neuen `SESSION_LIMIT = 10`).
