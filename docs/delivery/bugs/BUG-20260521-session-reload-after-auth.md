# BUG-20260521-session-reload-after-auth

**Erstellt:** 2026-05-21
**Status:** OPEN
**Risiko:** P1
**TARGET REPO:** negotiation-buddy (primary), negotiationcoach-backend (secondary)
**Layer:** Layer 0 — Data Foundation / Session Persistence
**Bug-Typ:** Auth-Bug + Data-Bug
**Betroffene Tiers:** Alle (free, privat, kmu, profi)
**ADR-Constraints:** ADR-002 (Session-Ownership — ein Writer), ADR-001 (Backend kanonisch)

## Symptom
Nach dem Abmelden und erneuten Anmelden sind die Chat-Sessions aus der vorherigen Nutzung nicht mehr sichtbar. Der Nutzer sieht eine leere Session-Liste, obwohl Sessions in der DB vorhanden sein sollten.

## Ort
- `src/hooks/useSessionManager.ts` — Session-Lade-Logik nach Login
- `GET /api/sessions` (negotiationcoach-backend) — Session-Abfrage-Endpunkt
- `src/pages/Index.tsx` — Session-Initialisierung beim Mount

## Reproduktion
1. Anmelden und mindestens eine Verhandlung starten
2. Abmelden
3. Erneut anmelden
4. Beobachten: Session-Liste leer — keine vorherigen Sessions sichtbar

## Logs / Fehlermeldungen
- RFB-014 dokumentiert fire-and-forget-Pattern in useSessionManager.ts — Silent Failures möglich
- R-003 dokumentiert async getUser()-Race-Condition in mehreren Hooks
- Kein spezifischer Fehler-Toast sichtbar

## Verdacht
- useSessionManager lädt Sessions möglicherweise ohne korrekten User-Filter nach Re-Auth (Inferred)
- JWT-Token-Refresh nach Login wird ggf. nicht abgewartet, bevor Sessions abgerufen werden (Inferred)
- Sessions werden clientseitig im State gehalten und bei Logout nicht aus DB neu geladen (Inferred)

## Diagnose-Fragen (vor Fix zu beantworten)
1. Wird `GET /api/sessions` nach Login aufgerufen? Welcher HTTP-Status kommt zurück? (Observed/Missing)
2. Enthält der JWT beim ersten API-Call nach Login das korrekte `sub` (user_id)? (Observed/Missing)
3. Filtert useSessionManager auf `user_id` oder lädt er alle Sessions ohne Filter? (Observed/Inferred)
4. Klassifiziere jeden Befund als: Observed / Inferred / Missing

## Plan
_Wird durch Template 1-DEV befüllt._

## Implement
_Wird durch Template 2-DEV befüllt._

## Abschluss
_Wird durch /close-task befüllt._
