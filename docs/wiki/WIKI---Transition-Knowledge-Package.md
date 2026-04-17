# WIKI — Transition Knowledge Package

**Klassifikation:** Observed | Inferred | Missing | Proposed
**Erstellt:** 2026-04-17
**Ablageort:** `shared-context/docs/wiki/`
**Basis:** initial-setup-baseline.md Abschnitt 4, Wave-1-Completion-Gate, ALL-PROMPTS-AUDIT.md
**Kontext:** Dieses Dokument beschreibt den Wissenstransfer vom alten Claude.ai Governance & Audit Projekt zum neuen Feature Delivery Controller Projekt (Wave 2). Es ist kein Betriebsdokument — es ist eine einmalige Transition-Dokumentation.

---

## 1. Memory-Status des alten Projekts

### 1.1 Zugänglichkeit

**Missing (strukturell):** Claude-Memory-Inhalte aus dem alten Governance & Audit Projekt sind nicht direkt zugänglich. Claude.ai Project Memory existiert als internes Projektkontextsystem, das nicht exportiert oder übertragen werden kann.

**Observed:** Kein wesentlicher Wissensverlust identifiziert. Der vollständige operative Wissensstand wurde parallel in git-getrackten Markdown-Artefakten geführt (gemäß GOV-01-Prinzip "Git-Docs sind die operative Wahrheit").

### 1.2 Kompensationsmechanismus

**Observed — vollständig aktiv:**

| Kompensationsebene | Mechanismus | Status |
|--------------------|-------------|--------|
| Prompt-Templates | Alle Templates exportiert nach `docs/claude-code-prompt-templates.md` und `docs/governance/ALL-PROMPTS-AUDIT.md` | ✅ Vollständig |
| Architektur-Entscheidungen | Alle ADRs in `docs/decision-log/` | ✅ ADR-001–006 abgeschlossen; ADR-007 DRAFT |
| Audit-Findings | `docs/audits/current-state-report.md`, `docs/audits/refactor-backlog.md` | ✅ Stand 2026-04-16 |
| Governance-Regeln | `docs/governance/GOV-01-audit-runbook.md` | ✅ Vollständig |
| System-Übersicht | `docs/system-overview.md`, `docs/bounded-contexts.md`, `docs/source-of-truth-matrix.md` | ✅ Aktuell |
| Repo-Profile | `docs/wiki/WIKI---Repo-Profile-negotiationcoach-backend.md`, `WIKI---Repo-Profile-negotiation-buddy.md` | ✅ Erstellt Wave 1 |
| Tier-Modell | ADR-006 + RFB-036 abgeschlossen | ✅ Unified |
| Delivery-Baseline | `docs/delivery/initial-setup-baseline.md` | ✅ Erstellt 2026-04-17 |

---

## 2. Übernommene Artefakte

**Observed** — alle folgenden Artefakte wurden aus dem alten Projekt extrahiert und im neuen Governance-System verankert.

### 2.1 Prompt-Templates

| Quelle (altes Projekt) | Zieldatei im neuen System | Inhalt |
|------------------------|--------------------------|--------|
| Audit-Workflow-Prompts (CAI-01/02, CC-BE/FE/XR-01, LOV-01/02, CC-BL/GR-01) | `docs/governance/ALL-PROMPTS-AUDIT.md` | Vollständige Prompt-Texte für Audit/Refactoring-Workflow |
| Refactor-Execution-Templates (Template 1, Template 2, CC-RP-01, CC-RI-01) | `docs/claude-code-prompt-templates.md` | Plan- und Implementierungs-Templates für täglichen Betrieb |

### 2.2 Governance-Regeln

| Quelle (altes Projekt) | Zieldatei im neuen System | Inhalt |
|------------------------|--------------------------|--------|
| Audit-Runbook und Prinzipien | `docs/governance/GOV-01-audit-runbook.md` | Schrittfolge, Kadenz, Grundprinzipien, Tool-Rollen |
| Nicht verhandelbare Regeln (12 Architekturregeln) | `docs/wiki/WIKI---Governance-Baseline.md` | Konsolidierte Regeln aus ADRs + Delivery-Erfahrung |

### 2.3 Audit-Findings

| Quelle (altes Projekt) | Zieldatei im neuen System | Inhalt |
|------------------------|--------------------------|--------|
| CRIT/HIGH/MED/LOW-Findings | `docs/audits/current-state-report.md` | Vollständiges Finding-Register |
| Priorisiertes Refactor-Backlog (RFB-001–036 + AB-001) | `docs/audits/refactor-backlog.md` | 36 Items mit Body-Entries, Summary Index, Abhängigkeitsgraph |
| Wave-1-Gate-Ergebnis | `docs/audits/wave1-completion-gate.md` | Formale Gate-Prüfliste; Status: CLEARED 2026-04-16 |

