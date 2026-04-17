# README-AUDIT.md

## Audit Runbook für [APP_NAME]

### Ziel
Dieses Runbook stellt sicher, dass Frontend, Backend und die gemeinsame Architektur wieder unter eine belastbare, versionierte Steuerung kommen. Es verhindert Architektur-Drift, doppelte Business-Logik, vergessene Entscheidungen und riskante Seiteneffekte.

### Grundprinzipien
- Git-getrackte Markdown-Dateien sind die operative Wahrheit.
- Notion ist Spiegel, nicht Source of Truth.
- Claude.ai ist die Steuerzentrale.
- Claude Code macht Audit, Doku, Cross-Repo-Synthese und Refactoring.
- Lovable macht Frontend-Planung und Knowledge-Sync.
- Antigravity ist optional für Workflow-Orchestrierung, nicht für Architekturwahrheit.
- Erst Audit und Dokumentation, dann Refactoring.
- Keine neuen Utilities, Services, Hooks oder Komponenten ohne Suche nach bestehender Logik.
- Jede Aussage wird als `Observed`, `Inferred`, `Missing` oder `Proposed` behandelt.

### Tool-Rollen
| Tool | Rolle |
|---|---|
| Claude.ai | Control Tower, Prompt-Pack, Review, nächste Schritte |
| Claude Code | Repo-Audit, Dokumentation, Cross-Repo-Synthese, Refactor-Plan |
| Lovable | Frontend Plan Mode, Workspace/Project Knowledge, sichere Frontend-Änderungen |
| Antigravity | Optionaler Workflow-Runner und Audit-Übersicht |
| Terminal | Repo-Struktur, Branches, Commits |

### Verzeichnisstruktur
```text
app-workspace/
  frontend/
  backend/
  shared-context/
```

### Schrittfolge

#### 0. Baseline sichern
- Audit-Branch in allen drei Bereichen anlegen.
- Aktuelle stabile Stände markieren.
- Supabase-Schemata, Policies und relevante Umgebungsinformationen sichern.
- Claude.ai Project `App Governance & Audit` anlegen.

#### 1. Repo-übergreifende Instruktionsschicht festlegen
Vor dem Audit werden nur die Leitplanken angelegt.

Pflichtdateien:
- `shared-context/AGENTS.md`
- `shared-context/CLAUDE.md`
- `shared-context/docs/source-of-truth-matrix.md`
- `shared-context/docs/contracts/frontend-backend.md`
- `frontend/AGENTS.md`
- `frontend/CLAUDE.md`
- `backend/AGENTS.md`
- `backend/CLAUDE.md`

Pflichtprinzipien:
- `AGENTS.md` enthält die neutralen Regeln.
- `CLAUDE.md` importiert `@AGENTS.md` und bleibt kurz.
- `.claude/rules/` und `.claude/skills/` nur vorbereiten, noch nicht voreilig befüllen.
- Mit `/memory` in Claude Code prüfen, dass die `CLAUDE.md` je Repo geladen wird.

#### 2. Backend-Audit
In `backend/` mit Claude Code ausführen.

Ziel:
- Repo-Map, Service-Katalog, API-Katalog, DB-Map, Redundanzen, Dead-Code-Kandidaten, Audit-Findings erstellen.

Pflichtoutputs:
- `docs/repo-map.md`
- `docs/service-catalog.md`
- `docs/api-catalog.md`
- `docs/db-map.md`
- `docs/redundancy-register.md`
- `docs/dead-code-candidates.md`
- `docs/audit-findings.md`

Danach committen:
```bash
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): initial backend audit baseline"
```

#### 3. Frontend-Audit
In `frontend/` mit Claude Code ausführen.

Ziel:
- Repo-Map, Feature-Katalog, Data-Access-Map, Redundanzen, Dead-Code-Kandidaten, Audit-Findings und erste Lovable-Knowledge-Dateien erstellen.

Pflichtoutputs:
- `docs/repo-map.md`
- `docs/feature-catalog.md`
- `docs/data-access-map.md`
- `docs/redundancy-register.md`
- `docs/dead-code-candidates.md`
- `docs/audit-findings.md`
- `docs/lovable-project-knowledge.md`
- `docs/lovable-workspace-knowledge.md`

Danach committen:
```bash
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): initial frontend audit baseline"
```

#### 4. Cross-Repo-Synthese
In `shared-context/` mit Claude Code und Zugriff auf `../frontend` und `../backend` ausführen.

