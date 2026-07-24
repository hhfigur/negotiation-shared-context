# Delivery Brief: NC-L3-SIM
## Layer 3 Simulation Engine — Redesign (L1/L2-geerdeter Gegner, dynamischer Intake, Debrief)

**Release:** TBD (Wave 3)
**Status:** Released — ✅ DONE `886d3e8` (2026-07-24). Alle 7 (effektiv 4,
nach Konsolidierung) Phasen abgeschlossen: Phase 1/2/3 (negotiationcoach-backend,
bereits Released) + Phase 6 (negotiation-buddy Frontend-Integration, dieser
Eintrag) — ehemalige Phase 4/5/7 bereits in Phase 3 aufgegangen. Siehe
Implement-Abschnitt für den vollständigen Phasenverlauf.
**Affected repos:** negotiationcoach-backend (primary), negotiation-buddy, shared-context (Docs/ADR)
**Tier impact:** profi only
**Created:** 2026-07-06 (Design-Stub) · Qualified: 2026-07-07
**Priority:** P3 — kein Tier-Druck, inhaltlicher Fortschritt für Profi-Wertversprechen
**Parent:** NC-L3 (Layer 3 Simulation Engine) — Nachfolger von NC-L3-OPPONENT / NC-L3-SIM-REALISM
**Full Design:** `docs/features/layer3-simulation.md` (Discovery A1–A4, Datenfluss, Types, Error-Cases, Test-Plan — vollständig)
**ADR:** ADR-009 (Routing, unverändert gültig) · ADR-010 DECIDED 2026-07-08 (Intake-Strategie: Option A, Option C trigger-basiert vorgemerkt)

---

## Goal / Outcome

Die bestehende Gegner-Simulation (NC-L3-OPPONENT, Released) ist zu trivial: der
Gegner kennt nur seine eigenen versteckten Zahlen, nicht die quantitativen
Layer-1-Ergebnisse der realen Analyse (ZOPA, Nash, Monte-Carlo, Acceptance
Curve). NC-L3-SIM macht die Simulation mathematisch geerdet und methodisch
fundiert (Harvard Principled Negotiation, Anchoring, MESO, kalibrierte Fragen):

- Gegner bewegt sich innerhalb eines quantitativ berechneten ZOPA-Bands,
  reagiert auf Nash-/Deadline-Druck, hat privaten Zustand (verdecktes BATNA,
  darf bluffen)
- Intake-Phase liest Kontext aus der bestehenden Nego-Session, LLM stellt
  gezielte Rückfragen statt starrem Formular
- Marktdaten (Layer 2) fließen als dritte Realitätsebene ein — **seit
  2026-07-07 aktiv**, kein Gate mehr (L2 verifiziert grün: R-2026-05 +
  R-2026-09 Released)
- Debrief liefert messbare Bewertung: ZOPA-Perzentil, Nash-Distanz,
  Konzessionsanalyse, verpasste Taktiken

---

## Verhältnis zu NC-L3-OPPONENT (wichtig)

**NC-L3-SIM ersetzt NC-L3-OPPONENT in diesem Item NICHT.** Die bestehenden,
released Endpoints `/api/opponent-simulation/{start,turn,finish}` bleiben
unverändert lauffähig. `opponentEngine.ts` wird additiv erweitert (optionale
Parameter für L1/L2-Injection) — kein Breaking Change am dokumentierten
Contract (`docs/contracts/frontend-backend.md:480-597`).

Konsequenz: bis zur separat geplanten UI-Migration existieren zwei parallele
Simulations-Einstiegspunkte im Frontend. Das ist eine bewusst akzeptierte,
befristete Konsequenz (Blast-Radius-Review 2026-07-07), keine Zielarchitektur.

**Side-Effect-Check bestätigt (2026-07-07):** `computeHiddenOpponentRange`,
`buildOpponentSystemPrompt`, `computeSimulationWarning`, `evaluateOutcome`
haben genau EINEN Caller im gesamten Repo: `opponentSimulationRoutes.ts`.
Das reduziert das Refactor-Risiko erheblich — ein einziger Call-Site zur
Migration auf additive Parameter.

---

## Architektur

