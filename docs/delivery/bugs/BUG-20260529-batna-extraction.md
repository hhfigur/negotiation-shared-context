# BUG-20260529-batna-extraction

**Erstellt:** 2026-05-29
**Status:** DONE
**Risiko:** P1
**TARGET REPO:** negotiation-buddy (primary), negotiationcoach-backend (secondary)
**Layer:** Layer 0 (extractedInputs Persistenz) / BC-03 (Chat & Input Extraction)
**Bug-Typ:** Data-Bug (Extraktion oder Merge-Logik — Hypothese offen)
**Betroffene Tiers:** alle
**ADR-Constraints:** ADR-002 (Data Ownership), ARCH02 (Chat-Extraktion)

## Symptom

Nutzer gibt im Chat eine BATNA-Beschreibung ein
(z.B. "Ich habe ein Konkurrenzangebot von 78.000€").
`batna_description` bleibt `null` oder leer — wird nicht in `extractedInputs`
gespeichert und steht für Layer-1-Analyse nicht zur Verfügung.

## Ort

- `negotiationcoach-backend/src/api/chatHelpers.ts` — System-Prompt + `parseChatResponse()`
- `negotiation-buddy/src/hooks/useProgressEngine.ts` — `setExtractedInputs()` Merge-Logik
- `negotiation-buddy/src/contexts/AnalysisContext.tsx` — `extractedInputs` State

## Reproduktion

1. Neue Verhandlungs-Session starten (Gehalt o.ä.)
2. Im Chat eingeben: "Ich habe ein Konkurrenzangebot von 78.000€"
3. Nach Chat-Response: `extractedInputs.batna_description` prüfen
4. Beobachten: `batna_description` bleibt `null`

## Logs / Fehlermeldungen

Kein expliziter Fehler — stilles Datenverlust-Muster. Symptom erst bei
Layer-1-Analyse sichtbar (BATNA-Stärke = 0 / keine Empfehlungen).

## Verdacht

**Drei konkurrierende Hypothesen (alle Inferred — Diagnose erforderlich):**

**Hypothese A — Extraktion im Backend schlägt fehl:**
System-Prompt in `chatHelpers.ts` erkennt BATNA-Beschreibungen nicht zuverlässig.
Claude gibt `batna_description: null` zurück obwohl BATNA im Text vorhanden.
Mögliche Ursachen: Prompt-Formulierung zu eng, `parseChatResponse()` Parse-Fehler.

**Hypothese B — Merge-Logik überschreibt BATNA:**
`setExtractedInputs()` nutzt `??`-Merge-Logik (RFB-014-Muster).
Bei einem Chat-Turn ohne BATNA-Content gibt Backend `batna_description: null` zurück.
Falls Merge-Richtung `newValue ?? prior` ist: `null ?? prior` → prior bleibt (korrekt).
Falls Merge-Richtung `prior ?? newValue` ist: sobald prior gesetzt, wird nie überschrieben.
Wenn Backend `null` explizit als Wert zurückgibt und Merge `newValue ?? prior` nutzt:
`null ?? prior` → prior bleibt (korrekt). Aber wenn `null` als "löschen" interpretiert
wird → BATNA geht verloren.
Verwandt: BUG-20260521-zopa-prefilled-values (Merge-Logik Root Cause identifiziert).

**Hypothese C — Persistenz-Problem (BUG-04-Verwandtschaft):**
BATNA wird korrekt extrahiert und gesetzt, geht aber bei Navigation verloren.
Kein Extraktions-Bug — separates Persistenz-Problem.

## Diagnose-Fragen

1. Gibt `/api/chat` bei BATNA-Input `batna_description !== null` zurück?
   → curl-Test: POST /api/chat mit `{"message": "Ich habe ein Konkurrenzangebot von 78.000€"}`
2. Wie lautet der BATNA-Extraktion-Prompt in `chatHelpers.ts`?
   Ist `batna_description` explizit im System-Prompt als zu extrahierendes Feld definiert?
3. Merge-Logik in `setExtractedInputs()`:
   `newValue ?? prior.batna_description` ODER `prior.batna_description ?? newValue`?
4. Wird `batna_description` bei einem Chat-Turn ohne BATNA-Content auf `null` gesetzt
   und überschreibt dann den bestehenden Wert?
5. Ist dies BUG-04 (Persistenz) oder ein separates Extraktion-/Merge-Problem?

## Diagnose-First-Regel (Prozess 2026-05-20)

Diagnose-Prompt ausführen → Report nach
`shared-context/docs/delivery/BUG-BATNA-EXTRACTION-diagnosis-report.md` committen →
dann erst Fix-Prompt.

## Verwandte Items

- BUG-20260521-batna-lost-after-nav — möglicherweise gleiche Ursache (Persistenz)
- BUG-20260521-zopa-prefilled-values — Merge-Logik in `setExtractedInputs()` Root Cause
- RFB-014 — fire-and-forget / Merge-Pattern (bekannte Schwachstelle)
- ARCH02 — Chat-Extraktion Spezifikation

## Plan
> Diagnose-Report: docs/delivery/BUG-BATNA-EXTRACTION-diagnosis-report.md

_Wird durch Diagnose-Prompt + Template 1-DEV befüllt._

## Implement

_Wird durch Template 2-DEV befüllt — erst nach Diagnose-Report._

## Abschluss

**Datum:** 2026-06-10
**Root Cause (Observed via curl-Replikation):** Die Supabase EF `chat` (`mode: 'extract'`)
nutzte ein naives `content.replace(/```json\s*/g,"").replace(/```\s*/g,"").trim()` +
`JSON.parse()`. Claude (Haiku 4.5) folgt der Anweisung "Antworte NUR mit validem JSON"
nicht zuverlässig — bei früh-/generischen Konversationen antwortet Claude im normalen
Coaching-Ton (Prosa) mit einem eingebetteten ` ```json ` Block. Die naive Logik entfernte
nur die Fence-Marker, ließ die umgebende Prosa aber stehen → `JSON.parse` auf
Prosa+JSON+Prosa wirft → Catch-Fallback `{details:null, goal:null, counterpart:null,
alternatives:null}` (oder in anderen Fällen literal `{}`) → `data.extracted.alternatives`
immer `null`/`undefined` → NC-CONTEXT A (Index.tsx) konnte `batna_description` nie setzen,
selbst wenn der Nutzer eine BATNA explizit genannt hatte.

**Fix:** `negotiation-buddy/supabase/functions/chat/index.ts`, extract-mode Parsing auf
3-stufiges Regex-Fallback umgestellt (analog zu `chatHelpers.ts::parseChatResponse` im
Backend):
1. JSON aus ` ```json ... ``` ` Block extrahieren — auch wenn von Prosa umgeben
2. Fallback: `{...}`-Objekt mit `"alternatives"`-Feld, auch ohne Fence
3. Fallback: irgendein `{...}`-Objekt
4. Ergebnis immer mit `{details:null, goal:null, counterpart:null, alternatives:null}`
   gemerged → konsistentes Schema

**Diagnose-Report:** docs/delivery/bugs/BUG-BATNA-combined-diagnosis-report.md
**Verifikation:** curl-Replikation des EF-Calls (Anthropic API, gleiches Modell/Prompt)
zeigte das Prosa+JSON-Antwortmuster reproduzierbar (Observed). `npx tsc --noEmit` clean.
**Verwandt:** BUG-20260521-batna-lost-after-nav (UI-Symptom dieses Bugs — mitgefixt).
