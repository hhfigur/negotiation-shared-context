# WIKI — Wiki Gap Analysis

**Erstellt:** 2026-04-18
**Basis:** Delivery Controller Session — Zielbild-Prüfung
**Status:** Observed / Proposed
**Review fällig:** nach Abschluss Wave 2

---

## Zweck

Dieses Dokument dokumentiert den Abgleich der vorhandenen Shared-context-Wiki-Struktur
gegen das definierte Zielbild (9 Bereiche). Es ist Grundlage für die geordnete
Wiki-Vervollständigung in Wave 2 und Wave 3.

---

## Zielbild — 9 Bereiche

| # | Bereich | Status | Priorität |
|---|---|---|---|
| 1 | System Overview | ✅ Weitgehend vorhanden | P3 |
| 2 | Architecture Governance | ⚠️ Verteilt, kein Single-Page Reference | P1 |
| 3 | Audit & Refactoring Baseline | ✅ Vollständig vorhanden | P3 |
| 4 | Repo Profiles | ⚠️ Backend-Profil fragmentiert | P2 |
| 5 | Supabase Governance | ⚠️ Vorhanden, aber auf 4 Dateien verteilt | P2 |
| 6 | Delivery Playbook | ⚠️ Operativ vorhanden, strukturell verteilt | P2 |
| 7 | Skills Catalog | ⚠️ Funktional dokumentiert, kein eigenständiger Katalog | P2 |
| 8 | Decisions / ADRs | ⚠️ ADR-007-Inhalt zu verifizieren | P0 |
| 9 | Change Documentation Standard | ❌ Nur im Delivery-Controller-Prompt, nicht repo-seitig | P2 |

---

## Detailanalyse

### 1 — System Overview
**Status:** ✅ Weitgehend vorhanden — Observed

Vorhandene Dokumente:
- `docs/system-overview.md` — Produktziel, Systemlandschaft
- `docs/repo-map.md` — Repo-Rollen, Zusammenspiel
- `docs/bounded-contexts.md` — Bounded Contexts BC-01 bis BC-06
- `docs/auth-permission-map.md` — Supabase-Aufteilung, Auth-Flows

Ergänzungsbedarf: `docs/system-overview.md` sollte Abschnitt zur Engine-Layer-Matrix
aufnehmen (Layer 0–3, Status, Module). Aktuell nur in `initial-setup-baseline.md`
vorhanden.

Empfehlung: Kein separates Dokument nötig — Ergänzung in bestehendem system-overview.md.

---

### 2 — Architecture Governance
**Status:** ⚠️ Vorhanden, aber verteilt — Observed

Vorhandene Dokumente:
- `docs/governance/GOV-01-audit-runbook.md` — Governance-Prinzipien, Tool-Rollen
- `docs/governance/ALL-PROMPTS-AUDIT.md` — Prompt-Templates, Audit-Regeln
- `initial-setup-baseline.md` Sec. 8.1 — Workflow, Quality Rules (verteilt)
- Architekturregeln: nur im Delivery-Controller-Systemprompt vollständig

Ergänzungsbedarf: `docs/governance/architecture-guardrails.md` — Single-page Reference
für alle Architekturregeln, Non-negotiables, Anti-Patterns und Quality Rules.
Ohne dieses Dokument sind Claude-Code-Übergaben anfällig für Regelverluste.

Empfehlung: **P1 — erstellen in Wave 2, vor erstem Backend-Prompt.**

---

### 3 — Audit & Refactoring Baseline
**Status:** ✅ Vollständig vorhanden — Observed

Vorhandene Dokumente:
- `docs/audits/refactor-backlog.md` — 36 Items, Stand 2026-04-16
- `docs/audits/current-state-report.md` — Current State
- `docs/audits/audit-dashboard.md` — Dashboard
- `initial-setup-baseline.md` Sec. 4 — Lessons Learned, Memory-Kompensation
- `wave2-scope.md` Gap-Tabelle — Offene Risiken

Ergänzungsbedarf: `docs/lessons-learned.md` als standalone-Dokument optional.
Nicht kritisch — Inhalte aus initial-setup-baseline zugänglich.

Empfehlung: P3 — Wave 3 oder nach Wave-2-Abschluss.

