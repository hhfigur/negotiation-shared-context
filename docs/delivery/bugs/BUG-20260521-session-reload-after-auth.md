# BUG-20260521-session-reload-after-auth

**Erstellt:** 2026-05-21
**Status:** DONE
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
Diagnosis Report: `shared-context/docs/delivery/BUG-20260521-session-reload-after-auth-report.md`
Root cause: `useSessionManager.ts:46–50` — Dependency-Array `[personaType, loadSessions]` ohne Auth-Signal.
Nach Re-Login mit identischem Account ändert sich `personaType` nicht → Effekt feuert nicht → Sessions leer.

## Implement
Zwei Dateien, 4 Änderungen:
1. `useSessionManager.ts` — `authSession?.user?.id` statt `supabase.auth.getSession()` intern (R-003)
2. `useSessionManager.ts` — `authSession` in `useCallback`-Dep-Array + `useEffect`-Dep-Array
3. `useSessionManager.ts` — Error-Logging: `console.error` + `toast.error` bei Lade-Fehler
4. `Index.tsx` — `setPersona(null)` bei Logout vor early return

## Abschluss

**Status:** DONE
Commit: `e813f42` (negotiation-buddy) — 2026-05-21
Verified: tsc --noEmit clean ✓ | Spec-Review PASS (10/10) | Code-Quality APPROVED_WITH_DEBT
Debt dokumentiert: (1) kein `loadError`-State für programmatischen Retry; (2) Token-Refresh triggert `loadSessions` ~1h — benign bei aktuellem Scale
Docs updated: `shared-context/docs/delivery/BUG-20260521-session-reload-after-auth-report.md` (Diagnose)
