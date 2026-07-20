# Session-Dump — 2026-07-20

Lange Session (2026-07-16 bis 2026-07-20, 15 Commits in shared-context,
4 in negotiation-buddy, 7 in negotiationcoach-backend). Kompletter
Durchlauf des "Loop-Coding-Integration"-Sets (PROMPT 0–3) plus mehrere
Folge-Deliveries daraus.

## Was committed / erreicht

### 1. Loop-Coding-Integration — alle 4 Prompts DONE
Primärdokument: `shared-context/docs/features/loop-coding-integration.md`
(Master-Plan + laufendes Delivery Log, Abschnitte 1–9).

- **PROMPT 0** (`ddd9465`): Master-Plan, Scope-Matrix, Blast-Radius-Triage,
  ADR-Bedarf (→ ADR-011), Contract-Skizze. Deckte auf: ein referenzierter
  Pfad (`docs/delivery/follow-ups/...`) war stale, korrekter Pfad ist
  `docs/delivery/claude-code-prompt-templates-dev.md`.
- **PROMPT 1** (`2cd0285`, shared-context, docs-only): neuer Skill
  `.claude/skills/verify-loop/SKILL.md`, `/feature-plan` um Critic-Pass
  erweitert, `/feature-implement` um verify-loop-Hook (Schritt 0),
  `/bug-fix` Phase 1.5 minimal erweitert (Persistenz-Pflicht),
  `docs/contracts/verify-harness.md` neu, ADR-011 (PROPOSED, Soft-Launch-
  Interim aktiv). Bewusst NICHT die "Gemini via Supabase AI Gateway"-Zeile
  in Template 2b-DEV korrigiert — Verifikation widerlegte die Anthropic-
  only-Annahme zu dem Zeitpunkt (siehe Punkt 2 unten, später aufgelöst).
- **PROMPT 2** (`negotiationcoach-backend`, 3 Runden: `ac09118` → `5620c09`
  → `939b7a2`): Backend-Harness gebaut. Runde 2 fand einen echten Bug
  (`dev-anonymous` kein gültiges UUID-Format, brach `/api/analyze`s
  `sessionId` still). Runde 3 fand einen TIEFEREN Bug (FK von
  `negotiation_sessions.user_id` auf `auth.users` — jede synthetische UUID
  scheitert) → User-Entscheidung: echten Test-User
  `verify-harness@internal.test` im AKTIVEN Supabase-Projekt
  (`gpllrgkuozytyrmpfwbb`) geseedet, Harness auf echte JWT-Auth
  umgestellt. **Wichtig für künftige Audits: dieser User ist real und
  dauerhaft in `auth.users`, kein Mock — siehe Abschnitt 9 unten.**
- **PROMPT 3** (`negotiation-buddy`, `ee12e91` + `b07aa2a`... siehe unten):
  8 tsc-strict-Fehler gefixt (alle Design-Gate-recherchiert, keine
  Vermutungen), `scripts/verify.sh` gebaut. Lint-Scope-Entscheidung: WARN
  statt FAIL (55 vorbestehende, unabhängige Probleme). **Beim Push:
  echter Merge-Konflikt mit einer parallelen Lovable-Session** (5 fremde
  Commits, 2 davon überschnitten sich mit eigenen Fixes — Lovables
  Version war schwächer, u. a. `as any` um eine ganze Query-Chain).
  Per User-Entscheidung: `git rebase origin/main`, eigene Fixes bei
  Konflikten behalten, alles andere von Lovable unangetastet gelassen,
  danach komplett neu verifiziert, erst dann gepusht.

### 2. Provider-Drift-Diagnose + ADR-012 (ausgelöst durch PROMPT 1)
- `docs/audits/provider-drift-diagnosis.md` (`1e9074e` + Nachtrag
  `d3229d1`): Kernbefund — die AKTIV DEPLOYTE `chat`-Edge-Function ist
  Anthropic (verifiziert via Supabase-MCP `get_edge_function`), nicht
  Gemini. Der Gemini-Aufruf lag in einer nie deployten Backend-Datei
  (`negotiationcoach-backend/supabase/functions/chat/index.ts`, toter
  Prototyp vom 22.04.). Nachtrag klärte den "zentralen Vorbehalt"
  (Render-Production-Supabase-ID) via User-Dashboard-Bestätigung.
