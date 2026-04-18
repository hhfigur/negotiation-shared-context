# WIKI — Memory Compensation Baseline

**Erstellt:** 2026-04-18
**Klassifizierung:** Observed / Inferred / Missing / Proposed
**Projekt:** NegotiationCoach AI — Feature Delivery Controller
**Anlass:** Projektstart — Claude Memory aus Governance & Audit Projekt nicht direkt zugänglich

---

## 1. Memory-Status

**Observed:** Claude Memory aus dem Governance & Audit Projekt ist im Feature Delivery Controller Projekt nicht direkt zugänglich. Es liegen keine exportierten Memory-Dumps vor.

**Wissenslücke:** Kurzfristig getroffene Micro-Entscheidungen, die nur im Chat-Verlauf des alten Projekts existierten — z.B. verworfene Optionen, Begründungen für Implementierungsreihenfolgen, mündliche Klärungen von VG-Fragen.

**Kompensationsergebnis (Observed):** Die Lücke ist vollständig kompensierbar. Alle operativ relevanten Inhalte liegen in git-tracked Markdown vor. Die Artefaktabdeckung ist vollständig für alle abgeschlossenen Workstreams. Bestätigt in `docs/delivery/initial-setup-baseline.md` Abschnitt Gap Analysis: "Claude Memory — Missing — vollständig kompensiert. Kein Handlungsbedarf."

**Kompensationsquellen:** Instructions, Prompt-Templates, Control-Tower-Commands, ADRs, refactor-backlog.md, source-of-truth-matrix.md, bounded-contexts.md, frontend-backend.md, ALL-PROMPTS-AUDIT.md, GOV-01-audit-runbook.md, AGENTS.md aller Repos, alle IMP/ARCH/ENGB01 PDFs.

---

## 2. Rekonstruiertes implizites Wissen

### 2.1 Wiederkehrende Architekturregeln

**Inferred** aus ADR-001, ADR-002, AGENTS.md, CLAUDE.md, refactor-backlog.md (jeweils ≥3× belegt):

| Regel | Evidenz-Quellen | Durchsetzungsgrad |
|---|---|---|
| Railway ist kanonischer Execution-Path — keine Ausnahmen | ADR-001, CRIT-01, 5× im Backlog | Absolut |
| Jede neue DB-Tabelle braucht RLS vor Frontend-Zugriff | ADR-001, GOV-01, RFB-002 | Absolut |
| Schema-Änderungen nur via Migration-Files | IMP01, system-overview.md | Absolut |
| Tier-Prüfungen serverseitig — Frontend-Gates sind UI-only | ADR-006, source-of-truth-matrix.md VG-05 | Absolut |
| Kein Algorithmus-Code in Edge Functions oder Frontend | ADR-001, CRIT-01, RFB-006 | Absolut |
| Neue Utilities/Services erst nach Wiederverwendungsprüfung | ALL-PROMPTS-AUDIT, CLAUDE.md | Absolut |
| Jede Architekturentscheidung in git-tracked Markdown — nie nur im Chat | GOV-01, AGENTS.md | Absolut |
| Notion = Spiegel, nicht operative Wahrheit | ALL-PROMPTS-AUDIT, GOV-01 | Absolut |

### 2.2 Wiederkehrende Entscheidungsmuster

**Inferred** aus Backlog-Verlauf, ADR-Sequenz, VG-Auflösungen:

**Muster 1 — Defer statt voreilig entscheiden:** Wenn eine Architekturentscheidung fehlt, wird die abhängige Implementierung explizit geblockt (RFB-006 → RFB-026; RFB-016a → Knowledge Pipeline). Kein Quick Fix ohne ADR.

**Muster 2 — Observed/Inferred/Missing/Proposed als Pflichtklassifikation:** Jedes Dokument und jede Aussage trägt eine Klassifikation. Implizite Annahmen als Fakten zu behandeln ist systemwidrig.

**Muster 3 — Plan-before-implement zwingend:** Template 1 (Plan Only) immer vor Template 2 (Implement). Kein Code ohne REVIEW PLAN → GO.

**Muster 4 — Minimaler Diff:** "Stay within the approved scope", "Minimal change only", "Do not broaden the refactor" — in jedem Implementierungs-Prompt dreifach verankert.

**Muster 5 — Commit-Punkte nach jeder Phase:** Kein freischwebender Zustand. Jede Phase endet mit git commit, Docs-Update, Backlog-Update.

**Muster 6 — Cross-Repo immer zuerst auf Auswirkungen prüfen:** Kein Change ohne Impact Assessment auf beide Repos und beide Supabase-Clients.

### 2.3 Häufige Warnhinweise (wiederholt in ≥3 Dokumenten)

**Observed:**

- "Do not invent facts about code you cannot see" — MASTER-ARCH-01, CC-BE-01, CC-FE-01, AGENTS.md
- "Kein neues Utility/Service ohne Wiederverwendungsprüfung" — CLAUDE.md, ALL-PROMPTS-AUDIT, Backlog
- "Keine neuen Business-Regeln im Frontend" — ADR-001, CLAUDE.md, GOV-01
- "RLS vor Frontend-Zugriff" — ADR-001, ADR-002, RFB-002, IMP01
- "Stripe nicht live — kein Tier-Gating in Produktion aktiv" — source-of-truth-matrix.md, RFB-032, wave2-scope.md

