# Diagnose-Report — BUG-20260521-batna-lost-after-nav + BUG-20260529-batna-extraction

**Datum:** 2026-06-09
**Symptom (BUG-20260529):** `batna_description` bleibt null — wird nicht in `extractedInputs` gespeichert
**Symptom (BUG-20260521):** BATNA erscheint nach Navigation zu anderem Tool und Rückkehr als "ausstehend"

---

## Verbindung zwischen beiden Bugs

Die Bugs sind nicht unabhängig. BUG-20260521 ist das **UI-Symptom** von BUG-20260529:

1. `analyze-progress` EF erkennt BATNA korrekt → setzt `progressStatus.batna = { completed: true }` ✓
2. `progressStatus` ist local state in `Index.tsx` → wird bei unmount/remount zurückgesetzt
3. `extractedInputs.batna_description` wird durch NC-CONTEXT A Extraktion **nicht zuverlässig gesetzt** (BUG-20260529)
4. Nach Navigation → Remount → `progressStatus = null`, `contextDerivedProgress.batna` liest null aus `extractedInputs` → BATNA "verschwunden"

Wenn BUG-20260529 gefixt ist, ist BUG-20260521 automatisch mitgefixt.

---

## Root Cause — BUG-20260529 (Inferred)

### Extraction-Architektur (Observed)

Das System hat zwei Extraktions-Pfade für `extractedInputs.batna_description`:

**Pfad A — `runExtractInputs` (useProgressEngine.ts:82-180)**
- Ruft Express-Backend `/api/chat` auf
- Antwortformat: `{ extractedInputs: { batna_description: "...", ... } }`
- **One-shot**: `executedRef.current` verhindert Re-Ausführung nach Turn 1
- Wenn BATNA erst in Turn 2+ erwähnt wird → nicht mehr erfasst

**Pfad B — NC-CONTEXT A (Index.tsx:449-526)**
- Ruft Supabase EF `/functions/v1/chat` mit `{ persona: { mode: 'extract' } }` auf
- EF-Antwortformat: `{ extracted: { details, goal, counterpart, alternatives } }`
- Liest BATNA aus `data.extracted?.alternatives` — Feldname stimmt mit EF-Response überein
- Läuft jede Runde bis BATNA + opponent gesetzt sind (max. 5 Versuche)

### Verdächtiger Failure-Punkt (Inferred)

**EF extract prompt — "die folgende Nachricht" vs. full conversation array:**

```
// supabase/functions/chat/index.ts:76
const extractPrompt = `Analysiere die folgende Nachricht und extrahiere...`
// ...
body: JSON.stringify({
  model: "claude-haiku-4-5-20251001",
  system: extractPrompt,
  messages: messages,  // voller Conversation-Array!
})
```

Der Prompt sagt "**die folgende Nachricht**" (singular), übergibt aber den **vollständigen Multi-Turn-Conversation-Array**. Haiku könnte dies als "analysiere nur die letzte Nachricht" interpretieren — BATNA aus früheren Turns würde nicht erkannt.

**Alternativ-Hypothese:** EF-HTTP-Fehler durch nicht-alternierende Message-Rollen → `alternatives = null` → `newBatna = null` → kein Update.

### Merge-Logik (Observed — korrekt)

```typescript
// AnalysisContext.tsx:141
batna_description: ei.batna_description ?? prior.batna_description,
```

Die Merge-Logik ist korrekt: `null ?? prior` behält bestehenden Wert. Dies ist kein Bug.

---

## Root Cause — BUG-20260521 (Observed + Inferred)

| Punkt | Status |
|-------|--------|
| `progressStatus` ist local state in Index.tsx (line 92) | **Observed** |
| `progressStatus` wird bei unmount/remount auf null gesetzt | **Observed** |
| `contextDerivedProgress.batna` liest aus `extractedInputs.batna_description` (line 155) | **Observed** |
| `extractedInputs` wird in localStorage persistiert (AnalysisContext.tsx) | **Observed** |
| BUG-20260529 → `extractedInputs.batna_description` ist null → Navigation zeigt BATNA verloren | **Inferred** |

---

## Betroffene Dateien

| Datei | Repo | Relevanz |
|-------|------|----------|
| `supabase/functions/chat/index.ts` | negotiation-buddy | EF extract — Prompt + Antwortformat |
| `src/pages/Index.tsx:449-526` | negotiation-buddy | NC-CONTEXT A Extraktion |
| `src/hooks/useProgressEngine.ts:82-180` | negotiation-buddy | One-shot runExtractInputs |
| `src/contexts/AnalysisContext.tsx` | negotiation-buddy | extractedInputs Persistenz |

---

## Kopplungsrisiken

- **EF-Änderung** am extract-Prompt ändert das Antwortformat → NC-CONTEXT A muss Feldnamen anpassen
- **Prompt-Änderung** beeinflusst alle EF-Nutzer die `mode: 'extract'` aufrufen
- `runExtractInputs` one-shot ist bewusst (Kosten-Kontrolle) — nicht anfassen

