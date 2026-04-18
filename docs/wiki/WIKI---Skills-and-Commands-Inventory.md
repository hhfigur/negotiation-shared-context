# Skills & Commands Inventory — NegotiationCoach AI

> **Status:** Aktiv | **Typ:** Knowledge | **Version:** 1.1
> **Erstellt:** 2026-04-18 | **Basis:** Delivery-Controller-Session 2026-04-18
> **Zielpfad:** `shared-context/docs/wiki/WIKI---Skills-and-Commands-Inventory.md`

---

## Zweck dieses Dokuments

Vollständiges Inventar aller wiederverwendbaren Artefakte über alle drei Repositories
(shared-context, negotiation-buddy, negotiationcoach-backend): Prompt-Templates,
Workflow-Skills, Controller-Assets, Governance-Prozesse und Knowledge-Mechanismen.

Dieses Dokument ist die kanonische Referenz für den Delivery Controller beim Routing
von Aufgaben, beim Skill-Reuse und bei der Lückenerkennung.

---

## Gesamtübersicht

| Gruppe | Artefakte | Aktiv | Archiviert | Lücken |
|---|---|---|---|---|
| Governance Skills | 7 | 7 | 0 | 0 |
| Delivery Skills | 7 | 6 | 0 | 1 |
| Execution Skills (Prompts) | 9 | 4 | 5 | 0 |
| Workflow Skills (Repo-Ebene) | 5 | 5* | 0 | 0 |
| Controller / Tower Assets | 8 | 6 | 1 | 1 |
| Knowledge Skills | 6 | 6 | 0 | 0 |
| **Gesamt** | **42** | **34** | **6** | **2** |

*Observed als spezifiziert. Installation in `.claude/skills/` — Inferred, nicht
verified ohne aktiven Repo-Zugriff.

---

## Gruppe 1 — Governance Skills

| ID | Name | Quelle | Status |
|---|---|---|---|
| GOV-01 | Audit Runbook | `docs/governance/GOV-01-audit-runbook.md` | Observed — aktiv |
| GOV-02 | Pflichtperspektiven-Checkliste (Architekturprüfung) | Delivery Controller System Prompt | Observed — eingebettet |
| GOV-03 | ADR-Erstellungsprozess | `docs/delivery/wave2-scope.md` + ADR-Vorlagen | Observed — operativ |
| GOV-04 | Audit-Kadenz (Mini / Hygiene / Light / Vollaudit) | `GOV-01-audit-runbook.md` | Observed — aktiv |
| GOV-05 | Definition of Done (Audit-Abschluss) | `GOV-01-audit-runbook.md` | Observed — aktiv |
| GOV-06 | Tages-Checkliste | `GOV-01-audit-runbook.md` | Observed — aktiv |
| GOV-07 | Pflichtartefakte bei größeren Changes | Delivery Controller System Prompt | Observed — eingebettet |

**Bewertung:** Governance-Ebene lückenlos. Stärkste und vollständigste Gruppe.

---

## Gruppe 2 — Delivery Skills

| ID | Name | Quelle | Status |
|---|---|---|---|
| DEL-01 | Standardvorgehen bei jeder Änderung (10 Schritte) | Delivery Controller System Prompt | Observed — aktiv |
| DEL-02 | Wave-2-Scope & Delivery-Sequenz | `docs/delivery/wave2-scope.md` | Observed — aktiv, Wave-2-Start-Gate |
| DEL-03 | Impact Assessment Cross-Repo | Delivery Controller System Prompt | Observed — eingebettet |
| DEL-04 | Layer-2-Diagnose-Prompt-Vorlage | `docs/delivery/wave2-scope.md` (Step 2) | Observed — sofort nutzbar |
| DEL-05 | Abhängigkeitsgraph Wave 2 | `docs/delivery/wave2-scope.md` | Observed — aktiv |
| DEL-06 | Pflichtartefakt-Checkliste (pro Step) | `docs/delivery/wave2-scope.md` | Observed — aktiv |
| DEL-07 | Feature-Docs-Erstellungsplan (Layer-3 / Marketplace / PDF) | `docs/delivery/initial-setup-baseline.md` | Missing — Docs noch nicht erstellt |

**Offene Lücke DEL-07:**
`docs/features/layer3-simulation.md`, `docs/features/scenario-marketplace.md`
und `docs/features/pdf-export.md` fehlen. Aus ENGB01 abzuleiten in Wave-2-Step-8.

---

## Gruppe 3 — Execution Skills (Prompt-Templates)

### Aktive Templates