Läuft im **Express Backend** (negotiationcoach-backend), nicht in der
Supabase Edge Function — ADR-009 bestätigt dies auch für die
Redesign-Variante (keine neue Prüfung nötig, Begründung identisch:
Layer-1-Funktionen leben nur im Backend, keine Duplikation).

Neue Endpoints unter `/api/simulate/*`, geschützt mit `authMiddleware` +
`requireTier('profi')`.

---

## Komponenten

**Backend (`negotiationcoach-backend/src/layer3/`):**
- `smlParser.ts` (neu) — Intake-Ergebnis → `ScenarioObject`
- `promptBuilder.ts` (neu) — System-Prompt-Konstruktion inkl. L1/L2-Grounding
- `simulationLoop.ts` (neu) — Turn-Orchestrierung, Offer-Detection, Terminierung
- `debriefEngine.ts` (neu) — Konzessionsanalyse, Taktik-Bewertung, `DebriefResult`
- `opponentEngine.ts` (refactor, additiv) — `computeHiddenOpponentRange` erweitert
  um optionale L1/L2-Parameter, bestehende Signatur ohne diese Parameter bleibt
  gültig
- `index.ts` (neu) — Orchestrierung
- `src/api/simulationRoutes.ts` (neu) — `/api/simulate/{start,turn,debrief}`

**Frontend (`negotiation-buddy`):** `OpponentSimulator.tsx`-Refactor oder neue
`SimulationPage.tsx` (Intake-Phase, neue Endpoints) — **separates Future-Item**,
nicht Teil der ersten Implementierungssequenz (siehe Design-Doc Abschnitt 11,
Phase 6).

**DB (Migration in `negotiationcoach-backend/supabase/migrations/`):**
- `simulation_sessions` (ScenarioObject, Layer1/2-Snapshot, private_state, evaluation)
- `simulation_turns` (Turn-Historie inkl. `coach_hint`, `offer_detected`)
- RLS von Anfang an: `user_id = auth.uid() AND tier = 'profi'`
- Bestehende Tabellen (`opponent_simulation_sessions/turns`) bleiben unverändert.

Vollständige Type-Definitionen (`ScenarioObject`, `SimulationTurn`,
`PrivateOpponentState`, `DebriefResult`, Request/Response-Typen): siehe
Design-Doc Abschnitt 4.

---

## Datenfluss

Siehe Design-Doc Abschnitt 3 (vollständige Skizze inkl. L2-Datenpfad).
Kurzfassung:

1. `/api/simulate/start` → lädt `layer1_result` (+ `layer2_result` wenn
   vorhanden) aus `negotiation_sessions` → Intake-Lückenanalyse (Sonnet)
2. `/api/simulate/turn` (Intake) → Extraktion aus Nutzerantworten, bis
   `ScenarioObject` vollständig → dann `computeHiddenOpponentRange`
   (erweitert) → Opening Message (Opus)
3. `/api/simulate/turn` (aktiv) → Offer-Detection, Acceptance-Curve-Lookup,
   Deadline-Eskalation, Gegner-Antwort (Opus), optionaler Coach-Hint
4. `/api/simulate/debrief` → Konzessionsanalyse, `DebriefResult`, enthüllt
   `hidden_opponent_minimum/target`

---

## Fehlerbehandlung

Vollständige Tabelle: Design-Doc Abschnitt 5. Kernpunkte:
- Fehlendes `layer1_result` → 422 `MISSING_LAYER1_DATA`
- Layer-2 für diese Session nicht verfügbar → kein Fehler, Simulation läuft
  ohne Marktdaten-Erdung (Per-Session-Check, kein globales Gate mehr)
- Anthropic-Timeout → 504, Idempotenz-Key retrybar
- Turn-Limit → Auto-finish, Debrief sofort verfügbar

---

## Nicht in Scope (dieses Item)

- Migration von `OpponentSimulator.tsx` auf `/api/simulate/*` (separates Future-Item)
- Deprecation/Ablösung von `/api/opponent-simulation/*`
- Streaming (spätere Ausbaustufe)
- ~~ADR-010-Entscheidung selbst~~ — ✅ DECIDED 2026-07-08, siehe `docs/decision-log/ADR-010-l3-sim-intake-strategy.md`

---

## Acceptance Criteria

