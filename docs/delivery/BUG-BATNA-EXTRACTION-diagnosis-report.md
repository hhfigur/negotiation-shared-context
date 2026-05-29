# Diagnose Report — BUG-BATNA-EXTRACTION

**Bug ID:** BUG-20260529-batna-extraction
**Erstellt:** 2026-05-29
**Autor:** Claude Code (Diagnose-Schritt, kein Code geändert)
**Status:** Diagnosed — ready for Template 1-DEV / GO decision

---

## 1. Bug Summary

`batna_description` bleibt nach dem Chat-Flow immer `null`, obwohl der Nutzer eine
BATNA explizit beschrieben hat. Ursache ist eine **One-Shot-Extraktion mit falschem
Auslösezeitpunkt**: `runExtractInputs()` in `useProgressEngine.ts` wird durch
`executedRef.current` auf genau eine Ausführung pro Session limitiert — ausgelöst
nach der **ersten** AI-Antwort. Wenn der Nutzer BATNA erst in Turn 2+ erwähnt,
ist `executedRef.current = true` bereits gesetzt und die Extraktion läuft nie wieder.

Das Backend (chatHelpers.ts) ist korrekt implementiert — `batna_description` ist im
Prompt definiert und wird geparst. Die Merge-Logik in AnalysisContext ist ebenfalls
korrekt. Der Fehler liegt ausschließlich im **One-Shot-Guard** in useProgressEngine.ts.

---

## 2. Observed — direkt im Code verifiziert

**1. chatHelpers.ts:74 — `batna_description` im System-Prompt definiert (Observed)**
```
"batna_description": "Text" oder null,
```
Explizit im JSON-Template. Kein sprachlicher Hinweis ("Konkurrenzangebot", "Alternative"),
aber das freie Feld erlaubt Claude, beliebige BATNA-Beschreibungen zu extrahieren.

**2. chatHelpers.ts:136–140 — parseChatResponse Spread-Reihenfolge (Observed)**
```typescript
const extracted: ExtractedInputs = {
  ...emptyExtraction,         // batna_description: null
  ...(previousInputs ?? {}),  // überschreibt falls previousInputs vorhanden
  ...(parsed.extracted ?? {}),// überschreibt mit Claude-Extraktion
};
```
Korrekt: Claude-Extraktion hat höchste Priorität. `batna_description` wird übernommen
wenn Claude es extrahiert. PROBLEM: `previousInputs` wird von useProgressEngine
als `undefined` übergeben (routes.ts:131) — Claude sieht keine vorherigen Extrakte.

**3. useProgressEngine.ts:87 — One-Shot-Guard (Observed — Root Cause)**
```typescript
if (executedRef.current) return;
```
Innerhalb `runExtractInputs()` — stoppt jeden zweiten und weiteren Aufruf.

**4. useProgressEngine.ts:160 — Guard wird nach erstem Erfolg gesetzt (Observed)**
```typescript
setExtractedInputs(patched);
executedRef.current = true;
```
Direkt nach dem ersten `setExtractedInputs`-Aufruf — kein weiterer Lauf möglich.

**5. useProgressEngine.ts:220–222 — Trigger prüft Guard (Observed)**
```typescript
if (!executedRef.current) {
  void runExtractInputs();
}
```
Trigger feuert nach jeder AI-Antwort (isLoading: true→false), aber `runExtractInputs`
wird durch den Guard nach dem ersten Lauf blockiert.

**6. useProgressEngine.ts:131 — previousInputs wird NICHT übergeben (Observed)**
```typescript
const response = await sendChatMessage(chatMessages, undefined, undefined, token);
```
Dritter Parameter (`previousInputs`) = `undefined`. Backend-`buildChatSystemPrompt`
zeigt Claude "Noch keine strukturierten Daten bekannt" — unabhängig vom Turn.

**7. AnalysisContext.tsx:141 — Merge-Richtung für batna_description (Observed)**
```typescript
batna_description: ei.batna_description ?? prior.batna_description,
```
Variante A: `newValue ?? prior` — neuer Wert bevorzugt, Fallback auf alten. **KORREKT.**
`null ?? prior` → prior bleibt. Nicht-null-Wert → überschreibt. Merge ist kein Bug.

**8. useProgressEngine.ts:75–79 — Guard-Reset bei leerer Session (Observed)**
```typescript
useEffect(() => {
  if (messages.length === 0) {
    executedRef.current = false;
  }
}, [messages.length]);
```
Guard wird korrekt bei "Neue Session" (messages = []) zurückgesetzt. Innerhalb
einer laufenden Session kein Reset.

**9. useProgressEngine.ts:110–127 — No-Token-Fallback: batna immer null (Observed)**
```typescript
setExtractedInputs({
  ...
  batna_description: null,
  ...
});
executedRef.current = true;
```
Unauthentifizierte Nutzer: `batna_description` wird explizit null gesetzt.
Keine BATNA-Extraktion möglich ohne auth-Token.