### 2.4 Wiederkehrende Refactoring-Motive

**Observed** aus RFB-001 bis RFB-036:

| Motiv | Backlog-Einträge | Kanonische Lösung |
|---|---|---|
| Frontend schreibt direkt in DB | RFB-003, RFB-004, HIGH-01 | Move to Railway API |
| Doppelte Logik (EF vs. Railway) | RFB-006, RFB-026, CRIT-01 | Railway als kanonischer Owner |
| Inkonsistente Tier-Definitionen | RFB-007, RFB-036, CRIT-04 | Unified enum + serverseitig |
| Silent failures / kein Error surfacing | RFB-024, RFB-004 | Explizite Fehler-Rückgabe statt Fallback |
| Middleware ohne Enforcement | RFB-001, VG-05 | Hard reject in Middleware |
| Auth-Check nur Frontend | RFB-002, CRIT-02 | RLS + Railway assertSessionOwner() |

---

## 3. Baseline-Lückenliste

### 3.1 Fehlende Memory-Inhalte (nicht rekonstruierbar)

| Lücke | Auswirkung | Risiko |
|---|---|---|
| Verworfene Optionen bei ADR-003 (warum nicht ein AI-Provider?) | Begründungstiefe fehlt | Niedrig — ADR-003 ist bindend |
| VG-04: user_profiles Signup-Erstellung — Verifikationsmechanismus | VG-04 noch offen | **Medium** — vor User-Profile-Features verifizieren |
| Layer-1-Test-Output-Protokoll nach RFB-023 | Keine Regressionsbasis | **Medium** — Layer-1 als "done" ohne Test-Protokoll |
| Produktionsdaten-Stand (aktive User, Live-Tier-Verteilung) | Deployment-Entscheidungen | **Medium** — Stripe nicht live |

### 3.2 Vermutete implizite Regeln (noch nicht formal dokumentiert)

**Proposed** — sollten in Shared-context nachgetragen werden:

| Vermutete Regel | Basis | Empfehlung |
|---|---|---|
| Layer-2 ist Tier-Gate: `privat` bekommt keine Marktdaten | IMP02, source-of-truth-matrix.md | In frontend-backend.md Tier-Gate-Tabelle explizit dokumentieren |
| `modelRouter.ts` muss bei allen LLM-Calls verwendet werden | RFB-011 | Als Constraint in CLAUDE.md backend eintragen |
| Jede neue EF muss im frontend-backend.md API-Vertrag stehen | ADR-001, frontend-backend.md | Als Guardrail in CC-GR-01 eintragen |
| Knowledge Graph TTL = 7 Tage ist Business-Rule | IMP02 | In source-of-truth-matrix.md als Business-Rule markieren |

### 3.3 Noch nicht gesicherte Annahmen

**Missing:**

| Annahme | Status | Abhängige Features |
|---|---|---|
| VG-04: user_profiles-Zeile bei Signup automatisch erstellt | ⚠️ Offen | User-Profile-Features, Tier-Anzeige |
| Layer-1-Tests laufen stabil durch | **Inferred** — kein Test-Output-Protokoll | Regression-Gate für Layer-2-Fix |
| VG-05-A: EF /chat ohne JWT Auth — kein RFB registriert | ⚠️ Offen | Jede EF-Nutzung durch authenticated users |

### 3.4 Empfohlene Nachdokumentation (priorisiert)

**Proposed:**

| Dokument | Inhalt | Priorität |
|---|---|---|
| `docs/decision-log/ADR-007-dual-layer1.md` | VG-06-Entscheidung | **Kritisch — Blocker** |
| `docs/delivery/layer2-diagnosis-plan.md` | Layer-2-Diagnoseplan | **Hoch — Wave-2-Gate** |
| `docs/features/layer3-simulation.md` | Layer-3-Spec aus ENGB01 | Mittel — vor Layer-3-Start |
| `docs/features/scenario-marketplace.md` | Marketplace-Spec | Mittel |
| `docs/features/pdf-export.md` | PDF-Export-Spec | Mittel |

---

## 4. Gesamtbewertung

**Observed:** Kein operativ relevantes Wissen ist verloren. Die Artefaktabdeckung ist vollständig für alle abgeschlossenen Workstreams.

**Inferred:** Das implizite Wissen des alten Projekts ist vollständig in systematische Regeln, Muster und Entscheidungen überführt worden — durch die Qualität der Governance-Dokumente selbst.

**Missing:** Fünf Wissenslücken mit Medium-Risiko (VG-04, Layer-1-Test-Output, Produktionsdaten-Stand, ADR-007, VG-05-A ohne RFB). Alle bekannt und im wave2-scope.md als adressierbar erfasst.

**Proposed:** Acht Nachdokumentierungen empfohlen — keine davon blockiert Wave-2-Start außer ADR-007.

---

*Dokument erstellt aus Session-Analyse 2026-04-18. Nicht automatisch aktualisiert — bei neuen Memory-Importen oder VG-Auflösungen manuell fortschreiben.*
