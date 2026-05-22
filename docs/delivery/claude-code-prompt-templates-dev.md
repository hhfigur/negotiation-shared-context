# Claude Code Prompt Templates — Feature Delivery Controller

**Location:** `shared-context/docs/delivery/claude-code-prompt-templates-dev.md`
**Owner:** Feature Delivery Controller (Claude)
**Basis:** Extends `docs/claude-code-prompt-templates.md` (Refactor Templates)
**Status:** Active
**Last updated:** 2026-04-24

---

## Purpose

These are the two canonical prompt templates used by the Feature Delivery Controller
when generating Claude Code prompts for feature development and bug fixes in the
`negotiationcoach` project.

- **Template 1-DEV — Plan** is used for every planning step before any code is touched.
- **Template 2-DEV — Implement** is used only after a plan has been reviewed and
  a GO decision has been issued by the Delivery Controller.

Relationship to refactor templates:
- Template 1-DEV extends Template 1 (Refactor) with feature-specific fields:
  Layer scope, Tier scope, ADR gate, API delta, DB delta.
- Template 2-DEV extends Template 2 (Refactor) with: architecture constraint guards,
  DB migration rules, and an automatic `/close-task-dev` invocation at the end.
- `/close-task-dev` extends `/close-task` with Wave-Scope stamping and API/DB
  artifact tracking.

Never skip Template 1-DEV. Never use Template 2-DEV without a reviewed and
approved plan. Never invoke `/close-task-dev` manually if Template 2-DEV ran —
it is invoked automatically at the end of Template 2-DEV.

---

## Template-Auswahl

| Situation | Template |
|---|---|
| Plan erstellen (immer zuerst) | Template 1-DEV |
| Reine Docs-Änderung implementieren | Template 2-DEV (Variante A) |
| Code-Delivery implementieren | Template 2b-DEV (Variante B — Subagent) |

---

## Template 1-DEV — Claude Code Plan (Feature / Bug)

> Trigger: `PLAN ITEM [ITEM_ID]` from the Feature Delivery Controller

```
SESSION CONTEXT:

Working directory: shared-context/
Available repos: negotiation-buddy (../negotiation-buddy), negotiationcoach-backend (../negotiationcoach-backend)
TARGET REPO: [TARGET_REPO]
TARGET PATH: ../[TARGET_REPO]/[konkreter Pfad — aus Prompt-Inhalt ableiten]
Active rules: shared-context/CLAUDE.md + ../[TARGET_REPO]/CLAUDE.md + ../[TARGET_REPO]/AGENTS.md
Git commits: cd ../[TARGET_REPO] && git add [files] && git commit -m "[type(scope): msg]"

---

BUG_FILE: [Pfad zur Bug-Datei — z.B. docs/delivery/bugs/BUG-20260427-xyz.md]
PLAN ONLY. DO NOT CHANGE CODE YET.
Lies zuerst vollständig: [BUG_FILE]
Lies zusätzlich:

  shared-context/docs/audits/refactor-backlog.md
  shared-context/docs/contracts/frontend-backend.md
  ../[TARGET REPO]/CLAUDE.md
  ../[TARGET REPO]/AGENTS.md
  [ADR-Constraints aus BUG_FILE]

Erstelle einen Planungsvorschlag:
1. Wahrscheinliche Fehlerursache (Dateiname + Funktion)
2. Kleinste sichere Fix-Scope
3. Exakt betroffene Dateien (vollständige Pfade)
4. SIDE-EFFECT-CHECK (PFLICHT — vor jedem anderen Schritt):
   Für jede betroffene Datei/Funktion:
   a) grep -r "[geänderte Funktion/Export]" src/ → wer importiert/nutzt sie?
   b) Kann die Änderung das Verhalten für andere Caller verändern? (ja/nein + Begründung)
   c) Loop-Risiko bei useEffect/useCallback: verändert sich eine Dep durch den Effect selbst?
   d) DB-Schema-Änderung: welche Inserts/Selects laufen auf betroffene Spalten/Tabellen?
   e) API-Contract-Änderung: welche Frontend-Caller rufen diesen Endpoint auf?
   → Erst wenn alle fünf Punkte beantwortet sind, weiter mit Schritt 5.
5. Tests die danach laufen müssen
6. Docs/Contracts die zu updaten sind
7. Rollback-Strategie
8. Exakter Git-Commit-Befehl

Schreibe den Plan nach Fertigstellung in den Abschnitt ## Plan der BUG_FILE.
Setze Status in BUG_FILE auf PLANNED.
Committe BUG_FILE: git add [BUG_FILE] && git commit -m "docs(bugs): [Bug-ID] plan hinzugefügt"
STOP. Warte auf GO / HOLD / SPLIT / BACK TO DOCS.
```

