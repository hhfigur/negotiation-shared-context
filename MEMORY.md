# Working Memory

## Nicht vergessen
- Backend: Render.com (negotiationcoach-backend.onrender.com) — push main → auto-deploy
- Supabase: **gpllrgkuozytyrmpfwbb** (eigenes Projekt)
- Frontend: Render.com Static Site + lokale Entwicklung `npm run dev` (Port 8080)
- Dev: Claude Code (nicht Lovable)

## Letzte Session
Datum: 2026-06-19

Gemacht:
- BUG-20260529 + BUG-20260521 (BATNA-Extraktion): EF v7 user-only filter deployed + verifiziert (User bestätigt). Commits: `8cb4f42` (negotiation-buddy), `3c5840c` (shared-context).
- BUG-20260619-canvas-fetch-aborted: neu registriert (P2, offen). "Fetch is aborted" Toast beim Rückkehr aus Canvas — useSessionManager.ts:138.

Problem:
- BUG-20260619 noch offen (P2) — Canvas-Navigation löst AbortError im createSession-Pfad aus.

## Nächster Schritt
/bug-fix BUG-20260619-canvas-fetch-aborted — useSessionManager.ts:138 AbortController-Seiteneffekt bei Canvas-Navigation diagnostizieren und fixen.
