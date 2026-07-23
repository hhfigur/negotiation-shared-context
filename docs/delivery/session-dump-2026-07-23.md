# Session-Dump — 2026-07-23

Sehr lange Session (über Mitternacht gelaufen, mehrstündige Subagent-Läufe
für NC-L3-SIM Phase 3). Vier thematisch getrennte Blöcke.

## Was committed / erreicht

**Block 1 — Permission/Sandbox-Setup (`/setup-permissions`):**
- `shared-context` `b097a93` — stack-abgeleitete Bash-Allowlist, Sandbox
  aktiviert (Credentials-Mechanismus für `~/.ssh`/`~/.aws`), Escape-Hatch-
  Deny-Regeln (rm -rf nach außen, Force-Push, sudo, globale Installs),
  rekursive Secret-Read-Deny-Regeln. Lokale `settings.local.json` zusätzlich
  bereinigt (tote Regeln entfernt, Glob-Syntax vereinheitlicht) — nicht
  committet (gitignored, wie vorgesehen).

**Block 2 — BUG-20260719-signup-trigger-tier-mismatch (`/bug-fix`):**
- Root Cause: `handle_new_user()`-Trigger überschrieb den korrekten
  `persona_type`-Default (`'private'`) hart mit `'pro'` bei jedem Signup.
- `negotiation-buddy` `f3f3008` — Fix (CASE-Allowlist statt direktem Enum-
  Cast, sicher gegen unerwartete Metadata-Werte), Migration live auf
  `gpllrgkuozytyrmpfwbb` angewendet, Regressions-Orakel als Repro-Script
  persistiert.
- `shared-context` `9062552` — BUG-FILE Status → DONE, Diagnose-Report,
  Lessons-Eintrag.
- Beide gepusht.

**Block 3 — Roadmap-Resync (`/pm-sync-status`):**
- `shared-context` `b3a01d9` — `product/roadmap.md` war in mehreren
  Bereichen stale gegenüber `feature-register.md` (R-2026-09-Items als
  "Planned" statt Released, drei bereits released Wave-3-Teilstücke als
  komplett offen dargestellt). Vollständig resynct. Gepusht.

**Block 4 — NC-L3-SIM Phase 3 (`/feature-plan` → `/feature-implement`):**
- Planung fand einen echten Scope-Fehler (Critic-Pass): Phase 3 hing laut
  Datenfluss bereits an der L1-erweiterten `opponentEngine.ts`-Version, die
  aber erst Phase 5 vorsah. Phase 3 + ehemalige Phase 4 (Migration) +
  ehemalige Phase 5 (Refactor) zu einer Einheit konsolidiert.
- `shared-context` `51644ca` — Phase-3-Plan in `docs/features/layer3-simulation.md`.
- `negotiationcoach-backend` `007a6ee` → Task-Review fand 5 Important
  Findings (u. a. zwei echte Laufzeit-Bugs: Turn-Number-Duplikate während
  Intake, `/debrief` vertraute Client-Input statt vorhandener serverseitiger
  Status-Disambiguierung) → `b5bf2d7` (Fix) → Re-Review Approved.
- Migration live angewendet + unabhängig verifiziert
  (`simulation_sessions`/`simulation_turns` existieren auf `gpllrgkuozytyrmpfwbb`).
- `shared-context` `e1a1130` — Brief + Feature-Register aktualisiert
  (Phase 3/7, ehemalige Phase 4+5+7 darin/bereits erledigt).
- `shared-context` `6be3ab1` — Lessons-Eintrag zum Critic-Pass-/Task-Review-Fund.
- `/close-task-dev NC-L3-SIM` korrekt HALTED (Step A2, Multi-Phase-Gate) —
  Phase 6 (Frontend) fehlt noch, daher keine Released-Stempelung.

## Uncommitted Changes

Keine inhaltlichen. Nur Rauschen, nicht meins:
- `shared-context`: `M .DS_Store`
- `negotiation-buddy`: `M supabase/.temp/cli-latest`, `storage-version` (Supabase-CLI-Cache)

## Offene Entscheidungen

- **Push ausstehend:** `shared-context` 3 Commits (`51644ca`, `e1a1130`,
  `6be3ab1`), `negotiationcoach-backend` 2 Commits (`007a6ee`, `b5bf2d7`) —
  noch nicht nach `origin main` gepusht. `negotiation-buddy` ist synced.
- **Tier-Gate-Reachability-Lücke (VG-03):** bewusst akzeptiert, nicht
  gefixt — kein Produktionspfad setzt `tier='profi'` im JWT. Betrifft
  NC-L3-OPPONENT und jetzt auch NC-L3-SIM gleichermaßen. Keine Entscheidung
  getroffen, ob/wann das behoben wird (hängt an AR-032/Stripe-Go-Live).
- **NC-L3-SIM Minor-Findings vorgemerkt, nicht entschieden:** `walkaway`-
  Status-Erzeugung fehlt, RLS-Tier-Check nutzt nur `user_metadata` (nicht
  `app_metadata`-Fallback wie die App-Schicht).

## Nächster Schritt (exakt)

1. Die 5 ausstehenden Commits pushen (`shared-context`: 3, `negotiationcoach-backend`: 2) — nur noch nicht gemacht, weil nicht explizit angefragt.
2. Danach: entweder NC-L3-SIM Phase 6 (negotiation-buddy Frontend-Integration
   mit `/api/simulate/*`) via `/feature-plan NC-L3-SIM` neu anstoßen, oder
   einen der verbleibenden P2/P3-Bugs angehen (BUG-20260521-zopa-prefilled-values,
   BUG-20260619-canvas-fetch-aborted, BUG-20260529-debrief-dialog-repeat,
   BUG-20260529-l2-context-smoke-test) — beide Optionen offen, keine
   Priorität festgelegt.

## Ausstehende Acceptance Criteria

Keine offenen ACs für die in dieser Session abgeschlossenen Items — NC-L3-SIM
Phase 3 hat alle 6 curl-Tests + tsc + Task-Review bestanden. BUG-20260719 hat
RED/GREEN-Beweis + Oracle-Schärfe-Test. Roadmap-Resync und Permission-Setup
sind reine Doku-/Config-Änderungen ohne ACs.

Offen bleibt (nicht Teil dieser Session, für später vorgemerkt): NC-L3-SIM
Phase 6 hat noch keinen eigenen Plan/keine eigenen ACs — die bestehenden
Brief-ACs (AC-1 bis AC-8) decken das Gesamtfeature ab, nicht phasenspezifisch.
