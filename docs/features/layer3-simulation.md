**Status:** DRAFT — Proposed (awaiting GO/HOLD)
**Item-ID:** NC-L3-SIM
**Erstellt:** 2026-07-06
**Owner/Repo:** negotiationcoach-backend (src/layer3/)
**Blockiert durch:**
  - Layer-2-Fix — Marktdaten-Pfad bleibt inaktiv bis L2-Qualität verifiziert (Q8-Gate); alle L2-Felder im Design hinter `MarketDataContext.available`-Flag gekapselt
  - ADR-007 (Option A) ist entschieden und blockiert NICHT mehr — NC-L3-OPPONENT ist Released; dieses Item betrifft keine EF-Engine-Logik
**Feature-Register-Abgleich:** NICHT durchgeführt in dieser Session — NC-L3-SIM ist noch nicht im Register eingetragen (NC-L3 = Idea, NC-L3-OPPONENT/UI = Released). Vor jeder Freigabe: Item in `product/feature-register.md` eintragen, Release-Stufe (Wave 3) bestätigen, Brief in `product/briefs/NC-L3-SIM.md` anlegen.

---

# NC-L3-SIM — Layer 3 Simulation Engine: Design & Discovery

## 1. Change Summary

**Ziel:** Die bestehende, LLM-basierte Gegner-Simulation ist zu trivial — `buildOpponentSystemPrompt` ist blind gegenüber den quantitativen Layer-1-Outputs (ZOPA, Nash, monte_carlo, acceptance_curve). Der Gegner agiert mit fixen hidden numbers, aber ohne Zugang zu Verhandlungssubstanz. NC-L3-SIM macht die Simulation mathematisch geerdet und methodisch fundiert.

**Kernergebnis für den User:**
- Simulierter Gegner bewegt sich innerhalb eines quantitativ berechneten ZOPA-Bands, reagiert auf Nash/Deadline-Druck und mimt szenariospezifische Taktiken (Anchoring, BATNA-Bluffing, MESO).
- Intake-Phase erklärt aus der bestehenden Nego-Session, was fehlt — kein manuelles Formular.
- Debrief liefert messbare Bewertung: Deal vs. ZOPA-Perzentil, Nash-Distanz, Konzessionsmuster, verpasste Taktiken.
- Marktdaten (Layer 2) als dritte Realitätsebene — gated bis L2-Qualität gesichert.

**Nutzen:** Profi-User erhalten eine reproduzierbare, quantitativ kalibrierte Übungsumgebung statt einer generativen Spielerei.

---

## 2. Discovery-Ergebnisse A1–A4

### A1 — Bestehende Simulations-Logik

**`negotiationcoach-backend/src/layer3/opponentEngine.ts`** — **refactor (80% keep)**

*Was trivial ist (Observed):*
- `buildOpponentSystemPrompt` (Z. 65–108): stateless, erhält kein `AnalysisResult`. ZOPA, Nash, `monte_carlo_p50/p90`, `acceptance_curve`, `strategy_score`, `user_batna_strength` werden NICHT übergeben. Gegner kennt nur seine eigenen hidden numbers — keine mathematische Substanz.
- Urgency-Note (Z. 86–88): rein turn-count-basiert (`"noch X Runden"`), kein `deadline_effect`-Input.
- `styleInstructions` (Z. 71–84): verbal, kein differenziertes Taktik-Framework. Kein BATNA-Bluffing-Mechanismus, keine MESO-Logik, kein Logrolling.
- `evaluateOutcome` (Z. 121–159): liefert ZOPA-Perzentil + Nash-Distanz, aber keine Konzessionsmuster-Analyse, keine Taktik-Auswertung der geführten Turns.

*Was wiederverwendbar ist (Observed):*
- `computeHiddenOpponentRange` — Formel korrekt, style/difficulty parameterisiert → **keep, extend mit L1-Inputs und L2-Gate**
- `computeSimulationWarning` — **keep vollständig**
- `evaluateOutcome` — Basisberechnung keep, **extend** mit Konzessionsanalyse + Taktik-Bewertung
- Typ-Definitionen `OpponentSimulationSetup`, `HiddenOpponentRange`, `OpponentSimulationEvaluation` — **keep, extend additiv**

**`negotiationcoach-backend/src/api/opponentSimulationRoutes.ts`** — **refactor**

*Was trivial ist (Observed):*
- `/start` (Z. 52–62): `buildOpponentSystemPrompt` erhält kein `AnalysisResult`, obwohl `negotiation_session.layer1_result` aus der DB geladen wird — Daten werden nicht weitergegeben.
- `/turn` (Z. 156–164): `setup` wird aus DB rekonstruiert, aber `opponent_estimated_max/min` werden mit `hidden_opponent_target/minimum` vertauscht — Inkonsistenz.
- Kein Intake: User gibt 4 Zahlen manuell ein, kein LLM-gestützter Kontext-Intake.

*Was wiederverwendbar ist (Observed):* Idempotenz-Pattern (`client_turn_id`), auto-finish bei max_turns, Owner-Check + tier-gate-Middleware, 30s Anthropic-Timeout — **alle keep**.