| ID | Prompt-ID | Trigger | Tool | Status |
|---|---|---|---|---|
| EXE-01 | Template 1 / CC-RP-01 | `PLAN ONLY. DO NOT CHANGE CODE YET.` | Claude Code Plan Mode | Observed — kanonisch |
| EXE-02 | Template 2 / CC-RI-01 | `IMPLEMENT THE APPROVED PLAN ONLY.` | Claude Code / Lovable | Observed — kanonisch |
| EXE-06 | LOV-01 | Lovable Knowledge Sync | Lovable Plan Mode | Observed — aktiv, recurring |
| EXE-07 | LOV-02 | Risikoreiche Änderung vor Coding | Lovable Plan Mode | Observed — aktiv, recurring |

**Kanonische Quelle:** `docs/templates/claude-code-prompt-templates.md`
(Template 1 + 2). `ALL-PROMPTS-AUDIT.md` enthält CC-RP-01 / CC-RI-01 als
Aufruf-Wrapper — akzeptable strukturelle Redundanz, kein Widerspruch.

### Archivierte Templates (Wave 1 abgeschlossen — als Vorlage für künftige Audits)

| ID | Prompt-ID | Zweck | Tool |
|---|---|---|---|
| EXE-03 | CC-BE-01 | Backend-Audit und Dokumentation | Claude Code |
| EXE-04 | CC-FE-01 | Frontend-Audit und Dokumentation | Claude Code |
| EXE-05 | CC-XR-01 | Cross-Repo-Synthese | Claude Code (multi-dir) |
| EXE-08 | CC-BL-01 | Cleanup-Backlog-Erstellung | Claude Code |
| EXE-09 | CC-GR-01 | Guardrails-Installation | Claude Code |

**Reaktivierung:** Bei neuem Vollaudit (quartalsweise oder bei Architekturereignis)
gemäß `GOV-01-audit-runbook.md`.

---

## Gruppe 4 — Workflow Skills (Repo-Ebene)

Spezifiziert via `CC-GR-01`. Installiert in `.claude/skills/` beider Repos.

| ID | Slash-Command | Wann verwenden | Verhalten | Status |
|---|---|---|---|---|
| WFL-01 | `/session-start` | Beginn jeder Claude-Code-Session | Lädt CLAUDE.md, AGENTS.md, Tasks | Inferred installiert |
| WFL-02 | `/impact-check` | Vor Änderung mit shared state / API / DB | Prüft Cross-Repo-Auswirkungen | Inferred installiert |
| WFL-03 | `/contract-check` | Vor Merge/Ship mit API-Contract-Änderungen | Prüft api-catalog, db-map, Types | Inferred installiert |
| WFL-04 | `/cleanup-audit` | Bei Dead-Code/Debt-Untersuchung | Read-only, kein Code | Inferred installiert |
| WFL-05 | `/close-task` | Vor Task-Markierung als DONE | TypeCheck, Tests, Docs, Commit | Observed — SKILL.md vorhanden |

**Verifikation:** Bei nächster Claude-Code-Session `/session-start` aufrufen und
prüfen, ob alle 5 Skills geladen werden. Falls nicht: `CC-GR-01` erneut ausführen.

---

## Gruppe 5 — Controller / Tower Assets

| ID | Name | Prompt-ID | Zweck | Status |
|---|---|---|---|---|
| CTR-01 | Delivery Controller | `CAI-01` (Basis) | Claude.ai als Steuerzentrale — dieser Controller | Observed — aktiv |
| CTR-02 | Phase Review | `CAI-02` | Output reviewen, nächsten Schritt definieren | Observed — aktiv, recurring |
| CTR-03 | PREPARE NEXT STEP Trigger | Eingebettet in `CAI-01` | Strukturierter 8-Punkte-Output auf Abruf | Observed — aktiv |
| CTR-04 | REVIEW PLAN Gate | Template-Workflow | GO / HOLD / SPLIT / BACK TO DOCS | Observed — aktiv, zwingend |
| CTR-05 | Master-Arch-Prompt | `MASTER-ARCH-01` | One-Shot Governance-Setup | Archiviert — einmalig ausgeführt |
| CTR-06 | Antigravity Dashboard | `ANT-01` | Optionaler Audit-Board-Überblick | Proposed — nicht aktiv eingesetzt |
| CTR-07 | ALL-PROMPTS Routing-Matrix | `docs/governance/ALL-PROMPTS-AUDIT.md` | Routing-Tabelle aller Audit-Phase-Prompts | Observed — aktiv als Referenz |
| CTR-08 | Tool-Routing-Tabelle | Delivery Controller System Prompt | Welches Tool für welche Arbeit | Observed — eingebettet |

**Rollen-Trennung (wichtig):**
`CAI-01` ist das Audit-Phase-Initialisierungsartefakt (Wave 1).
Der Delivery Controller System Prompt ist der neue Träger der Tower-Rolle (Wave 2+).
Beide bleiben erhalten — unterschiedliche Phasen, keine Redundanz.

