# WIKI — Skills and Commands Inventory

**Klassifikation:** Observed | Inferred | Missing | Proposed
**Erstellt:** 2026-04-17
**Ablageort:** `shared-context/docs/wiki/`
**Basis:** initial-setup-baseline.md Abschnitt 5, claude-code-prompt-templates.md, GOV-01-audit-runbook.md, Repo-Profile beider App-Repos

> **Hinweis:** Prompt-Template-Volltexte stehen in `docs/governance/ALL-PROMPTS-AUDIT.md` (Audit-Workflow) und `docs/claude-code-prompt-templates.md` (Refactor-Execution). Dieses Dokument ist der Index und das Quick-Reference — keine Duplikation der Volltexte.

---

## 1. Skills — beide App-Repos

**Observed** — alle fünf Skills sind in beiden App-Repos identisch installiert:
- `negotiationcoach-backend/.claude/skills/<skill-name>/SKILL.md`
- `negotiation-buddy/.claude/skills/<skill-name>/SKILL.md`

Die kanonische Version liegt in `shared-context/.claude/skills/close-task/` (nur close-task).

### 1.1 session-start

| Attribut | Wert |
|---------|------|
| **Pfad** | `.claude/skills/session-start/SKILL.md` |
| **Status** | Aktiv (Observed, beide Repos) |
| **Zweck** | Session-Initialisierung: CLAUDE.md, AGENTS.md und Tasks laden |
| **Auslöser** | Beginn jeder Claude Code Session in einem App-Repo |
| **Verhalten** | Liest CLAUDE.md und AGENTS.md; prüft Branch-Status; lädt offene Tasks aus `tasks/todo.md`; prüft MCP-Verbindungen; reviewt `tasks/lessons.md` für relevante Patterns |
| **Voraussetzung** | Claude Code muss mit korrektem Working Directory gestartet sein |
| **Ausgelöst durch** | `/session-start` |

### 1.2 impact-check

| Attribut | Wert |
|---------|------|
| **Pfad** | `.claude/skills/impact-check/SKILL.md` |
| **Status** | Aktiv (Observed, beide Repos) |
| **Zweck** | Cross-Repo Impact Assessment vor Änderungen mit shared state / API / DB |
| **Auslöser** | Vor jeder Änderung die API-Contracts, Supabase-Schema, Auth-Flow oder geteilte Typen berührt |
| **Verhalten** | Liest relevante Docs; bewertet Auswirkung auf Frontend, Backend und shared-context; gibt GO / HOLD / NEEDS-ADR zurück |
| **Pflicht bei** | API-Endpunkt-Änderungen, Schema-Migrationen, Tier-Gate-Änderungen, neuen Tabellen, Auth-Flow-Änderungen |
| **Ausgelöst durch** | `/impact-check` |

### 1.3 contract-check

| Attribut | Wert |
|---------|------|
| **Pfad** | `.claude/skills/contract-check/SKILL.md` |
| **Status** | Aktiv (Observed, beide Repos) |
| **Zweck** | API-Contract-Verifikation vor Merge oder Ship |
| **Auslöser** | Vor jedem Merge/Ship einer Änderung mit API-Contract-Auswirkung |
| **Verhalten** | Prüft `docs/api-catalog.md` auf Aktualität; prüft `docs/db-map.md` auf Schema-Änderungen; verifiziert TypeScript-Typ-Regeneration nach Migrationen; prüft RLS-Policies für neue Tabellen |
| **Output** | Checkliste: api-catalog aktuell / db-map aktuell / Types regeneriert / RLS vorhanden |
| **Ausgelöst durch** | `/contract-check` |

### 1.4 cleanup-audit