### 2.4 Architektur-Entscheidungsregister

| Quelle (altes Projekt) | Zieldatei im neuen System | Status |
|------------------------|--------------------------|--------|
| System Boundary Decisions | `docs/decision-log/ADR-001-system-boundaries.md` | ✅ Entschieden |
| Data Ownership Rules | `docs/decision-log/ADR-002-data-ownership.md` | ✅ Entschieden |
| AI Provider Split | `docs/decision-log/ADR-003-ai-provider-strategy.md` | ✅ Entschieden (permanent) |
| Chat Path Routing | `docs/decision-log/ADR-004-chat-path-routing.md` | ✅ Entschieden |
| Plan Generation Path | `docs/decision-log/ADR-005-plan-generation-path.md` | ✅ Entschieden |
| Tier Mapping | `docs/decision-log/ADR-006-tier-mapping.md` | ✅ Entschieden; RFB-036 abgeschlossen |
| Dual Layer-1-Architektur | `docs/decision-log/ADR-007-dual-layer1.md` | ⚠️ DRAFT — Entscheidung ausstehend |

### 2.5 Repo-Profile und Kontext

| Quelle (altes Projekt) | Zieldatei im neuen System | Inhalt |
|------------------------|--------------------------|--------|
| Backend-Repo-Wissen aus Audit-Sessions | `docs/wiki/WIKI---Repo-Profile-negotiationcoach-backend.md` | Vollständiges Backend-Profil: Architektur, API, Risiken, Skills |
| Frontend-Repo-Wissen aus Audit-Sessions | `docs/wiki/WIKI---Repo-Profile-negotiation-buddy.md` | Vollständiges Frontend-Profil |
| System-Gesamtbild | `docs/system-overview.md` | Runtime-Map, Datenflüsse, Auth-Fluss |
| Entity-Ownership-Matrix | `docs/source-of-truth-matrix.md` | Kanonischer Owner für alle Kern-Entities |
| Bounded Contexts (BC-01–06) | `docs/bounded-contexts.md` | Ownership-Grenzen und Violations |
| Auth-Permission-Map | `docs/auth-permission-map.md` | Auth-Flows, Tier-Gates, Permission-Violations |
| API-Vertrag | `docs/contracts/frontend-backend.md` | Endpunkte, Typen, bekannter Type-Drift |

---

## 3. Was angepasst wurde (mit Begründung)

**Observed** — folgende Artefakte wurden bei der Übernahme angepasst, nicht direkt kopiert.

| Artefakt | Anpassung | Begründung |
|----------|-----------|-----------|
| close-task SKILL.md (alle drei Repos) | Step J hinzugefügt (Wiki-Update: index.md + session-log.md entfernen/anfügen); Step I auf Zwei-Commit-Pattern erweitert; Full Output Format mit Wiki-Statuszeilen ergänzt | Wave-1-Erfahrung: ohne Step J fehlten Wiki-Updates nach Task-Abschluss |
| negotiation-buddy close-task SKILL.md | Vollständig ersetzt: altes Format (Steps 1–6 Checkliste ohne ITEM_ID-Parameter) durch kanonisches A–J-Format | Formatdivergenz zwischen Repos — Vereinheitlichung erzwungen |
| Refactor-Backlog Summary Index | RFB-004-Zeile repariert (fehlende Spalten); RFB-006 und RFB-026 auf DEFERRED gestempelt mit Rationale | Konsistenz-Pflege nach Wave-1-Gate-Clearing |
| wave1-completion-gate.md | Mehrfach iteriert bis finale CLEARED-Struktur (3-Spalten-Tabellen, narrative Gate-Status-Sektion) | Formale Gate-Struktur entwickelte sich während Clearing |
| WIKI---Repo-Profile-negotiationcoach-backend.md | Im Wiki-Format als vollständiges Operationsprofil erstellt (nicht nur Audit-Snapshot) | Wiki-Profil ist Betriebsdokument; Audit-Finding ist Point-in-Time-Snapshot |

---

## 4. Was bewusst nicht übernommen wurde

**Inferred / Proposed** — folgende Artefakte aus dem alten Projekt wurden nicht übertragen.

