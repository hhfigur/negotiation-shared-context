**Status:** DRAFT — Template 1-DEV Ausgabe (PLAN ONLY). Wartet auf GO / HOLD / SPLIT / BACK TO DOCS.
**Item-Typ:** Cross-cutting Engineering-Prozess (kein Produkt-Feature — kein NC-ID, kein Layer/Tier im Produktsinn)
**Quelle:** `loop-coding-integration-prompts.md` (User-Downloads), PROMPT 0
**Erstellt:** 2026-07-16
**Betroffene Repos:** shared-context (Governance), negotiationcoach-backend (Harness), negotiation-buddy (Harness + tsc strict)

---

# Loop-Coding Integration — Master-Plan

## 0. Vorarbeit (Observed)

- `docs/delivery/claude-code-prompt-templates-dev.md` existiert und wurde vollständig gelesen. Der in PROMPT 0/1 referenzierte Pfad `docs/delivery/follow-ups/claude-code-prompt-templates-dev.md` war **stale** (falscher Ordner) — im Quell-Dokument bereits korrigiert.
- `/feature-plan`, `/feature-implement`, `/bug-fix` gelesen.
- `tasks/lessons.md` gelesen — keine früheren Einträge zu verify-loops oder Acceptance-Orakeln; ein Eintrag (2026-07-08) zu `/close-task-dev`-Formatmismatch ist strukturell relevant (siehe 6.7).
- Kein bestehender `product/feature-register.md`-Eintrag für dieses Thema — Layer-Abhängigkeit (0→3) greift hier nicht, da es sich um Tooling/Governance handelt, nicht um eine Produktschicht.

---

## 1. Scope-Matrix

| Baustein | Typ | Repo | Betroffene Dateien |
|---|---|---|---|
| A — Kritik-/Red-Team-Loop | docs-only | shared-context | `.claude/skills/feature-plan/SKILL.md` (neuer Schritt "Critic-Pass" zwischen Schritt 4b und 5) |
| B — Ausführbare Acceptance-Orakel | docs-only | shared-context | `.claude/skills/feature-implement/SKILL.md` (Schritt 1/2), `docs/delivery/claude-code-prompt-templates-dev.md` (Template 2b-DEV Acceptance-Abschnitt) |
| C — Verifikations-Harness (`verify.sh`) | **code** | negotiationcoach-backend + negotiation-buddy | neue Dateien: `scripts/verify.sh`, `scripts/curl-assert.sh`, `scripts/smoke-enrich.sh` (Backend); `scripts/verify.sh` (Frontend) |
| D — Reproduktions-Test-First | docs-only | shared-context | `.claude/skills/bug-fix/SKILL.md` — **Überlappung mit bestehender Phase 1.5, siehe 1.1** |
| Contract | docs-only | shared-context | neu: `docs/contracts/verify-harness.md` |
| Neuer Skill | docs-only | shared-context | neu: `.claude/skills/verify-loop/SKILL.md` |

### 1.1 Wichtiger Befund: Baustein D existiert bereits zu ~80%

`bug-fix/SKILL.md` Phase 1.5 ("Laufzeit-Evidenz-Gate", Zeilen 58–120) verlangt bereits **heute**:
- mindestens eine Laufzeit-Evidenzquelle (curl-Aufruf, Test-Script, Supabase-Logs) vor jedem Fix-Prompt
- explizite Observed/Inferred/Missing-Klassifizierung
- "`Inferred` allein ist kein ausreichender Grund für einen Fix-Prompt"

Das ist inhaltlich fast deckungsgleich mit PROMPT 1 Baustein D ("erst fehlschlagendes curl/Test (RED), dann Fix bis GREEN"). Die **einzige echte Lücke**: Phase 1.5 verlangt aktuell nur *dokumentierten* Output, nicht dass der Repro-Test als **Datei committet und als Regressions-Orakel** erhalten bleibt.

**Empfehlung:** Baustein D nicht als neue Phase einführen, sondern Phase 1.5 um einen Satz erweitern: "Falls die Evidenzquelle ein Test-Script/curl-Aufruf ist, wird dieser als Datei committet (nicht nur als Output dokumentiert) und bleibt nach dem Fix als Regressions-Orakel bestehen." Minimal-Diff statt Parallel-Prozess.

---

## 2. Sequenzierung & Abhängigkeiten

