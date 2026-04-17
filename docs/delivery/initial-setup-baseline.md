# Initial Setup Baseline — NegotiationCoach AI Feature Delivery Controller

**Erstellt:** 2026-04-17
**Status:** Established
**Klassifizierung:** Observed / Inferred / Missing / Proposed
**Projekt:** NegotiationCoach AI — Feature Delivery Controller
**Vorgänger:** Governance & Audit Project (Wave 1)

---

## Zweck dieses Dokuments

Dieses Dokument sichert die Ergebnisse des Initial-Setups für das Feature Delivery Controller Projekt. Es konsolidiert alle relevanten Erkenntnisse aus Audit, Refactoring und Systemanalyse und dient als Referenzbasis für alle weiteren Delivery-Entscheidungen.

---

## 1. System Landscape Summary

Das System besteht aus drei Repositories über zwei Supabase-Instanzen, einem Railway-Backend und einem Lovable-Frontend. Die Architektur ist im Wesentlichen stabil, enthält aber drei strukturelle Carry-Forward-Items aus Wave 1, die als erste Architekturentscheidungen des neuen Projekts adressiert werden müssen.

**Observed:** Alle Layer-0- und Layer-1-Module sind implementiert und verifiziert. Layer 2 ist implementiert, liefert aber fehlerhafte Ergebnisse (höchste Priorität Wave 1 Feature Delivery). Layer 3 ist geplant, nicht begonnen. 6 Frontend-Screens sind vollständig.

**Inferred:** Der Layer-2-Fehler liegt wahrscheinlich in `marketDataResolver.ts` oder `marketDataInterpreter.ts`, da diese den Cache-/Web-Search-Entscheidungsweg kontrollieren.

**Missing:** Claude-Memory-Inhalte aus dem alten Audit/Refactoring-Projekt sind nicht direkt zugänglich. Kompensation erfolgt vollständig über die exportierten Artefakte (Markdown-Docs, Prompt-Templates, PDF-Blueprints — alle vorhanden und ausgewertet). Kein wesentlicher Governanceverlust identifiziert.

### Repository-Übersicht

| Repository | Tool | Supabase-Instanz | Rolle | Status |
|---|---|---|---|---|
| `shared-context` | Claude Code | — | Governance, Wissen, Dokumentation | ✅ Aktiv |
| `negotiation-buddy` | Lovable | Lovable-Instanz (anon key) | Frontend / React SPA | ✅ Aktiv |
| `negotiationcoach-backend` | Claude Code | Railway-Instanz (service role key) | Backend / Engine | ✅ Aktiv |

### Engine-Layer-Status

| Layer | Name | Status |
|---|---|---|
| 0 | Data Foundation | ✅ Abgeschlossen |
| 1 | Analysis Engine | ✅ Abgeschlossen (ZOPA, Monte Carlo, Nash, strategyScore, deadlineEffect, batnaDetector) |
| 2 | Context Engine | ⚠️ Implementiert, fehlerhaft — Market-Data-Research broken |
| 3 | Simulation Engine | ❌ Nicht gestartet (Interfaces definiert, kein Code) |
| 4 | UI / Frontend | ✅ Stufe 1+2 Screens vollständig — Stufe 3+4 nicht gestartet |

---

## 2. Repository-Profile

### 2.1 `negotiation-buddy` (Frontend · Lovable)

**Stack:** React SPA, TypeScript strict, Vite, Tailwind, Supabase JS (anon key), Edge Functions via SSE

**Verantwortlichkeiten:** 6 UI-Screens (Canvas, What-If, Strategy, Debrief, Auth, Profile), Chat-Streaming-UI, Session-State via `AnalysisContext`, alle Railway-API-Calls via `apiClient.ts`

**API-Endpunkte die das Frontend aufruft:**

| Method | Pfad | Screen | Auth |
|---|---|---|---|
| POST | `/api/analyze-full` | Negotiation Canvas | JWT |
| POST | `/api/analyze` | What-If Simulator | JWT |
| POST | `/api/enrich` | Strategy Generator (KMU/Profi) | JWT |
| GET | `/api/sessions/:id` | Debrief Dashboard | JWT |
| POST | `/api/plan` | Strategy Generator | JWT |
| POST | `/api/chat` | Index / Chat | JWT |

