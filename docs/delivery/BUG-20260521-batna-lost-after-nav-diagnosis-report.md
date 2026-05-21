# Diagnosis Report — BUG-20260521-batna-lost-after-nav

**Datum:** 2026-05-21  
**Bug-ID:** BUG-20260521-batna-lost-after-nav  
**Titel:** App langsam nach Tool-Navigation + BATNA nach Navigation verloren  
**Status:** DIAGNOSED — kein Code geändert  

> Note: Dieser Report deckt zwei verwandte Symptome ab — Verlangsamung (BUG-02) und
> BATNA-Verlust (BUG-04) haben dieselbe Wurzel: unkontrolliertes Effect-Firing beim
> Index.tsx-Remount.

---

## 1. Bug Summary

Nach Navigation `/app → /zopa → /app` wird `Index.tsx` vollständig unmounted und remounted.
Beim Remount feuern **bis zu 7 parallele Netzwerk-Requests** ohne Koordination, was die App
für mehrere Sekunden blockiert. Zusätzlich überschreibt der Extraktions-Effect
(`extractInputs`, Z. 351–398) `extractedInputs.batna_description` mit `null`, wenn die
Chat-EF für Extract-Mode keine `alternatives` zurückgibt — und persistiert diesen
null-Wert in localStorage, womit das BATNA dauerhaft verloren ist.

---

## 2. Observed — direkt im Code sichtbar

### O-01 — AnalysisProvider ist außerhalb des Routers, Index.tsx remountet vollständig
**Datei:** `src/App.tsx:32,36`
```tsx
<AnalysisProvider>        // außerhalb Router
  <BrowserRouter>         // Router inside Provider
    ...
    <Route path="/app" element={<ProtectedRoute><Index /></ProtectedRoute>} />
    <Route path="/zopa" element={<ProtectedRoute><ZopaCalculator /></ProtectedRoute>} />
```
AnalysisProvider überlebt Navigation. `Index.tsx` wird bei jedem Route-Wechsel vollständig
unmounted und remounted.

---

### O-02 — AnalysisContext persistiert in localStorage (7-Tage-TTL)
**Datei:** `src/contexts/AnalysisContext.tsx:6, 115, 117-119`
- `loadFromStorage()` via `useState(loadFromStorage)` bei Provider-Mount
- `useEffect` speichert bei jeder State-Änderung in localStorage
- `extractedInputs`, `messages`, `analysis`, `zopaResult` — alle persistiert
- `isLoading` explizit ausgeschlossen (Z. ~102)

---

### O-03 — 14 useEffects in Index.tsx, keiner mit Cleanup-Return
**Datei:** `src/pages/Index.tsx`

| Zeilen | Zweck | Dependencies | Cleanup? | Feuert on Mount? |
|---|---|---|---|---|
| 83–89 | Chat-Messages aus Context wiederherstellen | `[contextMessages, messages.length, setMessages]` | ❌ | Ja, wenn Context-Messages vorhanden |
| 92–98 | Neue Messages in Context syncen | `[messages, addMessage]` | ❌ | Ja |
| 105–114 | Finales Assistant-Message nach Stream syncen | `[isLoading, messages, updateLastMessage]` | ❌ | Ja |
| 183–209 | User-Profil aus DB laden | `[user]` | ❌ | Ja (1 DB-Query) |
| 212–244 | Guest-Messages nach Login migrieren | `[user, persona, toast]` | ❌ | Ja |
| 246 | Version-Check | `[checkAndReload]` | ❌ | Ja |
| 281–283 | Toast bei Error | `[error, toast]` | ❌ | Ja |
| 286–298 | Guest-Registrierungs-Prompt | `[messages, isLoading, isGuest, ...]` | ❌ | Ja, nach 1. AI-Response |
| 301–304 | Guest-Messages in localStorage | `[messages, isGuest]` | ❌ | Ja |
| 307–313 | Auto-save Messages in DB | `[messages, isLoading, activeSessionId, ...]` | ❌ | Ja, bei neuer Message |
| **318–398** | **Analyze-Progress + Extract-Inputs (2 API-Calls)** | `[isLoading, messages, persona, activeSessionId]` | ❌ | **Ja, wenn messages vorhanden** |
| 402–451 | Plan generieren | `[effectiveProgress, negotiationPlan, ...]` | ❌ | Ja, wenn ready |
| 454–474 | Sessions auf Outcome-Feedback prüfen | `[user, isGuest]` | ❌ | Ja (1 DB-Query) |

