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

---

## 8. Delivery Log

### PROMPT 1 — Governance/Skills (shared-context, docs-only)

**Status: DONE.** Commits: `2cd0285` (verify-loop-Skill, feature-plan/
feature-implement/bug-fix-Erweiterungen, ADR-011 PROPOSED, verify-harness.md,
Template-2b-DEV-Update), `668f7bd` (Lessons-Eintrag zum `/close-task`-
Formatmismatch bei item-losen Governance-Deliveries).

Abweichungen vom wörtlichen Prompt-Text (dokumentiert, nicht stillschweigend):
ADR-011 liegt unter `docs/decision-log/` statt `docs/adr/` (folgt der
bestehenden Konvention aller zehn Vorgänger-ADRs). Die
"Gemini via Supabase AI Gateway"-Zeile in Template 2b-DEV wurde **nicht**
korrigiert — Code-Verifikation ergab, dass diese Zeile zum damaligen
Zeitpunkt tatsächlich noch der Realität einer nie deployten
`negotiationcoach-backend`-Datei entsprach, siehe separate Untersuchung
unten.

### Zwischen-Investigation — Provider-Drift (nicht Teil des Loop-Coding-Sets, aber davon ausgelöst)

Während PROMPT 1 auffiel: `negotiationcoach-backend/supabase/functions/chat/index.ts`
ruft Gemini direkt auf, obwohl `CLAUDE.md` "alle EFs nutzen
claude-haiku-4-5-20251001" behauptet. Zwei separate READ-ONLY-Investigationen
(`docs/audits/provider-drift-diagnosis.md`, Commits `1e9074e` + `d3229d1`)
klärten: die tatsächlich **deployte** `chat`-Function (verifiziert via
Supabase-MCP) ist die Anthropic-Version aus `negotiation-buddy` — die
Gemini-Datei in `negotiationcoach-backend` ist ein nie deployter Prototyp
vom 2026-04-22. Zentraler offener Punkt: ob der Render-Production-Build
tatsächlich das aktive (`gpllrgkuozytyrmpfwbb`) oder das Legacy-Supabase-
Projekt (`ujnyioggxipvuxxxcivr`) nutzt, bleibt Missing (nur im
Render-Dashboard prüfbar, nicht aus dem Repo).

### PROMPT 2 — Backend-Harness (negotiationcoach-backend)

**Status: DONE.** Drei Runden, alle gepusht (`origin/main`, `939b7a2`):

- **Runde 1** (`ac09118`): `scripts/verify.sh`, `curl-assert.sh`,
  `smoke-enrich.sh` gebaut. Deckte real auf: `AUTH_REQUIRED`/Dev-Bypass war
  in der lokalen `.env` **nicht** aktiv (echte Supabase-Credentials
  konfiguriert) — die im PROMPT-Text angenommene "RED-Zustand"-Prämisse für
  `smoke-enrich.sh` (aus dem Loop-Coding-Master-Plan bereits als stale
  korrigiert) hielt; stattdessen ein neuer Design-Punkt: Auth-Bypass-Status
  muss als Pre-Flight geprüft werden.
- **Runde 2** (`5620c09`): Spec-Reviewer fand `dev-anonymous` sei kein
  gültiges UUID-Format → Insert in `negotiation_sessions.user_id` schlug
  fehl, `/api/analyze` gab `sessionId: null` mit `200` zurück (stiller
  Contract-Bruch). Fix: fester UUID-Konstante `DEV_BYPASS_USER_ID`. Zweiter
  Fund: `smoke-enrich.sh` prüfte `reality_score` fälschlich gegen 0-100,
  obwohl das Feld vorzeichenbehaftet ist (reale Werte: -5.3, -2.7) — auf
  Finite-Number-Check korrigiert.