**Skills im Repo (Observed):**

| Skill | Pfad | Status |
|---|---|---|
| `session-start` | `.claude/skills/session-start/` | Aktiv |
| `impact-check` | `.claude/skills/impact-check/` | Aktiv |
| `contract-check` | `.claude/skills/contract-check/` | Aktiv |
| `cleanup-audit` | `.claude/skills/cleanup-audit/` | Aktiv |
| `close-task` | `.claude/skills/close-task/` | Aktiv |

**Rule-Files (Observed):** `architecture.md` · `protected-files.md` · `ui-boundaries.md` · `data-access.md` · `api-contracts.md` · `db-boundaries.md`

**Offene Risiken:**
- `F-001`: Direkte DB-Writes aus Frontend — dokumentiert, nicht alle behoben
- `RFB-020`: Index.tsx God Component (~929 Zeilen) — P3-Debt, nicht dekomponiert
- `persona_type` vs `subscription_tier` — Mapping via `personaTypeToTier()` vorhanden, EF-Boundary offen (VG-06-abhängig)
- **CRITICAL DRIFT**: Edge Function nutzt `user_goal/user_walkaway`, Railway nutzt `own_target/own_minimum`

**Dokumentation (vollständig):** `AGENTS.md`, `CLAUDE.md`, `.claude/rules/`, `docs/` (audit-findings, redundancy-register, data-access-map, feature-catalog, repo-map, dead-code-candidates)

---

### 2.2 `negotiationcoach-backend` (Backend · Claude Code · Railway)

**Stack:** Express.js 5, TypeScript strict, Anthropic SDK, Supabase JS (service role key), Zod, Nodemon, ts-node

**API-Endpunkte (Observed):**

| Method | Pfad | Layer | Auth | Tier |
|---|---|---|---|---|
| GET | `/api/health` | — | Public | — |
| POST | `/api/analyze` | Layer 1 | JWT | Alle |
| POST | `/api/enrich` | Layer 2 | JWT | KMU, Profi |
| POST | `/api/analyze-full` | L1+L2 | JWT | Alle |
| GET | `/api/sessions/:id` | — | JWT | Alle |
| POST | `/api/plan` | Plan | JWT | Alle |
| POST | `/api/chat` | Chat | JWT | Alle |
| POST | `/api/teams/*` | Teams | JWT | Alle |

**Layer-Datei-Status:**

| Layer | Dateien | Status |
|---|---|---|
| 0 | `supabaseClient.ts` | ✅ |
| 1 | `zopaCalculator.ts`, `nashBargaining.ts`, `monteCarlo.ts`, `strategyScore.ts`, `deadlineEffect.ts`, `batnaDetector.ts` | ✅ (EF-Version undeployable) |
| 2 | `marketDataResolver.ts`, `marketDataInterpreter.ts`, `knowledgeGraph.ts`, `realityScore.ts` | ⚠️ fehlerhaft |
| 3 | `smlParser.ts`, `promptBuilder.ts`, `simulationLoop.ts`, `opponentEngine.ts`, `debriefEngine.ts` | ❌ nicht begonnen |
| API | `routes.ts`, `middleware.ts`, `errors.ts`, `planHelpers.ts`, `chatHelpers.ts` | ✅ |

**Offene Risiken:**
- Doppelte Layer-1-Implementierung in Edge Function (`_shared/engine/`) — undeployable, unresolved (RFB-006, abhängig von VG-06 → ADR-007)
- `generatePlan()` als ADR-005-Migrationsziel annotiert (dead code bis VG-06)
- Zod nur teilweise genutzt (vollständige Validierung ausstehend)

**Dokumentation (vollständig):** `AGENTS.md`, `CLAUDE.md`, `docs/` (repo-map, service-catalog, api-catalog, audit-findings), `tasks/` (todo, lessons)

---

### 2.3 `shared-context` (Governance · Claude Code)

**Verantwortlichkeit:** Einzige Source of Truth für Architektur-, Governance-, Vertrags- und Audit-Dokumente

**Vorhandene Inhalte (Observed):**