---

## 3. Inferred — aus Kontext erschlossen

1. **Claude extrahiert batna_description korrekt wenn aufgerufen (Inferred — Hohe Konfidenz):**
   Der System-Prompt ist klar, die Extraktionsregel explizit. Das Backend ist technisch
   korrekt. Es gibt keine Evidence für einen Prompt-Bug. Hypothese A kann ausgeschlossen werden.

2. **One-Shot Extraktion feuert nach der ersten AI-Antwort (Inferred — Hohe Konfidenz):**
   Die ersten Messages eines Nutzers enthalten typischerweise Zielwert, Mindestpreis, Szenario.
   BATNA wird meist später im Dialog erwähnt, nachdem der Coach gezielt danach fragt.
   → Die One-Shot-Extraktion trifft zu einem Zeitpunkt, an dem batna_description noch nicht
   im Chat-Verlauf steht.

3. **previousInputs=undefined verschärft das Problem (Inferred):**
   Selbst wenn die Extraktion mehrfach liefe, würde Claude ohne previousInputs jedes Mal
   alle Felder neu aus dem Gesamtverlauf ableiten. Mit korrekt übergebenem previousInputs
   würde er bestehende Felder respektieren und nur Lücken füllen.

4. **BUG-04 (extractedInputs verloren bei Navigation) ist kein Faktor hier (Inferred):**
   Das Problem tritt auf bevor Navigation stattfindet. BATNA wird im laufenden Chat nicht
   gesetzt — das ist kein Persistenz-Problem.

---

## 4. Missing — nicht verifizierbbar ohne Live-Run

1. **AC-2 Smoke-Test (Missing — kein Live-Zugriff):**
   Ob `/api/chat` bei Eingabe "Ich habe ein Konkurrenzangebot von 78.000€" tatsächlich
   `batna_description != null` zurückgibt, konnte nicht per curl verifiziert werden
   (API-Keys nicht in Claude-Code-Umgebung verfügbar). Hypothese A bleibt theoretisch
   offen — praktisch aber unwahrscheinlich (Prompt ist klar).

2. **progressStatus.batna vs. batna_description Verhältnis:**
   Die Edge Function `analyze-progress` setzt `progressStatus.batna = true/completed`
   wenn BATNA im Chat erkannt wurde. Diese Information wird nicht zurück in
   `extractedInputs.batna_description` geschrieben. Ob dies ein weiteres Gap ist oder
   bewusst getrennt, ist aus dem Code nicht ablesbar.

---

## 5. Hypothese A — Backend-Extraktion (chatHelpers.ts)

**Ergebnis: Ausgeschlossen als primärer Root Cause.**

- `batna_description` ist explizit im System-Prompt definiert (Observed, chatHelpers.ts:74)
- `parseChatResponse` verarbeitet es korrekt via Spread (Observed, chatHelpers.ts:136–140)
- Der Prompt gibt keine falschen Beispiele oder einschränkenden Keywords
- **Einschränkung:** Kein Smoke-Test durchgeführt (Missing). Theoretisch möglich, dass
  Claude trotz korrektem Prompt nicht extrahiert — sehr unwahrscheinlich.
- **Sekundäres Problem:** `previousInputs = undefined` wird übergeben — Claude sieht
  keine vorherigen Extrakte (Observed). Dies ist kein BATNA-spezifischer Bug, betrifft
  alle Felder. Eigenes P3-Item empfohlen.

---

## 6. Hypothese B — Merge-Logik (AnalysisContext.tsx)

**Ergebnis: Ausgeschlossen als Root Cause.**

- Merge-Richtung ist `ei.batna_description ?? prior.batna_description` (Observed, Zeile 141)
- **Variante A** (newValue bevorzugt) — die korrekte Richtung
- `null ?? prior` → prior bleibt erhalten ✓
- Nicht-null-Wert → überschreibt korrekt ✓
- Problem: Die Merge-Logik wird nie mit einem nicht-null `batna_description` aufgerufen,
  weil die Extraktion nach Turn 1 stoppt. Merge kann korrekt sein und der Bug trotzdem auftreten.

**Drei-Turns Verhaltensanalyse:**
| Turn | Nutzer-Input | executedRef | runExtractInputs | batna_description Ergebnis |
|---|---|---|---|---|
| 1 | Text ohne BATNA | false → true | **feuert** | null (BATNA nicht im Text) → gespeichert als null |
| 2 | "Konkurrenzangebot 78.000€" | true | **blockiert** | null (keine Extraktion) |
| 3 | Weiterer Text | true | **blockiert** | null (unverändert) |

Nach Turn 3 ist `batna_description = null` — nicht weil die Merge-Logik falsch ist,
sondern weil Extraktion nach Turn 1 nie wieder läuft.

---

## 7. Hypothese C — Persistenz / BUG-04-Verwandtschaft

**Ergebnis: Ausgeschlossen als primärer Root Cause.**