**`negotiation-buddy/src/pages/OpponentSimulator.tsx`** — **refactor (Skelett keep)**

*Was trivial ist (Observed):*
- Tier-Check liest `localStorage` direkt (nicht Server-Auth) — kein echter Gate.
- Formularfelder für 4 Zahlen ohne Vorausfüllen aus `negotiation_session.layer1_result`.
- Keine Intake-Phase, keine inline-Coach-Hinweise.

*Was wiederverwendbar ist (Observed):* Phase-State-Machine (setup/playing/evaluation), Warning-Banner, Turn-Counter-Visualisierung, `handleSendTurn` + `crypto.randomUUID()` Pattern, Evaluation-Darstellung (refactor + erweitern).

**Supabase Edge Functions:** Kein Simulations-Code vorhanden. [Observed — grep liefert null Treffer]

---

### A2 — ScenarioObject Schema-Drift

**`ScenarioObject`:** Existiert NICHT als TypeScript-Interface in aktivem Code. [Observed — grep über beide Repos, null Treffer] Ist reine Design-Anforderung, keine bestehende Implementierung.

**`supabase/functions/_shared/engine/`:** Verzeichnis gelöscht (ADR-007-A, Commit 9c6f1f2, 2026-04-21). [Observed] Kein Code referenziert es.

**`SimulationTurn` in `types/index.ts`:** `{ turn_number: number; role: 'user'|'assistant'; content: string; metadata?: Record<string,unknown> }` — definiert, aber **nicht importiert in beiden Repos** (tot). [Observed] → reaktivieren und erweitern als kanonisches Turn-Interface.

**`OpponentSimulationSetup` (aktiv):** Felder: `negotiation_type, opponent_style, scenario_difficulty, own_target, own_minimum, opponent_estimated_max, opponent_estimated_min, negotiation_session_id?` — **fehlt:** `layer1_result, layer2_result, batna_description, deadline_days`. [Observed]

**DB-Tabellen (aktiv, in Produktion):** [Observed — Migration 20260630170000]
- `opponent_simulation_sessions`: id, user_id, negotiation_session_id (nullable FK), negotiation_type, opponent_style, scenario_difficulty, own_target, own_minimum, hidden_opponent_minimum, hidden_opponent_target, status (active/finished/abandoned), turn_count, max_turns (default 12), final_outcome, evaluation (jsonb), created_at, finished_at
- `opponent_simulation_turns`: id, simulation_session_id, client_turn_id (UNIQUE mit session), turn_number, role (user/assistant), content, metadata (jsonb), created_at

**Empfehlung kanonisches Schema Layer 3:** Neue Tabelle `simulation_sessions` (parallel zu `opponent_simulation_sessions`), da der State-Machine-Unterschied (Intake-Phase, komplexere Terminierung, private Interests) eine saubere Trennung rechtfertigt. `SimulationTurn` reaktivieren + um `offer_detected?, coach_hint?` erweitern. `ScenarioObject` als Intake-Output neu definieren. [Proposed]

---

### A3 — Modell-Strings

Alle Strings aus `src/utils/modelRouter.ts` (Observed):

| Konstante | String | Verwendet für |
|-----------|--------|---------------|
| `MODELS.HAIKU` | `claude-haiku-4-5-20251001` | validate_input, tier_check, classify_scenario, recommendation_short, session_summary, strategy_coaching (free) |
| `MODELS.SONNET` | `claude-sonnet-4-6` | strategy_coaching (standard), generate_plan, market_data_interpretation, reality_check, pdf_section |
| `MODELS.OPUS` | `claude-opus-4-6` | what_if_analysis (profi), opponent_simulation (profi) |

`modelRouter` existiert und ist vollständig implementiert (`src/utils/modelRouter.ts`, re-exportiert via `src/utils/claudeClient.ts`). MED-01 ist teilweise gelöst — `/api/chat` und `/api/plan` nutzen `selectModel()` korrekt. Layer 2 (`marketContextExtractor.ts`) nutzt `MODELS.SONNET` hardcoded (kein Breaking Issue da Sonnet für L2 immer gewünscht).

**Task-Typ `opponent_simulation`** ist bereits in modelRouter definiert: `selectModel('opponent_simulation', 'profi') → MODELS.OPUS`. Da NC-L3-SIM `requireTier('profi')` verwendet, läuft der Simulation-LLM-Call immer mit Opus.

**Empfehlung Layer 3 SIM:** `selectModel('opponent_simulation', req.tier)` — konsistent mit bestehendem Pattern. Intake-Phase und Coach-Hints können mit `MODELS.SONNET` laufen (weniger komplex, günstiger). [Proposed]

---

### A4 — Persistierte Input-Shapes

**`AnalysisResult` (Layer 1)** — definiert in `src/types/index.ts:24–36`, persistiert als `negotiation_sessions.layer1_result JSONB` [Observed]:

| Feld | Typ | Verfügbarkeit |
|------|-----|--------------|
| `zopa_exists` | boolean | ✅ Observed |
| `zopa_min` | number | ✅ Observed |
| `zopa_max` | number | ✅ Observed |
| `nash_solution` | number | ✅ Observed |
| `monte_carlo_p50` | number | ✅ Observed (0 wenn kein ZOPA) |
| `monte_carlo_p90` | number | ✅ Observed (0 wenn kein ZOPA) |
| `acceptance_curve` | `AcceptanceCurvePoint[]` | ✅ Observed (leer wenn kein ZOPA) |
| `strategy_score` | number (0–100) | ✅ Observed |
| `deadline_effect` | number? | ✅ Observed (optional) |
| `missing_inputs` | string[] | ✅ Observed |
| `recommendations` | string[] | ✅ Observed (3 Sätze via Haiku) |
| `user_batna_strength` | — | ❌ **Missing** — intern in `strategyScore.ts` als `batnaScore = margin/own_target` berechnet, aber nicht in AnalysisResult exportiert |
| `recommended_opening` | — | ❌ **Missing** — kein Algorithmus |
| `tactics` | — | ❌ **Missing** — kein Feld, kein Algorithmus |

**Design-Entscheidung `user_batna_strength`:** Statt Layer-1-Interface zu brechen, wird `user_batna_strength` zur Simulation-Zeit aus vorhandenen Feldern abgeleitet: `(own_minimum / own_target)` — je näher an 1, desto schwächeres BATNA (wenig Spielraum). Diese Heuristik ist ausreichend für die Simulation-Steuerung. [Proposed]

**Design-Entscheidung `recommended_opening`:** Wird in `smlParser.ts` berechnet: `nash_solution + (nash_solution - own_minimum) * difficulty_factor` (Anchoring-Heuristik). Kein Layer-1-Change erforderlich. [Proposed]

**Design-Entscheidung `tactics`:** Wird nicht als separates Feld benötigt; `recommendations[]` aus Layer 1 + `strategy_score` reichen als Coaching-Input. [Proposed]

**`EnrichedAnalysisResult` (Layer 2)** — erweitert `AnalysisResult`, persistiert als `negotiation_sessions.layer2_result JSONB` [Observed]:

| Feld | Typ | Verfügbarkeit |
|------|-----|--------------|
| `market_data_source` | `'web_search'\|'knowledge_graph'\|'none'` | ✅ Observed |
| `market_median` | number? | ✅ Observed (optional) |
| `market_range_min` | number? | ✅ Observed (optional) |
| `market_range_max` | number? | ✅ Observed (optional) |
| `reality_score` | number? | ✅ Observed (optional) |
| `market_context_summary` | string? | ✅ Observed (optional) |
| `market_comparison` | `'below'\|'at'\|'above'`? | ✅ Observed (Bonus-Feld) |

`negotiation_sessions` hat kein `layer3_result`-Feld. [Observed] Neue Simulationen persistieren in `simulation_sessions` (neue Tabelle).

---

## 3. Datenfluss-Skizze

```
negotiation_session
  ├── layer1_result (ZOPA, Nash, MC, strategy_score, acceptance_curve, deadline_effect)
  └── layer2_result? (market_median, reality_score, market_context_summary) [GATED]
          │
          ▼
POST /api/simulate/start { session_id }
          │
          ├─ Lade layer1_result + layer2_result aus DB
          ├─ LLM (Sonnet): Lückenanalyse — was fehlt für realistische Simulation?
          │   → clarifying_questions[] (style, difficulty, batna, deadline, context)
          │
          ▼ status: 'intake'  ←──────────────────┐
                                                  │
POST /api/simulate/turn { user_message }         │
    [während Intake]                              │
          │                                       │
          ├─ LLM (Sonnet): Extraktion aus Antworten  │
          ├─ Prüfe: intake vollständig?           │
          │   nein → weitere Fragen ─────────────┘
          │   ja   ↓
          ├─ Build ScenarioObject (inkl. L1-Snapshot, L2-Snapshot wenn verfügbar)
          ├─ computeHiddenOpponentRange (extended: L1 ZOPA + difficulty + style)
          ├─ computeSimulationWarning
          ├─ buildOpponentSystemPrompt (neu: mit ZOPA-Band, Nash-Referenz, MC-Pacing)
          ├─ LLM (Opus): Opening Message
          ├─ INSERT simulation_sessions (+ simulation_turns turn 0)
          └─ Response: { status: 'ready', opening_message, warning? }

POST /api/simulate/turn { user_message, client_turn_id }
    [während aktiver Simulation]
          │
          ├─ Idempotenz-Check (client_turn_id)
          ├─ Offer-Detection aus user_message (Regex + LLM)
          ├─ acceptance_curve lookup: P(accept | offer) → stochastische Terminierung
          ├─ deadline_effect: Urgency-Eskalation über Turns
          ├─ buildOpponentSystemPrompt (stateless, per Turn; L1-Grounding injiziert)
          │   ├─ ZOPA-Band als Verhandlungsraum
          │   ├─ Nash als fairer Referenzpunkt (Gegner nennt ihn nur unter Druck)
          │   ├─ acceptance_curve bestimmt Konzessions-Pacing
          │   ├─ user_batna_strength → Gegner darf stärkeres BATNA bluffen
          │   ├─ reality_score [GATED]: wenn > 20% → Gegner zitiert Marktdaten als Argument
          │   └─ private hidden interests (Relation, Zeit, Präzedenz)
          ├─ Coach-Hint-Trigger (optional, max 1× alle 3 Turns): erkenne verpasste Taktiken
          ├─ LLM (Opus): Gegner-Antwort
          ├─ UPSERT simulation_turns (ON CONFLICT DO NOTHING)
          ├─ Terminierungs-Check: deal / walkaway / max_turns / user_abort
          └─ Response: { opponent_message, coach_hint?, offer_detected?, turn_number, status }

POST /api/simulate/debrief { simulation_id, final_offer? }
          │
          ├─ Lade alle Turns
          ├─ Konzessionsanalyse: Timeline user vs. Gegner offers
          ├─ evaluateOutcome (extended): ZOPA-Perzentil, Nash-Distanz, MC-Vergleich
          ├─ Taktik-Analyse: was wurde genutzt / verpasst
          ├─ LLM (Sonnet): qualitative Empfehlungen + key_mistakes
          ├─ L2-Vergleich [GATED]: Deal vs. market_median
          ├─ UPDATE simulation_sessions (evaluation, status=finished)
          └─ Response: DebriefResult (+ hidden_opponent_minimum/target enthüllt)
```