| Kategorie | Dateien | Status |
|---|---|---|
| ADRs | ADR-001 bis ADR-006 | ✅ entschieden |
| ADR-007 | VG-06-Entscheidung | ❌ fehlt — erste Aufgabe |
| Contracts | `frontend-backend.md` | ✅ aktuell |
| Audit | `refactor-backlog.md` (36 Items, Stand 2026-04-16), `current-state-report.md` | ✅ |
| Governance | `ALL-PROMPTS-AUDIT.md`, `GOV-01-audit-runbook.md` | ✅ |
| Templates | `claude-code-prompt-templates.md` | ✅ |
| Bounded Contexts | `bounded-contexts.md` (BC-01 bis BC-06) | ✅ |
| Source of Truth | `source-of-truth-matrix.md` | ✅ |

---

## 3. Consolidated Governance Baseline

### 3.1 Nicht verhandelbare Architekturregeln (alle aktiv, Observed)

- Railway = kanonischer Execution-Path für alle Business-Logik (ADR-001)
- Ein Writer pro Business-Entity (ADR-002) — Railway für Sessions/Results, Frontend nur für User-Profile mit RLS-Verifikation
- Anthropic/Railway + Gemini/Edge Function — permanent (ADR-003)
- `subscription_tier` DB-Enum = ausgerichtet auf Railway Tier-Werte (`free | privat | kmu | profi`) — abgeschlossen RFB-036, ADR-006
- `personaTypeToTier()` ist die kanonische Mapping-Funktion für UI-Persona → Railway Tier
- Keine direkten Supabase-Calls aus Frontend-Komponenten — immer via Railway API
- Alle LLM-Calls serverseitig via Railway Backend (Anthropic Claude)
- Jede neue DB-Tabelle muss eine RLS-Policy bei Erstellung haben
- Schema-Änderungen nur via Migration-Files — nie über Supabase Dashboard
- Tier-Prüfungen immer serverseitig — Frontend-Gates sind UI-only
- Keine Cross-Repo-Änderungen ohne Impact Assessment

### 3.2 Aktive Violations / Strukturelle Restrisiken

| ID | Problem | Repos | Abhängigkeit | Priorität |
|---|---|---|---|---|
| CRIT-01 | Dual Layer-1-Implementierung (EF `_shared/engine/` vs. Railway `src/layer1/`) | Backend | ADR-007 (VG-06) | Wave 2 P1 |
| CRIT-DRIFT | EF schema (`user_goal`) ≠ Railway schema (`own_target`) | Frontend+Backend | VG-06 | Wave 2 P1 |
| RFB-004-C | DB-Count-Constraint für session_history ausstehend | Backend | kein | Wave 2 P2 |
| RFB-020 | Index.tsx God Component | Frontend | kein | P3 Debt |
| RFB-032 | Stripe Webhook Handler | Backend | Stripe nicht live | Deferred |

### 3.3 Tier-Modell (kanonisch, Stand 2026-04-16)

| Tier | Preis | Zugang |
|---|---|---|
| `free` | 0€ | Demo-Modus, read-only |
| `privat` | 12€ | Nur Layer 1 Analyse |
| `kmu` | 49€ | Layer 1 + Layer 2 Basis, Scenario Marketplace lesen |
| `profi` | 99€ | Alle Features, Layer 3, Scenario Marketplace erstellen, PDF Export |

DB-Enum `subscription_tier` ist seit RFB-036 (`a28d28c`, 2026-04-16) auf Railway Tier-Werte ausgerichtet.

---

## 4. Audit/Refactoring Knowledge Transfer Summary

### 4.1 Wave 1 — Abgeschlossene Items (Stand 2026-04-16)

**P0 Boundary-Violations (alle behoben):**

| Item | Titel | Commit |
|---|---|---|
| RFB-001 | authMiddleware 401-Enforcement | `fd68e1e` |
| RFB-002 | RLS für team admin | `<hash>` |
| RFB-003 | Team CRUD zu Railway | `0b10d9c` + Lovable |
| RFB-004 | Session/Message Writes zu Railway | `2c51cb4` + `2415f72` + `6021665` + Lovable |
| RFB-005 | CORS-Wildcard-Fix | `e00e400` |
| RFB-029 | negotiation_sessions fehlende Analyse-Columns | `f759c18` |
| RFB-031 | session_history Tabellenname | `2c51cb4` |