- AC-1: Nicht-profi-Nutzer erhalten 403 bei allen drei neuen Endpoints
- AC-2: `/api/opponent-simulation/{start,turn,finish}` funktionieren nach dem
  `opponentEngine.ts`-Refactor unverändert (Regressionstest Pflicht)
- AC-3: Gegner-Privatzustand (`private_state`) ist zu keinem Zeitpunkt vor
  `/debrief` im Response sichtbar
- AC-4: Turn-Schreiben ist idempotent (`client_turn_id`)
- AC-5: Marktdaten fließen ein, wenn `layer2_result` in der Session vorhanden
  ist (kein manueller Aktivierungsschritt nötig)
- AC-6: TypeCheck negotiation-buddy + negotiationcoach-backend: 0 Fehler
- AC-7: `docs/contracts/frontend-backend.md` enthält die drei neuen Endpoints
- AC-8: Alle 6 curl-Tests aus Design-Doc Abschnitt 10 laufen gegen den
  Live-Endpoint erfolgreich (TypeCheck-only zählt nicht als DONE)

---

## Abhängigkeiten

- ADR-009 (Routing) — entschieden, keine offene Frage
- Layer 2 (Market Data) — grün seit R-2026-05/R-2026-09, kein Blocker mehr
- Bestehendes `modelRouter`-Scaffolding (`opponent_simulation` → Opus)
- `layer1/zopaCalculator.ts`, `layer1/nashBargaining.ts`

---

## Open Decisions

- max_turns für SIM-v2: **15** (entschieden 2026-07-07) — höher als
  NC-L3-OPPONENT-Default (12), da die Intake-Phase zusätzliche Turns
  verbraucht, bevor die eigentliche Verhandlung beginnt
- ~~ADR-010 (dynamischer Intake vs. SML-Bibliothek)~~ — ✅ DECIDED 2026-07-08 (Option A)

---

## Plan

Implementierungssequenz (Design-Doc Abschnitt 11): Phase 1 (`smlParser.ts` +
`promptBuilder.ts`, reine Logik) zuerst. Phase-1-Plan wird via Template 1-DEV
in `docs/features/layer3-simulation.md` (Abschnitt `## Phase-1-Plan`)
dokumentiert, nicht in diesem Brief dupliziert.

## Implement

**Phase 1 — smlParser.ts + promptBuilder.ts (reine Logik):**

- **Repo/Branch:** negotiationcoach-backend, direkt auf `main` (explizite
  User-Zustimmung 2026-07-08 — Begründung: additiv, risikoarm, konsistent
  mit bisherigem Ein-Branch-Workflow des Projekts)
- **Commit:** `c00e719` — feat(layer3): NC-L3-SIM Phase 1 — smlParser + promptBuilder (pure logic)
- **Umgesetzt via:** `/subagent-driven-development` (Implementer + Task-Reviewer, Modell Sonnet)
- **Geänderte Dateien:**
  `src/layer3/smlParser.ts` (neu), `src/layer3/promptBuilder.ts` (neu),
  `src/types/index.ts` (additiv — `ScenarioObject`, `MarketDataContext`),
  `tests/layer3/smlParser.test.ts` (neu), `tests/layer3/promptBuilder.test.ts` (neu)
- **Verifikation:** `npx tsc --noEmit` → 0 Fehler (Controller-seitig unabhängig
  bestätigt, nicht nur Implementer-Report). `git diff --stat` bestätigt: nur
  geplante Dateien geändert. `opponentEngine.ts`/`opponentSimulationRoutes.ts`
  byte-identisch zu vorher (Task-Reviewer via `git show`-Diff verifiziert) —
  DO-NOT-TOUCH-Vorgabe eingehalten.
- **Task-Review:** ✅ Spec compliant, 0 Critical/Important Findings.
  **Task quality: Approved.**
- **Minor-Findings (nicht blockierend, für spätere Phasen vormerken):**
  1. `ScenarioIntakeInput`-Typ liegt in `smlParser.ts`, nicht `types/index.ts`
     — Phase 3 soll ihn von dort importieren, nicht neu definieren.
  2. `DIFFICULTY_FACTOR`-Werte (0.1/0.25/0.4) sind Platzhalter ohne
     Produkt-Quelle — Sign-off nötig bevor Phase 3 `recommended_opening`
     Endnutzern zeigt.
  3. Neue Phase-1-Tests sind noch nicht in `package.json`
     `scripts.test` verkabelt — spätere Phase muss das nachholen, sonst
     fängt CI keine Regression in diesen Funktionen ab.
