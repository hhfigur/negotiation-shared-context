# WIKI — Index: NegotiationCoach AI

**Erstellt:** 2026-04-17
**Ablageort:** `shared-context/docs/wiki/WIKI---Index.md`
**Zweck:** Navigationszentrale für alle Governance-, Architektur- und Betriebsdokumente in `shared-context`. Jede Seite hat eine Beschreibung in einem Satz. Für operative Navigation — kein Inhaltsduplikat.

> Hinweis: `wiki/index.md` und `wiki/session-log.md` sind die Legacy-Betriebslogs aus Wave 1. Die hier verlinkten Dokumente unter `docs/wiki/` sind die vollständigen Wiki-Seiten.

---

## System-Docs

Kernarchitektur-Dokumentation — primäre Referenz vor jeder Implementierung.

| Dokument | Pfad | Beschreibung |
|---------|------|-------------|
| System Overview | `docs/system-overview.md` | Gesamtarchitektur, Runtime-Map, Datenflüsse und Integrationen |
| Bounded Contexts | `docs/bounded-contexts.md` | Sechs Bounded Contexts (BC-01–BC-06) mit kanonischem Owner und bekannten Violations |
| Source of Truth Matrix | `docs/source-of-truth-matrix.md` | Kanonischer Owner, Write-Path und Verification-Status für jede Kern-Entity |
| Auth Permission Map | `docs/auth-permission-map.md` | Auth-Flows, Tier-Gates, Permission-Violations und Auflösungshistorie |
| DB Map | `docs/db-map.md` | Tabellen-Übersicht: Felder, RLS-Status, Ownership, bekannte Migrations |

---

## Contracts

API- und Typ-Verträge — bindend für alle Frontend/Backend-Implementierungen.

| Dokument | Pfad | Beschreibung |
|---------|------|-------------|
| Frontend ↔ Backend Contract | `docs/contracts/frontend-backend.md` | Alle API-Endpunkte, Request-/Response-Typen, Transport-Tabelle und Type-Drift-Register |

---

## Architecture Decision Records (ADRs)

Entschiedene und ausstehende Architekturentscheidungen — nicht für Diskussion, nur für Referenz und Ausführung.

| ADR | Pfad | Status | Beschreibung |
|-----|------|--------|-------------|
| ADR-001 | `docs/decision-log/ADR-001-system-boundaries.md` | ✅ Entschieden | Wo Code hingehört: Browser vs. Railway vs. Supabase |
| ADR-002 | `docs/decision-log/ADR-002-data-ownership.md` | ✅ Entschieden | Wer welche Tabellen schreibt — Write-Path-Regeln |
| ADR-003 | `docs/decision-log/ADR-003-ai-provider-strategy.md` | ✅ Entschieden (permanent) | Zwei-Provider-Split: Anthropic/Railway + Gemini/Edge Function |
| ADR-004 | `docs/decision-log/ADR-004-chat-path-routing.md` | ✅ Entschieden | Edge Function ist kanonischer Chat-Pfad für alle Tiers |
| ADR-005 | `docs/decision-log/ADR-005-plan-generation-path.md` | ✅ Entschieden | Railway `/api/plan` ist kanonischer Langzeit-Pfad; `generate-plan` EF temporär |
| ADR-006 | `docs/decision-log/ADR-006-tier-mapping.md` | ✅ Entschieden; RFB-036 DONE | `subscription_tier` DB-Enum auf Railway Tier-Werte migriert |
| ADR-007 | `docs/decision-log/ADR-007-dual-layer1.md` | ⚠️ DRAFT — Entscheidung ausstehend | Dual Layer-1-Architektur: EF engine retire / migrate / adapter — Wave-2-Start-Gate |

---

## Audits

Refactor- und Audit-Dokumentation — Backlog und Findings.

| Dokument | Pfad | Beschreibung |
|---------|------|-------------|
| Refactor Backlog | `docs/audits/refactor-backlog.md` | 36 Items (RFB-001–036 + AB-001) mit Body-Entries, Summary Index, Abhängigkeitsgraph; Stand 2026-04-16 |
| Current State Report | `docs/audits/current-state-report.md` | Vollständiges Finding-Register (CRIT / HIGH / MED / LOW) mit Auflösungshistorie |
| Wave 1 Completion Gate | `docs/audits/wave1-completion-gate.md` | Formale Gate-Prüfliste; Status: CLEARED 2026-04-16 |
| Audit Dashboard | `docs/audit-dashboard.md` | Legacy-Dashboard aus Wave-1-Audit (Antigravity-Output); operative Referenz ist refactor-backlog.md |

