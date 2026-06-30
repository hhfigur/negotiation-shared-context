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

## Plan

**Erstellt:** 2026-06-30 — Backend-Plan, TARGET REPO negotiationcoach-backend
**Status:** PLANNED — wartet auf GO

### 1. Gegen-ZOPA-Formel (deterministisch, kein LLM-Call)

Eingabe: `own_target`, `own_minimum`, `opponent_estimated_max`, `opponent_estimated_min`
(reale Werte der Session) + `ScenarioDifficulty` + `OpponentStyle`.

```
zopa = calculateZopa(own_minimum, opponent_estimated_max)   // bestehende Funktion, layer1/zopaCalculator.ts
range = zopa.zopa_max - zopa.zopa_min

DIFFICULTY_OFFSET = { einfach: 0.15, mittel: 0.45, schwer: 0.75 }
hidden_opponent_minimum = zopa.zopa_min + DIFFICULTY_OFFSET[difficulty] * range
hidden_opponent_target  = opponent_estimated_max - STYLE_ANCHOR_MARGIN[style] * range
```

`hidden_opponent_minimum` ist der Punkt, unter den die simulierte Gegenseite nie geht
(symmetrisch zu `own_minimum` des Nutzers). Je höher die Difficulty, desto näher liegt
er an `opponent_estimated_max` → weniger Raum für den Nutzer. `hidden_opponent_target`
ist der Anker für die Eröffnungs-Nachricht.

`OpponentStyle` fließt NICHT in die Zahlen, sondern ausschließlich in den
System-Prompt (Zugeständnis-Tempo, Taktik-Beschreibung):
- `kooperativ`: schnelle, sichtbare Zugeständnisse pro Turn
- `hart`: minimale Zugeständnisse, hält lange an `hidden_opponent_target` fest
- `manipulativ`: nutzt Taktiken (künstlicher Zeitdruck, Ankereffekte) bei gleichem Zahlenverhalten wie `hart`
- `sachlich`: linear-vorhersehbare Zugeständnisse, strikt an die Restlaufzeit der Runde gekoppelt

Reines Zahlen-Setup ist unit-testbar ohne LLM/DB-Abhängigkeit (siehe Tests).

### 2. DB-Migration

Neue Datei: `supabase/migrations/20260630170000_create_opponent_simulation_tables.sql`

```sql
CREATE TABLE IF NOT EXISTS public.opponent_simulation_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  negotiation_session_id uuid REFERENCES public.negotiation_sessions(id) ON DELETE SET NULL,
  negotiation_type text NOT NULL,
  opponent_style text NOT NULL,
  scenario_difficulty text NOT NULL,
  own_target numeric NOT NULL,
  own_minimum numeric NOT NULL,
  hidden_opponent_minimum numeric NOT NULL,
  hidden_opponent_target numeric NOT NULL,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','finished','abandoned')),
  turn_count integer NOT NULL DEFAULT 0,
  max_turns integer NOT NULL DEFAULT 12,
  final_outcome numeric,
  evaluation jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz
);

ALTER TABLE public.opponent_simulation_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_manage_own_simulation_sessions"
  ON public.opponent_simulation_sessions
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE TABLE IF NOT EXISTS public.opponent_simulation_turns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_session_id uuid NOT NULL REFERENCES public.opponent_simulation_sessions(id) ON DELETE CASCADE,
  client_turn_id uuid NOT NULL,
  turn_number integer NOT NULL,
  role text NOT NULL CHECK (role IN ('user','assistant')),
  content text NOT NULL,
  metadata jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (simulation_session_id, client_turn_id)
);

ALTER TABLE public.opponent_simulation_turns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_manage_own_simulation_turns"
  ON public.opponent_simulation_turns
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.opponent_simulation_sessions s
      WHERE s.id = simulation_session_id AND s.user_id = auth.uid()
    )
  );

CREATE INDEX IF NOT EXISTS idx_opponent_sim_turns_session
  ON public.opponent_simulation_turns (simulation_session_id, turn_number);
```

`client_turn_id` ist ein vom Frontend generierter UUID (Idempotenz-Key) —
`UNIQUE (simulation_session_id, client_turn_id)` verhindert Doppel-Schreiben bei
Connection-Retry (`INSERT ... ON CONFLICT DO NOTHING` im Backend).

**Wichtiger Schutz für AC-2** (versteckte Zahlen dürfen vor `finish` nie sichtbar
sein): RLS erlaubt `auth.uid() = user_id` zwar grundsätzlich SELECT auf
`hidden_opponent_minimum`/`hidden_opponent_target` — die eigentliche Durchsetzung
ist, dass **kein Frontend-Code diese Tabelle je direkt per Supabase-Client abfragt**
(Architekturregel: "Keine direkten Supabase-Calls aus Frontend-Komponenten"). Der
Express-Response-Serializer darf diese beiden Felder erst ab `status='finished'`
in die JSON-Antwort aufnehmen. Dieser Punkt muss im Implementierungs-Review explizit
geprüft werden.

### 3. Dateien

| Datei | Art |
|---|---|
| `supabase/migrations/20260630170000_create_opponent_simulation_tables.sql` | neu |
| `src/layer3/opponentEngine.ts` | neu — `computeHiddenOpponentRange()`, `buildOpponentSystemPrompt()`, `evaluateOutcome()` |
| `src/api/opponentSimulationRoutes.ts` | neu — eigener Router, Pattern wie `teamRoutes.ts`/`sessionRoutes.ts` (nicht in `routes.ts` gequetscht) |
| `src/api/validation.ts` | erweitert — `StartOpponentSimulationSchema`, `TurnOpponentSimulationSchema` |
| `src/types/index.ts` | erweitert — `OpponentSimulationSession`, `OpponentSimulationEvaluation` (additiv, `OpponentStyle`/`ScenarioDifficulty`/`SimulationTurn` bereits vorhanden) |
| `src/api/routes.ts` | 1 Zeile — `app.use('/api', opponentSimulationRouter)` |
| `docs/contracts/frontend-backend.md` | erweitert — 3 neue Endpoints |

