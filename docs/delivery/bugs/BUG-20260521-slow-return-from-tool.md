# BUG-20260521-slow-return-from-tool

**Erstellt:** 2026-05-21
**Status:** OPEN
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
_Wird durch Template 1-DEV befüllt._

## Implement
_Wird durch Template 2-DEV befüllt._

## Abschluss
_Wird durch /close-task befüllt._
