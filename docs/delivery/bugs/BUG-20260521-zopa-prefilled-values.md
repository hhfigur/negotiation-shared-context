# BUG-20260521-zopa-prefilled-values

**Erstellt:** 2026-05-21
**Status:** OPEN
**Risiko:** P2
**TARGET REPO:** negotiation-buddy
**Layer:** Layer 1 — Analysis Engine / Frontend State
**Bug-Typ:** Data-Bug (unbeabsichtigter State-Transfer)
**Betroffene Tiers:** privat, kmu, profi
**ADR-Constraints:** ADR-002 (Data Ownership — Frontend schreibt nicht direkt in DB)

## Symptom
Beim Aufruf des ZOPA-Rechners sind Felder bereits mit Werten befüllt, obwohl der Nutzer in dieser Session noch keine Eingaben gemacht hat.

## Ort
- `src/pages/ZopaCalculator.tsx` — Initialisierung der Formularfelder
- `src/contexts/AnalysisContext.tsx` — extractedInputs und inputs als Quelle der Vorbefüllung

## Reproduktion
1. App starten (ggf. mit bestehender Session oder nach vorheriger Session)
2. ZOPA-Rechner über Sidebar aufrufen
3. Beobachten: Felder (own_target, own_minimum, opponent_max, opponent_min) bereits befüllt — ohne eigene Eingaben in dieser Session

## Logs / Fehlermeldungen
- Keine Fehlermeldung — visuelles Symptom
- AnalysisContext ist shared state über alle Screens (impact-check Dokumentation)
- RFB-039 (Context lost on navigation) deutet auf instabilen Context-State hin — verwandtes Problem

## Verdacht
- AnalysisContext enthält persistierten State aus einer vorherigen Session, der nicht zurückgesetzt wird (Inferred)
- ZopaCalculator.tsx liest initial aus AnalysisContext statt aus leerem Default-State (Inferred)
- Alternativ: extractedInputs aus Chat-Verlauf werden automatisch in ZOPA-Felder gespiegelt — unklar ob beabsichtigt (Missing)

## Diagnose-Fragen (vor Fix zu beantworten)
1. Woher kommen die vorbefüllten Werte? Aus AnalysisContext, localStorage oder extractedInputs? (Observed/Missing)
2. Wird AnalysisContext bei Session-Start / Login zurückgesetzt? (Inferred — verifizieren)
3. Ist das Vorbefüllen aus extractedInputs ein Feature (dokumentiert?) oder ein Bug? (Missing)
4. Klassifiziere jeden Befund als: Observed / Inferred / Missing

## Verwandte Issues
- RFB-039 (Context lost on navigation) — möglicherweise gleiche Ursache

## Plan
> Diagnose-Report: docs/delivery/BUG-20260521-zopa-prefilled-values-diagnosis-report.md

_Wird durch Template 1-DEV befüllt._

## Implement
_Wird durch Template 2-DEV befüllt._

## Implement

**Fix:** Neue Action `clearExtractedInputs()` in `AnalysisContext.tsx` — setzt `extractedInputs: null`
direkt ohne `??`-Merge-Logik. Aufgerufen in `handleNewSession`, `handleSelectSession`,
`handleUseCaseStart` in `Index.tsx`. Alter 11-Felder-null-Literal in `handleNewSession` entfernt.

## Abschluss

**Status:** DONE
Commit: `3d0cb31` (negotiation-buddy) — 2026-05-26
Verified: tsc --noEmit clean ✓ | Spec-Review 10/10 PASS ✓ | Code-Quality APPROVED_WITH_DEBT (pre-existing) ✓
Docs updated: shared-context/docs/delivery/BUG-20260521-zopa-prefilled-values-diagnosis-report.md
