# Diagnosis Report — BUG-20260521-zopa-prefilled-values

**Bug ID:** BUG-20260521-zopa-prefilled-values
**Erstellt:** 2026-05-26
**Autor:** Claude Code (Diagnose-Schritt, kein Code geändert)
**Status:** Diagnosed — ready for Template 1-DEV / GO decision

---

## 1. Bug Summary

Der ZOPA-Rechner zeigt beim Öffnen Werte in allen vier Feldern, weil er diese direkt aus
`extractedInputs` in `AnalysisContext` liest — was ein intentionales Feature ist. Der Bug
liegt eine Ebene tiefer: `handleNewSession()` in `Index.tsx` versucht `extractedInputs`
zurückzusetzen, indem es `setExtractedInputsFn` mit lauter `null`-Werten aufruft. Die
`setExtractedInputs`-Implementierung in `AnalysisContext` enthält jedoch eine Merge-Logik
(`??`-Operator), die `null`-Werte stillschweigend ignoriert und die alten Werte beibehält.
Dadurch überlebt `extractedInputs` den Session-Reset und befüllt beim nächsten Öffnen des
ZOPA-Rechners die Felder mit Daten aus der Vorsession.

---

## 2. Observed — direkt im Code verifiziert

1. **ZopaCalculator.tsx:24–27** — Formular-Initialisierung liest direkt aus AnalysisContext:
   ```ts
   const ei = extractedInputs;      // aus useAnalysis()
   const fallback = inputs;          // legacy canvas, ebenfalls aus useAnalysis()
   const [ownTarget, setOwnTarget] = useState((ei?.own_target ?? fallback?.own_target)?.toString() ?? '');
   const [ownMinimum, setOwnMinimum] = useState((ei?.own_minimum ?? fallback?.own_minimum)?.toString() ?? '');
   const [oppMax, setOppMax] = useState((ei?.opponent_estimated_max ?? fallback?.opponent_estimated_max)?.toString() ?? '');
   const [oppMin, setOppMin] = useState((ei?.opponent_estimated_min ?? fallback?.opponent_estimated_min)?.toString() ?? '');
   ```
   Wertequelle: `extractedInputs` (primär), `inputs` (Fallback) — beide aus `AnalysisContext`.

2. **ZopaCalculator.tsx:35–41** — zweiter Sync-Effekt: hält Felder mit `ei` synchron,
   solange die Komponente gemountet ist:
   ```ts
   useEffect(() => {
     if (!ei) return;
     if (ei.own_target != null) setOwnTarget(ei.own_target.toString());
     ...
   }, [ei]);
   ```
   Wenn `extractedInputs` nicht null ist, werden alle nicht-null-Felder erzwungen.

3. **AnalysisContext.tsx:80–98** — `loadFromStorage()` deserialisiert `extractedInputs`
   aus `localStorage` unter dem Key `negotiationcoach_session`. Felder geladen:
   `extractedInputs`, `inputs`, `sessionId`, `analysis`, `enriched`, `zopaResult`,
   `messages`, `activeScenario`, `cachedPlan`, `planHash`, `lastUpdated`.
   - STORAGE_VERSION = 2 — Versionsprüfung vorhanden ✓
   - STORAGE_TTL = 604_800_000 ms (7 Tage) — TTL-Prüfung vorhanden ✓
   - Kein Schema-Migrations-Guard für Teilfelder innerhalb `extractedInputs`.

4. **AnalysisContext.tsx:126–146** — `setExtractedInputs` Merge-Logik:
   ```ts
   const merged: ExtractedInputs = {
     negotiation_type: ei.negotiation_type ?? prior.negotiation_type,
     own_target: ei.own_target ?? prior.own_target,
     own_minimum: ei.own_minimum ?? prior.own_minimum,
     ...
   };
   ```
   `null ?? prior.x` ergibt `prior.x` — ein `null`-Wert im übergebenen Objekt
   überschreibt den alten Wert **nicht**. Der Merge ist additiv, nicht resettend.