Ziel:
- Einzel-Audits zu einer echten Systemarchitektur zusammenführen.

Pflichtoutputs:
- `docs/system-overview.md`
- `docs/bounded-contexts.md`
- `docs/source-of-truth-matrix.md`
- `docs/auth-permission-map.md`
- `docs/contracts/frontend-backend.md`
- `docs/audits/current-state-report.md`
- `docs/decision-log/ADR-001-system-boundaries.md`
- `docs/decision-log/ADR-002-data-ownership.md`

Danach committen:
```bash
git add AGENTS.md CLAUDE.md docs/
git commit -m "docs(audit): initial cross-repo architecture baseline"
```

#### 5. Lovable Knowledge Sync
In Lovable ausschließlich im **Plan Mode**.

Ziel:
- Frontend-Grenzen und Knowledge mit der auditieren Repo-Wahrheit synchronisieren.

Danach:
- Workspace Knowledge aktualisieren.
- Project Knowledge aktualisieren.
- finalen Text zurück in diese Dateien spiegeln:
  - `frontend/docs/lovable-workspace-knowledge.md`
  - `frontend/docs/lovable-project-knowledge.md`

Optional commit:
```bash
git add docs/lovable-workspace-knowledge.md docs/lovable-project-knowledge.md
git commit -m "docs(lovable): sync workspace and project knowledge"
```

#### 6. Cleanup- und Refactor-Backlog
In `shared-context/` mit Claude Code erstellen.

Pflichtoutput:
- `docs/audits/refactor-backlog.md`

Priorisierung:
- `P0`: Auth, Berechtigungen, doppelte Writes, Sicherheits- und Ownership-Probleme
- `P1`: doppelte Business-Logik, widersprüchliche Validierung, Contract-Gaps
- `P2`: redundante Hooks, Komponenten, Services, Utilities
- `P3`: Naming, Ordnerstruktur, kosmetische Bereinigung

#### 7. Guardrails installieren
Pro Repo mit Claude Code aufsetzen.

Pflichtartefakte:
- `CLAUDE.md`
- `.claude/rules/*`
- `.claude/skills/*`
- `docs/hook-spec.md`

Pflicht-Skills:
- `/session-start`
- `/impact-check`
- `/contract-check`
- `/cleanup-audit`
- `/close-task`

Pflicht-Hooks:
- `PreToolUse` für riskante Änderungen
- `Stop` für Doku-/Contract-/ADR-Prüfung vor Task-Abschluss

#### 8. Refactoring erst jetzt
Jedes Refactor-Item läuft in kleinen, testbaren Schritten:
1. Plan erstellen
2. betroffene Dateien benennen
3. Seiteneffekte prüfen
4. Tests definieren
5. Docs/Contracts/ADRs aktualisieren
6. minimal implementieren
7. Abschluss mit `/close-task`

### Prompt-Matrix
| Prompt-ID | Eingabeort | Zweck |
|---|---|---|
| `CAI-01` | Claude.ai Project | Audit-Steuerzentrale aufsetzen |
| `CC-BE-01` | Claude Code in `backend/` | Backend auditieren und dokumentieren |
| `CC-FE-01` | Claude Code in `frontend/` | Frontend auditieren und dokumentieren |
| `CC-XR-01` | Claude Code in `shared-context/` | Cross-Repo-Synthese |
| `LOV-01` | Lovable Plan Mode | Knowledge- und Boundary-Sync |
| `CAI-02` | Claude.ai Project | Phase reviewen und nächsten Schritt definieren |

### Commit-Punkte
Es wird mindestens an diesen Stellen committed:
1. nach der Instruktionsschicht
2. nach dem Backend-Audit
3. nach dem Frontend-Audit
4. nach der Cross-Repo-Synthese
5. optional nach Lovable-Knowledge-Sync
6. danach pro Refactor-Welle

### Audit-Kadenz und Auslöser
Nicht jedes Mal ein Vollaudit. Sinnvoll ist ein vierstufiger Rhythmus.