- **Runde 3** (`939b7a2`, **Produktionsauswirkung, User-Entscheidung
  eingeholt**): Nach Runde-2-Fix zeigte sich ein tieferer Root Cause:
  `negotiation_sessions.user_id` hat ein Live-FK zu `auth.users(id)` auf dem
  aktiven Supabase-Projekt (`gpllrgkuozytyrmpfwbb`) — jede synthetische
  UUID scheitert daran, unabhängig vom Format. User-Entscheidung (von drei
  Optionen): **einen dedizierten echten Test-User seeden** statt FK zu
  lockern oder die Lücke nur zu dokumentieren. Umgesetzt:
  `scripts/seed-verify-user.ts` (idempotent, Supabase Admin API,
  `user_metadata.tier: 'kmu'`) legt `verify-harness@internal.test` in
  `auth.users` an; `scripts/lib-jwt.sh` holt darüber ein echtes JWT
  (Password-Grant) für `curl-assert.sh`/`smoke-enrich.sh`. Das generierte
  Test-Passwort liegt ausschließlich in der lokalen, git-ignorierten `.env`
  (`VERIFY_HARNESS_TEST_PASSWORD`) — nie geloggt, nie committet, per
  Spec-Review explizit auf Leak-Freiheit geprüft.
  **Wichtig für zukünftige Audits:** `verify-harness@internal.test` ist ab
  sofort ein echter, dauerhafter User in der Produktions-`auth.users`-Tabelle
  des aktiven Supabase-Projekts — kein Mock, kein Wegwerf-Objekt. Bei
  zukünftigen Auth-/User-Audits (z. B. VG-01/VG-02) als bekannte,
  absichtliche Ausnahme mitführen, nicht als Anomalie behandeln.
- **Reviews:** Spec-Reviewer (2 Durchläufe) und Code-Quality-Reviewer —
  beide **Approved** (keine Critical/Important-Findings). Offene Minor-Punkte
  (nicht behoben, bewusst als akzeptable Schulden für internes Tooling
  eingestuft): `scripts/seed-verify-user.ts` liegt in keinem
  `tsconfig`-`include` (wird nur indirekt beim `ts-node`-Lauf typgeprüft);
  `curl-assert.sh`/`smoke-enrich.sh` duplizieren ein ~15-Zeilen-Preamble
  (bei einem dritten Script: auf eine gemeinsame Funktion ziehen);
  `SUPABASE_SERVICE_KEY` als `apikey`-Header für den Password-Grant-Login
  ist empirisch verifiziert, aber kein dokumentiert-garantiertes
  Supabase-Verhalten.
- **`/close-task` nicht ausgeführt** — gleicher, bereits in `tasks/lessons.md`
  (2026-07-16) dokumentierter Formatmismatch: kein RFB-/NC-ID für dieses
  cross-cutting Tooling-Item. Dieser Delivery-Log-Eintrag + der Push nach
  `origin/main` sind die Two-Location-Closure für PROMPT 2.

### PROMPT 3 — Frontend-Harness + tsc-strict (negotiation-buddy)

**Status: DONE.** Gepusht nach `origin/main` (`ee12e91`) → Render Static
Site Auto-Deploy ausgelöst.

- Blast-Radius re-verifiziert: exakt 8 Fehler, 6 Dateien (deckt sich mit
  der PROMPT-0-Messung) — Single-Pass, kein SPLIT nötig.
- **Lint-Scope-Entscheidung (User, vor Implementierung):** `npm run lint`
  hatte 55 vorbestehende, unabhängige Probleme (34 Errors/21 Warnings,
  ~30 Dateien) — Entscheidung: Lint-Schritt in `verify.sh` ist `[WARN]`,
  nicht `[FAIL]`, meldet aber den echten Live-Count statt eines
  Platzhalters. Nach Fertigstellung: 54/33/21 (ein Error weniger — Fix #7
  hat zufällig denselben `as any`-Ausdruck behoben, den auch ESLint
  bemängelte).
  Nach dem Rebase (siehe unten) weiterhin 54/33/21 — unverändert von den
  Lovable-Commits.