| Nicht übernommenes Artefakt | Grund |
|----------------------------|-------|
| Notion-Spiegelseiten | Notion ist Mirror, nicht Source of Truth (GOV-01-Grundprinzip). Git-Markdown ist operativ. |
| Antigravity Agent-Chat-Output (ANT-01) | Dashboard-Output war transient; relevante Erkenntnisse sind in refactor-backlog.md und current-state-report.md eingeflossen. |
| Intermediate CAI-02 Review-Outputs (Zwischenergebnisse) | Nur Endergebnisse sind relevant; Intermediate-Outputs sind durch Backlog und ADRs abgedeckt. |
| `audit-dashboard.md` Content (altes Format) | Die Datei existiert in shared-context, ist aber ein Überbleibsel. Relevanter Inhalt ist in current-state-report.md und refactor-backlog.md. |
| Wave-1-intermediate Commits (Zwischenstände) | Git-History bewahrt diese; keine extra Dokumentation erforderlich. |

---

## 5. Offene Lücken und Kompensationsmaßnahmen

**Missing / Proposed**

| Lücke | Klassifikation | Schwere | Kompensation |
|-------|---------------|---------|-------------|
| ADR-007 nicht entschieden | Missing — kritisch | 🔴 Blockiert RFB-006, RFB-026 | Wave-2-Start-Gate: VG-06 entscheiden, ADR-007 abschließen |
| Layer-2-Fehler nicht diagnostiziert | Missing — höchste Priorität | 🔴 Marktdaten fehlerhaft | Wave-2-Step-2: Diagnose-Sprint (marketDataResolver + marketDataInterpreter trace) |
| Layer-3-Code nicht begonnen | Observed — planmäßig | Kein Risiko | Wave-2-Step-6: nach Layer-2-Fix; Interfaces bereits definiert |
| Feature-Docs Layer-3/Marketplace/PDF | Missing | 🟡 Kein Planungsdokument | Wave-2-Step-8: Docs aus ENGB01 ableiten |
| `docs/delivery/layer2-diagnosis-plan.md` | Missing | 🟡 Fehlende Diagnose-Dokumentation | Erstellen nach Layer-2-Diagnose (Wave-2-Step-2) |
| Knowledge Pipeline ADR | Missing | 🟡 RFB-016a: ADR vor Impl erforderlich | Deferred — Wave 3+ |
| Stripe Webhook Handler | Missing — business critical | 🔴 Kein echtes Tier-Upgrade möglich | RFB-032: Aktivieren wenn Stripe live |

---

## 6. DEVS01 Session Log — Was extrahiert wurde

**Observed / Inferred** — Die folgenden Erkenntnisse wurden aus dem alten Audit-Projekt in strukturierte Artefakte überführt.

| Erkenntnis | Quelle (Session) | Artefakt |
|-----------|-----------------|---------|
| CRIT-01: Dual Layer-1 mit inkompatiblem Schema | Backend-Audit-Session | current-state-report.md CRIT-01; ADR-007 DRAFT |
| Layer-2 fehlerhaft — Fehlerursache undiagnostiziert | Backend-Audit-Session | current-state-report.md; wave2-scope.md Step 2 |
| CRIT-02: Team Admin Check rein im Frontend | Frontend-Audit-Session | current-state-report.md CRIT-02 |
| HIGH-01: Direkte Frontend-Writes zu Supabase | Cross-Repo-Synthese | RFB-004 (DONE), bounded-contexts.md BC-03 |
| Drei inkompatible Tier-Systeme (Railway/Supabase/EF) | Cross-Repo-Synthese | RFB-007 → RFB-036 (DONE); ADR-006 |
| VG-05: Tier in EF ist dekorative Prompt-Metadata | VG-06-Analyse-Session | auth-permission-map.md; VG-05 RESOLVED |
| VG-05-A: Kein JWT-Auth in EF | VG-05-Folge-Analyse | current-state-report.md; RFB-033 (DONE) |
| VG-06: Dual Layer-1-Architekturentscheidung fehlt | Cross-Repo-Synthese | ADR-007 DRAFT; RFB-006 DEFERRED |
| session_history war als session_messages falsch referenziert | Backend-Audit | RFB-031 (DONE commit `2c51cb4`) |
| modelRouter.ts in /api/chat und /api/plan bypassed | Backend-Audit | RFB-011 (DONE commit `60848db`) |
| Stripe-Webhook-Handler fehlt — kein echtes Tier-Gating | Backend-Audit | RFB-032 (DEFERRED — Stripe nicht live) |
| CORS Wildcard überschreibt Allowlist | Backend-Audit | R-04; unbehandelt |
| knowledge_candidates Extraktion und Insertion Pipeline fehlt | Frontend-Audit | RFB-016 (DONE commit `a647d5a`) |
| Index.tsx God Component (~929 Zeilen) | Frontend-Audit | RFB-020 (P3 Debt, Wave-2-Step-7) |

---

*Dieses Dokument ist eine einmalige Transition-Dokumentation. Es muss nicht kontinuierlich aktualisiert werden. Änderungen am System werden in den operativen Docs (refactor-backlog.md, source-of-truth-matrix.md, ADRs) dokumentiert.*