| Attribut | Wert |
|---------|------|
| **Pfad** | `.claude/skills/cleanup-audit/SKILL.md` |
| **Status** | Aktiv (Observed, beide Repos) |
| **Zweck** | Redundanz- und Dead-Code-Check ohne Code-Änderung |
| **Auslöser** | Bei Dead-Code- oder Debt-Untersuchungen; optional vor Wave-Start |
| **Verhalten** | Read-only Analyse; durchsucht Repo nach Dead-Code-Kandidaten, Duplikaten, ungenutzten Importen; gibt strukturierten Report zurück |
| **Einschränkung** | Kein Code-Fix in dieser Session — nur Diagnose und Dokumentation |
| **Ausgelöst durch** | `/cleanup-audit` |

### 1.5 close-task

| Attribut | Wert |
|---------|------|
| **Pfad** | `.claude/skills/close-task/SKILL.md` (alle drei Repos) |
| **Kanonisch** | `shared-context/.claude/skills/close-task/` |
| **Status** | Aktiv (Observed, alle Repos) |
| **Zweck** | Atomischer Task-Abschluss mit Verifikation, Docs-Update und Backlog-Stempel |
| **Auslöser** | Vor jedem DONE-Stempel auf einem Backlog-Item |
| **Parameter** | `ITEM_ID=<RFB-xxx>` `COMMIT=<hash>` `REPO=<repo-name>` `DATE=<YYYY-MM-DD>` |
| **Schritte** | A: Backlog lesen / B: Entry finden / C: DONE-Check / D: Entry-Stempel / E: Summary-Index finden / F: ✅-Check / G: Summary-Index-Stempel / H: Output / I: Git-Befehle (zwei Commits: Impl-Repo + shared-context) / J: wiki/index.md und session-log.md aktualisieren |
| **Ausgelöst durch** | `/close-task ITEM_ID=RFB-xxx COMMIT=<hash> REPO=<repo> DATE=<datum>` |

**Zwei-Commit-Pattern (Step I):**
```bash
# Commit 1 — Implementation Repo
git add <changed files>
git commit -m "<implementation commit message>"

# Commit 2 — shared-context (Backlog + Wiki)
cd ../shared-context
git add docs/audits/refactor-backlog.md wiki/index.md wiki/session-log.md
git commit -m "docs(backlog): close <ITEM_ID> — <short title> <COMMIT>"
```

---

## 2. Prompt-Templates (Quick Reference)

**Observed** — Volltexte in `docs/claude-code-prompt-templates.md` und `docs/governance/ALL-PROMPTS-AUDIT.md`.

### 2.1 Refactor-Execution-Templates (täglicher Betrieb)

| Template | Trigger-Phrase | Tool | Mode | Zweck | Wann einsetzen |
|----------|---------------|------|------|-------|---------------|
| **Template 1 — Plan** | `PLAN ONLY. DO NOT CHANGE CODE YET.` | Claude Code (Ziel-Repo) | normal oder plan | Planungsschritt für jeden Backlog-Item | Immer zuerst, bevor Code berührt wird |
| **Template 2 — Implement** | `IMPLEMENT THE APPROVED PLAN ONLY.` | Claude Code oder Lovable | normal | Implementierung nach GO-Entscheidung | Nur nach dokumentiertem GO aus Template-1-Review |
| **CC-RP-01** | `Plan only. Do not write code yet.` | Claude Code (Ziel-Repo) | `--permission-mode plan` | Einzelnen Backlog-Item planen | Äquivalent Template 1, formaler |
| **CC-RI-01** | `Implement only the approved plan for [ITEM_ID]` | Claude Code oder Lovable | normal | Einzelnen Backlog-Item implementieren | Äquivalent Template 2, formaler |

**Workflow-Sequenz:**
```
Template 1 → Review → GO / HOLD / SPLIT / BACK TO DOCS → Template 2
```
Template 2 darf niemals ohne GO ausgegeben werden.

### 2.2 Audit-Workflow-Templates (Governance & Audit Projekt)

