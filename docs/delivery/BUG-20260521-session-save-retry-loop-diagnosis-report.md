# Diagnosis Report — BUG-20260521-session-save-retry-loop

**Datum:** 2026-05-21
**Bug-ID:** BUG-20260521-session-save-retry-loop
**Status:** OPEN — Root Cause nicht vollständig bestätigt (Index.tsx nicht gelesen)
**Klassifizierung:** Data-Bug / Performance / Caller-Loop
**Untersucht:** useSessionManager.ts, AnalysisContext.tsx, frontend-backend.md, refactor-backlog.md (RFB-004, RFB-014, RFB-015)
**Nicht untersucht:** Index.tsx (primärer Verdächtiger), useChat.ts

---

## 1. Bug Summary

Beim Start einer neuen Verhandlungssession erscheint der Toast "Sitzung konnte nicht gespeichert
werden" wiederholt und kontinuierlich — auch ohne weitere Nutzereingabe. Die App verursacht
CPU/Memory-Erschöpfung bis zum System-Freeze.

Beide ursprünglich postulierten Hypothesen (Retry-Loop in useSessionManager, AnalysisContext-
Write-Loop) sind durch Code-Evidenz **ausgeschlossen**. Der tatsächliche Loop-Mechanismus
liegt mit hoher Wahrscheinlichkeit in **Index.tsx** — dem primären Caller von createSession
und saveMessage.

---

## 2. Observed — direkt im Code verifiziert

### useSessionManager.ts

**O-001:** `createSession` hat keinen Retry-Mechanismus.
Einziger Fehlerweg: `catch(err) → toast.error() → console.error() → return null`.
Kein `setTimeout`, kein `setInterval`, kein Retry-Loop.
```
Datei: src/hooks/useSessionManager.ts:59–89
```

**O-002:** `saveMessage` hat keinen Retry-Mechanismus.
`catch(err) → switch(err.status) → toast.error() → console.error()`.
Kein Retry. Nach dem try/catch: `setSessions(prev => prev.map(...))` — **immer ausgeführt**,
auch nach Fehler. Aktualisiert nur `updated_at`-Feld lokal.
```
Datei: src/hooks/useSessionManager.ts:92–128
```

**O-003:** Kein `AbortController` in `createSession` oder `saveMessage`.
Kein `cleanup` in useEffect-Return. Laufende Fetch-Promises werden bei Unmount nicht gecancelt.
```
Datei: src/hooks/useSessionManager.ts (gesamte Datei — kein Match auf AbortController/signal)
```

**O-004:** useEffect für loadSessions:
```typescript
useEffect(() => {
  loadSessions();
}, [personaType, authSession, loadSessions]);
```
Feuert nur bei Auth-/Persona-Änderung. Kein createSession-Aufruf darin.
```
Datei: src/hooks/useSessionManager.ts:52–56
```

**O-005:** RFB-004 Phase B vollständig abgeschlossen.
`createSession` → `createSessionApi` (Railway), `saveMessage` → `saveMessageApi` (Railway),
`archiveSession` → `updateSessionApi` (Railway). Direkter Supabase-Write in keiner Write-Operation.
Verbleibende Supabase-Calls: `loadSessions` + `loadSessionMessages` (read-only, korrekt).
```
Datei: src/hooks/useSessionManager.ts:2,4,64,96,150
Backlog: refactor-backlog.md — RFB-004 "Overall Status: DONE — Phases A/B/C complete."
```

**O-006:** `saveMessage` ruft immer `setSessions(prev => prev.map(...))` auf — auch nach
erfolgreicher Verarbeitung und nach Fehler. Dies triggert einen React-State-Update in
useSessionManager nach jedem saveMessage-Aufruf, unabhängig vom Ergebnis.
```
Datei: src/hooks/useSessionManager.ts:123–127
```

### AnalysisContext.tsx

**O-007:** `saveToStorage` wird bei **jedem** Session-State-Change aufgerufen:
```typescript
useEffect(() => {
  saveToStorage(session);
}, [session]);
```
Kein Debounce, kein Throttle. `saveToStorage` ist **synchrones** `localStorage.setItem` —
kein Netzwerk-Call, kann keine Resource-Exhaustion durch Netzwerk verursachen.
```
Datei: src/contexts/AnalysisContext.tsx:117–119
```

**O-008:** `saveToStorage` schreibt `isLoading`-Flag explizit heraus (`const { isLoading, ...persistable } = state`).
Kein Error-State existiert in AnalysisContext. Fehler aus useSessionManager werden NICHT
in AnalysisContext geschrieben — kein Cycle möglich.
```
Datei: src/contexts/AnalysisContext.tsx:100–110
```