---

## Template 2-DEV — Claude Code Implementation (Feature / Bug)

> Trigger: `REVIEW PLAN` → GO decision issued by Feature Delivery Controller

```
SESSION CONTEXT:

Working directory: shared-context/
Available repos: negotiation-buddy (../negotiation-buddy), negotiationcoach-backend (../negotiationcoach-backend)
TARGET REPO: [TARGET_REPO]
TARGET PATH: ../[TARGET_REPO]/[konkreter Pfad — aus Prompt-Inhalt ableiten]
Active rules: shared-context/CLAUDE.md + ../[TARGET_REPO]/CLAUDE.md + ../[TARGET_REPO]/AGENTS.md
Git commits: cd ../[TARGET_REPO] && git add [files] && git commit -m "[type(scope): msg]"

---

BUG_FILE: [Pfad zur Bug-Datei — gleiche Datei wie in Template 1-DEV]
IMPLEMENT THE APPROVED PLAN ONLY.
Lies zuerst vollständig: [BUG_FILE]
Der genehmigte Plan steht im Abschnitt ## Plan der BUG_FILE.
Weiche nicht vom Plan ab. Kein Gold-Plating.
Regeln:

  Minimale Änderung only
  Bestehenden Code wiederverwenden vor neuen Utilities/Services
  Contracts/Docs updaten wenn Boundaries sich ändern
  Unrelated shared logic nicht anfassen

Nach Implementierung:

  Geänderte Dateien ausgeben (vollständige Pfade)
  Tests ausgeführt und Ergebnis
  Docs aktualisiert
  Verbleibende Risiken
  SIDE-EFFECT-VERIFIKATION (PFLICHT vor Commit):
    - Alle aus Plan-Schritt 4 identifizierten Abhängigen: sind sie noch funktional?
    - npx tsc --noEmit: 0 Fehler
    - Render-Log-Check nach Deploy: keine neuen schema cache Errors
  Exakter Git-Commit-Befehl

Schreibe Ergebnis in Abschnitt ## Implement der BUG_FILE.
Setze Status in BUG_FILE auf IN PROGRESS.
Committe BUG_FILE: git add [BUG_FILE] && git commit -m "docs(bugs): [Bug-ID] implement-ergebnis hinzugefügt"
STOP. Warte auf /close-task.
```

---

## Template 2b-DEV — Claude Code Implement (Subagent-driven)

> Nutze dieses Template wenn: Code-Delivery (kein reines Docs-Item), approved Plan aus Template 1-DEV liegt vor.
> Nutze Template 2-DEV (Variante A) wenn: Reine Docs-Änderungen, Wiki-Updates, ADR-Writes ohne Code.