**L2-Gate-Pattern** (in allen Prompts):

```typescript
interface MarketDataContext {
  available: boolean;
  data?: Pick<EnrichedAnalysisResult,
    'market_median' | 'market_range_min' | 'market_range_max' |
    'reality_score' | 'market_context_summary'>;
}

function buildMarketDataContext(layer2?: EnrichedAnalysisResult): MarketDataContext {
  if (!layer2 || layer2.market_data_source === 'none' || !layer2.market_median) {
    return { available: false }; // Gate inaktiv — kein L2 in Simulation
  }
  return { available: true, data: { ...layer2 } };
}
```

---

## 4. Type-Definitionen

### ScenarioObject (Intake-Output, kanonisch für Layer 3)

```typescript
interface ScenarioObject {
  // Basis (aus OpponentSimulationSetup, aktiv)
  negotiation_type: NegotiationType;
  opponent_style: OpponentStyle;
  scenario_difficulty: ScenarioDifficulty;
  own_target: number;
  own_minimum: number;
  opponent_estimated_max: number;
  opponent_estimated_min: number;
  negotiation_session_id?: string;

  // Intake-Ergebnisse
  intake_complete: boolean;
  clarifying_questions_asked: string[];
  scenario_description?: string;         // LLM-generierte Kontext-Zusammenfassung
  batna_description?: string;
  deadline_days?: number;
  relationship_importance?: 'low' | 'medium' | 'high';

  // Derived (zur Simulation-Zeit berechnet, nicht aus L1 exportiert)
  user_batna_strength: number;           // = own_minimum / own_target (0–1, höher = stärker)
  recommended_opening: number;           // Nash + (Nash - own_minimum) * difficulty_factor

  // L1-Snapshot (geladen bei Intake, unveränderlich für diese Simulation)
  layer1_snapshot: AnalysisResult;

  // L2-Snapshot [GATED — null bis L2-Fix verifiziert]
  layer2_snapshot: MarketDataContext;
}
```

### SimulationTurn (reaktiviert + erweitert aus types/index.ts)

```typescript
interface SimulationTurn {
  turn_number: number;
  role: 'user' | 'assistant' | 'coach'; // coach = inline Coach-Hint
  content: string;
  offer_detected?: number;               // geparster Angebotsbetrag
  coach_hint?: string;                   // optionaler inline Coach-Hinweis
  metadata?: Record<string, unknown>;
}
```

### PrivateOpponentState (server-only, wird nie an Client gesendet)

```typescript
interface PrivateOpponentState {
  hidden_minimum: number;                // echtes Walkaway (aus computeHiddenOpponentRange)
  hidden_target: number;                 // Eröffnungsanker
  hidden_interests: string[];            // z.B. ["relationship", "speed", "precedent"]
  hidden_batna_strength: 'weak' | 'medium' | 'strong'; // darf bluffed werden
  bluff_active: boolean;                 // ob Gegner gerade ein stärkeres BATNA behauptet
  concession_pace: 'fast' | 'moderate' | 'slow'; // aus scenario_difficulty
}
// Persistiert in simulation_sessions.private_state JSONB (RLS: user sieht es nie via API)
// Enthüllt in /debrief Response als hidden_opponent_minimum, hidden_opponent_target
```

### DebriefResult