---

## Governance

Prompt-Systeme, Audit-Runbook und Delivery-Dokumentation.

| Dokument | Pfad | Beschreibung |
|---------|------|-------------|
| GOV-01 Audit Runbook | `docs/governance/GOV-01-audit-runbook.md` | Vollständiger Audit-Workflow: Schrittfolge, Kadenz, Grundprinzipien, Commit-Punkte |
| All Prompts Audit | `docs/governance/ALL-PROMPTS-AUDIT.md` | Alle Prompt-Texte (CAI-01/02, CC-BE/FE/XR-01, LOV-01/02, CC-BL/GR-01) mit Prompt-Matrix und Step-Map |
| Delivery Controller Setup | `docs/governance/delivery-controller-setup.md` | Aktivierungspaket für Feature Delivery Controller Projekt (Claude.ai) |
| Delivery Controller Grundinstruktion | `docs/governance/delivery-controller-grundinstruktion.md` | Lean Projekt-Instruktion für Delivery Controller (Deutsche Betriebsanleitung) |

---

## Templates

Wiederverwendbare Prompt- und Workflow-Templates für den täglichen Betrieb.

| Dokument | Pfad | Beschreibung |
|---------|------|-------------|
| Claude Code Prompt Templates | `docs/claude-code-prompt-templates.md` | Template 1 (Plan) und Template 2 (Implement) für Refactor-Execution-Workflow |

---

## Delivery

Planung und Baseline für Feature-Delivery-Wellen.

| Dokument | Pfad | Beschreibung |
|---------|------|-------------|
| Initial Setup Baseline | `docs/delivery/initial-setup-baseline.md` | Vollständige Baseline des Feature Delivery Controller Projekts bei Start (2026-04-17) |
| Wave 2 Scope | `docs/delivery/wave2-scope.md` | Geordnete Delivery-Sequenz für Wave 2: ADR-007, Layer-2-Fix, Layer-3-Vorbereitung |

---

## Wiki-Seiten (docs/wiki/)

Operationsprofile, Governance-Übersichten und Inventare — vollständige Wiki-Seiten.

| Wiki-Seite | Pfad | Beschreibung |
|-----------|------|-------------|
| **Governance Baseline** | `docs/wiki/WIKI---Governance-Baseline.md` | 12 nicht verhandelbare Architekturregeln, Anti-Patterns, Entscheidungsprinzipien, aktive Restrisiken, Tier-Modell |
| **Transition Knowledge Package** | `docs/wiki/WIKI---Transition-Knowledge-Package.md` | Was aus dem alten Audit-Projekt übernommen wurde — Artefakte, Anpassungen, Lücken, DEVS01-Extrakt |
| **Skills and Commands Inventory** | `docs/wiki/WIKI---Skills-and-Commands-Inventory.md` | Vollständiges Inventar aller 42 Artefakte in 6 Gruppen (Governance, Delivery, Execution, Workflow, Controller, Knowledge) mit Redundanz- und Lückenanalyse — v1.1 (2026-04-18) |
| **Repo Profile: Backend** | `docs/wiki/WIKI---Repo-Profile-negotiationcoach-backend.md` | Vollständiges Operationsprofil des Backend-Repos: Architektur, API, Supabase-Nutzung, Risiken, Skills |
| **Repo Profile: Frontend** | `docs/wiki/WIKI---Repo-Profile-negotiation-buddy.md` | Vollständiges Operationsprofil des Frontend-Repos: Screens, Hooks, Supabase-Nutzung, Risiken |
| **Wiki Index** | `docs/wiki/WIKI---Index.md` | Dieses Dokument |
| **Delivery Controller Betriebsmodell** | `docs/wiki/WIKI---Delivery-Controller-Betriebsmodell.md` | Kanonische Betriebsdefinition: Rolle, Systemlandschaft, Produktstatus, Architekturregeln, ADR-Referenz, Tool-Routing, Standardvorgehen, Pflichtperspektiven, Pflichtartefakte, Kommunikationsstil — Established 2026-04-18 |
| **Wiki Gap Analysis** | `docs/wiki/WIKI---Wiki-Gap-Analysis.md` | Gap-Analyse der Wiki-Struktur gegen 9-Bereiche-Zielbild — offene Governance-Docs identifiziert, priorisierte Empfehlungsliste (P0–P3) — 2026-04-18 |
| **Memory Compensation Baseline** | `docs/wiki/WIKI---Memory-Compensation-Baseline.md` | Analyse des Memory-Verlusts beim Projektübergang; rekonstruierte implizite Regeln, Entscheidungsmuster, Warnhinweise; Baseline-Lückenliste — 2026-04-18 |
| **Delivery Controller Betriebshandbuch** | `docs/wiki/WIKI---Delivery-Controller-Betriebshandbuch.md` | Operative Protokolle des Delivery Controllers: Control Tower Commands, Prompt-Templates, Tool-Routing, Lernprinzipien, Session-End-Protokoll — 2026-04-18 |