- `batna_description` ist Teil von `extractedInputs`, das in localStorage persistiert wird
- Da `batna_description` nie gesetzt wird (One-Shot-Problem), gibt es nichts zu verlieren
- BUG-04 beschreibt den Verlust von korrekt gesetzten Werten — hier wird der Wert
  gar nicht erst gesetzt
- Die Two-Shot-Verwandtschaft mit BUG-20260521-zopa-prefilled-values besteht nur im
  Mechanismus (AnalysisContext + Merge), nicht im Root Cause

---

## 8. Primäre Root Cause Hypothesis (Proposed)

`batna_description` wird nie extrahiert weil `runExtractInputs()` in
`useProgressEngine.ts` exakt einmal pro Session ausgeführt wird — sofort nach der
**ersten** AI-Antwort, bevor der Nutzer typischerweise BATNA erwähnt hat.
`executedRef.current` verhindert jeden weiteren Lauf. Das Backend ist korrekt;
die Merge-Logik ist korrekt; die Persistenz ist korrekt. Nur der Auslösezeitpunkt
und die One-Shot-Beschränkung sind das Problem.

**Sekundäres Problem (P3, separates Item empfohlen):**
`previousInputs` wird nicht an `sendChatMessage` übergeben — Claude hat keinen
Kontext über bereits extrahierte Felder. Dies ist für BATNA nicht entscheidend
(da Extraktion gar nicht läuft), aber verschlechtert die Genauigkeit aller Felder.

---

## 9. Betroffene Dateien

| Datei | Rolle | Änderung nötig |
|---|---|---|
| `negotiation-buddy/src/hooks/useProgressEngine.ts` | Root Cause — One-Shot-Guard | Ja — Guard-Logik anpassen |
| `negotiation-buddy/src/lib/apiClient.ts` | sendChatMessage Signature | Nein (Signatur korrekt) |
| `negotiation-buddy/src/contexts/AnalysisContext.tsx` | Merge-Logik | Nein (korrekt) |
| `negotiationcoach-backend/src/api/chatHelpers.ts` | Extraktion | Nein (korrekt) |
| `negotiationcoach-backend/src/api/routes.ts` | /api/chat Handler | Nein (korrekt) |

---

## 10. Recommended Fix Scope (Proposed — nicht implementieren)

**Minimal-Fix — empfohlen:**
Den One-Shot-Guard lockern: Extraktion läuft nach jedem Turn, bis `batna_description`
gesetzt ist. Danach Guard wie bisher.

```typescript
// useProgressEngine.ts — Guard-Bedingung ändern (Proposed)
// VORHER:
if (executedRef.current) return;

// NACHHER (Pseudocode — nicht implementieren):
// Extraktion läuft wenn (a) noch nie gelaufen ODER (b) batna_description noch fehlt
const currentExtracted = /* aktuellen extractedInputs-Wert lesen */;
if (executedRef.current && currentExtracted?.batna_description != null) return;
```

**Implikation:** Extraktion kann 2–3× pro Session laufen (bis BATNA gesetzt ist).
Da `strategy_coaching` für kmu/profi = SONNET: moderate Mehrkosten pro Session.
Für `free/privat` = HAIKU: minimal.

**Alternative (vollständiger Fix):**
`previousInputs` aus `extractedInputs` an `sendChatMessage` übergeben — Claude
weiß was bereits extrahiert wurde und füllt nur Lücken. Merge-Logik unverändert.
Reduziert Redundanz bei Multi-Turn-Extraktion.

**Scope:** 5–10 Zeilen in `useProgressEngine.ts`.
Kein DB-Zugriff, kein API-Contract-Change, kein Migration-Risiko.
TypeCheck-Impact: minimal (Typänderung nur wenn previousInputs-Übergabe geändert).

---

## 11. AC Assessment

| AC | Prüfbar heute? | Ergebnis (vor Fix) |
|---|---|---|
| AC-1: `npx tsc --noEmit` clean | ✓ sofort | Erwartung: clean (kein Code geändert) |
| AC-2: curl /api/chat mit BATNA-Text → batna_description != null | ✗ Missing (kein Live-Zugriff) | Erwartung: Backend liefert korrekt — Hypothese A ausgeschlossen |
| AC-3: Drei Turns (ohne/mit/ohne BATNA) → batna nach Turn 3 = Turn-2-Wert | ✓ per Code-Analyse | **Schlägt fehl** — Turn 2 läuft keine Extraktion (executedRef=true) |
| AC-4: Layer-1-Tests grün | ✓ via npm test (backend) | Erwartung: grün (keine Layer-1-Logik betroffen) |
| AC-5: Output-Nachweis im Report | ✓ | Vorliegender Report |

**AC-3 schlägt durch Code-Analyse nachweisbar fehl → bestätigt Root Cause.**
AC-2 bleibt offen (Missing) — für Vollständigkeit nach Fix per curl verifizieren.
