# GOV-01 — Audit Runbook & Governance System

> **Status:** Aktiv | **Typ:** Governance | **Version:** 1.0 | **Datum:** 2026-03-30
> **Zielpfad:** `shared-context/docs/governance/GOV-01-audit-runbook.md`

---

## Leitidee

Kein Prompt-Chaos, sondern ein versioniertes System:

- **Git-Docs** sind die operative Wahrheit
- **Claude.ai** ist die Steuerzentrale
- **Claude Code** macht repo-nahe Analyse, Doku und Refactoring
- **Lovable** macht Frontend-Planung und Knowledge-Sync
- **Antigravity** ist optional für wiederholbare Workflows und Übersichten, aber nicht die Architektur-Quelle

---

## Tool-Rollen

| Tool | Rolle | Pflicht |
|---|---|---|
| Git-Repos + shared-context Repo | Source of Truth für Architektur, Verträge, Audit, Cleanup | Ja |
| Claude.ai Project | Steuerung, Spezifikation, Prompt-Packs, Review | Ja |
| Claude Code | Audit, Doku-Erstellung, Cross-Repo-Synthese, Refactor | Ja |
| Lovable | Frontend-Planung, Project/Workspace Knowledge, sichere UI-Änderungen | Ja |
| Antigravity | Optionaler Workflow-Runner und Audit-Dashboard | Optional |

> **Wichtig:** Lovable sieht standardmäßig nur das Frontend-Projekt. Der relevante Teil des Shared Context muss zusätzlich in `frontend/AGENTS.md` und in Lovable Project Knowledge gespiegelt werden. Claude Code kann mit `--add-dir` mehrere Verzeichnisse gemeinsam analysieren; mit `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` lädt es dort auch `CLAUDE.md` und `.claude/rules/`.

---

## Grundprinzipien

- Git-getrackte Markdown-Dateien sind die operative Wahrheit
- Notion ist Spiegel, nicht Source of Truth
- Claude.ai ist die Steuerzentrale
- Erst Audit und Dokumentation, dann Refactoring
- Keine neuen Utilities, Services, Hooks oder Komponenten ohne Suche nach bestehender Logik
- Jede Aussage wird als `Observed`, `Inferred`, `Missing` oder `Proposed` deklariert
- Nie ein generisches Cross-Tool-Prompt erzeugen — immer tool-spezifische Prompt-Packs
- Keine Implementierung ohne Repo-Audit

---

## Verzeichnisstruktur

```text
app-workspace/
  frontend/
  backend/
  shared-context/
```

---

## Schrittfolge

### Schritt 0 — Baseline sichern

- Audit-Branch in allen drei Bereichen anlegen
- Aktuelle stabile Stände markieren
- Supabase-Schemata, Policies und relevante Umgebungsinformationen sichern
- Claude.ai Project `App Governance & Audit` anlegen

### Schritt 1 — Repo-übergreifende Instruktionsschicht festlegen

Pflichtdateien:

```text
shared-context/AGENTS.md
shared-context/CLAUDE.md
shared-context/docs/source-of-truth-matrix.md
shared-context/docs/contracts/frontend-backend.md
frontend/AGENTS.md
frontend/CLAUDE.md
backend/AGENTS.md
backend/CLAUDE.md
```

Pflichtprinzipien:
- `AGENTS.md` enthält die neutralen Regeln
- `CLAUDE.md` importiert `@AGENTS.md` und bleibt kurz
- `.claude/rules/` und `.claude/skills/` nur vorbereiten, noch nicht voreilig befüllen
- Mit `/memory` prüfen, dass `CLAUDE.md` je Repo geladen wird

```bash
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): instruktionsschicht angelegt"
```

### Schritt 2 — Backend-Audit

In `backend/` mit Claude Code ausführen.

Pflichtoutputs:
- `docs/repo-map.md`
- `docs/service-catalog.md`
- `docs/api-catalog.md`
- `docs/db-map.md`
- `docs/redundancy-register.md`
- `docs/dead-code-candidates.md`
- `docs/audit-findings.md`