5. **Index.tsx:628–659** — `handleNewSession()`:
   ```ts
   clearMessages();
   clearContextMessages();
   setExtractedInputsFn({
     negotiation_type: null, own_target: null, own_minimum: null,
     opponent_estimated_max: null, opponent_estimated_min: null,
     deadline_days: null, batna_description: null, context_notes: null,
     confidence: 0, missing_fields: [],
   });
   ```
   `setExtractedInputsFn` = `setExtractedInputs` aus AnalysisContext. Da alle vier
   Kernfelder `null` sind, ignoriert die Merge-Logik sie vollständig. Alter `extractedInputs`-
   State bleibt erhalten. **Das ist der unmittelbare Root Cause.**

6. **Index.tsx:667–698** — `handleSelectSession()`:
   - Lädt DB-Nachrichten per `loadSessionMessages(sessionId)`
   - Setzt `progressStatus` und `negotiationPlan` aus `session.progress_status`
   - Ruft **kein** Reset für `extractedInputs` auf — alter extractedInputs-State der
     Vorsession wird in die neu gewählte Session mitgenommen.

7. **AnalysisContext.tsx:207–210** — `resetSession()` existiert und setzt korrekt auf
   `defaultSession` zurück (setzt `extractedInputs: null`), inklusive `localStorage.removeItem`.
   Sie wird jedoch weder in `handleNewSession()` noch in `handleSelectSession()` aufgerufen.

8. **AGENTS.md:F-003** — Eintrag lautet: "localStorage no TTL/versioning". Dieser Eintrag
   ist **veraltet** — der aktuelle Code hat sowohl STORAGE_VERSION als auch STORAGE_TTL.

---

## 3. Inferred — aus Kontext erschlossen

1. **Intentionales Feature:** Die Vorbefüllung aus `extractedInputs` in `ZopaCalculator.tsx`
   ist beabsichtigt — die Logik ist explizit und wurde vor kurzem aktiv erweitert
   (handleNewSession-Patch aus BUG-20260521-session-save-retry-loop-Kontext). Kein
   Zufallscode.

2. **7-Tage-Persistenz als Sekundärursache:** Selbst wenn der Merge-Bug behoben wird,
   überlebt `extractedInputs` nach Browser-Neustart bis zu 7 Tage. Nutzer, die nach einer
   Woche die App erneut öffnen, sehen noch Werte aus der letzten Session.

3. **`handleSelectSession` setzt extractedInputs nicht zurück:** Beim Wechsel über die
   Sidebar bleiben ZOPA-Werte der bisherigen Session in extractedInputs erhalten, auch wenn
   die neue Session keine Extraktion hat.

4. **Auth-Wechsel ohne extractedInputs-Reset:** Kein `onAuthStateChange`-Listener in
   AnalysisContext, der `resetSession()` aufruft. Nach Logout→Login bleibt der
   localStorage-State (bis TTL-Ablauf) erhalten.

---

## 4. Missing — fehlende Information für vollständige Diagnose

1. **`confidence: 0` vs. `null` in merge-Logik:** Bei `confidence: 0 ?? prior.confidence`
   ergibt sich `0`, weil `0` kein Nullish-Wert ist — Confidence wird also korrekt
   zurückgesetzt. Ob dieses Verhalten für alle Felder korrekt ist, kann nur durch
   Produktentscheidung validiert werden.

2. **ADR-001 Proposed Canonical Rules für localStorage:** Laut Prompt referenziert
   ADR-001 Proposed Boundary Map und localStorage-Risiken. Das Dokument konnte im
   Repo nicht gefunden werden. Möglicherweise als ADR nicht formalisiert.

3. **Ob `handleUseCaseStart` (guided flow) extractedInputs zurücksetzt:**
   `handleUseCaseStart` (Index.tsx:281–295) setzt viele State-Variablen zurück,
   ruft aber `setExtractedInputsFn` **nicht** auf. Derselbe Merge-Bug trifft also
   auch den Guided-Flow-Start.

---

## 5. Wertequelle — Ergebnis Block A

| Feld | Quelle |
|---|---|
| `own_target` | `extractedInputs.own_target` (AnalysisContext) → aus localStorage deserialisiert |
| `own_minimum` | `extractedInputs.own_minimum` (AnalysisContext) → aus localStorage deserialisiert |
| `opponent_estimated_max` | `extractedInputs.opponent_estimated_max` (AnalysisContext) → aus localStorage |
| `opponent_estimated_min` | `extractedInputs.opponent_estimated_min` (AnalysisContext) → aus localStorage |