---

## Nicht einsehbar (Missing)

- Tatsächliche EF-Antwort für einen BATNA-Input im Produktions-Kontext
- Ob Haiku den Prompt als "letzte Nachricht" oder "gesamte Konversation" interpretiert
- Ob die EF-Call-Kette erfolgreich feuert (kein Console-Log vorhanden)

---

## Empfohlener Fix-Scope

**Minimal:**

Option A — EF extract prompt reparieren: "die folgende Nachricht" → "die folgende Konversation" + explizite Anweisung alle Nachrichten zu scannen.

Option B — Falls Option A reicht: kein Frontend-Code-Change nötig. NC-CONTEXT A liest bereits `alternatives` korrekt.

**Laufzeit-Evidenz vor Fix erforderlich** → Phase 1.5 Gate nicht erfüllt.

---

## Phase 1.5 Logging-Instruktionen

Füge temporäre `// DEBUG-TEMP` Logs in `Index.tsx` NC-CONTEXT A (Zeile ~466) ein:

```typescript
// DEBUG-TEMP
console.log('[NC-CONTEXT A] firing, attempt:', extractionAttemptsRef.current,
  'batnaStillMissing:', batnaStillMissing,
  'messages count:', chatMessages.length);

// nach resp.json():
// DEBUG-TEMP
console.log('[NC-CONTEXT A] EF response:', JSON.stringify(data));
console.log('[NC-CONTEXT A] newBatna:', newBatna, '| opponentMax:', opponentMax);
```

**Ausführen mit:**
1. Chat starten, im zweiten Turn BATNA eingeben: "Ich habe ein Angebot von einer anderen Firma über 78.000€"
2. DevTools Console öffnen → NC-CONTEXT A Logs prüfen
3. Beobachten: feuert der Log? Was gibt `data.extracted` zurück?

---

## Evidenz-Report

**Evidenzquelle:** (1) DEBUG-TEMP Console-Logs aus Production (User-Screenshots) + (2) curl-Replikation
des EF-Anthropic-Calls (gleiches Modell `claude-haiku-4-5-20251001`, gleicher extract-Prompt)

**Tatsächlicher Output (Production, NC-CONTEXT A):**
```
[NC-CONTEXT A] firing — attempt: 1 | batnaStillMissing: true | messages count: 2
[NC-CONTEXT A] EF response: {"extracted":{}}
[NC-CONTEXT A] newBatna: null | opponentMax: null | will update: false
```
→ EF liefert `{"extracted":{}}` — `alternatives` fehlt komplett.

**Tatsächlicher Output (curl-Replikation, generische 2-Message-Konversation):**
```
extractData.content[0].text =
"\n\nDamit ich dir die besten Strategien geben kann, benötige ich noch ein paar Details:

- **Details**: ...
- **Goal**: ...
- **Counterpart**: ...
- **Alternativen**: ...

```json
{
  \"details\": null,
  \"goal\": null,
  \"counterpart\": null,
  \"alternatives\": null
}
```

Bitte ergänz die Informationen..."
```

**Bestätigte Fehlerursache (Observed):**

Claude folgt der Anweisung "Antworte NUR mit validem JSON" nicht zuverlässig — bei früh-/generischen
Konversationen antwortet Claude im Coaching-Ton (volle Prosa) mit eingebettetem ` ```json `-Block.

Die EF-Parsing-Logik
```js
const jsonStr = content.replace(/```json\s*/g, "").replace(/```\s*/g, "").trim();
parsed = JSON.parse(jsonStr);
```
entfernt nur die Fence-Marker, nicht den umgebenden Fließtext. Der resultierende String beginnt mit
"Damit ich dir..." → `JSON.parse` wirft → Catch-Fallback `{details:null, goal:null, counterpart:null,
alternatives:null}` (4 Null-Keys) bzw. in anderen Fällen literal `{}` → `data.extracted.alternatives`
ist immer `null`/`undefined` → NC-CONTEXT A kann `batna_description` nie setzen.

**Klassifizierung:** Observed (Production-Logs + curl-Replikation stimmen im Endergebnis überein:
`alternatives` nie gesetzt). Root Cause der EF-Parsing-Fragilität ist Observed (Code + Replikation).

**Fix-Scope (final):** EF-Parsing in `chat/index.ts` extract-mode auf 3-stufiges Regex-Fallback
umstellen (analog `chatHelpers.ts::parseChatResponse`). Kein Prompt-Change nötig — NC-CONTEXT A
liest `alternatives` bereits korrekt (Option B bestätigt).

---

## Status: GO erteilt (2026-06-10) — Phase 3 durchgeführt + deployed

EF `chat` deployed via Supabase MCP — version 6, status ACTIVE,
project `gpllrgkuozytyrmpfwbb`, verify_jwt: false (unverändert, ADR-004-konform).
