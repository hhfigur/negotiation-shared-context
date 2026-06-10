# BUG-20260521-batna-lost-after-nav

**Erstellt:** 2026-05-21
**Status:** DONE
**Risiko:** P1
**TARGET REPO:** negotiation-buddy (primary), negotiationcoach-backend (secondary — Persistenz-Pfad)
**Layer:** Layer 0 — Session Persistence / Layer 1 — extractedInputs
**Bug-Typ:** Data-Bug (State-Verlust bei Navigation)
**Betroffene Tiers:** Alle
**ADR-Constraints:** ADR-002 (Data Ownership), ADR-001 (Backend kanonisch)

## Symptom
Ein im Chat eingegebenes BATNA wird korrekt erkannt und im Fortschritts-Indikator angezeigt. Nach Navigation zu einem anderen Tool und Rückkehr in den Chat ist das BATNA verschwunden — sowohl aus dem State als auch aus der Fortschrittsanzeige.

## Ort
- `src/pages/Index.tsx` — contextDerivedProgress.batna prüft extractedInputs.batna_description
- `src/contexts/AnalysisContext.tsx` — extractedInputs State (In-Memory, keine Persistenz)
- `src/hooks/useProgressEngine.ts` — BATNA-Tracking

## Reproduktion
1. Chat-Session starten, BATNA-Information eingeben (z. B. "Ich habe ein Angebot einer anderen Firma")
2. BATNA-Erkennung im Fortschritts-Dialog bestätigen (grüner Haken)
3. Zu ZOPA-Rechner oder anderem Tool navigieren
4. Über "← Zurück" in den Chat zurückkehren
5. Beobachten: BATNA im Fortschritts-Dialog wieder als "ausstehend" — Daten verloren

## Logs / Fehlermeldungen
- RFB-039 (Context lost on navigation) ist als aktiver offener Punkt bekannt
- extractedInputs sind In-Memory im AnalysisContext — kein DB-Persistenz-Pfad für BATNA bekannt
- Safari-Page-Reload bei Memory-Druck löscht gesamten In-Memory-State

## Verdacht
- extractedInputs werden nur im React-State gehalten, nicht in DB persistiert (Inferred)
- AnalysisContext wird beim Route-Wechsel zurückgesetzt oder neu initialisiert (Inferred)
- Fortschrittsanzeige liest aus AnalysisContext, nicht aus DB-gesichertem State (Inferred)

## Diagnose-Fragen (vor Fix zu beantworten)
1. Werden extractedInputs nach jedem Chat-Turn in die DB geschrieben? Welche Tabelle, welcher Endpunkt? (Missing)
2. Wird beim Remount von ChatInterface der letzte DB-State von extractedInputs geladen? (Missing)
3. Ist RFB-039 die Wurzelursache oder nur ein verwandter Bug? (Inferred — verifizieren)
4. Klassifiziere jeden Befund als: Observed / Inferred / Missing

## Verwandte Issues
- RFB-039 (direkt verwandt — prüfen ob zusammenführbar)
- BUG-20260521-slow-return-from-tool (gemeinsame Context-Instabilität)
- BUG-20260521-zopa-prefilled-values (gleiche Ursache: AnalysisContext-Persistenz)

## Plan
> Diagnose-Report: docs/delivery/BUG-20260521-batna-lost-after-nav-diagnosis-report.md

_Wird durch Template 1-DEV befüllt._

## Implement
_Wird durch Template 2-DEV befüllt._

## Abschluss

**Datum:** 2026-06-10
**Root Cause:** UI-Symptom von BUG-20260529 — `extractedInputs.batna_description` wurde nie persistiert,
weil die NC-CONTEXT-A-Extraktion (Supabase EF `chat`, `mode: extract`) leer/fehlerhaft zurückkam.
`progressStatus` (ephemeral, lokaler State) zeigte BATNA korrekt an, ging aber bei Remount nach
Navigation verloren. `contextDerivedProgress` (persistiert) blieb leer → BATNA "verschwand".

**Fix:** Mit BUG-20260529 zusammen gefixt — siehe dort. Kein eigenständiger Code-Change in diesem Bug.

**Diagnose-Report:** docs/delivery/bugs/BUG-BATNA-combined-diagnosis-report.md
**Verifikation:** Laufzeit-Evidenz (curl-Replikation des EF-Calls) + tsc clean. Siehe BUG-20260529.