---

### O-04 — Effect Z. 318–398: Zwei API-Calls auf Mount, kein AbortController
**Datei:** `src/pages/Index.tsx:318–398`

```typescript
// Fires when isLoading: true→false (after AI response) OR on mount with messages
const analyzeProgress = async () => { /* POST /analyze-progress */ };
const extractInputs = async () => { /* POST /functions/v1/chat (extract mode) */ };
analyzeProgress();
extractInputs();
```
- Dependencies: `[isLoading, messages, persona, activeSessionId]`
- Kein `AbortController` → alte Requests können nach Navigation-back noch feuern
- `analyzeProgressCountRef.current` wird bei Remount **auf 0 zurückgesetzt**
  → Effect feuert sofort beim ersten Durchlauf (Throttling-Counter neu gestartet)

---

### O-05 — extractInputs überschreibt batna_description mit null
**Datei:** `src/pages/Index.tsx:372–397`

```typescript
if (data.extracted?.alternatives) {
  setExtractedInputsFn({
    negotiation_type: extractedInputs?.negotiation_type ?? null,
    ...
    batna_description: data.extracted.alternatives,  // nur gesetzt wenn alternatives != null
  });
}
```
**WENN** `data.extracted?.alternatives` **falsy** ist (EF gibt null zurück), wird
`setExtractedInputsFn` **nicht aufgerufen** — BATNA bleibt erhalten.

**WENN** `data.extracted?.alternatives` **truthy** ist aber kurz danach eine zweite
Extraction mit `alternatives: null` feuert (z. B. weil der Conversation-Context nach
Navigation ohne BATNA-Kontext analysiert wird), wird BATNA überschrieben.

---

### O-06 — Netzwerk-Requests bei Remount: bis zu 7
**Datei:** `src/pages/Index.tsx` (mehrere)

| Request | Trigger | Blocking? |
|---|---|---|
| `SELECT user_profiles` | Effect Z. 183–209 | Nein (async) |
| `SELECT negotiation_sessions` (outcome check) | Effect Z. 454–474 | Nein |
| `POST /analyze-progress` | Effect Z. 319–347 | Nein |
| `POST /functions/v1/chat` (extract) | Effect Z. 351–374 | Nein |
| `SELECT negotiation_sessions` (loadSessions) | useSessionManager on authSession change | Nein |
| `SELECT session_messages` (wenn session aktiv) | handleSelectSession | Nein |
| `POST /summarize-session` (wenn session aktiv) | isResumeLoading effect | Nein |

Alle async, aber **unkordiniert** — kein Loader-Gate, keine Sequenzierung.
React-Renders zwischen jedem State-Update erhöhen den Re-render-Druck.

---

### O-07 — Kein setTimeout / setInterval / Event-Listener in Index.tsx
**Datei:** `src/pages/Index.tsx` (gesamte Datei)  
Keine Timer oder Event-Listener ohne Cleanup. Ein AbortController-Pattern existiert
für Document-Upload (Z. ~524), aber nicht für die Performance-kritischen Effects.

---

### O-08 — R-002: Mehrere unabhängige isLoading-States
**Datei:** `src/pages/Index.tsx:67–72`
```typescript
const [isAnalyzingProgress, setIsAnalyzingProgress] = useState(false);
const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
const [isResumeLoading, setIsResumeLoading] = useState(false);
// + isLoading from useChat
// + isLoadingSessions from useSessionManager
```
5 separate Loading-States, keine gemeinsame Koordination. Jeder State-Change triggert
eigene Re-renders ohne Abhängigkeit von den anderen.

---

## 3. Inferred — aus Kontext erschlossen