| Prompt-ID | Eingabeort | Zweck | Wann einsetzen |
|-----------|-----------|-------|---------------|
| **CAI-01** | Claude.ai Project Chat | Audit-Steuerzentrale aufsetzen | Beim Start eines neuen Audit/Refactoring-Projekts |
| **CAI-02** | Claude.ai Project Chat | Phase-Output reviewen und nächsten Schritt definieren | Nach jedem Audit-Schritt (Backend, Frontend, Cross-Repo, Lovable-Sync) |
| **CC-BE-01** | Claude Code in `backend/` | Backend vollständig auditieren und dokumentieren | Backend-Audit-Phase |
| **CC-FE-01** | Claude Code in `frontend/` | Frontend auditieren und dokumentieren | Frontend-Audit-Phase |
| **CC-XR-01** | Claude Code in `shared-context/` (mit `--add-dir`) | Cross-Repo-Synthese und shared-context Docs erstellen | Nach Backend- und Frontend-Audit |
| **LOV-01** | Lovable Plan Mode | Lovable Knowledge- und Boundary-Sync | Nach Cross-Repo-Synthese |
| **LOV-02** | Lovable Plan Mode | Risikoreiche Frontend-Änderung vor Implementierung untersuchen | Optional; vor riskanten Lovable-Änderungen |
| **CC-BL-01** | Claude Code in `shared-context/` | Refactor-Backlog aufbauen | Nach Audit-Abschluss |
| **CC-GR-01** | Claude Code in `frontend/`, dann `backend/` | Rules, Skills und Hook-Spec installieren | Nach Backlog-Erstellung |
| **MASTER-ARCH-01** | Claude Code | One-Shot Master-Prompt für Gesamtsystem | Optional; für breite Erstinstallation |

---

## 3. Hook-Spezifikation

**Observed** — Hook-Spec ist in `docs/hook-spec.md` in beiden App-Repos dokumentiert. Hooks müssen manuell via `/hooks` in Claude Code eingerichtet werden — sie sind nicht automatisch aktiv.

### 3.1 Impact-Check-Reminder (PreToolUse)

| Attribut | Wert |
|---------|------|
| **Typ** | PreToolUse |
| **Auslöser** | Edit- oder Write-Tool-Aufruf auf Dateien in `src/api/routes.ts`, `src/api/middleware.ts`, `supabase/migrations/`, `.claude/skills/close-task/` |
| **Verhalten** | Erinnert an `/impact-check` vor API-Contract-, Schema- oder Auth-Flow-Änderungen |
| **Zweck** | Verhindert ungesehene Cross-Repo-Auswirkungen |

### 3.2 Protected-Files-Guard (PreToolUse)

| Attribut | Wert |
|---------|------|
| **Typ** | PreToolUse |
| **Auslöser** | Edit- oder Write-Tool-Aufruf auf geschützte Dateien (Liste in `.claude/rules/protected-files.md`) |
| **Verhalten** | Warnt bei Änderungsversuchen an generierten oder hochriskanten Dateien |
| **Zweck** | Verhindert versehentliche Änderungen an Dateien die gesonderte Genehmigung erfordern |

### 3.3 Contract-Update-Reminder (Stop)

| Attribut | Wert |
|---------|------|
| **Typ** | Stop (nach Task-Abschluss) |
| **Auslöser** | Am Ende jeder Session die API-Endpunkte, Typen oder Schema-Struktur geändert hat |
| **Verhalten** | Fragt ob `api-catalog.md`, `db-map.md`, `frontend-backend.md` aktualisiert wurden |
| **Zweck** | Contract-Hygiene — keine ungestempelten API-Änderungen |

### 3.4 Verification-Enforcer (Stop)

| Attribut | Wert |
|---------|------|
| **Typ** | Stop (vor Task-Abschluss) |
| **Auslöser** | Am Ende jeder Implementation-Session |
| **Verhalten** | Fordert TypeCheck (`npx tsc --noEmit`) und Test-Ausführung (`npm test`) bevor DONE markiert wird |
| **Zweck** | "Würde ein Staff Engineer das so absegnen?" — Verifikation vor Closure |

---

## 4. Tool-Routing-Tabelle