```typescript
interface DebriefResult {
  deal_reached: boolean;
  final_offer?: number;
  walkaway_reason?: 'max_turns' | 'user_walkaway' | 'opponent_walkaway';

  // Quantitative Metrics (aus L1)
  final_vs_zopa_percentile: number;     // 0=ungünstig, 100=optimal für User
  final_vs_nash_distance: number;       // absolute Distanz von Nash-Lösung
  final_vs_nash_direction: 'above_nash' | 'below_nash' | 'at_nash';
  vs_monte_carlo_p50: 'above' | 'at' | 'below';
  vs_monte_carlo_p90: 'above' | 'at' | 'below';

  // L2 [GATED]
  vs_market_median?: number;            // nur wenn L2 aktiv: Deal - market_median
  market_comparison?: 'below' | 'at' | 'above';

  // Konzessionsanalyse
  concession_timeline: Array<{
    turn: number;
    user_offer?: number;
    opponent_offer?: number;
    user_concession_pct?: number;       // relativ zu prev. offer
    opponent_concession_pct?: number;
  }>;
  total_user_concession_pct: number;
  total_opponent_concession_pct: number;

  // Taktik-Bewertung
  tactics_used_well: string[];           // z.B. ["Anchoring", "BATNA signaling"]
  tactics_missed: string[];              // z.B. ["MESO nicht versucht", "kein Prinzip zitiert"]
  opponent_tactics_observed: string[];   // was der Gegner tat
  key_mistakes: string[];
  recommendations: string[];

  // Summary
  overall_score: number;                // 0–100

  // Enthüllter Gegner-Privatzustand
  hidden_opponent_minimum: number;
  hidden_opponent_target: number;
}
```

### Request/Response-Typen

```typescript
// POST /api/simulate/start
interface StartSimulationRequest {
  session_id: string;                   // negotiation_session mit L1/L2 data
}
interface StartSimulationResponse {
  simulation_id: string;
  status: 'intake' | 'ready';
  clarifying_questions: string[];       // leer wenn status='ready'
  scenario_preview?: {                  // nur wenn status='ready'
    opponent_style: OpponentStyle;
    scenario_difficulty: ScenarioDifficulty;
    opening_message: string;
    warning?: string;
  };
}

// POST /api/simulate/turn
interface SimulateTurnRequest {
  simulation_id: string;
  user_message: string;
  client_turn_id: string;              // UUID, Idempotenz-Key
}
interface SimulateTurnResponse {
  opponent_message?: string;           // null während Intake-Fragen
  coach_message?: string;              // inline Coach-Hint (max 1×/3 Turns)
  clarifying_question?: string;        // nächste Intake-Frage wenn status='intake'
  turn_number: number;
  offer_detected?: number;
  status: 'intake' | 'active' | 'deal' | 'walkaway' | 'max_turns' | 'user_abort';
  idempotent?: boolean;
}

// POST /api/simulate/debrief
interface SimulateDebriefRequest {
  simulation_id: string;
  final_offer?: number;
}
// Response: DebriefResult (oben definiert)
```

---

## 5. Error-Cases & Degradation

| Fehler-Case | Handling |
|------------|---------|
| Layer-2 nicht verfügbar | `MarketDataContext.available = false` → L2-Pfad inaktiv; Simulation läuft ohne Marktdaten-Erdung; kein Fehler |
| Unvollständige Session (kein layer1_result) | `/start` → HTTP 422 `MISSING_LAYER1_DATA` — Simulation setzt L1-Daten voraus |
| Intake bricht ab (User sendet "abbrechen") | Status → `user_abort`; `simulation_sessions.status = 'abandoned'`; Ressourcen freigegeben |
| Anthropic-Timeout (>30s) | HTTP 504 `LLM_TIMEOUT`; client kann Idempotenz-Key wiederverwenden → identischer Call retrybar |
| Idempotenz: gleicher `client_turn_id` | HTTP 200 mit `idempotent: true` + gecachtem Content (kein neuer LLM-Call) |
| Turn-Limit erreicht | Auto-finish: `status = 'max_turns'`; Debrief sofort verfügbar |
| ZOPA existiert nicht (kein Überschneidungsbereich) | Simulation startet mit Warnung: "Kein ZOPA — harte Verhandlung"; Gegner-Parameters werden konservativ gesetzt; Debrief markiert als `no_zopa_scenario` |
| Simulation bereits `finished/abandoned` | Turn-Call → 409 `SIMULATION_ALREADY_FINISHED` |
| Gegner-Antwort leer/unparsierbar | Retry mit gekürztem History-Window (max 3 Versuche); danach 500 `LLM_RESPONSE_INVALID` |
| `session_id` gehört nicht zu `req.user.id` | 403 `UNAUTHORIZED_SESSION` |

---

## 6. ENGB01-Blueprint-Konformität

**Abweichungen vom Blueprint (explizit):**

| Blueprint-Konzept | Design-Abweichung | Begründung |
|---|---|---|
| SML-Bibliothek mit statischen `ScenarioObjects` | Dynamischer LLM-Intake statt reiner SML-Bibliothek | Statische Szenarien müssen gepflegt werden; LLM-Intake deriviert Szenarien aus realer Session — höherer Realismus, kein Pflegeaufwand |
| `ai_opponent.tactics` als fester Array im Schema | Taktiken als Prompt-Instruktionen im `PrivateOpponentState` | Flexibler, LLM-getrieben; expliziter Array würde Taktik-Set einfrieren |
| `fallback_position` als explizites Feld | `hidden_minimum` in `PrivateOpponentState` | Semantisch äquivalent, klarere Namensgebung |
| Separate SML-Parsing-Library | `smlParser.ts` als eigenständiges Modul | Funktional äquivalent; kein Library-Overhead |
| `win_conditions` im alten EF-Schema | Abgebildet auf `acceptance_curve` aus Layer 1 | Mathematisch präziser als verbale Win-Conditions |

