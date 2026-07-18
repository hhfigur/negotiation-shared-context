# Working Memory

## Nicht vergessen
- Backend: Render.com (negotiationcoach-backend.onrender.com) — push main → auto-deploy
- Supabase: **gpllrgkuozytyrmpfwbb** (eigenes Projekt)
- Frontend: Render.com Static Site + lokale Entwicklung `npm run dev` (Port 8080)
- Dev: Claude Code (nicht Lovable)

## Letzte Session
Datum: 2026-07-18

Gemacht:
- ADR-012 committed (AI Provider Strategy — Anthropic-only, ADR-003 superseded).
- Claude-Code-Permissions-Setup für shared-context: sandbox.enabled + credentials-Deny (~/.ssh, ~/.aws), stack-abgeleitete Allowlist (Scripts einzeln statt `npm run *`), Deny-Regeln (rm -rf außerhalb Baum, force-push, sudo, globale Installs, Secret-Reads inkl. Sub-Repo-Pfade), `.gitignore` um `settings.local.json` ergänzt. Globaler `/setup-permissions`-Slash-Command unter `~/.claude/commands/` angelegt.
Problem: keins — `.claude/settings.json` + `.gitignore` sind bewusst noch uncommitted (kein Commit angefragt).

## Nächster Schritt
`.claude/settings.json` + `.gitignore` in shared-context committen (sobald gewünscht), danach prüfen ob `/setup-permissions` nach Neustart im Autocomplete auftaucht.