**P1 Contract Gaps (alle behoben):**

| Item | Titel | Commit |
|---|---|---|
| RFB-007 | Tier-Unification (Steps A+B+C) | `1c68185` + `6ba5710` → RFB-036 |
| RFB-008 | Parallele Type-Wartung eliminiert | `9c51a43` |
| RFB-009 | User-Tier zu Edge Function propagiert | `d90d5c0` |
| RFB-011 | modelRouter in /api/chat und /api/plan | `60848db` |
| RFB-012 | user_profiles Creation bei Signup | 2026-04-03 |
| RFB-033 | JWT auth + Tier Gate für generate-plan EF | `477df3d` |
| RFB-035A/B | anon key durch User JWT in Index.tsx ersetzt | `ffe0274` + `c60c419` |
| RFB-036 | subscription_tier DB-Enum migriert (ADR-006) | `a28d28c` |

### 4.2 Carry-Forward Wave 1 → Wave 2

| Item | Titel | Blocker | Deferral-Bedingung |
|---|---|---|---|
| RFB-006 | Dual Layer-1-Unification | ADR-007 (VG-06) erforderlich | VG-06 muss erste Architekturentscheidung in Wave 2 sein |
| RFB-026 | batnaDetector EF Reparatur | abhängig von RFB-006 | Erst nach RFB-006 |
| RFB-032 | Stripe Webhook Handler | Stripe nicht live | Erst wenn Stripe aktiviert |

**Deferral-Regeln (zwingend):**
- Bis VG-06 resolved: keine neue Logik in Edge Function engine path
- EF batnaDetector.ts bleibt in aktuellem Zustand, darf nicht deployed werden
- Node.js Layer-1 (`negotiationcoach-backend`) ist kanonischer Execution-Path bis VG-06

### 4.3 Memory-Status

**Missing:** Claude-Memory-Inhalte aus dem alten Audit/Refactoring-Projekt nicht direkt zugänglich.

**Kompensationsmechanismus (aktiv und vollständig):** Alle wesentlichen Memory-Inhalte wurden in Markdown-Artefakte überführt: `refactor-backlog.md`, `source-of-truth-matrix.md`, `frontend-backend.md`, `bounded-contexts.md`, `ALL-PROMPTS-AUDIT.md`, `claude-code-prompt-templates.md`. Kein wesentlicher Governanceverlust identifiziert.

---

## 5. Inventory of Instructions, Templates, Commands and Skills

### 5.1 Prompt-Templates (Observed, voll operativ)

Alle Templates in `shared-context/docs/claude-code-prompt-templates.md`.

| Template | Trigger | Tool | Zweck |
|---|---|---|---|
| Template 1 (Plan) | `PLAN ONLY. DO NOT CHANGE CODE YET.` | Claude Code | Planungsschritt vor jeder Code-Änderung |
| Template 2 (Implement) | `IMPLEMENT THE APPROVED PLAN ONLY.` | Claude Code / Lovable | Implementierung nach GO-Entscheidung |
| CC-RP-01 | `Plan only. Do not write code yet.` | Claude Code (target repo, plan mode) | Einzelnen Backlog-Item planen |
| CC-RI-01 | `Implement only the approved plan for [ITEM_ID]` | Claude Code / Lovable | Einzelnen Backlog-Item implementieren |
| CAI-01 | Control Tower Setup | Claude.ai | Initialisierung |
| CAI-02 | Phase-Output reviewen | Claude.ai | Nach jedem Output |
| LOV-01 | Lovable Knowledge Sync | Lovable Plan Mode | Frontend-Änderungen planen |
| LOV-02 | Risikoreiche Frontend-Änderung | Lovable Plan Mode | Vor riskanten Änderungen |

### 5.2 Workflow-Skills (beide Repos)