**ADR-Bedarf:** Das dynamische Intake-Design ist eine signifikante Abweichung vom ursprünglichen SML-Ansatz und betrifft die Simulation-Architektur grundlegend. **Ein ADR-010 "NC-L3-SIM Intake Strategy" wird empfohlen** (DECISION: dynamischer LLM-Intake vs. statische SML-Bibliothek; STATUS: Proposed). ADR-009 bleibt unverändert (Backend-Routing für Layer 3 bestätigt).

---

## 7. Tier-/RLS-/Migration-Impact

**Tier:** profi-only. `requireTier('profi')` Middleware auf allen 3 Endpoints.

**Neue Supabase-Tabellen (Migration erforderlich):**

```sql
-- simulation_sessions (Layer 3 SIM, richer state machine)
CREATE TABLE simulation_sessions (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                 UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  negotiation_session_id  UUID REFERENCES negotiation_sessions(id) ON DELETE SET NULL,

  -- ScenarioObject fields
  scenario_object         JSONB NOT NULL,            -- vollständiges ScenarioObject
  intake_complete         BOOLEAN NOT NULL DEFAULT false,
  layer1_snapshot         JSONB NOT NULL,            -- Snapshot bei Simulation-Start
  layer2_snapshot         JSONB,                     -- NULL bis L2-Gate aktiv

  -- Simulation state
  status                  TEXT NOT NULL DEFAULT 'intake'
                            CHECK (status IN ('intake','active','finished','abandoned')),
  turn_count              INTEGER NOT NULL DEFAULT 0,
  max_turns               INTEGER NOT NULL DEFAULT 15,

  -- Private (never exposed via API)
  private_state           JSONB NOT NULL,            -- PrivateOpponentState

  -- Results
  final_outcome           NUMERIC,
  evaluation              JSONB,                     -- DebriefResult

  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at             TIMESTAMPTZ
);

ALTER TABLE simulation_sessions ENABLE ROW LEVEL SECURITY;

-- RLS: user sieht nur eigene Sessions; tier-gate via JWT
CREATE POLICY simulation_sessions_user_policy ON simulation_sessions
  FOR ALL USING (
    user_id = auth.uid()
    AND (auth.jwt() ->> 'user_metadata')::jsonb ->> 'tier' = 'profi'
  );

-- private_state niemals via SELECT für user_id sichtbar → API-Layer filtert es
-- (alternative: separate Spalte die nicht in SELECT-* inkludiert wird — einfacher via API-Filter)

-- simulation_turns (reuses concept from opponent_simulation_turns)
CREATE TABLE simulation_turns (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_session_id UUID NOT NULL REFERENCES simulation_sessions(id) ON DELETE CASCADE,
  client_turn_id        UUID,
  UNIQUE (simulation_session_id, client_turn_id),
  turn_number           INTEGER NOT NULL,
  role                  TEXT NOT NULL CHECK (role IN ('user','assistant','coach')),
  content               TEXT NOT NULL,
  offer_detected        NUMERIC,
  coach_hint            TEXT,
  metadata              JSONB,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_simulation_turns_session ON simulation_turns (simulation_session_id, turn_number);

ALTER TABLE simulation_turns ENABLE ROW LEVEL SECURITY;
CREATE POLICY simulation_turns_user_policy ON simulation_turns
  FOR ALL USING (
    simulation_session_id IN (
      SELECT id FROM simulation_sessions WHERE user_id = auth.uid()
    )
  );
```

**Bestehende Tabellen:** keine Änderungen an `opponent_simulation_sessions` oder `opponent_simulation_turns` — backward compat zu NC-L3-OPPONENT-UI.

---

## 8. Telemetrie-Plan

Alle Events via `trackEvent()` (PostHog, `src/utils/posthog.ts`):

| Event | Trigger | Properties |
|-------|---------|-----------|
| `simulation_started` | POST /start, status='ready' (Intake abgeschlossen) | tier, negotiation_type, opponent_style, scenario_difficulty, has_l2, zopa_exists, strategy_score |
| `simulation_intake_question` | Jede Intake-Runde | simulation_id, question_count |
| `simulation_turn` | Jeder aktive Turn | simulation_id, turn_number, offer_detected (bool), coach_hint_shown (bool) |
| `simulation_finished` | /debrief aufgerufen | simulation_id, deal_reached, turns_taken, final_vs_zopa_percentile, overall_score, walkaway_reason |
| `simulation_abandoned` | status→abandoned | simulation_id, at_turn |

**Metriken für Produkt-Entscheidungen:**
- Deal-Rate (deal_reached / simulation_finished)
- Durchschnittliche Turns bis Deal
- Coach-Hint-Akzeptanz (turns nach hint mit besseren offers)
- Debrief-Score-Distribution (overall_score Histogramm)
- Abbruchquote nach Phase (intake vs. active)
- L2-Gate-Aktivierungsrate (sobald L2-Fix aktiv)

---

## 9. Betroffene Repos, Supabase, API-Vertragsänderungen

**Repos:**