- Alle 8 Fixes vollständig Design-Gate-recherchiert (Root Cause + exaktes
  Fix-Pattern pro Datei:Zeile) vor der Implementierung — u. a. ein
  `.abortSignal()`/`.single()`-Call-Order-Bug in `TeamDashboard.tsx`
  (via `node_modules`-Quellcode-Analyse der `@supabase/postgrest-js`
  Klassenhierarchie verifiziert, nicht geraten) und ein Narrowing-Verlust
  über eine `await`-Grenze in `Index.tsx` (Fix: Werte vor dem `await` in
  lokale `const`s einfangen).
- UI-Spot-Check (Pflicht laut `negotiation-buddy/CLAUDE.md`): `ChatInput`
  und `effectiveProgress` liegen ausschließlich hinter
  `<ProtectedRoute>` (`/app`), kein Dev-Auth-Bypass vorhanden — echter
  Klick-Test in dieser Sandbox nicht möglich (kein Testnutzer). Ehrlich
  als Concern dokumentiert statt vorgetäuscht; stattdessen Headless-Chrome-
  CDP-Check der öffentlichen App-Shell (0 Konsolenfehler, Routing/Auth-Gate
  funktionieren) + tsc/vitest-Nachweis. Spec-Reviewer hat den Auth-Gate-
  Befund unabhängig durch Code-Lektüre (`App.tsx`, `ProtectedRoute.tsx`)
  bestätigt — kein übersehener erreichbarer Pfad.
- **Reviews:** Spec-Reviewer — vollständig clean, keine Findings (inkl.
  eigenständiger Re-Ausführung von tsc/vitest/verify.sh und empirischer
  Verifikation des Lint-Count-Deltas durch Checkout der Vorher-Version).
  Code-Quality-Reviewer — Approved with minor follow-ups: ein
  "Important"-markierter Kommentar-Vorschlag (abortSignal-Reihenfolge
  ohne Sibling-Pattern erklären) direkt umgesetzt statt eigenem Fix-Loop
  (triviale 1-Zeilen-Ergänzung); ein Minor-Punkt (ChatInput-Ref-Cast-Stil)
  bewusst nicht behoben.

**Merge-Konflikt mit paralleler Lovable-Session (wichtig für Nachvollziehbarkeit):**
Beim Push lehnte `origin/main` ab — 5 unabhängige Commits waren zwischenzeitlich
gelandet (Commit-Messages "Made the requested updates", "Changes" ×3, "Report
auf Synthese-Stil fixiert" — Muster passt zu Lovable, `BottomBar.tsx`,
`DebriefDashboard.tsx`, `strategyPlan.css`, `planHtmlTemplate.ts`,
`package.json`/`bun.lock`, `.lovable/plan.md` betroffen, unabhängig von
diesem Delivery). Echte Überschneidung auf zwei Dateien: `Profile.tsx` und
`TeamDashboard.tsx` — die Lovable-Session hatte **dieselben 2 der 8
tsc-strict-Fehler** unabhängig "gefixt", aber mit schwächeren Techniken
(`Profile.tsx`: Inline-Cast am Call-Site statt Parameter-Typ-Verengung an
der Quelle; `TeamDashboard.tsx`: die **gesamte** Query-Chain mit `as any`
umhüllt statt der korrekten Call-Order-Korrektur — hätte die Type-Safety
genau an der Stelle wieder ausgehebelt, die dieses Delivery beheben sollte).
User-Entscheidung: Rebase auf `origin/main`, bei den 2 echten Konflikten
die eigenen (saubereren) Fixes behalten, alle anderen Lovable-Änderungen
unangetastet lassen. Durchgeführt (`git rebase origin/main`, ein echter
Konflikt in `TeamDashboard.tsx` manuell aufgelöst, `Profile.tsx` mergte
automatisch — dort den nun redundanten Lovable-Cast entfernt, da die
eigene Parameter-Typ-Verengung ihn überflüssig macht). Nach dem Rebase
vollständig erneut verifiziert (tsc 0 Fehler, vitest 22/22, `verify.sh`
GRÜN) — dann erst gepusht.
**Lehre:** Cross-Session-Kollisionen mit Lovable auf `negotiation-buddy`
sind real und können identische Fixes mit unterschiedlicher Qualität
produzieren — vor jedem Push in diesem Repo `git fetch` + Ahead/Behind-
Check nicht blind aus einem früheren Turn übernehmen, sondern unmittelbar
vor dem tatsächlichen Push neu prüfen.
- **`/close-task` nicht ausgeführt** — gleicher Grund wie PROMPT 1/2: kein
  RFB-/NC-ID. Dieser Delivery-Log-Eintrag + der Push sind die
  Two-Location-Closure für PROMPT 3.