| Skill | Wann | Verhalten |
|---|---|---|
| `session-start` | Beginn jeder Claude-Code-Session | Lädt CLAUDE.md, AGENTS.md, Tasks |
| `impact-check` | Vor jeder Änderung mit shared state/API/DB | Prüft Cross-Repo-Auswirkungen |
| `contract-check` | Vor Merge/Ship mit API-Contract-Änderungen | Prüft api-catalog, db-map, Types |
| `cleanup-audit` | Bei Dead-Code/Debt-Untersuchung | Read-only, kein Code |
| `close-task` | Vor Task-Markierung als DONE | TypeCheck, Tests, Docs, Commit |

### 5.3 Steuerungsmechanismen (Claude.ai Delivery Controller)

| Mechanismus | Zweck |
|---|---|
| Template 1 → Review → GO/HOLD/SPLIT/BACK TO DOCS → Template 2 | Kernworkflow jeder Änderung |
| Impact Assessment vor Cross-Repo-Änderungen | Verhindert ungesehene Auswirkungen |
| ADR vor Implementierung | Keine Architekturarbeit ohne dokumentierte Entscheidung |
| Layer-Abhängigkeiten 0→1→2→3 | Kein Überspringen von Layers |
| Shared-context als Source of Truth | Jede Entscheidung wird zurückgeführt |

---

## 6. Gap Analysis

| Gap | Klassifikation | Auswirkung | Empfehlung |
|---|---|---|---|
| **ADR-007 nicht erstellt** | Missing — kritisch | Blockiert RFB-006, RFB-026; verhindert Layer-1-Klarheit | Erste Aufgabe Wave 2: VG-06 entscheiden, ADR-007 schreiben |
| **Layer-2-Fehler nicht diagnostiziert** | Missing — höchste Priorität | Marktdaten liefern falsche Ergebnisse | Diagnose-Sprint: marketDataResolver + marketDataInterpreter trace |
| **Layer-3-Code nicht begonnen** | Observed — planmäßig | Kein Risiko, aber Wave-2-Vorbereitung erforderlich | Prompt-Blueprint für Layer-3 aus ENGB01 ableiten nach Layer-2-Fix |
| **EF schema ≠ Railway schema (CRITICAL DRIFT)** | Observed — strukturelles Risiko | Inkompatible Inputs Chat EF vs. Railway | Blockiert durch VG-06; dokumentiert in frontend-backend.md |
| **Stripe nicht live** | Observed | Kein echtes Tier-Gating möglich | Deferred; kein Handlungsbedarf bis Stripe-Entscheidung |
| **Knowledge Pipeline** | Proposed — deferred | RFB-016a: ADR vor Implementierung erforderlich | Nicht Wave 2, ADR-Entwurf erforderlich wenn bereit |
| **RFB-020 Index.tsx** | Observed — P3 Debt | Wartungsrisiko, kein Blocker | Wave 2 nach Layer-3-Start |
| **Feature-Docs Layer-3 / Marketplace / PDF** | Missing | Kein Planungsdokument für kommende Features | In Wave-2-Vorbereitung erstellen |
| **`wave-planning/` Ordner fehlt** | Missing | Wave-2-Scope nirgendwo dokumentiert | Dieser Schritt: `wave2-scope.md` erstellen |
| **Claude Memory (altes Projekt)** | Missing — vollständig kompensiert | Kein Verlust | Kein Handlungsbedarf |

---

## 7. Empfohlene Zielstruktur — Shared-Context Wiki