**Phase 2 — debriefEngine.ts (reine Logik):**

- **Commit:** `2f163c8` — feat(layer3): NC-L3-SIM Phase 2 — debriefEngine (pure logic)
- **Umgesetzt via:** `/subagent-driven-development` (Implementer + Task-Reviewer, Modell Sonnet)
- **Geänderte Dateien:**
  `src/layer3/debriefEngine.ts` (neu — `computeConcessionTimeline`,
  `computeOutcomeMetrics`, `computeMarketComparison`, `buildDebriefResult`),
  `src/types/index.ts` (additiv — `DebriefResult` neu, `SimulationTurn`
  additiv erweitert um `role: 'coach'`, `offer_detected?`, `coach_hint?`),
  `tests/layer3/debriefEngine.test.ts` (neu)
- **Design-Entscheidung eingehalten:** `computeOutcomeMetrics` nutzt die
  echten `layer1_snapshot`-Werte (ZOPA/Nash/Monte-Carlo), keine
  Neuberechnung aus `opponent_estimated_*` — Task-Reviewer hat dies
  unabhängig verifiziert (kein `opponent_estimated_*`-Feld im gesamten Diff).
- **Verifikation:** `npx tsc --noEmit` → 0 Fehler (Controller-seitig
  unabhängig bestätigt). `git diff --stat` bestätigt: nur geplante Dateien
  geändert (3 Dateien: debriefEngine.ts, types/index.ts, Test-Datei).
  `opponentEngine.ts`/`opponentSimulationRoutes.ts` nicht im Diff enthalten.
  `SimulationTurn`-Erweiterung: 0 Fremd-Importeure bestätigt (Task-Reviewer,
  eigener grep-Check).
- **Task-Review:** ✅ Spec compliant, 0 Critical/Important Findings.
  **Task quality: Approved.**
- **Minor-Findings (nicht blockierend):**
  1. Neue Phase-2-Tests sind wie schon Phase 1 nicht in `package.json`
     `scripts.test` verkabelt (bestehende Repo-Konvention, kein neues Problem).
  2. Feldname `market_comparison` hat jetzt zwei inkompatible Semantiken im
     Code: Layer 2 (`EnrichedAnalysisResult`, range-basiert) vs. Layer 3
     Debrief (`DebriefResult`, ±2%-von-Median) — Brief-mandatiert, kein
     Implementierungsfehler, aber Verwechslungsrisiko für künftige
     Maintainer/LLM-Prompts vormerken.
