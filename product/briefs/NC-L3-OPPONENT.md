# Delivery Brief: NC-L3-OPPONENT
## KI-Gegner-Rollenspiel — Verhandlungsübung gegen simulierte Gegenseite

**Release:** TBD (Wave 3)
**Status:** Qualified
**Affected repos:** negotiationcoach-backend (primary), negotiation-buddy, shared-context (ADR)
**Tier impact:** profi only
**Created:** 2026-06-30
**Priority:** P3 — kein Tier-Druck, inhaltlicher Fortschritt nach mehreren Bugfix-Wochen
**Parent:** NC-L3 (Layer 3 Simulation Engine) — Sub-Item neben NC-L3-SCENARIO (Szenario-Simulation, noch nicht qualifiziert)
**ADR:** docs/decision-log/ADR-009-opponent-simulation-routing.md

---

## Goal / Outcome

Profi-Tier-Nutzer können in einem eigenständigen Tool eine vollständige
Verhandlung gegen eine simulierte Gegenseite üben. Die Gegenseite verhält
sich nicht frei improvisiert, sondern ist an eine serverseitig berechnete,
versteckte ZOPA-Range gekoppelt (gleiche Layer-1-Funktionen wie die reale
Analyse). Am Ende der Übungsrunde zeigt das Tool eine eigene Auswertung:
erreichtes Ergebnis vs. eigene ZOPA-Range, Vergleich zum Nash-Optimum,
kurze Taktik-Bewertung.

---

## Hintergrund (Observed)

Drei Bausteine existieren bereits im Code, aber ungenutzt:
- `negotiationcoach-backend/src/utils/modelRouter.ts:55-57` — Use-Case-Kategorie
  "Layer 3 — Simulation & Profi-Features" mit `what_if_analysis` und
  `opponent_simulation`, bereits auf Opus geroutet
- `negotiationcoach-backend/src/types/index.ts` — `OpponentStyle`
  ('kooperativ'|'hart'|'manipulativ'|'sachlich'), `ScenarioDifficulty`
  ('einfach'|'mittel'|'schwer'), `SimulationTurn` — keine einzige Verwendung
  im gesamten Repo
- `negotiation-buddy/src/pages/WhatIfSimulator.tsx` — bestehendes Tool-Muster
  (eigene Seite, ruft Backend statt EF, `useAnalysis()`-Context), als Vorlage
  für die neue Seite

Dieses Scaffolding deutet auf eine frühere, nie umgesetzte Planung für genau
dieses Feature hin.

---

## Architektur

Läuft im **Express Backend**, nicht in der Supabase Edge Function.
Begründung und Abgrenzung zu ADR-004: siehe ADR-009.

Neue Endpoints unter `/api/opponent-simulation/*`, geschützt mit
`authMiddleware` + `requireTier('profi')` (Pattern wie `/enrich` mit
`requireTier('kmu')`, `routes.ts:244`).

---

## Komponenten

**Frontend (`negotiation-buddy`):**
- `src/pages/OpponentSimulator.tsx` — Setup-Screen (Verhandlungstyp,
  `OpponentStyle`, `ScenarioDifficulty`), Turn-UI, Auswertungs-Screen
- Route + Sidebar/Landing-Eintrag — **Pflicht:** alle Stellen mit
  Tool-Routen-Strings ergänzen (Lesson aus BUG-20260630), idealerweise
  `TOOL_ROUTES`-Konstante einführen statt erneut zu streuen
- `trackEvent('tool_opened', { tool: 'opponent_simulator' })`

**Backend (`negotiationcoach-backend`):**
- `src/api/routes.ts` — `POST /api/opponent-simulation/start`,
  `POST /api/opponent-simulation/:id/turn`,
  `POST /api/opponent-simulation/:id/finish`
- `src/layer3/opponentEngine.ts` (neu) — berechnet versteckte Gegen-ZOPA aus
  `ScenarioDifficulty`/`OpponentStyle`, baut System-Prompt, ruft
  `selectModel('opponent_simulation', 'profi')`
- Zod-Schemas für Start/Turn-Payloads, Pattern wie bestehende
  `validateBody(...)`

**DB (Migration in `negotiationcoach-backend/supabase/migrations/`):**
- `opponent_simulation_sessions` (Setup, Status, Endergebnis)
- `opponent_simulation_turns` (`SimulationTurn`-Schema wiederverwenden)
- RLS von Anfang an: `auth.uid() = user_id`, Pattern wie
  `20260421000000_create_knowledge_graph.sql`