```
shared-context/
├── AGENTS.md                               ✅ vorhanden
├── CLAUDE.md                               ✅ vorhanden
├── docs/
│   ├── system-overview.md                  ✅ vorhanden
│   ├── bounded-contexts.md                 ✅ vorhanden
│   ├── source-of-truth-matrix.md           ✅ vorhanden
│   ├── repo-map.md                         ✅ vorhanden
│   ├── auth-permission-map.md              ✅ vorhanden
│   │
│   ├── contracts/
│   │   └── frontend-backend.md             ✅ vorhanden, aktuell
│   │
│   ├── decision-log/
│   │   ├── ADR-001-system-boundaries.md    ✅
│   │   ├── ADR-002-data-ownership.md       ✅
│   │   ├── ADR-003-ai-provider-strategy.md ✅
│   │   ├── ADR-004-chat-path-routing.md    ✅
│   │   ├── ADR-005-plan-generation-path.md ✅
│   │   ├── ADR-006-tier-mapping.md         ✅
│   │   └── ADR-007-dual-layer1.md          ❌ FEHLT — erste Aufgabe Wave 2
│   │
│   ├── audits/
│   │   ├── refactor-backlog.md             ✅ Stand 2026-04-16
│   │   ├── current-state-report.md         ✅
│   │   └── audit-dashboard.md              ✅
│   │
│   ├── governance/
│   │   ├── ALL-PROMPTS-AUDIT.md            ✅
│   │   └── GOV-01-audit-runbook.md         ✅
│   │
│   ├── templates/
│   │   └── claude-code-prompt-templates.md ✅
│   │
│   ├── features/
│   │   ├── knowledge-pipeline.md           ✅
│   │   ├── layer3-simulation.md            ❌ FEHLT (aus ENGB01 ableiten)
│   │   ├── scenario-marketplace.md         ❌ FEHLT
│   │   └── pdf-export.md                   ❌ FEHLT
│   │
│   └── delivery/                           ❌ NEU — dieser Ordner
│       ├── initial-setup-baseline.md       ← dieses Dokument
│       ├── wave2-scope.md                  ← nächstes Dokument
│       └── layer2-diagnosis-plan.md        ← nach ADR-007 erstellen
```

---

## 8. Delivery-Controller-Betriebsmodell

### 8.1 Prompt-Übergabe-Workflow (zwingend)

```
1. Ziel und Nutzen verstehen
         ↓
2. Klassifizieren (Bug / Feature / Architecture / UX / Docs)
         ↓
3. Scope bestimmen (Repos, Supabase-Instanzen, Tiers)
         ↓
4. Constraints prüfen (ADRs, RLS, Tier-Gates, Layer-Abhängigkeiten)
         ↓
5. Impact bewerten (Frontend, Backend, Shared-context, API-Vertrag, Auth/Schema)
         ↓
6. Template 1 (Plan) → Claude Code im Ziel-Repo ausgeben
         ↓
7. Plan reviewen: GO / HOLD / SPLIT / BACK TO DOCS
         ↓
8. Bei GO: Template 2 (Implement) ausgeben
         ↓
9. Output reviewen: TypeCheck, Tests, Contract-Check, close-task
         ↓
10. Shared-context updaten (ADR, Backlog, Source-of-Truth)
```

### 8.2 Tool-Routing

| Arbeitskategorie | Tool |
|---|---|
| Engine-Logik, API, Schema, RLS, Migrations | Claude Code in `negotiationcoach-backend` |
| UI-Komponenten, Screens, Frontend-Hooks | Lovable in `negotiation-buddy` |
| Architekturdokumente, ADRs, Verträge | Claude Code in `shared-context` |
| Cross-Repo-Koordination, Planung, Review | Delivery Controller Projekt (Claude.ai) |
| Governance, Audit, Refactoring-Entscheidungen | Governance & Audit Project |

### 8.3 Governance-Rückführung (bei jeder Änderung)

- Jede Architekturentscheidung → ADR in `shared-context/docs/decision-log/`
- Jedes abgeschlossene Backlog-Item → `refactor-backlog.md` updaten
- Jede Wave-Abschluss → `source-of-truth-matrix.md` und `bounded-contexts.md` prüfen
- Jede neue Erkenntnis mit Auswirkung auf Grenzen → `frontend-backend.md` updaten

---

## 9. Klassifizierungsschlüssel

Alle Aussagen in diesem und allen Folgedokumenten verwenden diesen Schlüssel:

| Label | Bedeutung |
|---|---|
| **Observed** | Direkt aus Code, Docs oder Artefakten verifiziert |
| **Inferred** | Aus Kontext erschlossen, nicht direkt verifiziert |
| **Missing** | Information fehlt und ist relevant |
| **Proposed** | Empfehlung, noch nicht entschieden |

---

*Dieses Dokument wird nicht automatisch aktualisiert. Bei wesentlichen Architekturänderungen oder nach jeder Wave ist es zu reviewen und ggf. zu aktualisieren.*