```
#0 (dieser Plan) → GO/HOLD/SPLIT
  → #1 Governance (shared-context, docs-only)
       → #2 Backend-Harness (negotiationcoach-backend, code)
       → #3 Frontend-Harness (negotiation-buddy, code)
```

#2 und #3 sind voneinander unabhängig (kein Datenfluss zwischen den Harnesses) und könnten parallel laufen — die im Quell-Dokument angegebene Präferenz "#2 hat Vorrang wegen `/api/enrich`-Smoke-Test als NC-L2-FIX-Orakel" ist **nicht mehr gültig**, siehe kritischer Befund 6.1. Empfehlung: #2 und #3 können in beliebiger Reihenfolge oder parallel laufen.

---

## 3. Blast-Radius-Triage

### 3.1 Frontend tsc-strict (Observed, tatsächlich gemessen — nicht geschätzt)

`npx tsc --noEmit -p tsconfig.app.json --strictNullChecks --noImplicitAny` gegen den aktuellen `negotiation-buddy`-Stand:

```
8 Fehler in 6 Dateien:
  src/components/ChatInput.tsx        (1)
  src/pages/Index.tsx                 (3)
  src/pages/Profile.tsx                (1)
  src/pages/StrategyGenerator.tsx      (1)
  src/pages/TeamDashboard.tsx           (1)
```

**Deutlich unter der SPLIT-Schwelle (>50) aus PROMPT 3.** Kein Grund für ein Staffel-Vorgehen pro Verzeichnis — Prompt 3 kann strict in einem Rutsch aktivieren und alle 8 Stellen fixen. Fehlerbilder sind homogen (fehlende Null-Checks bei `ref`, State-Defaults, Enum-Indexing) — geringes Regressionsrisiko.

### 3.2 Skill-Änderungsrisiko

`tasks/todo.md` ist aktuell leer (keine IN PROGRESS/BLOCKED-Items) — kein laufender Workflow, der durch Änderungen an `/feature-plan`, `/feature-implement`, `/bug-fix` mitten im Ablauf unterbrochen würde. Guter Zeitpunkt für Governance-Änderungen.

### 3.3 Backend-Harness-Lücken (Observed)

- **Kein Lint-Setup im Backend:** `negotiationcoach-backend/package.json` hat kein `lint`-Script, kein `.eslintrc*`/`eslint.config.*` gefunden. Der `verify.sh`-Contract (tsc → test → contract-check → curl-assert → lint) braucht für den letzten Schritt entweder ein neues Minimal-Eslint-Setup oder eine explizite "lint: n/a (kein Setup)"-Markierung — **kein stiller Skip**.
- **`npm test` deckt `tests/layer3/` nicht ab:** Script lautet `ts-node ... tests/layer1/layer1.test.ts && ts-node ... tests/layer2/layer2.test.ts` — `tests/layer3/` existiert als Verzeichnis, ist aber nicht verdrahtet. `verify.sh` würde diese Lücke sonst stillschweigend erben.
- **Dev-Port:** `PORT` env var, Default `3001` (`src/api/routes.ts:373`) — für Health-Check/curl-assert in Prompt 2 zu verwenden.

---

## 4. ADR-Bedarf

**Ja, ein ADR wird empfohlen.** Begründung: "verify-loop als Pflicht-Gate" verändert die Definition-of-Done für **jede** künftige Feature-/Bug-Delivery in beiden Code-Repos — vergleichbar in Tragweite mit ADR-007 (Architekturentscheidung mit Delivery-Gate-Charakter). Eine stillschweigende Skill-Änderung ohne ADR würde die in AGENTS.md/CLAUDE.md verankerte Regel "ADR-Entscheidungen vor Implementierung" selbst verletzen.

**Vorschlag: ADR-011 — Verify-Loop als Pflicht-Gate für Feature-/Bug-Delivery**

Optionsskizze (auszuarbeiten via `/adr-create` nach GO):
- **Option A — Sofort repo-weit verbindlich:** `verify-loop` wird ab Merge von PROMPT 1 in `/feature-implement` und `/bug-fix` hart verankert (kein DONE ohne grünes Orakel).
- **Option B — Pilot zuerst:** Nur Backend (wo `/api/enrich` als konkretes Orakel existiert) macht den Gate verbindlich; Frontend bleibt vorerst advisory, bis `verify.sh` dort erprobt ist.
- **Option C — Advisory only:** Skill dokumentiert den Loop als empfohlenes Muster, aber kein Hard-Gate — geringster Zwang, aber auch geringste Wirkung (widerspricht dem Zweck des Vorhabens).