| Repo | Änderungen |
|------|-----------|
| `negotiationcoach-backend` | `src/layer3/smlParser.ts` (neu), `src/layer3/promptBuilder.ts` (neu), `src/layer3/simulationLoop.ts` (neu), `src/layer3/opponentEngine.ts` (refactor), `src/layer3/debriefEngine.ts` (neu), `src/layer3/index.ts` (neu), `src/api/simulationRoutes.ts` (neu), `src/api/routes.ts` (neue Endpoints registrieren), `src/types/index.ts` (Types erweitern) |
| `negotiation-buddy` | `src/pages/OpponentSimulator.tsx` (refactor für Intake-Phase + neue Endpoints) oder neuer `SimulationPage.tsx`, `src/lib/apiClient.ts` (3 neue Funktionen), `src/lib/types.ts` (neue Response-Typen) |
| `shared-context` | `docs/features/layer3-simulation.md` (dieses Dokument), `docs/contracts/frontend-backend.md` (neue Endpoints), ADR-010 (empfohlen) |

**Supabase-Instanz:** Migration für 2 neue Tabellen (`simulation_sessions`, `simulation_turns`) + 2 RLS-Policies. Supabase-MCP für Anwendung verwenden.

**API-Vertragsänderungen:** `docs/contracts/frontend-backend.md` muss um 3 neue Endpoints erweitert werden (NC-L3-SIM-Abschnitt). `/contract-check` ist Pflicht vor Merge. Keine Breaking Changes an bestehenden Endpoints.

---

## 10. Risiken & Testansatz

### Risiken

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| Intake-LLM extrahiert Setup inkorrekt (falsche Zahlen) | Mittel | Regex-Fallback für numerische Felder (Lesson 2026-06-19); user_only messages; Validierung gegen own_target > own_minimum |
| Opus-Latenz >10s pro Turn → schlechte UX | Mittel | 30s Timeout + Idempotenz-Key; Streaming als spätere Ausbaustufe |
| Gegner ignoriert ZOPA-Instruktion, macht triviales Angebot | Mittel | System-Prompt explizit: "Dein Eröffnungsangebot MUSS unter X liegen"; computeSimulationWarning als fallback |
| L2-Gate versehentlich aktiv mit falschen Marktdaten | Niedrig | `MarketDataContext.available` muss `market_data_source !== 'none'` AND `market_median !== undefined` sein |
| Intake läuft unendlich (User beantwortet nichts Verwertbares) | Niedrig | max_intake_turns (default 8); danach auto-ready mit available Daten |
| `private_state` via API-Leak | Niedrig | API-Layer filtert private_state explizit aus allen Responses; Debrief-Endpoint enthüllt NUR hidden_minimum/target |

### Testansatz

**TypeCheck (notwendig, nicht hinreichend):**
```bash
cd ../negotiationcoach-backend && npx tsc --noEmit
cd ../negotiation-buddy && npx tsc --noEmit
```

**curl-Tests (Pflicht, 1 pro Endpoint):**

```bash
# Test 1: /api/simulate/start — Intake-Phase auslösen
curl -X POST https://negotiationcoach-backend.onrender.com/api/simulate/start \
  -H "Authorization: Bearer $PROFI_JWT" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<session_with_l1_result>"}' \
  | jq '{status, clarifying_questions_count: (.clarifying_questions | length)}'
# Erwartet: status='intake', clarifying_questions.length >= 1

# Test 2: /api/simulate/turn (Intake) — Setup abschließen
curl -X POST https://negotiationcoach-backend.onrender.com/api/simulate/turn \
  -H "Authorization: Bearer $PROFI_JWT" \
  -H "Content-Type: application/json" \
  -d '{"simulation_id": "<id>", "user_message": "kooperativ, mittlere Schwierigkeit, mein BATNA ist ein anderes Angebot über 41000", "client_turn_id": "<uuid>"}' \
  | jq '{status, has_opening_message: (.opponent_message != null)}'
# Erwartet: status='ready' oder 'intake' (wenn weitere Fragen), opponent_message vorhanden wenn ready

# Test 3: /api/simulate/turn (aktiv) — Angebot erkennen
curl -X POST https://negotiationcoach-backend.onrender.com/api/simulate/turn \
  -H "Authorization: Bearer $PROFI_JWT" \
  -H "Content-Type: application/json" \
  -d '{"simulation_id": "<id>", "user_message": "Ich biete 43500 an.", "client_turn_id": "<uuid2>"}' \
  | jq '{status, offer_detected, opponent_message_length: (.opponent_message | length)}'
# Erwartet: offer_detected=43500, status='active', opponent_message nicht leer

# Test 4: /api/simulate/turn (Idempotenz) — gleiche client_turn_id
curl -X POST https://negotiationcoach-backend.onrender.com/api/simulate/turn \
  -H "Authorization: Bearer $PROFI_JWT" \
  -H "Content-Type: application/json" \
  -d '{"simulation_id": "<id>", "user_message": "Ich biete 43500 an.", "client_turn_id": "<uuid2>"}' \
  | jq '{idempotent}'
# Erwartet: idempotent=true

# Test 5: /api/simulate/debrief — Ergebnis enthüllen
curl -X POST https://negotiationcoach-backend.onrender.com/api/simulate/debrief \
  -H "Authorization: Bearer $PROFI_JWT" \
  -H "Content-Type: application/json" \
  -d '{"simulation_id": "<id>", "final_offer": 43500}' \
  | jq '{deal_reached, final_vs_zopa_percentile, overall_score, hidden_opponent_minimum}'
# Erwartet: alle Felder vorhanden, hidden_opponent_minimum erstmals sichtbar

# Test 6: Tier-Gate — nicht-profi User
curl -X POST https://negotiationcoach-backend.onrender.com/api/simulate/start \
  -H "Authorization: Bearer $KMU_JWT" \
  -d '{"session_id": "<id>"}' | jq '{error}'
# Erwartet: 403 INSUFFICIENT_TIER
```