- **Nächster Schritt:** Phase 3 (`simulationRoutes.ts` + `routes.ts`-
  Integration, erste LLM-Calls, erste DB-Schreibzugriffe) gemäß Design-Doc
  Abschnitt 11 — deutlich größerer Scope als Phase 1/2 (erste echte
  Route-Registrierung, erster Anthropic-Call, erstmals nicht mehr "reine
  Logik"). Sollte vor Beginn erneut durch /feature-plan Schritt 4b
  (Konsequenz-Triage) laufen, nicht direkt per /feature-implement.

**Phase 3 — simulate routes, opponent L1-grounding, migration (erweitert — absorbiert ehemalige Phase 4 + Phase 5):**

- **Repo/Branch:** negotiationcoach-backend, direkt auf `main` (explizite
  User-Zustimmung 2026-07-21 — abweichend von Phase 1/2 erneut eingeholt,
  weil diese Phase ein qualitativ anderes Risiko trägt: Live-Migration +
  additiver Refactor von production-genutztem `opponentEngine.ts`, nicht nur
  ungenutzte reine Logik)
- **Plan:** `/feature-plan NC-L3-SIM`, Schritte 1–4c durchlaufen. Schritt 4b
  fand einen offenen, bewusst akzeptierten Befund: kein Produktionspfad
  setzt `auth.users.raw_user_meta_data.tier` auf `'profi'` (kein
  Stripe-Webhook, AR-032 weiterhin Paused) — dieselbe Lücke wie bei
  NC-L3-OPPONENT, kein neues Problem, GO trotzdem erteilt. Schritt 4c
  (Critic-Pass) fand einen echten Scope-Fehler in der ursprünglichen
  7-Phasen-Sequenz: Phase 3 setzt laut Datenfluss (Design-Doc Abschnitt 3)
  bereits den L1-erweiterten `computeHiddenOpponentRange`/
  `buildOpponentSystemPrompt` voraus — das war aber erst als Phase 5
  geplant. Phase 3, die ehemalige Phase 4 (Migration) und die ehemalige
  Phase 5 (`opponentEngine.ts`-Refactor) wurden deshalb zu einer
  Implementierungseinheit zusammengefasst (Design-Doc,
  "## Phase-3-Plan (erweitert)", Commit `51644ca`).
- **Commits:** `007a6ee` (Implementierung) → Task-Review fand 5 Important
  Findings → `b5bf2d7` (Fix) → Re-Review Approved.
- **Umgesetzt via:** `/subagent-driven-development` (Implementer + Task-Reviewer
  + Fix-Subagent + Re-Review, Modell Sonnet, ein Dispatch für die gesamte
  Phase — konsistent mit Phase 1/2, keine Sub-Task-Zerlegung)
- **Geänderte Dateien:**
  `src/layer3/simulationLoop.ts` (neu), `src/layer3/index.ts` (neu —
  `runIntake`/`runTurn`/`runDebrief`), `src/layer3/opponentEngine.ts`
  (additiv erweitert — optionale L1/L2-Grounding-Parameter),
  `src/api/simulationRoutes.ts` (neu — 3 Endpoints), `src/api/routes.ts`
  (additiv registriert), `src/api/validation.ts` (additiv — 3 Zod-Schemas),
  `src/utils/modelRouter.ts` (additiv — `l3_sim_intake`/`l3_sim_debrief`),
  `src/types/index.ts` (additiv), `supabase/migrations/20260721131832_...sql`
  (neu — `simulation_sessions`/`simulation_turns` + RLS), diverse
  `tests/layer3/*`-Dateien, `package.json` (Test-Wiring nachgeholt —
  schließt den seit Phase 1 offenen Minor-Finding).
- **Migration live angewendet:** `mcp__supabase__apply_migration` +
  Migrationsdatei (Präzedenzfall BUG-20260719-signup-trigger-tier-mismatch,
  2026-07-21). Unabhängig verifiziert (`information_schema.tables`):
  `simulation_sessions`/`simulation_turns` existieren live auf
  `gpllrgkuozytyrmpfwbb`.
- **Schema-Korrektur während der Planung:** ein Kommentar in
  `src/api/sessionRoutes.ts` (2026-04-08) behauptete, `negotiation_sessions`
  habe keine `layer1_result`/`layer2_result`-Spalten. Live gegengeprüft
  (2026-07-21): beide Spalten existieren (`jsonb`) und sind für 30/41 bzw.
  20/41 bestehende Sessions befüllt — der Kommentar ist veraltet, keine
  Blockade für Phase 3.
- **Task-Review (1. Durchlauf):** ❌ 5 Important Findings — Turn-Number-
  Duplikate während Intake, fehlender Pflicht-Test für `runTurn`s
  Privacy-Garantie, `intakeComplete`-Heuristik konnte `scenario_difficulty`
  überspringen, totes `existingTurn`-Feld, `/debrief` vertraute
  Client-Input statt serverseitig bereits vorhandener Status-Disambiguierung.
  Alle 5 in `b5bf2d7` gefixt.
- **Task-Review (2. Durchlauf, nach Fix):** ✅ Spec compliant, alle 5 Findings
  verifiziert gefixt (nicht nur behauptet — Reviewer hat Logik und Tests
  einzeln nachvollzogen). 0 neue Findings durch den Fix-Commit.
  **Task quality: Approved.**
- **Verifikation:** `npx tsc --noEmit` (Root + Test-Projekt) → 0 Fehler.
  `npm test` → alle grün, inkl. aller 6 Live-curl-Tests aus Design-Doc
  Abschnitt 10 gegen den lokalen Dev-Server (manuell geseedeter
  Profi-Test-User, analog `scripts/seed-verify-user.ts`). Zwei während der
  curl-Verifikation gefundene und gefixte Bugs (Idempotenz-Reihenfolge,
  UUID-Spalten-Typmismatch) waren bereits im Implementer-Commit `007a6ee`
  behoben, nicht Teil der Review-Findings.
- **Minor-Findings (nicht blockierend, vorgemerkt):**
  1. `walkaway`/`opponent_walkaway`-Status wird nirgends produziert (Typ
     existiert, kein Erzeugungspfad) — bräuchte eine separate,
     LLM-signalisierte Erkennung, nicht Teil dieses Scopes.
  2. Migration-RLS prüft Tier nur über `user_metadata`, nicht zusätzlich
     `app_metadata` (anders als `middleware.ts`s serverseitiger Check) —
     geringes Risiko, da alle Writes über den Service-Role-Key laufen,
     aber inkonsistente Konvention.
  3. Live-Anthropic-Calls laufen innerhalb von `npm test` (geerbte
     Konvention aus Phase 1/2) — nicht-deterministischer, kostenpflichtiger
     CI-Lauf, repo-weites Thema, nicht Phase-3-spezifisch.
- **Zwei-Repo-Regel:** negotiationcoach-backend (Commits `007a6ee`,
  `b5bf2d7`) + shared-context (dieser Brief-Eintrag, Design-Doc-Plan
  bereits in `51644ca`).
- **Nächster Schritt:** Phase 6 (negotiation-buddy `OpponentSimulator.tsx`-
  Integration mit den neuen `/api/simulate/*`-Endpoints — separates Item,
  Frontend-Repo) — Phase 7 (curl-Tests + manueller Acceptance-Test) ist
  durch die Konsolidierung bereits Teil dieser Phase 3 erledigt, nicht mehr
  separat offen.

**Phase 6 — negotiation-buddy Frontend-Integration (letzte verbleibende Phase, geliefert als "Substance Activation A-3"):**

- **Repo/Branch:** negotiation-buddy, isolierter Git-Worktree
  (`worktree-a3-simulate-debrief`, User-Zustimmung für Worktree-Isolation
  eingeholt), lokal auf `main` gemerged (fast-forward) nach GO des Users.
- **Plan:** Vier Tasks per `/subagent-driven-development`
  (Implementer → Task-Reviewer, je Modell nach Aufgabenkomplexität —
  Haiku für mechanische Tasks, Sonnet für Integrations-/Judgment-Tasks),
  plus abschließendes Whole-Branch-Review (Opus).
- **Commits:** `1bad815` (Task 1 — `apiClient.ts`/`types.ts` Wiring),
  `75b1b96` (Task 2 — `OpponentSimulator.tsx` auf session-geerdeten Flow
  umgestellt), `3ab37bb` (Task 3 — narrierte Debrief-Verdikte statt
  Rohzahlen, neues `debriefNarration.ts`, TDD via vitest), `e638844`
  (Task 4 — Dead-Reference-Cleanup + `DCC-FE-03`-Dokumentation),
  `886d3e8` (Fix-Runde nach Whole-Branch-Review).
- **Architektur-Erkenntnis während Task 2:** `/api/simulate/start` ist
  session-geerdet (nimmt nur `session_id`, lädt `layer1_result` server-seitig)
  — anders als das alte `/api/opponent-simulation/start`, das manuelle
  Zahlen-Eingabe (`own_target`/`own_minimum`/`opponent_estimated_*`)
  erforderte. Die Setup-Phase in `OpponentSimulator.tsx` wurde entsprechend
  vereinfacht: Pre-Flight-Check auf `useAnalysis().sessionId` statt
  manuellem Formular.
- **Produktkritischer Teil (Task 3):** Debrief-Felder werden nicht mehr als
  Rohzahlen angezeigt, sondern als narrierte Verdikte (z. B. "X € unter dem
  rechnerisch fairen Ausgleichspunkt (Nash-Lösung)"). Terminologie-Regel
  (P-1 aus `substance-activation-brief.md`): Fachbegriff + Erklärung in
  Klammern, einheitlich für alle Tiers, kein Tier-Gating auf Wortwahl.
- **Well-evidenced Abweichung von der illustrativen Plan-Vorlage:**
  `final_vs_nash_distance` ist ein absoluter €-Betrag, keine Prozentzahl —
  zweifach unabhängig verifiziert durch Quellcode-Nachverfolgung
  (`debriefEngine.ts:113`, `nashBargaining.ts:8-14`), nicht nur behauptet.
- **Whole-Branch-Review fand 1 Important Finding** (ZOPA-Perzentil-Tile und
  -Caption zeigten zwei widersprüchliche Zahlen nebeneinander, plus eine
  unverifizierte Annahme über die Richtung "höher = besser" — Perzentil ist
  laut Backend-Quelle richtungsneutral, "höher/niedriger ist besser" hängt
  von der Verhandlungsseite ab, die zu diesem Zeitpunkt nicht bekannt ist)
  + 2 Minor Findings (Rundungs-Inkonsistenz zwischen zwei Metric-Tiles und
  der Concession-Timeline-Liste; "Verhandlung beenden"-Button während
  Intake-Phase erreichbar). Alle 3 in `886d3e8` gefixt, Re-Review bestätigt
  Fix unabhängig (inkl. eigenem `tsc`/`vitest`-Re-Run).
- **Verifikation:** `npx tsc --noEmit --project tsconfig.app.json` → 0 Fehler
  (Controller-seitig auf gemergtem `main` unabhängig erneut bestätigt, nicht
  nur Implementer-Report). `npx vitest run` → 48/48 Tests grün auf gemergtem
  `main`. Vollständige Live-API-Chain-Verifikation (`/api/analyze` →
  `/api/simulate/start` → mehrere `/turn` → `/debrief`) gegen lokalen
  Dev-Server mit echtem Profi-JWT, zwei volle Durchläufe (echter `'deal'`-
  und echter `'user_abort'`-Ausgang), reale `DebriefResult`-JSON erfasst und
  gegen die Typdefinitionen abgeglichen. `git fetch origin` vor dem Merge
  bestätigte 0 Fremd-Commits auf `origin/main` (Lovable-Sync-Risiko
  geprüft, keine Kollision).
- **AC-Abgleich (Brief-Acceptance-Criteria):** AC-1/AC-3/AC-4 bereits durch
  Phase 3 (Backend) erfüllt, unverändert. AC-6 (TypeCheck 0 Fehler) erfüllt
  in beiden Repos. **AC-7** (`docs/contracts/frontend-backend.md` enthält
  die drei neuen Endpoints) war bis zu diesem Abschluss NICHT erfüllt —
  während `/close-task-dev` nachgeholt (dieser Commit-Batch, shared-context).
  AC-8 (6 curl-Tests) bereits in Phase 3 erledigt.
- **Dead-Code-Dokumentation:** `DCC-FE-03` (negotiation-buddy,
  `docs/dead-code-candidates.md`) + `DCC-BE-03` (negotiationcoach-backend,
  `docs/dead-code-candidates.md`, Commit `cb01e90`) — `/api/opponent-simulation/*`
  bleibt bewusst erhalten (kein Löschen), nur Frontend-Aufrufe entfernt,
  konsistent mit der bereits in Phase 3 dokumentierten "ersetzt NICHT
  NC-L3-OPPONENT"-Linie — jetzt präzisiert: Frontend ruft nur noch
  `/api/simulate/*` auf, Backend-Route bleibt parallel funktionsfähig, aber
  unaufgerufen (Entscheidung P-3, nicht mehr "zwei aktive Einstiegspunkte").
- **Bekannte, nicht neue Lücke bleibt bestehen:** kein Produktionspfad setzt
  `tier='profi'` im JWT (kein Stripe-Webhook) — UI ist ausgeliefert, aber
  für reale zahlende Nutzer noch nicht erreichbar (unverändert seit Phase 3).
- **Zwei-Repo-Regel:** negotiation-buddy (Commits `1bad815`..`886d3e8`) +
  negotiationcoach-backend (`cb01e90`, DCC-BE-03-Dokumentation) +
  shared-context (dieser Brief-Eintrag, `docs/contracts/frontend-backend.md`
  AC-7-Nachtrag, `product/feature-register.md`-Stempel).
- **Nächster Schritt:** Keiner — NC-L3-SIM ist mit dieser Phase vollständig
  Released. Verbleibende, bereits dokumentierte Minor-Findings aus allen
  Phasen (siehe oben) sind kein Blocker, nur vorgemerkte Folge-Punkte.