### Nächster Schritt

Alle drei Prompts (Governance, Backend-Harness, Frontend-Harness) sind
DONE. Offene Folge-Punkte, keine davon blockierend für dieses Set:
- ADR-011 (Soft-Launch) auf DECIDED heben, sobald genug reale
  verify-loop-Zyklen gelaufen sind.
- `negotiationcoach-backend`s `.claude/settings.json`-Sandbox-Änderung
  (`Read(.env*)`-Deny, blockiert `.env`-Zugriff auch für Kindprozesse)
  committen oder bewusst zurücksetzen — aktuell uncommitteter Drift.
- Der Merge-Konflikt oben zeigt: eine engere Lovable/Claude-Code-
  Koordination für `negotiation-buddy` wäre wertvoll (z. B. kurzer
  Fetch-Check als fester Bestandteil jedes Push-Schritts).

---

## 9. Follow-up: verify-harness Produktions-User

**Status:** Diagnose abgeschlossen — READ-ONLY (SQL-Queries + Advisors gegen
das aktive Supabase-Projekt, ein Curl-Test gegen den lokalen Dev-Server).
Keine Schema-/Daten-Änderung, kein Code-Fix.
**Datum:** 2026-07-19
**Auslöser:** Nachfrage zur Isolation von `verify-harness@internal.test`
(seit PROMPT 2, Round 3, in `auth.users` des aktiven Projekts
`gpllrgkuozytyrmpfwbb` geseedet) und zum `SUPABASE_SERVICE_KEY`-als-
Login-`apikey`-Muster in `scripts/lib-jwt.sh`.
**Klassifizierung:** Observed | Inferred | Missing

### Teil 1 — Tier-Isolation