---

## Features-Docs (geplant, noch nicht erstellt)

**Missing** — folgende Feature-Docs sind in Wave 2 zu erstellen.

| Dokument | Pfad (geplant) | Status | Abhängigkeit |
|---------|----------------|--------|-------------|
| Layer-3-Simulation | `docs/features/layer3-simulation.md` | ❌ Fehlt | Wave-2-Step-6 (nach Layer-2-Fix) |
| Scenario Marketplace | `docs/features/scenario-marketplace.md` | ❌ Fehlt | Wave-2-Step-8 |
| PDF Export | `docs/features/pdf-export.md` | ❌ Fehlt | Wave-2-Step-8 |
| Layer-2-Diagnose-Plan | `docs/delivery/layer2-diagnosis-plan.md` | ❌ Fehlt | Nach Wave-2-Step-2-Diagnose |

Bereits vorhanden: `docs/features/knowledge-pipeline.md` (deferred — ADR-016a erforderlich).

---

## Wiki-Zielbild — 9 Bereiche

Das vollständige Wiki deckt folgende 9 Bereiche ab. Den aktuellen
Dokumentationsstatus pro Bereich siehe `WIKI---Wiki-Gap-Analysis.md`.

1. System Overview
2. Architecture Governance
3. Audit & Refactoring Baseline
4. Repo Profiles
5. Supabase Governance
6. Delivery Playbook
7. Skills Catalog
8. Decisions / ADRs
9. Change Documentation Standard

---

## Aktualisierungsregeln

**Wer aktualisiert was — und wann:**

| Dokument | Aktualisiert durch | Anlass |
|---------|-------------------|--------|
| `refactor-backlog.md` | close-task Skill (Step D, G) + Delivery Controller | Nach jedem Task-Abschluss oder Deferral |
| `wiki/index.md` und `wiki/session-log.md` | close-task Skill (Step J) | Nach jedem Task-Abschluss |
| ADRs | Delivery Controller → Claude Code in shared-context | Vor jeder Architektur-Änderung |
| `docs/contracts/frontend-backend.md` | Claude Code in shared-context | Bei jedem API-Contract-Change |
| `docs/source-of-truth-matrix.md` | Claude Code in shared-context | Nach Wave-Abschluss oder Entity-Ownership-Änderung |
| `docs/bounded-contexts.md` | Claude Code in shared-context | Nach Boundary-Entscheidung oder Violation-Resolution |
| Wiki-Seiten (`docs/wiki/WIKI---*.md`) | Claude Code in shared-context | Nach wesentlichen Architektur- oder Governance-Änderungen |
| `docs/delivery/*.md` | Delivery Controller | Nach Step-Abschluss oder Wave-Transition |
| Repo-Profile (`WIKI---Repo-Profile-*.md`) | Claude Code in shared-context | Nach Layer-Start, wesentlichen Modul-Änderungen, Status-Änderungen |
| **Dieses Dokument** | Claude Code in shared-context | Wenn neue Docs hinzukommen oder Docs veralten |

**Faustregel:** Wenn ein Dokument erstellt oder ein Link hinzugefügt wird → dieses Index-Dokument aktualisieren.

---

*Dieser Index wird nicht automatisch aktualisiert. Nach jedem Wiki-Ergänzungs-Commit reviewen.*