**Fallback:** `inputs` (legacy canvas) aus AnalysisContext — ebenfalls localStorage-persistent.
Kein direkter localStorage-Zugriff in ZopaCalculator. Kein Prop. Keine externe Initialisierung.

---

## 6. Reset-Status — Ergebnis Block B

| Szenario | Reset vorhanden? | Details |
|---|---|---|
| `handleNewSession()` | **Fehlend (effektiv)** | `setExtractedInputsFn(nulls)` aufgerufen, aber Merge-Logik ignoriert null-Werte → kein Reset |
| `handleUseCaseStart()` | **Fehlend** | Kein Aufruf von `setExtractedInputsFn` überhaupt |
| Auth-Wechsel (Logout/Login) | **Fehlend** | Kein `onAuthStateChange`-Listener in AnalysisContext |
| `handleSelectSession()` | **Fehlend** | extractedInputs der alten Session bleibt beim Wechsel erhalten |
| `resetSession()` | **Vorhanden, aber nie aufgerufen** | Korrekte Implementierung in AnalysisContext — nicht in Session-Reset-Flows eingebunden |

---

## 7. RFB-039 Verwandtschaft — Ergebnis Block C

**RFB-039 beschreibt das inverse Problem:** Context geht bei Navigation VERLOREN
(Nachrichten truncated nach Route-Wechsel zu Tool-Seiten). Status: DONE (commit `2060c1b`).

**BUG-20260521-zopa-prefilled-values beschreibt das entgegengesetzte Problem:**
State überlebt Session-Reset unerwünscht und BLEIBT erhalten, wo er gelöscht werden sollte.

**Empfehlung: Separater Fix.** Gleicher Mechanismus (AnalysisContext + localStorage),
aber andere Richtung und anderer Root Cause. RFB-039-Fix hat `clearContextMessages()`
in `handleNewSession` eingebaut — der vorliegende Bug betrifft `extractedInputs`, das
von RFB-039 nicht addressiert wurde. Merge ist kein merge-Kandidat.

---

## 8. Feature-vs.-Bug Assessment — Ergebnis Block D

**Szenario 1 ist durch Code gestützt (Observed):**
- Die Vorbefüllung aus `extractedInputs` ist explizit implementiert (ZopaCalculator.tsx:24–41)
- Es gibt kein `extractedInputs`-Mapping das unbeabsichtigt aussieht
- Die Vorbefüllung ermöglicht einen nahtlosen Übergang von Chat → ZOPA

**Bug liegt nicht in der Vorbefüllung, sondern im fehlenden Reset:**
`handleNewSession` hat die Absicht, `extractedInputs` auf null zu setzen
(sichtbar am expliziten `setExtractedInputsFn({...nulls})`), scheitert aber an der
Merge-Logik. Es handelt sich um einen Implementierungsfehler im Reset-Pfad.

**Produktentscheidung (Proposed):** Ist es gewünscht, dass ZOPA-Felder beim Öffnen
des Rechners innerhalb einer laufenden Session (ohne handleNewSession) befüllt werden?
Falls ja: Feature korrekt — nur der Reset-Bug muss gefixt werden.
Falls nein: Vorbefüllung komplett entfernen (breaking change, nicht empfohlen).
→ **Diese Entscheidung trifft der Delivery Controller.**

**7-Tage-Persistenz:** Sekundäres Szenario-3-Element — Werte überleben bis zu 7 Tage
nach Browser-Schließen. Nicht der unmittelbare Bug, aber eine Follow-up-Überlegung.

---

## 9. Root Cause Hypothesis (Proposed)

Der Bug entsteht weil `handleNewSession()` versucht, `extractedInputs` durch Übergabe von
`null`-Werten an `setExtractedInputs` zurückzusetzen, die `setExtractedInputs`-Implementierung
in `AnalysisContext` jedoch eine Merge-Logik mit `??`-Operator verwendet, welche `null`-Werte
als "kein Update" behandelt — wodurch die alten ZOPA-relevanten Felder unberührt bleiben,
in localStorage persistiert werden, und beim nächsten Öffnen des ZOPA-Rechners in die
Formularfelder fließen.

---