---

## Datenfluss

1. **Start:** Frontend sendet `negotiation_type`, `OpponentStyle`,
   `ScenarioDifficulty` + eigene ZOPA/BATNA-Werte aus der Session → Backend
   berechnet versteckte Gegen-ZOPA, legt Zeile in
   `opponent_simulation_sessions` an, gibt nur Eröffnungs-Nachricht zurück
   (versteckte Zahlen verlassen das Backend nie vor `finish`)
2. **Turn-Loop:** Nutzer-Nachricht → Backend baut System-Prompt aus
   Persona + Stil + versteckter ZOPA + Verlauf aus
   `opponent_simulation_turns` → Opus generiert Antwort → Turn wird
   geschrieben → Antwort an Frontend. Serverseitiges Rundenlimit
   (z.B. 12 Turns) zur Kostenkontrolle bei Opus
3. **Finish:** Vergleich erreichtes Ergebnis vs. reale ZOPA/Nash (vorhandene
   `layer1`-Funktionen) → Endergebnis in `opponent_simulation_sessions` →
   Auswertungs-Payload an Frontend

---

## Fehlerbehandlung

- **Tier-Gate:** `requireTier('profi')` → 403 für privat/kmu. (CRIT-03 aus
  AGENTS.md betraf fehlende 401-Logik und ist laut `middleware.ts` bereits
  durch RFB-001 gefixt — Korrektur des veralteten AGENTS.md-Eintrags als
  Nebenaufgabe vormerken)
- **Opus-Timeout:** `AbortController` mit Timeout pro Turn-Call (Lesson:
  jeder externe Call braucht ein Timeout, vgl. BUG-20260521-Regression-3)
- **Rundenlimit erreicht ohne Abschluss:** Server beendet automatisch,
  liefert Teilauswertung statt Fehler
- **Verbindungsabbruch mitten im Turn:** Turn-Status `pending` → bei
  Reconnect letzten unvollständigen Turn erneut anzeigen, kein
  Doppel-Schreiben (Idempotenz von Anfang an, vgl. BUG-20260608
  session-accumulation)

---

## Nicht in Scope

- Integration in `DebriefDashboard` (eigene Auswertung im Tool stattdessen)
- Free/privat/kmu-Tiers (nur profi)
- NC-L3-SCENARIO (mehrstufige What-If-Simulation) — separates Brief, eigener
  Design-Zyklus nach diesem Item
- Persona-Varianten über die vier `OpponentStyle`-Werte hinaus

---

## Acceptance Criteria

- AC-1: Nicht-profi-Nutzer erhalten 403 bei allen drei Endpoints
- AC-2: Gegen-ZOPA-Werte sind im Frontend zu keinem Zeitpunkt vor `finish`
  sichtbar (Netzwerk-Tab-Check)
- AC-3: Rundenlimit wird serverseitig durchgesetzt, auch bei manipuliertem
  Frontend-Request
- AC-4: Turn-Schreiben ist idempotent bei Connection-Retry (kein Duplikat
  in `opponent_simulation_turns`)
- AC-5: Endauswertung nutzt dieselben `layer1`-Funktionen wie `/api/analyze`
  (kein eigener Berechnungspfad)
- AC-6: TypeCheck negotiation-buddy + negotiationcoach-backend: 0 Fehler
- AC-7: `docs/contracts/frontend-backend.md` enthält die drei neuen Endpoints

---

## Abhängigkeiten

- ADR-009 (Routing-Entscheidung) — entschieden, keine offene Frage mehr
- Bestehendes `modelRouter`-Scaffolding, `OpponentStyle`/`ScenarioDifficulty`/`SimulationTurn`-Typen
- `layer1/zopaCalculator.ts`, `layer1/nashBargaining.ts` für Gegen-ZOPA-Berechnung und Endauswertung

---

## Open Decisions

- Konkrete Formel für versteckte Gegen-ZOPA aus `ScenarioDifficulty` +
  `OpponentStyle` (Teil der Implementierungsplanung, nicht mehr Teil dieses
  Briefs)
- Genaues Rundenlimit (Vorschlag: 12, final bei Implementierung)

---

**Nächster Schritt:** Implementierungsplan (writing-plans) auf Basis dieses Briefs.