| Frage | Befund |
|---|---|
| **Aktueller Tier** | **Divergiert je nach System (Observed, SQL-Query):** `auth.users.raw_user_meta_data.tier = "kmu"` (von `seed-verify-user.ts` explizit gesetzt — das ist der Wert, den `authMiddleware` liest und der `/api/enrich`s `requireTier('kmu')` erfüllt). **Aber** `public.user_profiles.subscription_tier = "free"`, `persona_type = "pro"` — eine zweite, unabhängige Tier-Repräsentation in einer anderen Tabelle. |
| **Root Cause der Divergenz** | **Observed, aus Trigger-Definition:** `handle_new_user()` (Trigger `on_auth_user_created` auf `auth.users` INSERT) fügt bei **jedem** neuen Signup unbedingt `INSERT INTO user_profiles (user_id, persona_type, experience_level) VALUES (NEW.id, 'pro', 1)` ein — liest `raw_user_meta_data.tier` NICHT, setzt `subscription_tier` NICHT (bleibt beim Spalten-Default `'free'`). **Das ist systemisch, nicht spezifisch für den Test-User** — jeder neue Signup auf diesem Projekt bekommt dieselbe Divergenz. Bestätigt konkret (mit Live-Beispiel) das bereits in `AGENTS.md` dokumentierte HIGH-03 ("drei inkompatible Tier-Systeme"). |
| **RLS-Unterscheidung Test-User vs. Kunde** | **Missing — explizit bestätigt als nicht vorhanden.** `pg_policies` für `user_profiles` und `negotiation_sessions`: alle vier Policies (`SELECT`/`INSERT`/`UPDATE`/`DELETE` bzw. `SELECT`/`INSERT`) sind ausschließlich `auth.uid() = user_id`. Keine Policy, kein Column, kein Flag unterscheidet "interner Test-User" von "echter Kunde" — der Harness-User ist RLS-seitig nicht von einem realen Kunden zu unterscheiden. |
| **Analytics/Metrics-Kontamination** | **Ja, strukturell real (Observed, Code-Beleg).** `src/services/telemetry.ts:14`: `client.capture({ distinctId: 'server', event, properties })` — **jedes** `trackEvent()` (u. a. `analyze_completed` in `src/api/routes.ts:224-229`, mit `properties: { tier: req.tier, negotiation_type, zopa_exists, strategy_score }`) läuft unter derselben festen `distinctId: 'server'`. Es gibt **keinen** User-Identifier im Event überhaupt — weder zum Zuordnen noch zum Herausfiltern des Harness-Users. Jeder `verify.sh`-Lauf (curl-assert + smoke-enrich) erzeugt ein reales `analyze_completed`-Event mit `tier: "kmu"`, nicht unterscheidbar von echtem kmu-Traffic. Aktuell **praktisch folgenlos**, weil laut `product/metrics.md` noch kein Aggregations-Layer aktiv ist ("Baseline-Erhebung möglich erst nach NC-TELEMETRY-C") — das Risiko ist latent und wird real, sobald Tier-Verteilungs-Auswertungen aus PostHog oder Render-Logs gebaut werden. |
| **Ressourcen-Zugriff (Layer 2, kmu-Tier)** | **Observed, Laufzeit-Beweis gegen lokalen Dev-Server (2026-07-19, NICHT Production):** Mit einem über `scripts/lib-jwt.sh` bezogenen echten JWT für `verify-harness@internal.test`: `POST /api/analyze` → `200`, `sessionId` gesetzt, `zopa_exists: true`. Anschließend `POST /api/enrich` (verlangt `requireTier('kmu')`) mit derselben `sessionId` → `200`, `market_data_source: "knowledge_graph"`, kein Fehler. Der Harness-User kann Layer-2-Endpunkte exakt wie ein echter kmu-Kunde aufrufen — bestätigt, kein Sonderfall in der Zugriffsprüfung. |

**Weitere Missing-Punkte (Teil 1):**
- Ob `verify-harness@internal.test` in einer echten, bereits gebauten Tier-Verteilungs-Auswertung (Dashboard, Report) sichtbar mitgezählt wurde — es existiert noch keine solche Auswertung, daher nicht prüfbar (folgt aus dem "praktisch folgenlos"-Befund oben).
- Ob es außerhalb dieses Repos (z. B. in einem BI-Tool, falls eines existiert) eine Filterung nach E-Mail-Domain (`@internal.test`) o. ä. gibt — außerhalb der Reichweite von Repo-Grep/SQL-Query.

### Teil 2 — SERVICE_KEY-als-Login-apikey-Muster

| Frage | Befund |
|---|---|
| **Exakte Fundstelle** | `negotiationcoach-backend/scripts/lib-jwt.sh:56`, Funktion `fetch_verify_harness_jwt()` (beginnt Zeile 45): `-H "apikey: ${SUPABASE_SERVICE_KEY}"` als Header für `POST {SUPABASE_URL}/auth/v1/token?grant_type=password` (Supabase-Auth-Login-Endpunkt, nicht der DB-REST-Pfad). Dokumentiert im Datei-Header (Zeilen 16-21) als "empirisch verifiziert (round 3)". |
| **Weitere Fundstellen desselben Musters** | **Keine — bestätigt einmalig.** Repo-weiter Grep nach `SUPABASE_SERVICE_KEY` findet genau zwei weitere Stellen: `src/layer0/supabaseClient.ts:7` und `src/api/middleware.ts:46` — beide verwenden den Key für seinen **vorgesehenen** Zweck (Instanziierung eines Service-Role-DB-Clients via `createClient(url, serviceKey)`), nicht als Auth-/Login-Header. Das Login-apikey-Muster ist ein **isolierter Sonderfall**, ausschließlich im Harness-Script, nicht in Anwendungscode kopiert. |

