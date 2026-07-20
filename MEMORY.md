# Working Memory

## Nicht vergessen
- Backend: Render.com (negotiationcoach-backend.onrender.com) — push main → auto-deploy
- Supabase: **gpllrgkuozytyrmpfwbb** (eigenes Projekt)
- Frontend: Render.com Static Site + lokale Entwicklung `npm run dev` (Port 8080)
- Dev: Claude Code (nicht Lovable)

## Letzte Session
Datum: 2026-07-20

Gemacht: Loop-Coding-Integration komplett (PROMPT 0-3: verify-loop-Skill, Backend-/Frontend-Harness, ADR-011 Soft-Launch). Provider-Drift aufgeklärt (ADR-012 Anthropic-only, ADR-003 superseded, toter Gemini-Prototyp gelöscht). BUG-20260719-signup-trigger-tier-mismatch gefunden (Signup-Trigger ignoriert Tier-Metadata — offen). Telemetry-distinctId-Fix, close-task-Exemption-Pfad, negotiation-buddy .env-Tracking-Footgun behoben.
Problem: BUG-20260719 wartet auf Product-Owner-GO für den Fix. `.claude/settings.json`-Permissions-Setup vom 2026-07-18 bleibt weiterhin bewusst uncommitted.

## Nächster Schritt
Falls GO zu BUG-20260719 vorliegt: `/bug-fix` Phase 3 direkt starten (Diagnose + Runtime-Evidenz bereits vollständig im BUG-FILE). Sonst: `.claude/settings.json` + `.gitignore` (Permissions-Setup 2026-07-18) committen falls gewünscht.