**O-009:** TTL und Versionierung sind implementiert (`STORAGE_TTL = 604_800_000` = 7 Tage,
`STORAGE_VERSION = 2`). RFB-015 ist DONE.
```
Datei: src/contexts/AnalysisContext.tsx:5–6
```

**O-010:** Error-Codes aus useSessionManager.ts:
- "Sitzung konnte nicht gespeichert werden" erscheint in: createSession (Z.82/84),
  saveMessage (Z.104/111/114/117), archiveSession (Z.157/159).
- Drei separate Code-Pfade erzeugen identischen Toast-Text.

---

## 3. Inferred — aus Kontext erschlossen

**I-001:** Index.tsx ist die primäre Call-Site für `createSession` und `saveMessage`.
AGENTS.md: "Index.tsx god component (~37KB)" — F-011.
Ohne Index.tsx zu lesen: Es ist **highly probable** dass useEffects in Index.tsx
createSession oder saveMessage bei State-Änderungen aufrufen.

**I-002:** Wenn ein useEffect in Index.tsx createSession aufruft mit einer Bedingung
`messages.length > 0 && !activeSessionId`, und createSession bei Fehler `null` zurückgibt
(activeSessionId bleibt null), und die messages sich ändern (z.B. durch AnalysisContext-
Restore nach Navigation), dann wird createSession bei jeder weiteren Nachricht erneut
aufgerufen — bis zu N-mal je nach Message-Count. Kein klassischer Loop, aber ein
**Caller-seitiger Fan-Out**.

**I-003:** saveMessage wird für jede Chat-Nachricht aufgerufen — einschließlich SSE-Chunks.
Wenn Railway während einer Streaming-Session nicht erreichbar ist (5xx, Timeout), werden
alle Chunks mit toast.error quittiert. Je länger die Streaming-Antwort, desto mehr Toasts.

**I-004:** Keine AbortController-Cleanup-Patterns in useSessionManager → bei Unmount
(z.B. Navigation) bleiben laufende POST-Requests aktiv. Bei wiederholten Mount/Unmount-Zyklen
(L-005-Muster) akkumulieren sich offene Promises.

**I-005:** RFB-004-C bleibt OPEN (non-atomic message count constraint). Nicht ursächlich
für den beschriebenen Bug, aber relevant bei Race-Conditions.

**I-006:** `saveMessage`s `setSessions()` am Ende (O-006) triggert bei jedem Aufruf einen
State-Update in useSessionManager, auch nach Fehler. Falls ein übergeordneter Component
auf `sessions`-State re-rendert und dabei erneut saveMessage aufruft, ist ein
Render-Loop möglich — ohne weitere Code-Evidenz nicht bestätigbar.

---

## 4. Missing — fehlende Information für vollständige Diagnose

**M-001 [kritisch]:** `Index.tsx` — nicht gelesen. Alle createSession/saveMessage-Call-Sites,
deren useEffect-Dependencies und Bedingungslogik sind unbekannt.
Ohne Index.tsx: Root Cause kann nicht final bestätigt werden.

**M-002 [kritisch]:** `useChat.ts` — nicht gelesen. Unklar ob useChat.ts direkt
saveMessage aufruft oder ob Index.tsx die Call-Site ist. SSE-Chunk-Handling unbekannt.

**M-003:** Netzwerk-Logs / Railway-Logs aus dem Fehler-Zeitraum — fehlen.
Unklar ob POST /api/sessions oder POST /api/sessions/:id/messages fehlschlägt.
Status-Code (5xx, 401, Network Error) unbekannt.

**M-004:** Aufruffrequenz von saveMessage bei typischer Streaming-Session (Chunks-Zahl).
Unklar wie viele saveMessage-Calls ein einziger Chat-Response erzeugt.

**M-005:** Ob `activeSessionId` nach createSession-Fehler null bleibt und ob
Index.tsx dies als Trigger für erneuten createSession-Call verwendet.

---

## 5. Hypothese A Assessment — Retry-Loop in useSessionManager

**AUSGESCHLOSSEN** (Code-Evidenz, Observed)

`createSession` und `saveMessage` haben keinen eingebauten Retry-Mechanismus.
Single try/catch, `return null` nach Fehler. Kein `setTimeout`, kein rekursiver Aufruf,
kein Loop-Konstrukt. Der Toast kann aus useSessionManager heraus maximal **einmal
pro Aufruf** erscheinen.