---

### 4 — Repo Profiles
**Status:** ⚠️ Backend-Profil fragmentiert — Observed

Vorhandene Dokumente:
- `docs/wiki/WIKI---Repo-Profile-negotiation-buddy.md` — Frontend ✅
- `docs/wiki/WIKI---Repo-Profile-negotiationcoach-backend.md` — Backend ✅ (Observed: vorhanden)
- `docs/wiki/WIKI---Transition-Knowledge-Package.md` — Systemüberblick
- `AGENTS.md`, `CLAUDE.md` — shared-context Selbstdokumentation

Ergänzungsbedarf: Backend-Repo-Profil sollte Layer-Status (Layer 0–3), offene Risiken
(RFB-006, RFB-026) und Deployment-Kontext (Railway, Deno/Node.js Split) konsolidieren.
Prüfen ob `WIKI---Repo-Profile-negotiationcoach-backend.md` diese Informationen bereits
enthält — falls nicht, ergänzen.

Empfehlung: P2 — prüfen und ggf. ergänzen.

---

### 5 — Supabase Governance
**Status:** ⚠️ Vorhanden, auf 4 Dateien verteilt — Observed

Vorhandene Dokumente (verteilt):
- `docs/auth-permission-map.md` — Instanzzuordnung, Auth-Flows
- `docs/source-of-truth-matrix.md` — Entity-Ownership
- ADR-002 — Data Ownership
- `initial-setup-baseline.md` — Schema-Change-Regeln (implizit)

Ergänzungsbedarf: `docs/governance/supabase-governance.md` — konsolidierte
Single-page Reference für:
- Instanzzuordnung (Lovable vs. Railway)
- Verantwortlichkeiten (wer schreibt wohin)
- Regeln für Schema-Änderungen (nur via Migration-Files)
- Regeln für Auth / Policies / Migrations / Secrets

Empfehlung: P2 — erhöhtes Fehlerrisiko bei Migrations ohne dieses Dokument.

---

### 6 — Delivery Playbook
**Status:** ⚠️ Operativ vorhanden, strukturell verteilt — Observed

Vorhandene Dokumente (verteilt):
- `initial-setup-baseline.md` Sec. 8.1 — Prompt-Übergabe-Workflow
- `initial-setup-baseline.md` Sec. 8.2 — Tool-Routing
- `initial-setup-baseline.md` Sec. 8.3 — Governance-Rückführung
- `wave2-scope.md` — Wave-2-Delivery-Sequenz
- `docs/governance/GOV-01-audit-runbook.md` — Cross-Repo Impact (implizit)

Ergänzungsbedarf: `docs/delivery/playbook.md` — standalone Single-page Playbook.
Alle Inhalte vorhanden, aber auf 3 Dateien verteilt. Ein standalone-Dokument
eliminiert Suchaufwand bei Claude-Code-Übergaben.

Empfehlung: P2 — erstellen durch Konsolidierung bestehender Inhalte.

---

### 7 — Skills Catalog
**Status:** ⚠️ Funktional dokumentiert, kein eigenständiger Katalog — Observed

Vorhandene Dokumente (verteilt):
- `docs/wiki/WIKI---Skills-and-Commands-Inventory.md` — ✅ vorhanden
- `docs/templates/claude-code-prompt-templates.md` — 8 Prompt-Templates ✅
- `initial-setup-baseline.md` Sec. 5.2 — Workflow-Skills (5 Skills)
- `initial-setup-baseline.md` Sec. 5.3 — Steuerungsmechanismen
- `docs/governance/ALL-PROMPTS-AUDIT.md` — Prompt-IDs Matrix

Ergänzungsbedarf: Prüfen ob `WIKI---Skills-and-Commands-Inventory.md` bereits
Nutzungshinweise und Pflegestatus enthält. Falls nicht: dort ergänzen.
Kein neues Dokument nötig wenn WIKI-Datei vollständig ist.

Empfehlung: P2 — WIKI-Datei prüfen und ggf. Nutzungshinweise + Pflegestatus ergänzen.

---

### 8 — Decisions / ADRs
**Status:** ⚠️ Eine kritische Lücke — Observed / Missing