**Observed** — abgeleitet aus GOV-01-audit-runbook.md und Delivery-Controller-Betrieb.

| Arbeitskategorie | Primäres Tool | Repo |
|-----------------|---------------|------|
| Engine-Logik (Layer 1/2/3), Express-Routen, Auth-Middleware | Claude Code | `negotiationcoach-backend` |
| Supabase-Schema, RLS-Policies, Migrations | Claude Code | `negotiationcoach-backend` |
| UI-Komponenten, Screens, Frontend-Hooks, Styling | Lovable | `negotiation-buddy` |
| apiClient.ts, Frontend-API-Calls | Lovable | `negotiation-buddy` |
| Architektur-Docs, ADRs, Verträge, Wiki | Claude Code | `shared-context` |
| Cross-Repo-Koordination, Planung, Task-Briefs | Delivery Controller | Claude.ai Project |
| Governance, Audit, Refactoring-Entscheidungen | Governance & Audit | Claude.ai Project |
| Chat-Streaming (SSE), Edge Functions | Lovable | `negotiation-buddy` (Supabase EF) |
| Lovable Knowledge- und Boundary-Sync | Lovable Plan Mode | `negotiation-buddy` |

**Wichtig:** Claude Code kann mit `--add-dir ../frontend --add-dir ../backend` mehrere Repos gleichzeitig lesen. Writes sind immer nur im Working Directory erlaubt.

**Session-Start-Commands:**
```bash
# Backend-Session
cd app-workspace/negotiationcoach-backend
claude --add-dir ../shared-context

# Frontend-Session (Docs-Arbeit)
cd app-workspace/negotiation-buddy
claude --add-dir ../shared-context

# Shared-Context-Session (Architektur/Docs)
cd app-workspace/shared-context
claude --add-dir ../negotiationcoach-backend --add-dir ../negotiation-buddy
```

---

## 5. Rule-Files (beide App-Repos)

**Observed** — alle Rule-Files liegen in `.claude/rules/`.

| Rule-File | Repo | Inhalt |
|-----------|------|--------|
| `architecture.md` | Beide | Layer-Ordering, ADR-Konformität, Boundary-Regeln |
| `protected-files.md` | Beide | Liste nicht änderbare oder hochriskante Dateien |
| `api-contracts.md` | Backend | Contract-Stabilität, Breaking Changes verboten ohne ADR |
| `db-boundaries.md` | Backend | Migration-Only für Schema, RLS-Pflicht |
| `ui-boundaries.md` | Frontend | Keine Business-Logik in UI-Komponenten |
| `data-access.md` | Frontend | Kein direkter Supabase-Zugriff aus Komponenten |

---

## 6. Lücken und empfohlene Erweiterungen

**Missing / Proposed**

| Lücke | Klassifikation | Empfehlung |
|-------|---------------|-----------|
| Rate-Limiting-Pattern | Missing | Kein Rate-Limiting auf LLM-Endpunkten implementiert (R-06). Neuer Skill oder Rule: `rate-limit-guard.md` |
| Zod-Validation-Pattern | Missing | Zod installiert, nicht genutzt (R-05). Skill oder Rule: `zod-validation-required.md` für neue Endpunkte |
| Test-Coverage-Skill | Missing | Kein Skill der Test-Coverage-Gaps systematisch aufzeigt (FINDING-T04, T05 offen) |
| Layer-2-Diagnostic-Skill | Proposed | Spezialisierter Skill für Layer-2-Cache-Hit-Pfad-Verifikation (Wave-2-Step-2) |
| Logging-Pattern-Rule | Missing | Kein standardisiertes Logging-Pattern (nur `console.error`). Rule: `logging-standards.md` |
| Stripe-Webhook-Skill | Proposed | Wenn RFB-032 aktiviert wird: Skill für Webhook-Verifikation und Tier-Update-Pfad |

---

*Dieses Dokument wird bei neuen Skills, Hook-Änderungen oder Template-Erweiterungen aktualisiert.*
