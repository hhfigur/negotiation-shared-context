# BUG-20260521-marktdaten-wrong-dialog

**Erstellt:** 2026-05-21
**Status:** OPEN
**Risiko:** P2
**TARGET REPO:** negotiation-buddy
**Layer:** Layer 4 — UI/Frontend (kein Backend-Bezug)
**Bug-Typ:** UI-Bug (falsches Dialog-Routing)
**Betroffene Tiers:** kmu, profi (Marktdaten = Tier-Gate KMU+)
**ADR-Constraints:** keine direkten ADR-Implikationen — rein Frontend

## Symptom
Beim Klick auf den Marktdaten-Button wird nicht der Marktdaten-Dialog geöffnet, sondern der Dialog des Strategie-Scores. Falsches UI-Routing / falsche Event-Handler-Bindung.

Zusätzlich beobachtet: Die Berechnung des Strategie-Score selbst erscheint fehlerhaft. Wird separat als BUG-20260521-strategy-score-calc erfasst, sofern die Ursache nicht im falschen Dialog-Routing liegt.

## Ort
- `src/components/SessionSidebar.tsx` — Marktdaten-Button onClick
- Übergeordnete Komponente, die Modal/Dialog-State steuert
- `src/pages/Index.tsx` oder `src/pages/StrategyGenerator.tsx` — Dialog-Öffnungslogik

## Reproduktion
1. Eingeloggt sein mit kmu/profi-Account
2. In der Sidebar auf "Marktdaten" klicken
3. Beobachten: Strategie-Score-Dialog öffnet sich statt Marktdaten-Dialog

## Logs / Fehlermeldungen
- Kein Fehler-Toast — visuelles Symptom
- Symptom klar reproduzierbar (Observed)
- Strategie-Score und Marktdaten sind aktuell beide auf `/strategy` Route gerouted (potenzielle Ursache)

## Verdacht
- onClick-Handler am Marktdaten-Button zeigt auf den falschen Dialog-State oder die falsche Modal-Komponente (Inferred)
- Shared Modal-State-Variable (z. B. activeDialog) wird falsch gesetzt (Inferred)
- Marktdaten-Tool in Sidebar zeigt auf gleiche Route `/strategy` wie Strategie-Score — kein Differenzierungs-Mechanismus (Inferred — wahrscheinlichste Ursache)

## Diagnose-Fragen (vor Fix zu beantworten)
1. Welcher onClick-Handler ist am Marktdaten-Button registriert? (Code-Review SessionSidebar.tsx)
2. Welcher State-Wert steuert, welcher Dialog geöffnet wird? (Observed/Missing)
3. Ist die fehlerhafte Strategie-Score-Berechnung auf den falschen Aufruf-Context zurückzuführen? (Inferred)
4. Klassifiziere jeden Befund als: Observed / Inferred / Missing

## Verwandte Issues
- BUG-20260521-strategy-score-calc (ggf. Folge-Bug dieses Routing-Fehlers)

## Plan
_Wird durch Template 1-DEV befüllt._

## Implement
_Wird durch Template 2-DEV befüllt._

## Abschluss
_Wird durch /close-task befüllt._