Ursprüngliche RFB-014-Beobachtung (2 Retries mit 1500ms Delay) ist veraltet —
der finale Code nach RFB-004 Phase B enthält keinen Retry.

---

## 6. Hypothese B Assessment — AnalysisContext-Write-Loop

**AUSGESCHLOSSEN** (Code-Evidenz, Observed)

`saveToStorage` in AnalysisContext ist synchrones `localStorage.setItem` — kein Netzwerk-Call.
Error-State aus useSessionManager wird NICHT in AnalysisContext geschrieben.
Kein Cycle-Pfad existiert: `localStorage.setItem` triggert keine React-State-Änderung,
die einen weiteren Save-Versuch auslösen könnte.

---

## 7. Primäre Root Cause Hypothesis (Proposed)

**Hypothese C — Caller-seitiger Fan-Out in Index.tsx**

Der Loop entsteht NICHT in useSessionManager oder AnalysisContext, sondern im Caller.

**Wahrscheinlichste Mechanik (Inferred — M-001 nicht gelöst):**

```
Index.tsx useEffect:
  Bedingung: messages.length > 0 && !activeSessionId
  Aktion: createSession(title)
  → createSession schlägt fehl → return null
  → activeSessionId bleibt null
  → nächste Nachricht kommt (SSE-Stream) → AnalysisContext.addMessage()
  → session-State ändert sich → Index.tsx re-rendert
  → useEffect feuert erneut (messages.length > 0 && !activeSessionId noch true)
  → createSession erneut aufgerufen
  → Toast erneut
  → Repeat für jeden weiteren SSE-Chunk
```

**Resource-Exhaustion-Pfad:**
Jeder fehlgeschlagene `createSessionApi`-Call hält einen offenen Fetch-Promise
(kein AbortController). Bei langer Railway-Response-Zeit (Timeout 30s+) akkumulieren
sich N offene Promises — O(N) Memory-Usage bis Systemgrenze.

**Nebenursache — saveMessage Fan-Out:**
Wenn saveMessage für jeden SSE-Chunk aufgerufen wird und Railway nicht erreichbar ist,
entsteht pro Chunk ein Toast + ein offener Fetch-Promise. Kein Loop, aber
O(Chunk-Anzahl) parallele hängende Requests.

---

## 8. RFB-004 Phase B Status

**DONE** — vollständig abgeschlossen.

- Phase A (Railway-Endpoints): DONE `2415f72` 2026-04-08
- Phase B (useSessionManager-Migration): DONE (out-of-band)
- Phase C-Backend (Token + Error Handling): DONE 2026-04-10
- Phase C-Lovable (TeamDashboard): DONE 2026-04-10

Aktueller Write-Path:
- createSession → `POST /api/sessions` (Railway) ✓
- saveMessage → `POST /api/sessions/:id/messages` (Railway) ✓
- archiveSession → `PATCH /api/sessions/:id` (Railway) ✓
- loadSessions → `supabase.from('negotiation_sessions').select()` (read-only, korrekt)
- loadSessionMessages → `supabase.from('session_messages').select()` (read-only, korrekt)

Offen: RFB-004-C (non-atomic message count constraint) — nicht ursächlich für diesen Bug.

---

## 9. Files Involved

| Datei | Repo | Rolle | Status |
|---|---|---|---|
| `src/hooks/useSessionManager.ts` | negotiation-buddy | Write-Path (Railway API) | Untersucht — kein Loop |
| `src/contexts/AnalysisContext.tsx` | negotiation-buddy | localStorage-Write | Untersucht — kein Cycle |
| `src/pages/Index.tsx` | negotiation-buddy | **primärer Verdächtiger (M-001)** | NICHT gelesen |
| `src/hooks/useChat.ts` | negotiation-buddy | SSE-Streaming, ggf. saveMessage-Caller | NICHT gelesen |
| `src/lib/apiClient.ts` | negotiation-buddy | Railway-API-Client, Fetch-Timeout | Nicht gelesen |
| `src/api/sessionRoutes.ts` | negotiationcoach-backend | POST /api/sessions Endpunkt | Nicht gelesen |

---

## 10. Systemressourcen-Risiko Assessment

**Risiko: HOCH**

| Risiko-Pfad | Mechanismus | Schwere |
|---|---|---|
| Offene Fetch-Promises ohne AbortController | Kein Cleanup bei Unmount (O-003) | Hoch — Memory-Leak |
| Parallele hängende Railway-Requests | N Calls × Timeout-Dauer ohne Cancel | Hoch — CPU/Memory |
| Toast-Spam ohne Rate-Limit | N Toasts bei N fehlgeschlagenen Calls | Mittel — UX, nicht System-Killer |
| localStorage-Overwrite-Frequenz | O(Chunk-Anzahl) Writes bei SSE | Niedrig — synchron, schnell |

