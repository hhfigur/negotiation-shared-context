# BUG-20260529-debrief-dialog-repeat

**Erstellt:** 2026-05-29
**Status:** OPEN
**Risiko:** P2
**TARGET REPO:** negotiation-buddy
**Layer:** Frontend
**Bug-Typ:** UI-Bug (fehlende Dismiss-Persistenz)
**Betroffene Tiers:** privat, kmu, profi
**ADR-Constraints:** keine

## Symptom

Die Debrief-Umfrage ("Wie ist deine Verhandlung gelaufen?") erscheint bei jedem
Seitenaufruf erneut, auch wenn der Nutzer sie bereits weggeklickt hat.
Nur ein vollständiges Submit (Outcome auswählen und abschicken) stoppt die Wiederholung.

## Ort

- `src/pages/Index.tsx:478–499` — `useEffect` der den Dialog auslöst
- `src/pages/Index.tsx:799` — `onDismiss` Handler (setzt nur lokalen State zurück)

## Reproduktion

1. App öffnen — Debrief-Dialog erscheint (Session 24h+ alt, kein Outcome)
2. Dialog mit X / Dismiss schließen (nicht submitten)
3. Seite neu laden
4. Dialog erscheint erneut

## Logs / Fehlermeldungen

Kein Fehler — rein visuelles/UX-Problem.

## Verdacht

`onDismiss` ruft nur `setOutcomeSessionId(null)` auf — lokaler State, nicht persistiert.
Beim nächsten Seitenaufruf ist der State weg. Der `useEffect` findet dieselbe Session
(outcome = null, 24h+ alt) und setzt `outcomeSessionId` erneut.

Es gibt keine `dismissed_at`-Spalte in der DB und keinen localStorage-Eintrag.

## Plan

Fix in `src/pages/Index.tsx`:
1. Beim Dismiss: `localStorage.setItem(`outcome_dismissed_${sessionId}`, Date.now())`
2. Im `useEffect` vor `setOutcomeSessionId`: localStorage-Check — skip wenn dismissed < 7 Tage

## Implement

_Siehe Commit._

## Abschluss

_Nach Deployment verifizieren: Dialog nicht mehr nach Dismiss beim Reload._