*Empfehlung (proposed, nicht entschieden):* Option A, da Backend und Frontend beide realistische, kleine Blast-Radien haben (siehe 3.1/3.3) und ein Pilot hier eher Verzögerung als Risikoreduktion bringen würde.

---

## 5. Contract-Skizze `verify.sh` (repo-agnostisch)

```
Pflichtreihenfolge, Abbruch bei erstem Fehler (exit != 0 propagiert):
  1. tsc --noEmit
  2. Testsuite (npm test / vitest run)
  3. contract-check (nur wenn API/Contract-relevante Dateien geändert)
  4. curl-assert / smoke (nur Backend — setzt laufenden lokalen Dev-Server voraus)
  5. lint

Ausgabeformat pro Schritt:
  [PASS] <Schrittname>
  [FAIL] <Schrittname> (exit <code>) — <erste Fehlerzeile>

Abschluss-Summary (maschinenlesbar):
  VERIFY_RESULT: PASS  (alle Schritte grün)
  VERIFY_RESULT: FAIL  (n/5 Schritte grün) — erster Fehlerschritt: <Name>

Exit-Code des Gesamtscripts = Anzahl fehlgeschlagener Schritte (0 = grün).
```

Repo-Spezialisierung:
- **Backend:** Schritt 4 braucht einen Health-Check gegen `localhost:<PORT>` *vor* den curl-Assertions; wenn Server nicht erreichbar → eigener FAIL-Grund ("server not running"), nicht als curl-Fehler getarnt.
- **Frontend:** kein serverabhängiger Schritt; Schritt 4 entfällt (kein `curl-assert` im Frontend-Contract laut PROMPT 3).

---

## 6. Offene Punkte / Annahmen (Missing / Inferred / kritische Korrekturen)

### 6.1 KRITISCH — RED-Zustand-Prämisse in PROMPT 2 ist stale (Observed)

PROMPT 2 geht davon aus: *"/api/enrich ist aktuell fehlerhaft (Layer 2 broken) ... smoke-enrich.sh WIRD initial fehlschlagen."*

Das ist laut aktuellem Repo-Stand **nicht mehr korrekt**:
- `product/roadmap.md`: *"R-2026-05: NC-L2-FIX — Layer 2 Market Data ✅"* (Released, "Resolved since last update").
- `product/releases/current.md` (R-2026-09, NC-L2-UI): *"Market-Data-Werte (Marktmedian, Reality Score) im UI sichtbar ✅"* — Exit-Kriterium erfüllt.
- `docs/features/layer3-simulation.md` Zeile 6 bestätigt explizit: *"Layer-2-Fix: ✅ AUFGELÖST 2026-07-07 — R-2026-05 (NC-L2-FIX) und R-2026-09 (NC-L2-UI) sind Released und ... verifiziert."*

**Konsequenz für Prompt 2:** Die Akzeptanzkriterien müssen umgekehrt werden — `smoke-enrich.sh` sollte auf sauberem `main` **GREEN** laufen, nicht RED. Falls es tatsächlich rot ist, ist das ein neuer, unerwarteter Befund (potenzielle Regression), keine bekannte Baseline. Vor Ausführung von Prompt 2 empfiehlt sich ein kurzer manueller `/api/enrich`-Check gegen den lokalen Dev-Server, um den *tatsächlichen* Ist-Zustand zu bestätigen, bevor die Akzeptanzkriterien geschrieben werden.

### 6.2 Template-Inkonsistenz: Gemini vs. Anthropic für Edge Functions (Observed)

`docs/delivery/claude-code-prompt-templates-dev.md` Template 2b-DEV, Constraints-Block (Zeile 185): *"Edge Functions: Gemini via Supabase AI Gateway"*.

Das widerspricht der aktuellen, verbindlichen Regel in `shared-context/CLAUDE.md`: *"Alle LLM-Calls: Anthropic Claude (ADR-003) — sowohl Express Backend als auch Edge Functions (alle EFs nutzen claude-haiku-4-5-20251001)."* `ADR-003-ai-provider-strategy.md` selbst dokumentiert die Migration weg von Gemini ("Supersedes: MIG01 (Migration Lovable Gateway Gemini → Anthropic)"), scheint aber nicht vollständig auf den Post-Migrations-Stand aktualisiert (Zeile 31 listet noch "Gemini 2.5 Flash" für EF-Pfad).