---

## Gruppe 6 — Knowledge Skills

| ID | Name | Quelle | Status |
|---|---|---|---|
| KNW-01 | ADR-Vorlage + Entscheidungsprozess | ADR-001–006 als Muster, `wave2-scope.md` Step 1 | Observed — aktiv |
| KNW-02 | Wiki-Update-Prozess | `docs/source-of-truth-matrix.md` | Observed — aktiv |
| KNW-03 | Lessons-Learned (Wave-Transfer-Pattern) | `docs/delivery/initial-setup-baseline.md` | Observed — aktiv als Pattern |
| KNW-04 | Observed/Inferred/Missing/Proposed Klassifikation | Systemweit eingebettet | Observed — aktiv in allen Templates |
| KNW-05 | Bounded-Context-Dokumentation | `docs/bounded-contexts.md` | Observed — aktiv |
| KNW-06 | Source-of-Truth-Matrix | `docs/source-of-truth-matrix.md` | Observed — aktiv |

---

## Redundanzanalyse

| Redundanz | Artefakte | Bewertung |
|---|---|---|
| Plan-Template doppelt | Template 1 + CC-RP-01 | Akzeptabel — Template 1 ist Inhalt, CC-RP-01 ist Aufruf-Wrapper |
| Implement-Template doppelt | Template 2 + CC-RI-01 | Akzeptabel — gleiche Struktur wie oben |
| Controller-Rolle an zwei Stellen | CAI-01 + Delivery Controller Prompt | Keine Redundanz — unterschiedliche Phasen (Audit vs. Delivery) |
| Pflichtperspektiven doppelt | GOV-02 + GOV-01 Checkliste | Akzeptabel — unterschiedliche Detailtiefe |

**Fazit:** Keine kritischen Redundanzen. Alle Überschneidungen strukturell begründet.

---

## Identifizierte Lücken

| ID | Lücke | Kritikalität | Handlung |
|---|---|---|---|
| GAP-01 | ADR-007 fehlt | Kritisch — Wave-2-Blocker | Erste Aufgabe Wave 2, vor allem anderen |
| GAP-02 | Feature-Docs Layer-3 / Marketplace / PDF-Export | Mittel | Wave-2-Step-8: aus ENGB01 ableiten |
| GAP-03 | `layer2-diagnosis-plan.md` fehlt | Mittel | Nach Layer-2-Diagnose-Sprint erstellen |
| GAP-04 | `ALL-PROMPTS-DELIVERY.md` fehlt | Niedrig | Nach Wave 2: Delivery-Prompts aus `ALL-PROMPTS-AUDIT.md` separieren |
| GAP-05 | Repo-Skill-Installation nicht verifiziert | Niedrig | Bei nächster Session `/session-start` aufrufen |
| GAP-06 | Lovable Project Knowledge Aktualität unbekannt | Mittel | LOV-01 als ersten Lovable-Step Wave 2 ausführen |

---

## Empfohlene Zielstruktur

```
shared-context/docs/
├── governance/
│   ├── GOV-01-audit-runbook.md          ✅
│   └── ALL-PROMPTS-AUDIT.md             ✅ (historisch — Audit-Phase)
│
├── templates/
│   ├── claude-code-prompt-templates.md  ✅ (kanonisch)
│   └── ALL-PROMPTS-DELIVERY.md          ❌ NEU — nach Wave 2
│
├── delivery/
│   ├── initial-setup-baseline.md        ✅
│   ├── wave2-scope.md                   ✅
│   └── layer2-diagnosis-plan.md         ❌ nach Diagnose-Sprint
│
└── features/
    ├── layer3-simulation.md             ❌ Wave-2-Step-8
    ├── scenario-marketplace.md          ❌ Wave-2-Step-8
    └── pdf-export.md                    ❌ Wave-2-Step-8

.claude/skills/ (beide Repos)
├── session-start/SKILL.md              Inferred
├── impact-check/SKILL.md               Inferred
├── contract-check/SKILL.md             Inferred
├── cleanup-audit/SKILL.md              Inferred
└── close-task/SKILL.md                 Observed (vorhanden)
```

---

## Änderungshistorie

| Datum | Version | Änderung |
|---|---|---|
| 2026-04-17 | 1.0 | Erstversion — Skills A–J, Prompt-Templates, Hooks, Tool-Routing, Rule-Files |
| 2026-04-18 | 1.1 | Vollständige Neustrukturierung — 42 Artefakte, 6 Gruppen, Redundanz- und Lückenanalyse, Delivery-Controller-Kontext |