```bash
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): initial backend audit baseline"
```

### Schritt 3 — Frontend-Audit

In `frontend/` mit Claude Code ausführen.

Pflichtoutputs:
- `docs/repo-map.md`
- `docs/feature-catalog.md`
- `docs/data-access-map.md`
- `docs/redundancy-register.md`
- `docs/dead-code-candidates.md`
- `docs/audit-findings.md`
- `docs/lovable-project-knowledge.md`
- `docs/lovable-workspace-knowledge.md`

```bash
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): initial frontend audit baseline"
```

### Schritt 4 — Cross-Repo-Synthese

In `shared-context/` mit Claude Code und Zugriff auf `../frontend` und `../backend`.

Pflichtoutputs:
- `docs/system-overview.md`
- `docs/bounded-contexts.md`
- `docs/source-of-truth-matrix.md`
- `docs/auth-permission-map.md`
- `docs/contracts/frontend-backend.md`
- `docs/audits/current-state-report.md`
- `docs/decision-log/ADR-001-system-boundaries.md`
- `docs/decision-log/ADR-002-data-ownership.md`

```bash
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): initial cross-repo architecture baseline"
```

### Schritt 5 — Lovable Knowledge Sync

Ausschließlich im **Plan Mode**.

- Workspace Knowledge aktualisieren
- Project Knowledge aktualisieren
- Ergebnis zurückspiegeln in:
  - `frontend/docs/lovable-workspace-knowledge.md`
  - `frontend/docs/lovable-project-knowledge.md`

```bash
git add docs/lovable-workspace-knowledge.md docs/lovable-project-knowledge.md
git commit -m "docs(lovable): sync workspace and project knowledge"
```

### Schritt 6 — Cleanup- und Refactor-Backlog

Pflichtoutput: `docs/audits/refactor-backlog.md`

Priorisierung:
- `P0`: Auth, Berechtigungen, doppelte Writes, Sicherheits- und Ownership-Probleme
- `P1`: doppelte Business-Logik, widersprüchliche Validierung, Contract-Gaps
- `P2`: redundante Hooks, Komponenten, Services, Utilities
- `P3`: Naming, Ordnerstruktur, kosmetische Bereinigung

### Schritt 7 — Guardrails installieren

Pflichtartefakte: `CLAUDE.md`, `.claude/rules/*`, `.claude/skills/*`, `docs/hook-spec.md`

Pflicht-Skills: `/session-start`, `/impact-check`, `/contract-check`, `/cleanup-audit`, `/close-task`

Pflicht-Hooks:
- `PreToolUse` für riskante Änderungen
- `Stop` für Doku-/Contract-/ADR-Prüfung vor Task-Abschluss

### Schritt 8 — Refactoring

Jedes Refactor-Item läuft in kleinen, testbaren Schritten:
1. Plan erstellen
2. Betroffene Dateien benennen
3. Seiteneffekte prüfen
4. Tests definieren
5. Docs/Contracts/ADRs aktualisieren
6. Minimal implementieren
7. Abschluss mit `/close-task`

---

## Prompt-Matrix

| Prompt-ID | Eingabeort | Zweck |
|---|---|---|
| `CAI-01` | Claude.ai Project | Audit-Steuerzentrale aufsetzen |
| `CC-BE-01` | Claude Code in `backend/` | Backend auditieren und dokumentieren |
| `CC-FE-01` | Claude Code in `frontend/` | Frontend auditieren und dokumentieren |
| `CC-XR-01` | Claude Code in `shared-context/` | Cross-Repo-Synthese |
| `LOV-01` | Lovable Plan Mode | Knowledge- und Boundary-Sync |
| `CAI-02` | Claude.ai Project | Phase reviewen und nächsten Schritt definieren |

---

## Audit-Kadenz

