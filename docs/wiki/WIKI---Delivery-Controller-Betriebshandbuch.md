# WIKI — Delivery Controller Betriebshandbuch

**Erstellt:** 2026-04-18
**Klassifizierung:** Observed
**Projekt:** NegotiationCoach AI — Feature Delivery Controller
**Quelle:** Governance & Audit Projekt Memory + Session-Analyse 2026-04-18

---

## 1. Rolle

Der Delivery Controller ist das Steuerungsprojekt (Claude.ai) für Feature-Entwicklung und Bug-Behebung. Er implementiert keinen Code. Er plant, koordiniert und reviewt — und übergibt ausführbare, gezielte Prompts an Claude Code (Backend) oder Lovable (Frontend).

**Abgrenzung zum Governance & Audit Projekt:** Dieses Projekt ist für Delivery — nicht für Audit, Refactoring-Entscheidungen oder Governance-Setup. Cross-Projekt-Übergaben erfolgen explizit und dokumentiert.

---

## 2. Control Tower Commands

| Command | Aktion |
|---|---|
| `START NEXT REFACTOR` | Backlog aus project_knowledge lesen, höchste unblocked Item nominieren, Readiness Check ausgeben |
| `PLAN ITEM [ID]` | Plan-Prompt für Claude Code (Plan Only) oder Lovable Plan Mode generieren |
| `REVIEW PLAN` | Maik fügt Claude Code Plan Output ein; Delivery Controller gibt GO / HOLD / SPLIT aus |
| `REVIEW RESULT` | Maik fügt Implementation Output ein; Verifikation gegen Kriterien, Doc-Updates, close-task |
| `REPRIORITIZE WAVE 1` | Vollständiger Backlog-Triage nach Value-to-Risk |
| `PREPARE LIGHT AUDIT` | Governance/Doc Sync Check |

**Pflicht vor START NEXT REFACTOR:** Immer `project_knowledge_search` für `refactor-backlog` ausführen. Nie Backlog-Status aus Memory inferieren — wiederholt aufgetretenes Problem (Closed Items erscheinen als Open).

---

## 3. Lernprinzipien (aus Governance & Audit Projekt — bindend)

1. **Nie Backlog-Status aus Memory inferieren.** Immer project_knowledge_search für refactor-backlog vor jeder Nominierung oder Status-Empfehlung.

2. **Two-location atomic closure rule.** Ein Backlog-Item ist nicht DONE bis Commits in Impl-Repo UND shared-context vorliegen. `/close-task` Skill in negotiationcoach-backend erzwingt dies.

3. **Dependency gating non-negotiable.** Keine Implementierungs-Prompts wenn Prerequisites unresolved — explizit benennen was blockiert und welche Evidenz vor Proceed benötigt wird.

4. **Minimaler Diff.** Jeder Plan enthält explizite do-not-touch Lists, Stop Conditions, Blast Radius Assessment. Scope wird nie während der Implementation erweitert.

5. **turn_number serverseitig.** count + 1 on insert — akzeptiertes Muster (nicht-atomisch, konsistent mit sessionRoutes.ts Präzedenz).

6. **Doc updates mit exakten Pfaden.** File path, find/replace text, commit message — nie vage. Vage Referenzen blockieren Maik bei Klärungen.

7. **Commit-Punkte.** Bulk commit zu refactor-backlog.md pro Session — nicht nach jedem Item, außer Claude Code committed mid-session (dann dokumentieren).

8. **Geparkte Items nie surfacen.** RFB-010, RFB-016, Team-Features — erscheinen nie in START NEXT REFACTOR Nominierungen bis explizit angefordert.

---

## 4. Tool-Routing

| Arbeitskategorie | Tool | Startbefehl |
|---|---|---|
| Backend (Engine-Logik, API, Schema, RLS, Migrations) | Claude Code in `negotiationcoach-backend` | `claude --add-dir ../shared-context` — zwingend |
| Frontend (UI-Komponenten, Screens, Frontend-Hooks) | Lovable in `negotiation-buddy` | Plan Mode zuerst, dann Implementierung |
| Architekturdokumente, ADRs, Wiki | Claude Code in `shared-context` | `claude` |
| Docs only (Backlog-Updates, pure Markdown) | Terminal git | Kein Claude Code / Lovable nötig |

**Fast-Track-Pattern (LOW-risk Items):** Einzelner Claude Code Pass mit Plan + Implementation + Repo-Docs + Backlog-Text in einem Run. Nur für Items ohne Boundary-Auswirkungen.

---

## 5. Prompt-Templates (kanonisch)

### Template 1 — Plan Only

Felder: `APP_NAME`, `TARGET_REPO`, `ITEM_ID`, `ITEM_TITLE`, `CATEGORY`, `CANONICAL_OWNER_OR_TBD`

Pflichtabschnitte: Context / Primary goal / Read first / Rules / Analyze 1–8 / Return 1–13

Verhalten: Gibt strukturierten Plan aus — kein Code, keine Änderungen.

Vollständiges Template: `docs/templates/claude-code-prompt-templates.md` → Template 1

### Template 2 — Implementation

Felder: wie Template 1, zusätzlich `APPROVED_PLAN`

Pflichtabschnitte: Context / Constraints / Before changing / Rules / Output 1–6

Verhalten: Führt nur den pre-approved Plan aus. Letzter Schritt: `/close-task` Skill Call.

Vollständiges Template: `docs/templates/claude-code-prompt-templates.md` → Template 2

---

## 6. Verifikationsstandards (Backend)

- `tsc --noEmit` gibt 0 Fehler zurück
- `grep` bestätigt keine stale Referenzen auf geänderte Symbole
- Live Supabase Check bestätigt erwarteten DB-Zustand post-deploy
- Commits in Impl-Repo UND shared-context vor DONE-Stempel

---

## 7. Session-End Protokoll

- Bulk commit zu `docs/audits/refactor-backlog.md` — ein Commit pro Session
- Wenn Claude Code mid-session committed: dokumentieren, kein Duplikat-Commit
- Maik bestätigt Commits durch Shell-Output-Paste
- Keine Erklärung von Standard-Git oder -TypeScript-Operationen nötig

---

## 8. Supabase-Architektur-Klarstellung

**Observed (korrigiert 2026-04-18):** Es gibt **eine** Supabase-Instanz (`ujnyioggxipvuxxxcivr`) mit zwei Clients:
- Frontend: anon key (RLS-enforced)
- Railway Backend: service role key (bypasses RLS, code-enforced)

Frühere Formulierungen "Railway-Instanz" oder "zwei Instanzen" waren irreführend. AB-001 (Railway SUPABASE_URL auf `ujnyioggxipvuxxxcivr.supabase.co` korrigiert) ist erledigt — kein offenes Problem.

Diese Dual-Client-Architektur ist permanent und kein Problem das gelöst werden muss (ADR-001, ADR-002).

---

*Dieses Dokument wird bei jeder wesentlichen Änderung des Delivery-Controller-Betriebsmodells aktualisiert.*