**Konsequenz:** Da PROMPT 1 (Baustein 6) ohnehin Template 2b-DEV anfasst ("Prompt-Templates aktualisieren"), sollte dieser Constraints-Block im selben Commit korrigiert werden — kein Extra-Scope, sondern Konsistenzfix an einer Stelle, die gerade offen ist.

### 6.3 Kein Lint-Setup im Backend

Siehe 3.3 — Entscheidung nötig, ob Prompt 2 ein Minimal-Eslint-Setup mitliefert oder den Schritt explizit als "n/a" markiert.

### 6.4 `npm test` deckt `tests/layer3/` nicht ab

Siehe 3.3 — kleine, aber im Scope liegende Korrektur für Prompt 2, da sonst der neue `verify.sh` eine bestehende Lücke stillschweigend erbt.

### 6.5 CRIT-03 Status unklar für Auth-Fehler-Testfall

`AGENTS.md` listet `CRIT-03: backend authMiddleware never returns 401 — all endpoints publicly accessible` als bekannten Befund. `product/roadmap.md` zeigt NC-SEC-01/02 als Released (R-2026-08). Ob CRIT-03 dadurch aufgelöst wurde, ist hier nicht verifiziert (Missing) — relevant für den "Auth-Fehler"-Testfall im Backend-curl-assert (Prompt 2 Design-Gate deckt das bereits ab: "Fehlerfälle: ... Auth-Fehler" — Prompt 2 muss den aktuellen Ist-Zustand selbst verifizieren, nicht den alten Audit-Befund annehmen).

### 6.6 Kein NC-ID / kein Feature-Register-Eintrag

Dieses Vorhaben ist Tooling/Prozess, kein Produkt-Feature. Offene Frage an den User: Soll es trotzdem einen `product/feature-register.md`-Eintrag bekommen (Typ "Enabler", Status-Tracking), oder bleibt es ausschließlich über ADR + diesen Feature-Stub + zukünftige Skill-Commits nachvollziehbar? **Keine Annahme getroffen — explizite Entscheidung erforderlich.**

### 6.7 `/close-task-dev`-Formatmismatch (bekannt, aus lessons.md 2026-07-08)

Falls dieses Vorhaben über `product/feature-register.md` getrackt wird (siehe 6.6), gilt die bekannte Lücke: `/close-task-dev` unterstützt aktuell nur `refactor-backlog.md`-Format (`###`+Summary-Index), nicht das flache `feature-register.md`-Tabellenformat. Bei mehrphasigen Items (dieses hier hat 3 Folge-Deliveries #1–#3) nur nach *vollständigem* Abschluss aller Phasen aufrufen, nicht nach jeder einzelnen.

### 6.8 Nebenbefund (nicht Teil dieses Plans): verwaistes Worktree

`.claude/worktrees/quizzical-poitras-6b3676` (detached HEAD, locked) wurde beim Session-Start gefunden — unabhängig von diesem Vorhaben, wird hier nur der Vollständigkeit halber vermerkt, nicht bearbeitet.

---

## 7. Zusammenfassung für GO/HOLD/SPLIT-Entscheidung

- **Kein Layer-Blocker** (Baustein ist cross-cutting, keine Layer-Abhängigkeit 0→3 verletzt).
- **Ein ADR wird empfohlen** (ADR-011, Optionsskizze in Abschnitt 4) — sollte vor oder zusammen mit PROMPT 1 entschieden werden.
- **Blast Radius ist klein und beherrschbar** auf beiden Code-Repos (Frontend: 8 Fehler/6 Dateien; Backend: zwei dokumentierte Infra-Lücken, kein Architekturrisiko).
- **Ein kritischer Fakten-Fehler** in der Quelle (6.1, RED-Zustand-Prämisse) muss vor Ausführung von Prompt 2 korrigiert werden, sonst wird ein falsches Akzeptanzkriterium verifiziert.
- **Eine Redundanz** (6.1.1 — Baustein D) sollte als Erweiterung statt Neubau behandelt werden, um `bug-fix/SKILL.md` nicht unnötig aufzublähen.

**STOP — wartet auf GO / HOLD / SPLIT / BACK TO DOCS.**