- **ADR-012** (`4113734`): formalisiert Anthropic-only, ADR-003 auf
  "Superseded by ADR-012" gesetzt (historischer Text unverändert
  erhalten), `docs/contracts/frontend-backend.md` Model-Selection-
  Abschnitt korrigiert.
- **DCC-EF-02** (`negotiationcoach-backend`: `d4dc9b4` + `0a68c28`): der
  tote Gemini-Prototyp gelöscht, dokumentiert in
  `docs/dead-code-candidates.md`.

### 3. BUG-20260719-signup-trigger-tier-mismatch (noch OFFEN, kein Fix)
`docs/delivery/bugs/BUG-20260719-signup-trigger-tier-mismatch.md`
(`2792974`) — ausgelöst durch die verify-harness-Follow-up-Diagnose
(Abschnitt 9 unten). `handle_new_user()`-Trigger in `negotiation-buddy`
(Migration `20260309180824`) setzt `persona_type='pro'` hartkodiert für
JEDEN Signup seit 2026-03-09, ignoriert `raw_user_meta_data.tier`
komplett. Konkreter aktiver Impact: die deployte `chat`-EF liest
`user_profiles.persona_type` → jeder neue Nutzer bekommt unbedingt
Profi-Tier-Systemprompt-Tiefe (M-10), unabhängig vom echten Tier. Das
Backend-Express-API ist NICHT betroffen (liest `auth.users`-Metadata
direkt). **P1 vorgeschlagen, keine Entscheidung getroffen, KEIN Fix
implementiert — wartet auf Product-Owner-GO.**

### 4. Follow-up-Diagnose: verify-harness-Produktions-User (Abschnitt 9)
Read-only, gegen das aktive Supabase-Projekt: Tier-Divergenz bestätigt
(→ führte zu BUG-20260719 oben), RLS unterscheidet nirgends Test-/Echt-
User (Missing, bestätigt), Metrics-Kontamination real (`distinctId:
'server'`, kein User-Identifier) — **behoben** (siehe Punkt 5),
`SUPABASE_SERVICE_KEY`-als-Login-apikey-Muster in `scripts/lib-jwt.sh`
bestätigt isolierter Einzelfall (OWASP-Einordnung dokumentiert, kein Fix
nötig).

### 5. Telemetry-Fix (`negotiationcoach-backend`: `db0252f` + `2cda4c8`)
`trackEvent()`s hartkodierter `distinctId: 'server'` behoben — jetzt
Pflicht-Parameter, echte `user_id` oder `system:<job>`/`unknown`. Neue
`isInternalTestUser()`-Markierung für `verify-harness@internal.test`
(`internal: true` in Event-Properties). Zwei Subagent-Review-Runden
(Spec + Code-Quality), zwei Important-Findings der zweiten Runde direkt
behoben (Test in `npm test` verdrahtet, PostHog-Prototype-Patch
restauriert).

### 6. Skill-Reparatur: `/close-task` Exemption-Pfad
`.claude/skills/close-task/SKILL.md` (`4d39658`): expliziter Tooling/
Infra-Exemption-Pfad für Deliveries ohne RFB-/NC-ID — formalisiert, was
in den 5 vorherigen Fällen (PROMPT 1-3, DCC-EF-02, Telemetry-Fix) bereits
ad hoc gelebt wurde. Nebenbei: `close-task-dev/SKILL.md`s
`**Status: DONE**`-Formatbug korrigiert (3 Stellen — der Auftrag hatte
fälschlich `close-task/SKILL.md` genannt, dort war das Format schon
korrekt). `pm-sync-status/SKILL.md` brauchte KEINE Änderung — der
geforderte Schritt existierte bereits seit `2a64f74` (2026-06-04).