### I-01 — BATNA-Verlust durch Extraction-Effect nach Navigation
Nach Remount werden die Context-Messages über Effect Z. 83–89 wiederhergestellt.
Dadurch ändert sich `messages` → Effect Z. 318–398 hat `messages` in deps →
Wenn `isLoading` gerade false ist (`wasLoading` check in `prevLoadingRef`), **feuert
extractInputs()** mit dem aktuellen Conversation-Kontext.

Wenn der Conversation-Kontext in diesem Extract-Call keine BATNA-Signale enthält
(z. B. wenn der BATNA-Satz weit zurück in der History liegt und die Extraction-API
ihn in diesem Batch nicht erkennt), **wird die Extraction mit `alternatives: null`
zurückgegeben** → `setExtractedInputsFn` wird nicht aufgerufen → BATNA bleibt.

ABER: Wenn der vorherige extractInputs-Call doch `alternatives: ""` (leer-string)
zurückgibt, ist die Condition `if (data.extracted?.alternatives)` false (leerer String
ist falsy) → kein Überschreiben.

**Tatsächliches Risiko:** Das BATNA kann verloren gehen wenn:
1. Der `analyzeProgressCountRef` nach Navigation auf 0 resettet wird (O-04)
2. Die erste Extraction nach Navigation den BATNA nicht im Conversation-Context findet
3. Ein anderer Code-Pfad `extractedInputs` mit `batna_description: null` überschreibt

**Wahrscheinlichste Ursache:** `handleNewSession` (Z. 597–622) wird beim Klick auf einen
Sidebar-Link aufgerufen, löscht `extractedInputs` explizit → BATNA verloren.
Beim Zurück-Button (`navigate('/app')`) sollte AnalysisContext erhalten bleiben.

---

### I-02 — Verlangsamung durch unkordiniertes Effect-Firing
React rendert nach jedem `setState`-Call. Bei 7 parallelen async Requests, die alle
unterschiedliche State-Updates auslösen, entstehen **7+ Re-render-Zyklen** innerhalb
kurzer Zeit. Ohne `React.startTransition` oder Batching werden alle State-Updates
als separate Renders verarbeitet → App wirkt eingefroren für 2–4 Sekunden.

---

### I-03 — analyzeProgressCountRef-Reset als Trigger
`analyzeProgressCountRef` ist ein `useRef` (Z. ~316). Bei Remount von Index.tsx
startet es bei 0. Die erste Extraction nach Remount wird immer ausgeführt
(Counter 1 > 1 ist false → kein Throttling). Das ist korrekt für den Erstaufruf,
aber führt zu einem unnötigen API-Call wenn:
- BATNA bereits im Context vorhanden ist
- Die Messages aus dem Context stammen (kein neuer AI-Response)

---

## 4. Missing — fehlende Information

### M-01 — Exakter Trigger des BATNA-Verlusts unklar
Unklar ob der Verlust durch `handleNewSession` (Sidebar-Klick) oder durch
Navigation via `navigate('/app')` (Zurück-Button) ausgelöst wird. Beide
Pfade müssen im Browser-Netzwerk-Tab getrennt getestet werden.

### M-02 — Extraction-API-Response für BATNA-Konversation unbekannt
Ob `/functions/v1/chat` (extract mode) `alternatives` korrekt aus dem
Conversation-Kontext extrahiert, wenn BATNA weiter zurück liegt, ist nicht
aus dem Code-Reading ableitbar — muss live getestet werden.

### M-03 — Render-Count bei Navigation unbekannt
Wie viele Re-renders tatsächlich zwischen Navigation und stabiler UI auftreten,
kann nur via React DevTools Profiler gemessen werden.

---

## 5. Root Cause Hypothesis (Proposed)

**Für Verlangsamung:**
> Index.tsx remountet vollständig bei jedem Route-Wechsel. 5–7 unkordinierte async
> Effects feuern im Mount-Zyklus ohne Sequenzierung, Debouncing oder AbortController.
> Jede State-Änderung aus diesen Effects triggert separate Re-renders. Kumulierter
> Effekt: mehrere Sekunden Non-Responsiveness.