Vorhandene Dokumente:
- ADR-001 bis ADR-006: `docs/decision-log/` — ✅ entschieden
- ADR-007: Datei `docs/decision-log/ADR-007-dual-layer1.md` — vorhanden als Datei

**Missing:** ADR-007-Inhalt unbekannt. Datei existiert laut Projektstruktur, war aber
in `initial-setup-baseline.md` (Stand 2026-04-16) als ❌ FEHLT markiert.
Inferred: ADR-007 ist Placeholder oder Draft, noch nicht inhaltlich entschieden.

Ergänzungsbedarf: ADR-007-Inhalt verifizieren. Wenn nur Placeholder → entscheiden
(VG-06: Option A/B/C für Dual-Layer-1) und füllen. Das ist Wave-2-Start-Gate.

Empfehlung: **P0 — Blocker. Erste Aufgabe Wave 2.**

---

### 9 — Change Documentation Standard
**Status:** ❌ Nicht repo-seitig dokumentiert — Missing

Vorhandene Dokumente (nur im Prompt):
- Delivery-Controller-Systemprompt — Pflichtartefakte, Pflichtfelder ✅
- `wave2-scope.md` — Pflichtartefakte pro Step ✅ (wave-spezifisch)
- `initial-setup-baseline.md` — Mindestandards (verteilt)

Ergänzungsbedarf: `docs/governance/change-doc-standard.md` — repo-seitiges Dokument
mit Pflichtfeldern für größere Änderungen, Definition of Done für Dokumentation,
Mindestdokumentation pro Änderungstyp (Bug / Feature / Architecture / UX).

Ohne repo-seitiges Dokument geht dieses Wissen verloren wenn das Delivery-Controller-
Projekt gewechselt oder neu aufgesetzt wird.

Empfehlung: P2 — erstellen als Teil der Governance-Konsolidierung.

---

## Priorisierte Empfehlungsliste

### P0 — Blocker (sofort, Wave-2-Start-Gate)

| Aktion | Zieldokument | Tool |
|---|---|---|
| ADR-007 verifizieren und VG-06 entscheiden | `docs/decision-log/ADR-007-dual-layer1.md` | Claude Code in `shared-context` |

### P1 — Hohe Priorität (vor erstem Backend-Prompt in Wave 2)

| Aktion | Zieldokument | Tool |
|---|---|---|
| Architektur-Guardrails konsolidieren | `docs/governance/architecture-guardrails.md` | Claude Code in `shared-context` |

### P2 — Mittlere Priorität (parallel zu Wave-2-Delivery)

| Aktion | Zieldokument | Tool |
|---|---|---|
| Delivery Playbook konsolidieren | `docs/delivery/playbook.md` | Claude Code in `shared-context` |
| Skills Catalog prüfen und vervollständigen | `docs/wiki/WIKI---Skills-and-Commands-Inventory.md` | Claude Code in `shared-context` |
| Supabase Governance konsolidieren | `docs/governance/supabase-governance.md` | Claude Code in `shared-context` |
| Backend Repo Profile prüfen und ergänzen | `docs/wiki/WIKI---Repo-Profile-negotiationcoach-backend.md` | Claude Code in `shared-context` |
| Change Documentation Standard | `docs/governance/change-doc-standard.md` | Claude Code in `shared-context` |

### P3 — Niedrige Priorität (Wave 3 / nach Wave-2-Abschluss)

| Aktion | Zieldokument | Tool |
|---|---|---|
| Engine-Layer-Matrix in System Overview | `docs/system-overview.md` | Claude Code in `shared-context` |
| Feature-Docs für Layer-3 / Marketplace / PDF | `docs/features/layer3-*.md` | Claude Code in `shared-context` |
| Lessons Learned standalone | `docs/lessons-learned.md` | Claude Code in `shared-context` |

---

## Strukturelle Empfehlung

Kein Umbau der bestehenden Struktur erforderlich. Die vorhandene Verzeichnisstruktur
ist korrekt. Alle identifizierten Lücken sind Ergänzungen, keine Umstrukturierungen.
Das Zielbild aus `initial-setup-baseline.md` bleibt gültig.

---

*Dieses Dokument ist nach Abschluss von Wave 2 zu reviewen und ggf. zu aktualisieren.*