### 4. Side-Effect-Check (Pflicht)

a) `grep -r "opponent_simulation\|OpponentStyle\|ScenarioDifficulty\|SimulationTurn" src/` →
   ausschließlich `modelRouter.ts` (Routing-Konfiguration) und `types/index.ts`
   (Typ-Definitionen). **Keine einzige Verwendung im restlichen Code.** Aktivierung
   ist risikofrei — nichts Bestehendes hängt an diesen Symbolen.

b) Kann die Aktivierung des `modelRouter`-Use-Case bestehendes Routing-Verhalten
   verändern? **Nein.** `selectModel('opponent_simulation', tier)` wird heute von
   niemandem aufgerufen — `BASE_ROUTING`, `MAX_TOKENS`, `CACHEABLE_TASKS` für
   `opponent_simulation` sind bereits korrekt befüllt, keine Änderung an
   `modelRouter.ts` nötig.

c) AbortController/Timeout: Keiner der bestehenden Routen (`/chat`, `/plan`,
   `/analyze`) setzt aktuell ein Timeout auf `client.messages.create()`. Für
   `opponentSimulationRoutes.ts` wird das **neu eingeführt** (`{ timeout: 30_000 }`
   Anthropic-SDK-Option pro Call) — bewusst nur für diese neue Route, kein
   rückwirkender Eingriff in bestehende Routen (das wäre ein separates Refactor-Item,
   nicht Teil dieses Scopes).

d) DB-Schema-Änderung: ausschließlich zwei neue Tabellen. Kein `ALTER` auf
   `negotiation_sessions` oder `session_history`. Optionale FK
   `negotiation_session_id → negotiation_sessions(id) ON DELETE SET NULL` —
   `SET NULL` statt `CASCADE`, damit ein Löschen der Haupt-Session nie eine
   Übungsrunde mitreißt.

e) API-Contract-Änderung: drei komplett neue Endpoints, keine bestehenden
   Einträge in `frontend-backend.md` werden geändert. Kein bestehender
   Frontend-Caller betroffen.

→ Alle fünf Punkte beantwortet. Weiter mit Schritt 5.

### 5. Tests

Im Repo existiert aktuell **kein Test-Runner** (kein `test`-Script in
`package.json`, keine `*.test.ts`-Dateien) — Projekt-Konvention ist `tsc --noEmit`
+ manuelle curl-Verifikation (vgl. BUG-20260529-l2-context-smoke-test).

- `npx tsc --noEmit` — 0 Fehler, Pflicht
- Manuelle curl-Checks:
  - `POST /api/opponent-simulation/start` ohne profi-Tier → 403
  - `POST /api/opponent-simulation/start` mit profi-Tier → 201, Response enthält
    **keine** `hidden_opponent_*`-Felder
  - 13. Turn nach `max_turns=12` → Server beendet automatisch, keine 500
  - Wiederholter `POST .../turn` mit identischem `client_turn_id` → kein
    Duplikat in `opponent_simulation_turns` (Idempotenz-Check)
- Manueller Full-Flow-Test lokal mit bestehendem profi-Test-Account
  (Start → mehrere Turns → Finish), gemäß Lesson "Lokal testen vor Deploy"
- **Optionaler Follow-up (nicht Teil dieses Scopes):** `opponentEngine.ts`s
  `computeHiddenOpponentRange()` ist eine reine Funktion ohne LLM/DB-Abhängigkeit
  — guter Kandidat für den ersten Vitest-Test im Repo, falls ein Test-Runner
  später eingeführt wird.

### 6. Docs/Contracts zu aktualisieren

- `docs/contracts/frontend-backend.md` — 3 neue Endpoints
- `product/feature-register.md` (NC-L3-OPPONENT) — Status → `In Delivery` bei Implementierungsstart, → `Released` nach Deploy + Verifikation
- AGENTS.md CRIT-03-Eintrag korrigieren (veraltet — RFB-001 hat 401-Enforcement bereits gefixt) — Nebenaufgabe, nicht blockierend

### 7. Rollback-Strategie

- Migration: `DROP TABLE IF EXISTS public.opponent_simulation_turns, public.opponent_simulation_sessions;`
  (keine Fremdschlüssel von bestehenden Tabellen auf die neuen — gefahrlos rückbaubar)
- Route-Ebene: `app.use('/api', opponentSimulationRouter)`-Zeile in `routes.ts`
  entfernen oder auskommentieren → Endpoints verschwinden sofort, kein Einfluss
  auf andere Routen
- Kein Feature-Flag nötig — Tier-Gate (`profi`) begrenzt Blast Radius bereits auf
  eine kleine Nutzergruppe

### 8. Git-Commit

```
cd ../negotiationcoach-backend
git add supabase/migrations/20260630170000_create_opponent_simulation_tables.sql \
        src/layer3/opponentEngine.ts \
        src/api/opponentSimulationRoutes.ts \
        src/api/validation.ts \
        src/types/index.ts \
        src/api/routes.ts
git commit -m "feat(layer3): opponent simulation backend — endpoints, engine, migration (NC-L3-OPPONENT)"
```

---

**Nächster Schritt:** Implementierungsplan (writing-plans) auf Basis dieses Briefs.
