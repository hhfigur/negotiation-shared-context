## Working Context
Always read MEMORY.md first — current working state.

@AGENTS.md

## Shared Product Operations Layer

@product/README.md
@product/strategy.md
@product/roadmap.md
@product/releases/current.md
@product/metrics.md

<!-- PM entry points only. Longer PM procedures live in .claude/skills/pm-*. -->
<!-- Do not import individual briefs or decisions here — load on demand. -->

---

## Cross-Repo-Betrieb

Diese Session kann aus `shared-context/` heraus in allen drei Repositories arbeiten.
Start-Befehl: `claude --add-dir ../negotiation-buddy --add-dir ../negotiationcoach-backend`

### Repo-Mapping

| TARGET REPO               | Pfad                               | Primäre Verwendung                         |
|---------------------------|------------------------------------|--------------------------------------------|
| `shared-context`          | ./                                 | ADRs, Docs, Wiki, Governance               |
| `negotiationcoach-backend`| ../negotiationcoach-backend/       | Engine, API, Schema, Migrations            |
| `negotiation-buddy`       | ../negotiation-buddy/              | Frontend (primär Lovable, CC ausnahmsweise)|

### Regel: TARGET REPO im Prompt

Jeder operative Prompt MUSS eine `SESSION CONTEXT`-Kopfzeile mit explizitem `TARGET REPO` enthalten.
Ohne diese Kopfzeile darf Claude Code keine Dateien außerhalb von `shared-context/` verändern.

### Regel: CLAUDE.md Ziel-Repo laden

Wenn `TARGET REPO ≠ shared-context`, lädt Claude Code zusätzlich:
- `../[TARGET REPO]/CLAUDE.md`
- `../[TARGET REPO]/AGENTS.md`
- `../[TARGET REPO]/.claude/rules/`

Diese Regeln haben für das TARGET REPO Vorrang vor den shared-context-Regeln,
sofern kein Widerspruch zu den nicht verhandelbaren Architekturregeln besteht.

### Regel: Git-Commits

Git-Commits erfolgen immer im TARGET REPO:
- `shared-context`: `git add ... && git commit -m "..."`
- Andere Repos: `cd ../[TARGET REPO] && git add ... && git commit -m "..."`

Commit-Format: `type(scope): beschreibung`
Typen: `feat | fix | docs | refactor | test | chore`

### Skills im Cross-Repo-Kontext

Alle Skills aus `.claude/skills/` sind in jeder Cross-Repo-Session verfügbar.
Skills laufen immer im Kontext des aktiven TARGET REPO:

| Skill            | Cross-Repo-Verhalten                                              |
|------------------|-------------------------------------------------------------------|
| `/session-start` | Lädt shared-context-Kontext + TARGET REPO CLAUDE.md + AGENTS.md  |
| `/session-end`   | Am Ende jeder Session — MEMORY.md, Lessons-Check, Session-Dump   |
| `/impact-check`  | Prüft Auswirkungen auf ALLE drei Repos, nicht nur TARGET REPO     |
| `/contract-check`| Prüft shared-context/docs/contracts/ gegen TARGET REPO           |
| `/cleanup-audit` | Read-only — läuft im TARGET REPO, schreibt nach shared-context/  |
| `/close-task`    | Commit-Verifikation im TARGET REPO + Docs-Update in shared-context|

### Architekturregeln (nicht verhandelbar, immer aktiv)

Unabhängig von TARGET REPO gelten diese Regeln in jeder Session:
- Keine Logik oder Business-Regeln ins Frontend (negotiation-buddy)
- Alle LLM-Calls: Anthropic Claude (ADR-003) — sowohl Express Backend als auch Edge Functions (alle EFs nutzen claude-haiku-4-5-20251001)
- Keine direkten Supabase-Calls aus Frontend-Komponenten
- Tier-Prüfungen immer serverseitig (RLS)
- Schema-Änderungen nur via Migration-Files, nie Supabase Dashboard
- Neue DB-Tabellen brauchen RLS-Policy bei Erstellung
- Cross-Repo-Änderungen nur nach `/impact-check`
- Layer-Abhängigkeiten: 0 → 1 → 2 → 3 (nie überspringen)
- Bis ADR-007 entschieden: keine neue Logik in Edge Function engine path

---

## Architektur-Dokumentation (`docs/ARCHITECTURE.md`)

### Pflicht-Update-Trigger

Nach jeder Änderung an folgenden Dateitypen MUSS `docs/ARCHITECTURE.md` aktualisiert werden:
- Routing-Dateien (`routes.*`, `router.*`, `app.*`, `index.ts/js`)
- API-Endpunkte oder Service-Klassen
- Auth-Logik oder Middleware
- Externe Service-Integrationen (Supabase, Anthropic, PostHog, Resend, etc.)
- Error-Handler

### Update-Prozess

1. Identifiziere, welcher der vier Abschnitte betroffen ist (User Flows / Datenflüsse / Service Boundaries / Error Handling)
2. Aktualisiere nur die betroffenen Diagramme — andere nicht überschreiben
3. Trage die Änderung ins `## Letzte Aktualisierung`-Log ein (Datum + betroffene Dateien)
4. Bestätige am Ende jeder relevanten Task: "ARCHITECTURE.md aktualisiert ✓"

### Vollständige Neugenerierung

Bei größeren Refactorings: Prompt "regenerate architecture docs" führt eine komplette Neuanalyse aller vier Abschnitte durch.