**Acceptance-Test (manuell):**
- Gehaltsverhandlung own_target=44000, own_minimum=42000, opponent_max=48000, opponent_min=38000, kooperativ, mittel
- Gegner-Eröffnung muss unter 44000 liegen (computeSimulationWarning darf null sein)
- Nach 5 Turns: Konzessionsmuster erkennbar (Gegner bewegt sich Richtung Nash ~43000)
- Debrief: `final_vs_zopa_percentile` > 50 wenn Deal nahe Nash; `hidden_opponent_minimum` enthüllt

---

## 11. Abhängigkeiten & Sequenz

```
ADR-007 (Option A, 2026-04-21)   ✅ ENTSCHIEDEN — kein Blocker
NC-L3-OPPONENT (Backend)         ✅ Released (d6b39b6) — bestehende Infra nutzbar
NC-L3-OPPONENT-UI                ✅ Released (78ff4fb) — weiterhin mit alten Endpoints

NC-L3-SIM-REALISM                ✅ Released (690851c) — opponentEngine Basis korrigiert
                                      │
                                      ▼
[ADR-010 Proposal: Intake Strategy]  ←─ Empfohlen, kein Blocker für Design
                                      │
                                      ▼
                          Implementierungssequenz (nach GO):
                          Phase 1: smlParser.ts + promptBuilder.ts (pure Logik, testbar ohne DB)
                          Phase 2: debriefEngine.ts (pure Logik)
                          Phase 3: simulationRoutes.ts + routes.ts-Integration
                          Phase 4: Supabase-Migration (simulation_sessions + simulation_turns + RLS)
                          Phase 5: opponentEngine.ts refactor (L1-Injection)
                          Phase 6: negotiation-buddy OpponentSimulator.tsx refactor
                          Phase 7: curl-Tests + TypeCheck + manueller Acceptance-Test

Layer-2-Fix (GATED):              ─── unabhängig von Implementierungssequenz
                                      L2-Gate in promptBuilder.ts aktivieren sobald L2 grün
                                      kein Code-Change benötigt — nur env/config Flag?
                                      %% TODO: nicht eindeutig aus Code ableitbar — L2-Gate-Aktivierung über Code oder Config klären

NC-L3-OPPONENT-UI Migration:          separates Future-Item — OpponentSimulator.tsx auf neue
                                      /api/simulate/* Endpoints umstellen (nach Verifikation)
```

**Was NICHT zuerst implementiert wird:** NC-L3-OPPONENT-UI-Migration, L2-Aktivierung, Streaming.

---

## 12. Skill-/Doc-/ADR-Update-Bedarf

| Artefakt | Aktion | Zeitpunkt |
|---------|--------|-----------|
| `docs/contracts/frontend-backend.md` | 3 neue Endpoints dokumentieren (NC-L3-SIM-Abschnitt) | nach GO, vor erstem Merge |
| `product/feature-register.md` | NC-L3-SIM eintragen (ID, Status: Qualified, Repos, Release: Wave 3) | vor GO-Entscheidung |
| `product/briefs/NC-L3-SIM.md` | Delivery Brief aus diesem Dokument ableiten | nach GO |
| `docs/decision-log/ADR-010-*.md` | ADR-010 "NC-L3-SIM Intake Strategy" (dynamischer Intake vs. SML-Bibliothek) | empfohlen, nicht blockierend |
| `docs/ARCHITECTURE.md` | Abschnitt 2 (Datenflüsse) + 3 (Service Boundaries) erweitern um /api/simulate/* | nach Implementierung |
| `/contract-check` | Pflicht vor Merge | nach Implementierung |
| `/impact-check` | cross-repo — negotiation-buddy OpponentSimulator.tsx refactor | vor Phase 6 |

---

## Offene Freigabe-Punkte

- [ ] Feature-Register-Abgleich (`product/feature-register.md`, `product/releases/current.md`) — NC-L3-SIM als Item eintragen
- [ ] ADR-010-Status prüfen (empfohlen: dynamischer Intake vs. SML-Bibliothek)
- [ ] Layer-2-Fix-Status prüfen — L2-Gate-Aktivierungs-Mechanismus klären (Code vs. Config)
- [ ] NC-L3-OPPONENT-UI Migration-Zeitpunkt klären (weiterhin alte Endpoints oder sofort auf /api/simulate/*)
- [ ] max_turns für SIM-v2 abstimmen (Default 15 — höher als NC-L3-OPPONENT Default 12?)
- [ ] GO / HOLD / SPLIT / BACK TO DOCS Entscheidung dokumentiert