**Für BATNA-Verlust:**
> Primär-Hypothese: Nutzer klickt auf Sidebar-Link (z.B. "Gehaltserhöhung" oder
> "Neue Verhandlung"), was `handleNewSession()` aufruft und `extractedInputs` explizit
> auf null setzt. Das führt zu BATNA-Verlust.
>
> Sekundär-Hypothese: Nach Remount feuert `extractInputs()` auf Basis des wiederhergestellten
> Conversation-Kontexts. Wenn der extrahierte Wert für `alternatives` null/undefined ist,
> überschreibt `setExtractedInputsFn` das BATNA mit null (only if alternatives is provided).
> Da der Code `if (data.extracted?.alternatives)` prüft, passiert das Überschreiben nur
> wenn alternatives truthy ist — somit ist diese Pfad weniger wahrscheinlich.

---

## 6. Files Involved (read-only)

| Datei | Relevanz |
|---|---|
| `src/App.tsx:32,36` | Provider/Router-Hierarchie — O-01 |
| `src/contexts/AnalysisContext.tsx:6,80-119` | localStorage-Persistenz — O-02 |
| `src/pages/Index.tsx:83-474` | 14 useEffects, keine Cleanups — O-03/04/05/06/08 |
| `src/hooks/useSessionManager.ts:52-56` | loadSessions on authSession change |

---

## 7. Performance Impact Assessment

| Faktor | Schwere | Anmerkung |
|---|---|---|
| 7 parallele Netzwerk-Requests auf Remount | Mittel | Alle async, kein Blocking I/O |
| 14 useEffects ohne Cleanup | Mittel | Keine Memory Leaks, aber viele Re-renders |
| Kein AbortController | Mittel | Race-Condition bei schneller Navigation möglich |
| analyzeProgressCountRef-Reset | Niedrig | Unnötiger API-Call, aber nicht blockierend |
| 5 unkoordinierte isLoading-States | Mittel | Excessive Re-renders |
| Keine gemeinsame Lade-Koordination | Hoch | UI-Freeze für 2–4s bei komplexen Sessions |

---

## 8. Recommended Fix Scope (Proposed — nicht implementieren)

**Fix A — BATNA-Verlust (einfacher, hohe Priorität):**
1. In `handleNewSession` prüfen ob der User explizit eine neue Session startet vs.
   nur navigiert — `resetExtractedInputs` nur bei explizitem New-Session-Intent aufrufen
2. Den Trigger für BATNA-Verlust durch Browser-Testing von Zurück-Button vs. Sidebar-Klick
   identifizieren, dann gezielt beheben

**Fix B — Performance (moderater Aufwand):**
1. Effect Z. 318–398: Guard hinzufügen: nur ausführen wenn `messages.length > 0`
   UND `!isGuest` UND neu-gesendete Nachrichten vorhanden (nicht nur wiederhergestellte)
2. Separate `restoredRef` oder Flag: unterscheide "Messages aus Context wiederhergestellt"
   von "neue AI-Response" — extrahiere nur bei letzterem
3. AbortController für Analyze-Progress und Extract-Inputs-Fetch hinzufügen

**Nicht in diesem Fix:**
- Vollständige Effect-Koordination (zu großer Scope)
- Migration zu React.startTransition (separate Refactor-Aufgabe, RFB-020-Bereich)

---

## 9. Acceptance Criteria — Bewertung

| Kriterium | Prüfbar? | Bewertung |
|---|---|---|
| `tsc --noEmit` clean | ✅ Ja | Standardprüfung |
| curl-Befehl | ❌ N/A | Kein Backend-Fix in diesem Scope |
| Layer-1-Tests grün | ⚠️ Eingeschränkt | Keine spezifischen Tests für useEffect-Behavior |
| App reagiert nach Navigation in < 1s | ✅ Manuell | Performance-Regression messbar via React Profiler |
| BATNA bleibt nach Zurück-Navigation erhalten | ✅ Manuell | Smoke-Test: BATNA eingeben → /zopa → zurück → BATNA noch da |
| Browser Network Tab: max 2 API-Calls auf Remount (wenn keine neue AI-Response) | ✅ Ja | Testbar via DevTools |

**Empfehlung:** AC-2 (curl) durch AC-5 (BATNA Smoke-Test) und AC-6 (Network Tab Check) ersetzen.