| Rhythmus | Umfang | Pflichtartefakte |
|---|---|---|
| Pro Änderung / PR | Mini-Update | betroffene Repo-Docs, Contract, ADR, Lovable Knowledge falls betroffen |
| Wöchentlich | Hygiene-Review | `redundancy-register`, `dead-code-candidates`, offene Verification Gaps |
| Monatlich | Light Audit | `repo-map`, `feature/service-catalog`, `data-access-map`, `db-map` |
| Quartalsweise / vor Release | Vollaudit | komplette Cross-Repo-Synthese inkl. Matrix, Contracts, ADRs, Current-State-Report |

### Mini-Update auslösen bei:
- neuen oder geänderten API-Endpunkten
- Änderungen an Request- oder Response-Strukturen
- Änderungen an Rollen, Permissions oder Auth-Flows
- neuen direkten Frontend-Datenzugriffen
- neuen Tabellen, Views, RPCs, Triggers oder RLS-Policies
- Refactorings mit Modulverschiebungen oder Ownership-Wechseln
- Änderungen an Lovable Workspace oder Project Knowledge

### Wöchentlich prüfen:
- gibt es neue Dead-Code-Kandidaten?
- gibt es neue Doppel-Logik?
- sind Verification Gaps aus der Vorwoche noch offen?
- passt Lovable Knowledge noch zu den Repo-Dokumenten?
- wurden in offenen Tasks Docs vergessen?

### Monatlich prüfen:
- stimmen `repo-map` und reale Struktur noch überein?
- stimmt `feature-catalog` oder `service-catalog` noch?
- sind `data-access-map` und `db-map` aktuell?
- wurden neue Übergangslösungen dauerhaft, obwohl sie nur temporär sein sollten?
- ist das Refactor-Backlog noch richtig priorisiert?

### Vollaudit sofort bei:
- neuem größerem Feature über Frontend- und Backend-Grenzen
- Einführung oder Ablösung einer zentralen Integration
- größeren Schemaänderungen oder Migrationen
- Umbau von Auth, Rollen oder Permissions
- Wechsel bei Datenhoheit oder Write Paths
- wiederkehrenden Seiteneffekten oder Regressionen in mehreren Bereichen
- vor Major Release, größerem Kunden-Rollout oder Team-Onboarding

### Praktische Faustregel
- Mini-Update: immer im selben Task oder Pull Request
- Hygiene-Review: jede Woche
- Light Audit: alle 4–6 Wochen
- Vollaudit: alle 3 Monate oder bei Architektur-Ereignissen sofort

---

## Definition of Done für den Audit

Der Audit ist abgeschlossen, wenn:
- jede Kern-Entität einen klaren Owner hat
- beide Supabase-Welten in der Source-of-Truth-Matrix beschrieben sind
- Frontend/Backend-Verträge dokumentiert sind
- Redundanzen Evidenz und kanonischen Owner haben
- Dead-Code-Kandidaten Evidenz und Status haben
- Lovable Knowledge mit der Repo-Wahrheit abgestimmt ist
- `AGENTS.md`, `CLAUDE.md`, Rules und Skills eingerichtet sind
- ein priorisiertes Refactor-Backlog existiert

---

## Was wir nicht tun

- kein Big-Bang-Refactor
- keine Volltext-Dokumentation jeder Codezeile
- keine Architekturentscheidungen nur im Chat
- keine neuen Utilities/Services ohne Wiederverwendungsprüfung
- keine Implementierung in Lovable bei unklarer Architektur

---

## Tages-Checkliste

1. Bin ich im richtigen Repo und Branch?
2. Ist die `CLAUDE.md` geladen?
3. Arbeite ich im Audit-, Plan- oder Implementierungsmodus?
4. Welche Docs müssen heute aktualisiert werden?
5. Gibt es Cross-Repo- oder Contract-Auswirkungen?
6. Muss ich nach diesem Schritt committen?

---

## Commit-Punkte

1. nach der Instruktionsschicht
2. nach dem Backend-Audit
3. nach dem Frontend-Audit
4. nach der Cross-Repo-Synthese
5. optional nach Lovable-Knowledge-Sync
6. danach pro Refactor-Welle

---

> **Hinweis:** Notion-Seite `GOV-01` ist der Spiegel dieses Dokuments. Git-Markdown ist die operative Wahrheit.