**Systemressourcen-Kill-Pfad (Inferred):**
Wenn Index.tsx createSession pro SSE-Chunk aufruft (~50–100 Chunks/Antwort),
und Railway hängt mit 30s Timeout, entstehen gleichzeitig 50–100 offene Fetch-Promises
à 30s Hold. Das erklärt CPU-Erschöpfung durch Thread/Event-Loop-Blockierung.

---

## 11. ADR / Contract Implications

**ADR-001:** Railway ist kanonischer Session-Write-Owner. Write-Path korrekt (O-005).
Kein ADR-Verstoß in useSessionManager.

**ADR-002:** Data Ownership korrekt — keine Frontend-Supabase-Writes für Sessions.

**Contract:** `POST /api/sessions` → `500 SESSION_CREATE_ERROR` bei Supabase-Insert-Failure.
Falls Railway selbst nicht erreichbar ist (Network Error), kommt kein Error-Code —
`fetch()` wirft einen Network-Exception. useSessionManager caught dies korrekt (O-001).
Kein Contract-Verstoß — aber: **kein Retry-Circuit-Breaker im Contract definiert**.

**Empfehlung:** Contract-Dokumentation um "Client-side retry policy: none" ergänzen.

---

## 12. Recommended Fix Scope (Proposed — nicht implementieren)

**Fix 1 — AbortController in createSession + saveMessage [P1]:**
Beim Unmount der Komponente (useEffect cleanup) laufende Requests abbrechen.
Verhindert Memory-Leak bei Navigation während laufender Saves.

**Fix 2 — Index.tsx useEffect-Bedingung prüfen [P1 — M-001 muss zuerst gelöst werden]:**
Wenn createSession scheitert (returns null), darf der useEffect **nicht** bei jeder
weiteren Nachricht erneut createSession aufrufen. Entweder:
- Flag `sessionCreateFailed` setzen, useEffect blockiert
- Oder: createSession nur einmal beim Session-Start aufrufen, nicht reaktiv

**Fix 3 — saveMessage: einmalig pro Nachrichten-Abschluss, nicht pro Chunk [P1 — nach M-002]:**
Wenn useChat.ts saveMessage pro SSE-Chunk aufruft, muss das auf "letzten Chunk" / "done"
reduziert werden.

**Fix 4 — Toast-Rate-Limiting / Deduplication [P2]:**
Identische Toast-Texte innerhalb von 5s deduplizieren. Symptom-Behandlung, kein Root-Cause-Fix.

**Nicht empfohlen:**
- Retry-Loop mit Backoff in useSessionManager — kein Retry ohne Circuit-Breaker und
  User-Feedback ist sicherer als blindes Wiederholen bei 5xx.

---

## 13. Acceptance Criteria — Bewertung

| AC | Kriterium | Bewertbar? | Anmerkung |
|---|---|---|---|
| AC-1 | `npx tsc --noEmit` clean | ✓ prüfbar | Baseline bereits 0 Fehler |
| AC-2 | `curl POST /api/sessions` → Session-Objekt | ✓ prüfbar | Railway muss erreichbar sein |
| AC-3 | Layer-1-Tests grün | ⚠ eingeschränkt | Testcoverage minimal (nur boilerplate, AGENTS.md) |
| AC-4 | Output-Nachweis im Report | ✓ prüfbar | curl-Output oder Netzwerk-Tab |

**Ergänzende AC für diesen Bug:**
- AC-5: Toast "Sitzung konnte nicht gespeichert werden" erscheint maximal 1× pro User-Aktion (nicht pro SSE-Chunk)
- AC-6: Bei Railway-Fehler während SSE-Streaming: keine akkumulierenden offenen Fetch-Promises (Memory-Profiler)
- AC-7: Bei createSession-Fehler: useEffect in Index.tsx ruft createSession nicht erneut auf
  bis zur nächsten expliziten User-Aktion

---

## Nächster Schritt

**M-001 zuerst auflösen:** `src/pages/Index.tsx` lesen — gezielt:
1. Alle useEffect-Blöcke, die `createSession` oder `saveMessage` aufrufen
2. Dependencies dieser useEffects
3. Bedingungslogik (check auf `activeSessionId`, `messages.length`)

Erst danach kann Hypothese C bestätigt oder falsifiziert werden.