| Rhythmus | Umfang | Zweck | Pflichtartefakte |
|---|---|---|---|
| Pro Änderung / PR | Mini-Update | Doku-Drift sofort verhindern | betroffene Repo-Docs, Contract, ADR, Lovable Knowledge falls betroffen |
| Wöchentlich | Hygiene-Review | Backlog und offene Drift-Risiken sichtbar halten | `redundancy-register`, `dead-code-candidates`, offene Verification Gaps |
| Monatlich | Light Audit | Repo-Dokus und Datenzugriffe nachziehen | `repo-map`, `feature/service-catalog`, `data-access-map`, `db-map` |
| Quartalsweise oder vor größeren Releases | Vollaudit | Systembild, Ownership und Verträge neu verifizieren | komplette Cross-Repo-Synthese inkl. Matrix, Contracts, ADRs, Current-State-Report |

#### Pflicht bei jeder Änderung
Ein sofortiges Mini-Update reicht aus, wenn sich nur ein klar abgegrenzter Bereich ändert.

Mini-Update ausführen bei:
- neuen oder geänderten API-Endpunkten
- Änderungen an Request- oder Response-Strukturen
- Änderungen an Rollen, Permissions oder Auth-Flows
- neuen direkten Frontend-Datenzugriffen
- neuen Tabellen, Views, RPCs, Triggers oder RLS-Policies
- Refactorings mit Modulverschiebungen oder Ownership-Wechseln
- Änderungen an Lovable Workspace oder Project Knowledge

#### Wöchentlich prüfen
Ein kurzer Hygiene-Review von 20 bis 30 Minuten reicht meist aus.

Wöchentlich prüfen:
- gibt es neue Dead-Code-Kandidaten?
- gibt es neue Doppel-Logik?
- sind Verification Gaps aus der Vorwoche noch offen?
- passt Lovable Knowledge noch zu den Repo-Dokumenten?
- wurden in offenen Tasks Docs vergessen?

#### Monatlich prüfen
Der Light Audit ist sinnvoll, wenn laufend entwickelt wird und mehrere Features parallel entstehen.

Monatlich prüfen:
- stimmen `repo-map` und reale Struktur noch überein?
- stimmt `feature-catalog` oder `service-catalog` noch?
- sind `data-access-map` und `db-map` aktuell?
- wurden neue Übergangslösungen dauerhaft, obwohl sie nur temporär sein sollten?
- ist das Refactor-Backlog noch richtig priorisiert?

#### Vollaudit erzwingen bei diesen Auslösern
Zusätzlich zum Rhythmus sollte ein Vollaudit sofort eingeplant werden, wenn einer dieser Fälle eintritt:
- neues größeres Feature über Frontend- und Backend-Grenzen hinweg
- Einführung oder Ablösung einer zentralen Integration
- größere Schemaänderungen oder Migrationen
- Umbau von Auth, Rollen oder Permissions
- Wechsel bei Datenhoheit oder Write Paths
- wiederkehrende Seiteneffekte oder Regressionen in mehreren Bereichen
- vor einem Major Release, größerem Kunden-Rollout oder Team-Onboarding

#### Praktische Faustregel
- Mini-Update: immer im selben Task oder Pull Request
- Hygiene-Review: jede Woche
- Light Audit: alle 4 bis 6 Wochen
- Vollaudit: alle 3 Monate oder bei Architektur-Ereignissen sofort

### Definition of Done für den Audit
Der Audit ist abgeschlossen, wenn:
- jede Kern-Entität einen klaren Owner hat
- beide Supabase-Welten in der Source-of-Truth-Matrix beschrieben sind
- Frontend/Backend-Verträge dokumentiert sind
- Redundanzen Evidenz und kanonischen Owner haben
- Dead-Code-Kandidaten Evidenz und Status haben
- Lovable Knowledge mit der Repo-Wahrheit abgestimmt ist
- `AGENTS.md`, `CLAUDE.md`, Rules und Skills eingerichtet sind
- ein priorisiertes Refactor-Backlog existiert

### Was wir nicht tun
- kein Big-Bang-Refactor
- keine Volltext-Dokumentation jeder Codezeile
- keine Architekturentscheidungen nur im Chat
- keine neuen Utilities/Services ohne Wiederverwendungsprüfung
- keine Implementierung in Lovable bei unklarer Architektur

### Tages-Checkliste
1. Bin ich im richtigen Repo und Branch?
2. Ist die `CLAUDE.md` geladen?
3. Arbeite ich im Audit-, Plan- oder Implementierungsmodus?
4. Welche Docs müssen heute aktualisiert werden?
5. Gibt es Cross-Repo- oder Contract-Auswirkungen?
6. Muss ich nach diesem Schritt committen?
