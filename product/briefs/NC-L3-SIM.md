# Delivery Brief: NC-L3-SIM
## Layer 3 Simulation Engine — Redesign (L1/L2-geerdeter Gegner, dynamischer Intake, Debrief)

**Release:** TBD (Wave 3)
**Status:** IN PROGRESS — Phase 2 von 7 implementiert (2026-07-08)
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