**OWASP-Rahmen (Einordnung, kein voller Lauf):**
Der `service_role`-Key ist der maximal privilegierte Supabase-Key — er umgeht RLS vollständig für jede Tabelle. `lib-jwt.sh:56` nutzt ihn zweckentfremdet als `apikey`-Header an einem öffentlich erreichbaren Auth-Endpunkt, weil dieses Repo (anders als `negotiation-buddy`) keinen separaten anon/publishable Key konfiguriert hat. Das funktioniert hier nur, weil der Aufrufer (das Harness-Script) vollständig unter eigener Kontrolle läuft und der Key nie das Dateisystem/den Prozess verlässt. **Würde dieses Muster unreflektiert in einen anderen Kontext kopiert** (z. B. ein neues Feature, das denselben "Login via Service-Key-als-apikey"-Trick für echten User-facing Code wiederverwendet, oder falls der Rückgabewert/Fehlertext dieses Aufrufs jemals in einen client-erreichbaren Pfad geriete), wäre der Impact ein vollständiger RLS-Bypass für die gesamte Datenbank — nicht nur ein falscher Tier, sondern uneingeschränkter Lese-/Schreibzugriff auf alle Tabellen. Klassifikation: A01:2021-Broken Access Control-adjacent (Verwendung eines übermäßig privilegierten Credentials in einem replay-fähigen, für einen weniger privilegierten Zweck gedachten Code-Pfad).

### Risikobewertung (Proposed, keine Entscheidung)

**Vor GA vermutlich fix-bedürftig:**
- **Metrics-Kontamination (Teil 1) — ✅ BEHOBEN 2026-07-20.** `distinctId` ist jetzt Pflicht-Parameter (echte `user_id`, kein Default, kein `'server'` mehr) und ein `internal: true`-Flag markiert `verify-harness@internal.test`-Events explizit filterbar. Backend-Commits `db0252f` + `2cda4c8` (Code-Quality-Follow-up), gepusht. Details: `tasks/lessons.md` Eintrag 2026-07-20 "Telemetry distinctId-Fix".

**Als dokumentierte Ausnahme vertretbar (kein Blocker):**
- **Tier-Divergenz zwischen `auth.users`-Metadata und `user_profiles`** — ist ein systemisches, vorbestehendes Problem (HIGH-03), nicht durch den Harness verursacht und nicht durch ihn verschlimmert. Der Harness-User macht das bestehende Problem nur sichtbar, ist aber kein neuer Risikofaktor.
- **RLS-Nichtunterscheidung Test-/Echt-User** — entspricht dem Modell, das ohnehin für alle User gilt (Isolation ist rein zeilenbasiert). Eine explizite "Test-User"-Sonderbehandlung in RLS einzuführen wäre selbst ein neues Risiko (zusätzliche Komplexität, potenzielle neue Bypass-Fläche) für einen Nutzen, der über "sauberere Metrics" (siehe oben, dort adressiert) nicht hinausgeht.
- **`SUPABASE_SERVICE_KEY`-als-Login-apikey in `lib-jwt.sh`** — bestätigt isolierter Einzelfall, kein kopiertes Anti-Pattern. Vertretbar als dokumentierte, kommentierte Ausnahme in einem Skript, das nie Teil des ausgelieferten Produkts ist — sollte aber im Kommentar (bereits vorhanden) bleiben, damit niemand es unreflektiert in echten Feature-Code überträgt.

**Diese Einordnung ist eine Vorlage, keine Entscheidung.** Fix-Priorisierung
liegt beim Product Owner nach Review dieses Nachtrags.
