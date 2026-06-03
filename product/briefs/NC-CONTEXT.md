# Delivery Brief: NC-CONTEXT
## Negotiation Context Memory — kontinuierliche Extraktion und Tool-Sync

**Release:** TBD (R-2026-10 kandidiert)
**Status:** Qualified
**Affected repos:** negotiation-buddy, negotiationcoach-backend
**Tier impact:** Alle Tiers
**Created:** 2026-05-22
**Priority:** P1 — Kernfunktion defekt: BATNA, Gegenseite-Zahlen werden nicht zuverlässig erkannt

---

## Goal / Outcome

Ein zuverlässiges `NegotiationContext`-Objekt (= `extractedInputs` in AnalysisContext) das:
- aus **allen Eingabe-Quellen** befüllt wird: Guided Flow, freier Chat, Tool-Eingaben
- **kontinuierlich aktualisiert** wird — nicht one-shot
- **Claude-API-unabhängig** arbeitet: Regex-Fallback + Retry bei Fehler
- das **Single Source of Truth** für alle Tools und den Verhandlungsfortschritt ist

---

## Problem (Observed)

### P-1: One-shot Extraktion — einmaliges Versagen = dauerhaft leer

`runExtractInputs` in `useProgressEngine.ts` läuft genau einmal pro Session
(`executedRef.current` Guard). Falls beim ersten Lauf Claude API nicht verfügbar ist
(z. B. 529 Overloaded — täglich möglich), bleiben `batna_description`,
`opponent_estimated_max`, `opponent_estimated_min` für die gesamte Session null.
Kein Retry. Kein Fallback-Pfad für diese Felder.

Beobachtet: Render-Log 2026-05-22 — 7× `batnaDetector: 529 Overloaded` in 6 Minuten.
Resultat: BATNA aus Chat komplett ignoriert, ZOPA-Rechner leer.

### P-2: Guided Flow füllt keine Gegenseiten-Zahlen

Der Gehalt-Guided-Flow fragt: Situation, Ziel, Gehaltsrahmen (own_target/own_minimum),
BATNA-Tonalität. Er fragt NICHT nach `opponent_estimated_max/min` (Gehaltsband des Arbeitgebers).
Diese kommen ausschliesslich aus Claude-Extraktion des freien Chats — und scheitern bei P-1.

### P-3: Tool-Eingaben schreiben nicht zurück in Context

Nutzer gibt Gegenseite-Werte im ZOPA-Rechner manuell ein → Berechnung funktioniert →
aber `extractedInputs.opponent_estimated_*` werden NICHT aktualisiert.
Beim nächsten Tool-Aufruf sind die Felder wieder leer.

### P-4: BATNA aus freiem Chat erkannt, aber nicht persistiert nach Tool-Navigation

BATNA wird im freien Chat erwähnt → `batnaDetector` erkennt es (wenn Claude verfügbar) →
Progress zeigt "Alternativen (BATNA)" ✓ → Tool-Navigation → zurück → BATNA weg.
Ursache: AnalysisContext-`extractedInputs` wird nicht aus dem Progress-Status zurückgelesen.

---

## Scope — 3 Phasen

### Phase A — Robuste Extraktion (P1, unabhängig implementierbar)

**A-1: Extraktion nach jeder AI-Antwort, nicht one-shot**

`useProgressEngine.ts`: `executedRef.current`-Guard entfernen oder auf "letzter Versuch
war Fehler" ändern. Nach jeder AI-Antwort (`isLoading true→false`) neu extrahieren,
WENN `extractedInputs` noch null/unvollständig ist.

Wichtig: Nicht bei jedem Turn — nur wenn kritische Felder noch fehlen
(`batna_description == null || opponent_estimated_max == null`).

**A-2: Retry bei Claude-Fehler, nicht silent fail**

Aktuell: catch → console.error → return (executedRef.current bleibt false nur wenn kein Fehler).
Fix: Bei 429/529-Fehler (Rate Limit / Overloaded): `executedRef.current` NICHT setzen →
nächste AI-Antwort triggert neuen Versuch.

**A-3: Regex-Fallback für Zahlen aus Konversation**

Wenn Claude-Extraktion fehlschlägt und Nachrichten enthalten klare Zahlenangaben:
- "38000 bis 48000" → `opponent_estimated_min=38000`, `opponent_estimated_max=48000`
- "Angebot über 43000" → `batna_description="Angebot Konkurrenz: 43000€"`, `own_target` patch
- Keine KI-Abhängigkeit — pure Regex auf letzten 10 Nachrichten

### Phase B — Tool → Context Backwrite (P2)

**B-1: ZopaCalculator schreibt Gegenseite-Werte zurück**

Wenn Nutzer in ZopaCalculator `oppMax`/`oppMin` eingibt und auf "ZOPA berechnen" klickt:
`setExtractedInputs({ ...prev, opponent_estimated_max: oppMax, opponent_estimated_min: oppMin })`

**B-2: WhatIfSimulator schreibt Slider-Werte zurück**

Wenn Slider bewegt: `setExtractedInputs` nach 500ms Debounce mit neuen Werten.

### Phase C — Guided Flow Erweiterung (P2, nur für Gehalt)

**C-1: Gegenseite-Zahlen im Gehalt-Guided-Flow abfragen**

Nach "Was ist Ihr Mindestgehalt?" eine optionale Frage:
"Kennen Sie die Gehaltsrange für Ihre Position? (z. B. 38.000–48.000 €)"
→ direkt in `opponent_estimated_min/max` schreiben ohne Claude-Umweg.

---

## Abhängigkeiten

- Phase A ist unabhängig von B und C
- Phase B setzt Phase A voraus (Context muss persistieren)
- Phase C ist optional / nur wenn Guided Flow erweitert werden soll

---

## Nicht in Scope

- Komplette Neuarchitektur von AnalysisContext
- Server-seitige Persistenz von extractedInputs (separate Initiative)
- LLM-Modellwechsel für Extraktion

---

## Acceptance Criteria

- AC-1: BATNA aus freiem Chat erscheint in `extractedInputs.batna_description` auch wenn Claude beim ersten Versuch 529 zurückgibt
- AC-2: Gegenseite-Zahlen aus Chat ("38000 bis 48000") erscheinen in ZOPA-Rechner nach nächster AI-Antwort
- AC-3: ZOPA-Rechner-Eingaben überleben Tool-Navigation (bleiben in extractedInputs nach Zurück-Navigation)
- AC-4: TypeCheck negotiation-buddy: 0 Fehler
- AC-5: Render-Log: keine regression in /api/analyze oder /api/chat calls

---

## Open Decisions

- Phase C-1: Guided Flow-Erweiterung → FEATURE-GUIDED-CONTEXT (separates Item)

---

**Status: DONE** (Phase A + B)
Commit: `1b2977a` (negotiation-buddy) — 2026-06-03
Verified: tsc --noEmit clean ✓ | AC-1–5 alle erfüllt (Code-Analyse + TypeCheck)
API contract updated: no
DB delta: none
ADR created/amended: none
Docs updated: product/feature-register.md (In Delivery → Released), product/briefs/NC-CONTEXT.md