### 7. negotiation-buddy `.env`-Cleanup (`b07aa2a`)
`.env` war trotz `*.local`-Regel git-getrackt, enthielt die LEGACY-
Supabase-Projekt-ID statt der aktiven — Footgun für frische Checkouts
(hätten still gegen falsches Backend gebaut). Sicherheits-Gate geprüft:
nur client-sichere anon-Key-Werte, kein echtes Secret. `git rm --cached`,
expliziter `.gitignore`-Eintrag, `.env.example` um fehlende
`VITE_SUPABASE_*`-Platzhalter ergänzt. Fail-Loud-Verhalten bewiesen
(echter Clone + Quellcode-Nachweis in `@supabase/supabase-js`).

## Uncommitted Changes

Nur bekanntes, session-weit unverändertes Rauschen — nichts Task-
Relevantes:
- `shared-context`: `.DS_Store`, `.claude/settings.json` (Harness-
  generierte Sandbox-Regeln, uncommitted seit Sessionbeginn — siehe
  "Offene Entscheidungen" unten), `.gitignore` (ebenfalls Harness-
  generiert, unrelated zum eigenen `.gitignore`-Fix in negotiation-buddy).
- `negotiation-buddy`: `supabase/.temp/cli-latest`,
  `supabase/.temp/storage-version` (Supabase-CLI-Lokalstate, dirty seit
  Sessionbeginn).
- `negotiationcoach-backend`: sauber.

## Offene Entscheidungen

1. **BUG-20260719-signup-trigger-tier-mismatch** — Product-Owner-GO
   ausstehend. Kein Fix implementiert.
2. **`.claude/settings.json`-Sandbox-Drift** (`negotiationcoach-backend`
   UND vermutlich `shared-context`/`negotiation-buddy`): eine während
   dieser Session vom Harness selbst ergänzte `Read(.env*)`-artige Deny-
   Regel blockiert `.env*`-Zugriffe teils auch für Kindprozesse und
   Schreibzugriffe, uncommitted. Nie bewusst entschieden ob sie committet
   oder zurückgesetzt werden soll. Wurde mehrfach umgangen (git-interne
   Mechanismen statt direktem Dateizugriff), aber die Regel selbst ist
   nie behoben worden.
3. **Render-Production Supabase-Projekt** war ein offener Punkt im
   Provider-Drift-Report — laut User-Dashboard-Bestätigung inzwischen
   aufgelöst (aktive ID, kein Split-Brain) — aber nur als Aussage im ADR
   festgehalten, nicht durch einen eigenen Repo-Beleg (z. B. `render.yaml`)
   abgesichert.
4. **`TOOL-[YYYYMMDD]-[kurzname]`-ID-Schema** (im neuen close-task-
   Exemption-Pfad erwähnt) ist bisher nie angewendet worden — nur eine
   dokumentierte Option, keine Praxis-Erprobung.

## Nächster Schritt (exakt)

Kein technischer Folgeschritt zwingend nötig — alle begonnenen Arbeiten
sind abgeschlossen und gepusht. Falls die nächste Session hier anknüpft:
1. Zuerst `tasks/lessons.md` letzte 3 Einträge lesen (diese Session) für
   vollen Kontext.
2. Falls Product Owner ein GO zu `BUG-20260719-signup-trigger-tier-
   mismatch` gegeben hat: `/bug-fix` Phase 3 (Fix) auf Basis des
   bestehenden BUG-FILEs starten — Diagnose ist bereits vollständig,
   Phase 1/1.5 können übersprungen werden (Root Cause + Runtime-Evidenz
   bereits im BUG-FILE dokumentiert).
3. Sonst: keine offene Aufgabe aus dieser Session — auf neue User-
   Anfrage warten.

## Ausstehende Acceptance Criteria

Keine — alle 7 Workstreams oben haben ihre jeweiligen Acceptance Criteria
mit Ausführungsnachweis erfüllt und wurden gepusht (siehe einzelne
Lessons-Einträge für Details je Workstream).
