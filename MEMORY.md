# Working Memory

## Aktueller Stand
- Session-Save-Bug: `session_history` Tabelle fehlte im neuen Supabase-Projekt → Migration 20260519130000 deployed
- Supabase FK-Fix: `negotiation_sessions.user_id` referenzierte falsche Tabelle → Migration 20260519120000 deployed
- Edge Functions: Lovable AI Gateway → Anthropic claude-haiku (alle 5 EFs umgestellt)
- Sidebar UX: Tools-Sektion fixiert am unteren Rand, Sessions scrollbar, Timestamps entfernt
- analyze-progress: auf jede 3. AI-Antwort gedrosselt (Memory-Entlastung)
- ADR-007: implementiert — formal noch auf DECIDED setzen
- NC-PLAN-FIX / NC-L2-UI: als behoben markiert, Verhandlungsplan-Trigger aktiv

## Nicht vergessen
- Backend: Render.com (negotiationcoach-backend.onrender.com)
- Supabase: **gpllrgkuozytyrmpfwbb** (eigenes Projekt — ujnyioggxipvuxxxcivr war Lovable, aufgegeben)
- Frontend: Render.com Static Site + lokale Entwicklung mit `npm run dev` (Port 8080)
- Dev: Claude Code (nicht Lovable) — Lovable nur noch als Fallback-Editor
- Templates: T1-DEV / T2b-DEV

## Letzte Session
Datum: 2026-05-14 bis 2026-05-21

Gemacht:
- Supabase von Lovable-managed auf eigenes Projekt migriert (gpllrgkuozytyrmpfwbb)
- Edge Functions: Lovable AI Gateway → Google AI → Anthropic (wegen Quota-Problemen)
- `session_history` Tabelle erstellt (Backend schreibt dort hin, fehlte im neuen Projekt)
- `negotiation_sessions` FK-Constraint korrigiert (user_profiles → auth.users)
- Sidebar-Layout: Tools fest am unteren Rand, Sessions-Bereich scrollbar
- BATNA-Erkennung im Chat: EF-Extract-Mode-Bug gefixt, alternatives → batna_description gemappt
- SPA-Routing: `public/_redirects` für Render.com Static Site

Problem:
- Session-Save-Fehler persistiert möglicherweise noch — letzte Migration (session_history) sollte es beheben
- BATNA-Daten gehen nach Seitenreload verloren (nur In-Memory — keine localStorage-Persistenz)
- Marktdaten erscheinen erst nach ZOPA-Berechnung (enrich() wird jetzt im ZopaCalculator aufgerufen)
- Performance: Safari-Reload wegen Memory-Druck, Ursache: häufige EF-Calls → gedrosselt

## Nächster Schritt
1. Session-Save verifizieren: neue Verhandlung starten, prüfen ob Fehler noch kommt
2. Marktdaten testen: ZOPA-Rechner → Werte eingeben → Strategie-Score → Marktdaten-Sektion prüfen
3. NC-ONBOARDING unblocked sobald PostHog-Baseline (Mitte Mai 2026 → prüfen ob daten da)
4. ADR-007 formal auf DECIDED setzen in docs/decision-log/