## 10. Betroffene Dateien (read-only)

| Datei | Rolle |
|---|---|
| `src/pages/ZopaCalculator.tsx` | Symptom-Ort: liest extractedInputs für Formular-Init |
| `src/contexts/AnalysisContext.tsx` | Root-Cause-Ort: Merge-Logik + resetSession-Lücke |
| `src/pages/Index.tsx` | Aufruf-Ort: handleNewSession, handleSelectSession, handleUseCaseStart |

---

## 11. Recommended Fix Scope (Proposed — nicht implementieren)

**Minimal-Fix (empfohlen):**
Eine neue Action `clearExtractedInputs()` in `AnalysisContext.tsx` hinzufügen, die
`extractedInputs` direkt auf `null` setzt — ohne Merge-Logik. In `handleNewSession()`,
`handleSelectSession()` und `handleUseCaseStart()` anstelle (bzw. ergänzend) zu
`setExtractedInputsFn({...nulls})` aufrufen.

```ts
// AnalysisContext.tsx — neue Action (Proposed)
const clearExtractedInputs = () =>
  setSession(prev => ({ ...prev, extractedInputs: null, lastUpdated: new Date().toISOString() }));
```

**Alternativ:** `resetSession()` ist korrekt implementiert. In `handleNewSession` könnten
relevante Teile von `resetSession` selektiv angewendet werden — aber `resetSession` räumt
auch `messages`, `sessionId` etc. auf, was in `handleNewSession` anderweitig gesteuert ist.
Eine eigene `clearExtractedInputs`-Action ist sauberer.

**Scope:** 2–3 Zeilen in `AnalysisContext.tsx` + 3 Aufrufstellen in `Index.tsx`.
Kein DB-Zugriff, kein API-Contract-Change, kein Migration-Risiko.

---

## 12. ADR-001 Implikation

**ADR-001 konnte im Repo nicht lokalisiert werden** (Missing). Der Refactor-Backlog
enthält keinen Eintrag mit expliziten localStorage-Canonical-Rules (TTL, Schema-Version,
Clear on new session).

**Relevant aus bestehendem Code:**
- TTL (7 Tage) ist vorhanden → keine neue TTL nötig
- Schema-Version (v2) ist vorhanden → kein neues Versioning nötig
- "Clear on new session" für `extractedInputs`: **fehlend** → wird durch diesen Fix umgesetzt

Der Fix implementiert die implizit vorgesehene Regel "extractedInputs gehört zur Session
und muss beim Session-Reset auf null gesetzt werden" — unabhängig von ADR-001.

---

## 13. Acceptance Criteria Assessment

| AC | Prüfbar? | Erwartetes Ergebnis (aktuell, vor Fix) |
|---|---|---|
| AC-1: `npx tsc --noEmit` clean | ✓ sofort prüfbar | Bestanden (kein Fix nötig für TypeCheck) |
| AC-2: ZOPA nach "Neue Session" → alle 4 Felder leer | ✓ manuell (DOM-Inspektion) | **Schlägt fehl** — Merge-Bug verhindert Reset |
| AC-3: ZOPA nach Logout + Login → alle 4 Felder leer | ✓ manuell | **Schlägt fehl** — localStorage überlebt Logout (kein Auth-State-Reset) |
| AC-4: Layer-1-Tests grün | ✓ via `npm test` | Erwartung: grün (keine Layer-1-Logik betroffen) |
| AC-5: Output-Nachweis im Report | ✓ nach Fix | Nicht prüfbar bis Fix — wird nach Implementierung ergänzt |

**AC-2 und AC-3 schlagen aktuell fehl → bestätigt den Bug.**

AC-3 erfordert zusätzlich einen Auth-State-Reset (keinen Merge-Fix allein) — dies ist
ein eigenständiges Sub-Problem (Missing: Auth-Wechsel ohne Context-Reset).
Der Minimal-Fix (clearExtractedInputs in handleNewSession) behebt AC-2.
AC-3 ist nur vollständig lösbar wenn zusätzlich ein `onAuthStateChange`-Reset eingebaut wird.

**Empfehlung AC-3:** Als separates Issue erfassen oder als Scope-Erweiterung des Fix
explizit durch Delivery Controller genehmigen lassen, bevor implementiert wird.