```
SESSION CONTEXT:

Working directory: shared-context/
Available repos: negotiation-buddy (../negotiation-buddy), negotiationcoach-backend (../negotiationcoach-backend)
TARGET REPO: [TARGET_REPO]
TARGET PATH: ../[TARGET_REPO]/[konkreter Pfad]
Active rules: shared-context/CLAUDE.md + ../[TARGET_REPO]/CLAUDE.md + ../[TARGET_REPO]/AGENTS.md
Git commits: cd ../[TARGET_REPO] && git add [files] && git commit -m "[type(scope): msg]"

---

BRIEF: [Pfad zur Brief-Datei — z.B. product/briefs/NC-SEC-01.md]
APPROVED PLAN: [Pfad zur Plan-Ausgabe oder Inline-Plan]
IMPLEMENT THE APPROVED PLAN ONLY. NO GOLD-PLATING.
/subagent-driven-development

Subagent-Konfiguration:

  Implementer: Umsetzt den approved Plan. Stellt Fragen BEVOR er beginnt.
  Committet nach Implementierung.
  Report-Format: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

  Spec-Reviewer: Liest Code direkt — vertraut NICHT dem Implementer-Report.
  Prüft: Missing requirements, Extra work, Misunderstandings.
  Output: ✅ Spec compliant ODER ❌ Issues found: [file:line]

  Code-Quality-Reviewer: Nur nach bestandenem Spec-Review dispatchen.
  Prüft: Single responsibility, Unit-Decomposition, File-Growth.
  Output: Strengths | Issues (Critical/Important/Minor) | Assessment

Constraints (immer aktiv, nicht verhandelbar):

  Keine Logik oder Business-Regeln ins Frontend
  Alle LLM-Calls: Backend (Render.com) → Anthropic Claude (ADR-003)
  Edge Functions: Gemini via Supabase AI Gateway
  Tier-Prüfungen immer serverseitig
  Schema-Änderungen nur via Migration-Files + supabase db push
  Layer-Abhängigkeiten: 0 → 1 → 2 → 3

SIDE-EFFECT-CHECK (PFLICHT — Implementer führt aus, bevor Code geschrieben wird):
  Für jede zu ändernde Datei/Funktion:
  1. grep -r "[Funktion/Export]" src/ → alle Caller auflisten
  2. Verändert die Änderung das Verhalten für ANDERE Caller? (explizit beantworten)
  3. Loop-Risiko: verändert sich eine useEffect/useCallback-Dep durch den Effect selbst?
  4. DB-Änderung: welche Inserts/Selects auf betroffene Tabelle/Spalte existieren?
  5. API-Änderung: welche Frontend-Caller nutzen diesen Endpoint?
  Ergebnis: "Side-Effect-Check: [Liste der Abhängigen] — alle geprüft, kein Regressionsrisiko"
  Oder: "Side-Effect-Check: [Abhängiger X] könnte betroffen sein → fixe auch [X]"

Nach bestandenem Code-Quality-Review:
Schreibe Ergebnis in Abschnitt ## Implement der Brief-Datei.
Setze Status in Brief-Datei auf IN PROGRESS.
git add [BRIEF_FILE] && git commit -m "docs(briefs): [Item-ID] implement-ergebnis hinzugefügt"
STOP. Warte auf /close-task.
```

---

## Field Reference

| Field | Content |
|---|---|
| `[TARGET_REPO]` | `negotiation-buddy` or `negotiationcoach-backend` |
| `[ITEM_ID]` | Item ID from wave2-scope.md or refactor-backlog.md (e.g. NC-014, RFB-026) |
| `[ITEM_TITLE]` | Exact title from the backlog or wave scope |
| `[TYPE]` | `bug`, `feature`, or `arch` |
| `[LAYER]` | `0`, `1`, `2`, `3`, or `cross-cutting` |
| `[TIER_SCOPE]` | `free`, `privat`, `kmu`, `profi`, or `all` |
| `[PASTE_SHORT_APPROVED_PLAN]` | 3–5 sentence summary of the reviewed plan |
| `[COMMIT_HASH]` | Short git commit hash after implementation commit |
| `[DATE]` | ISO date of implementation (e.g. 2026-04-24) |

---

## Rules for the Feature Delivery Controller

- Template 1-DEV is always used before Template 2-DEV. No exceptions.
- Template 2-DEV is only issued after a GO decision in a `REVIEW PLAN` response.
- If an ADR is required and not yet decided, the next output is an ADR task —
  not an implementation prompt.
- If Layer N-1 is unstable, no Template 1-DEV or 2-DEV is issued for Layer N.
- Cross-repo items require an explicit impact assessment before Template 1-DEV.
- `/close-task-dev` is always invoked automatically at the end of Template 2-DEV.
  Never wait for the user to trigger it.
