**Status:** GO — Qualified 2026-07-07 (feature-plan Schritt 2–5 durchlaufen), Phase-1-Planung läuft
**Item-ID:** NC-L3-SIM
**Erstellt:** 2026-07-06 · **Qualified:** 2026-07-07
**Owner/Repo:** negotiationcoach-backend (src/layer3/)
**Blockiert durch:** nichts mehr.
  - Layer-2-Fix: ✅ AUFGELÖST 2026-07-07 — R-2026-05 (NC-L2-FIX) und R-2026-09 (NC-L2-UI) sind Released und laut `product/roadmap.md`/`product/strategy.md` verifiziert. `MarketDataContext.available` bleibt als defensiver Per-Session-Check bestehen (einzelne Sessions können weiterhin ohne L2-Daten sein), ist aber **kein globaler Kill-Switch mehr** — siehe aktualisierten Abschnitt 3.
  - ADR-007 (Option A) ist entschieden und blockiert NICHT mehr — NC-L3-OPPONENT ist Released; dieses Item betrifft keine EF-Engine-Logik
**Neue verbindliche Design-Vorgabe (2026-07-07):** `opponentEngine.ts`-Refactor MUSS additive/optionale Parameter verwenden — die bestehenden, released `/api/opponent-simulation/*`-Endpoints (Contract: `docs/contracts/frontend-backend.md:480-597`) laufen unverändert weiter, kein Breaking Change. Siehe aktualisierten Abschnitt 7/11.
**Feature-Register-Abgleich:** ✅ Erledigt 2026-07-07 — `product/feature-register.md` (Status: Qualified, Wave 3), Brief `product/briefs/NC-L3-SIM.md` angelegt.

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

**L2-Datenpfad** (in allen Prompts) — **AKTIV seit 2026-07-07** (Layer 2 verifiziert grün, R-2026-05/R-2026-09 Released). Die Funktion bleibt als Per-Session-Defensivcheck bestehen (nicht jede `negotiation_session` hat zwangsläufig ein valides `layer2_result`), ist aber kein globales Feature-Flag mehr:

```typescript
interface MarketDataContext {
  available: boolean;
  data?: Pick<EnrichedAnalysisResult,
    'market_median' | 'market_range_min' | 'market_range_max' |
    'reality_score' | 'market_context_summary'>;
}

function buildMarketDataContext(layer2?: EnrichedAnalysisResult): MarketDataContext {
  if (!layer2 || layer2.market_data_source === 'none' || !layer2.market_median) {
    return { available: false }; // Diese Session hat keine L2-Daten — kein globales Gate
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
| Layer-2 nicht verfügbar für diese Session | `MarketDataContext.available = false` → L2-Pfad für DIESE Simulation inaktiv (kein globales Gate mehr, siehe Abschnitt 3); Simulation läuft ohne Marktdaten-Erdung; kein Fehler |
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

**ADR-Bedarf:** ✅ Erledigt — `docs/decision-log/ADR-010-l3-sim-intake-strategy.md`, **DECIDED 2026-07-08**: Option A (dynamischer LLM-Intake), Option C (Hybrid) als trigger-basierte Zukunftsoption dokumentiert. ADR-009 bleibt unverändert (Backend-Routing für Layer 3 bestätigt).

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

**Bestehender Code — verbindliche Backward-Compat-Vorgabe (2026-07-07):** `opponentEngine.ts` wird aktuell live von `/api/opponent-simulation/{start,turn,finish}` genutzt (dokumentierter Contract, `docs/contracts/frontend-backend.md:480-597`, Released). Der Refactor von `computeHiddenOpponentRange` (L1/L2-Erweiterung) MUSS additive, optionale Parameter verwenden — alte Caller ohne die neuen Argumente müssen unverändertes Verhalten erhalten. Kein Deprecation der alten Endpoints in diesem Item; Migration von `OpponentSimulator.tsx` auf `/api/simulate/*` bleibt separates Future-Item (Abschnitt 11).

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
                          Phase 5: opponentEngine.ts refactor (L1-Injection, additive/optionale
                                      Parameter — /api/opponent-simulation/* bleibt unverändert lauffähig)
                          Phase 6: negotiation-buddy OpponentSimulator.tsx refactor
                          Phase 7: curl-Tests + TypeCheck + manueller Acceptance-Test

Layer-2-Datenpfad:                 ✅ AKTIV seit 2026-07-07 (kein Gate mehr, siehe Abschnitt 3) —
                                      buildMarketDataContext läuft ab Phase 1 mit echten L2-Daten,
                                      kein separater Aktivierungsschritt nötig

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

- [x] Feature-Register-Abgleich (2026-07-07) — NC-L3-SIM in `product/feature-register.md` eingetragen (Status: Qualified, Wave 3)
- [x] ADR-010-Status geprüft (2026-07-08) — **DECIDED**, Option A (dynamischer Intake), Option C als spätere Erweiterung vorgemerkt
- [x] Layer-2-Fix-Status geprüft (2026-07-07) — ✅ grün, kein Gate mehr; siehe Abschnitt 3
- [x] opponentEngine.ts-Kompatibilität geklärt (2026-07-07) — additive/optionale Parameter verbindlich, siehe Abschnitt 7
- [ ] NC-L3-OPPONENT-UI Migration-Zeitpunkt klären (weiterhin alte Endpoints oder sofort auf /api/simulate/*) — bewusst als separates Future-Item zurückgestellt (2026-07-07), zwei parallele Simulations-Einstiegspunkte bis dahin akzeptiert
- [x] max_turns für SIM-v2 entschieden (2026-07-07) — **15** (höher als NC-L3-OPPONENT Default 12, da Intake-Phase zusätzliche Turns verbraucht)
- [x] GO / HOLD / SPLIT / BACK TO DOCS Entscheidung dokumentiert (2026-07-07) — **GO**. Feature-Register-Eintrag (Status: Qualified) und `product/briefs/NC-L3-SIM.md` erstellt. ADR-010 bleibt offen (empfohlen, nicht blockierend, separat via `/adr-create`). Nächster Schritt: Phase-1-Plan (siehe unten).

---

## Phase-1-Plan

**Erstellt:** 2026-07-07 — Backend-Plan, TARGET REPO negotiationcoach-backend
**Status:** PLANNED — wartet auf GO für Implementierung (Template 2b-DEV)
**Scope:** kleinste sichere erste Slice aus Abschnitt 11 — reine Logik-Module, kein DB-Zugriff, keine Route-Registrierung, kein Eingriff in `opponentEngine.ts`/`opponentSimulationRoutes.ts`.

### 1. Umfang

Zwei neue, isolierte Module in `negotiationcoach-backend/src/layer3/`:

**`smlParser.ts` (neu):**
- `deriveUserBatnaStrength(own_minimum, own_target): number` — `own_minimum / own_target`, geklemmt auf `[0,1]`
- `computeRecommendedOpening(nash_solution, own_minimum, difficulty_factor): number` — `nash_solution + (nash_solution - own_minimum) * difficulty_factor`
- `buildScenarioObject(intakeResult, layer1Snapshot, layer2Snapshot?): ScenarioObject` — reine Zusammenführung, keine LLM-Calls, kein DB-Zugriff (Intake-LLM-Orchestrierung selbst ist Phase 3, `simulationRoutes.ts`)

**`promptBuilder.ts` (neu):**
- `buildMarketDataContext(layer2?: EnrichedAnalysisResult): MarketDataContext` — exakt wie in Abschnitt 3 spezifiziert (Per-Session-Defensivcheck, kein globales Gate)
- Grundgerüst für Intake-Fragen-Prompt (Lückenanalyse-Prompt-Text, noch ohne Anthropic-Client-Call — der Call selbst gehört zu `simulationRoutes.ts`, Phase 3)

**Nicht Teil von Phase 1:** `simulationLoop.ts`, `debriefEngine.ts`, `index.ts`, `simulationRoutes.ts`, `opponentEngine.ts`-Refactor, Migration — folgen in Phase 2–5 (Abschnitt 11).

### 2. Exakt betroffene Dateien

| Datei | Art |
|---|---|
| `negotiationcoach-backend/src/layer3/smlParser.ts` | neu |
| `negotiationcoach-backend/src/layer3/promptBuilder.ts` | neu |
| `negotiationcoach-backend/src/types/index.ts` | erweitert — `ScenarioObject`, `MarketDataContext` als Typen ergänzen (additiv, keine bestehenden Typen ändern) |

### 3. SIDE-EFFECT-CHECK (PFLICHT — bereits durchgeführt 2026-07-07)

a) `grep -rn "computeHiddenOpponentRange\|buildOpponentSystemPrompt\|computeSimulationWarning\|evaluateOutcome" src/` → **genau ein Treffer-File:** `src/api/opponentSimulationRoutes.ts` (4 Importe, keine anderen Caller im Repo). Phase 1 fasst diese Funktionen nicht an — Befund dokumentiert für spätere Phase-5-Referenz.
b) Kann die Änderung Verhalten für andere Caller verändern? **Nein** — `smlParser.ts`/`promptBuilder.ts` sind neue Dateien ohne bestehende Importe; `types/index.ts`-Erweiterung ist rein additiv (neue Interfaces, keine bestehenden Felder geändert).
c) Loop-Risiko (useEffect/useCallback)? **Entfällt** — reiner Backend-Code, kein React.
d) DB-Schema-Änderung? **Keine** in Phase 1.
e) API-Contract-Änderung? **Keine** in Phase 1 — keine Route registriert.

→ Alle fünf Punkte beantwortet, Blast Radius für Phase 1: **isoliert, keine Regressionsgefahr für bestehenden Code.**

### 4. Tests die danach laufen müssen

- Unit-Tests für `deriveUserBatnaStrength`, `computeRecommendedOpening`, `buildMarketDataContext` — pure Funktionen, kein DB/LLM-Mock nötig
- `npx tsc --noEmit` (negotiationcoach-backend) — 0 Fehler, insbesondere für die additiven `types/index.ts`-Erweiterungen
- Kein curl-Test in Phase 1 möglich (keine Route) — curl-Tests (Design-Doc Abschnitt 10) erst ab Phase 3

### 5. Docs/Contracts die zu updaten sind

- Keine — `docs/contracts/frontend-backend.md` erst bei Phase 3 (neue Routen)
- ADR-010 weiterhin empfohlen, nicht blockierend für Phase 1

### 6. Rollback-Strategie

Zwei neue, ungenutzte Dateien + additive Typen ohne Downstream-Referenzen — Rollback = Dateien löschen bzw. Types-Erweiterung revertieren. Kein DB-State, kein Deploy-Risiko, kein Caller betroffen.

### 7. Exakter Git-Commit-Befehl

```bash
cd ../negotiationcoach-backend && git add src/layer3/smlParser.ts src/layer3/promptBuilder.ts src/types/index.ts && git commit -m "feat(layer3): NC-L3-SIM Phase 1 — smlParser + promptBuilder (pure logic)"
```

**STOP — Phase-1-Plan steht. Wartet auf GO für Template 2b-DEV (Implementierung durch Subagent-Pattern).**

**✅ Phase 1 implementiert 2026-07-08 — commit `c00e719`, Task-Review Approved. Details: `product/briefs/NC-L3-SIM.md` Abschnitt "## Implement".**

---

## Phase-2-Plan

**Erstellt:** 2026-07-08 — Backend-Plan, TARGET REPO negotiationcoach-backend
**Status:** PLANNED — wartet auf GO für Implementierung (Template 2b-DEV)
**Scope:** zweite sichere Slice aus Abschnitt 11 — `debriefEngine.ts`, weiterhin reine Logik, kein DB-Zugriff, keine Route-Registrierung, kein LLM-Call.

### 1. Umfang

**`src/layer3/debriefEngine.ts` (neu):**

- `computeConcessionTimeline(turns: SimulationTurn[]): { concession_timeline: DebriefResult['concession_timeline']; total_user_concession_pct: number; total_opponent_concession_pct: number }`
  — liest `offer_detected` aus den Turns (Feld existiert nach der Typ-Erweiterung unten), baut die Timeline paarweise, berechnet prozentuale Zugeständnisse relativ zum jeweils vorherigen eigenen Angebot. Reine Funktion, kein DB-Zugriff (Turns werden als Array übergeben, nicht geladen).
- `computeOutcomeMetrics(finalOffer: number, layer1Snapshot: AnalysisResult): Pick<DebriefResult, 'final_vs_zopa_percentile' | 'final_vs_nash_distance' | 'final_vs_nash_direction' | 'vs_monte_carlo_p50' | 'vs_monte_carlo_p90'>`
  — **wichtig, Design-Entscheidung:** nutzt die bereits im `layer1_snapshot` gespeicherten `zopa_min/zopa_max/nash_solution/monte_carlo_p50/monte_carlo_p90` (echte Analyse-Werte), NICHT eine Neuberechnung aus `opponent_estimated_*`-Werten wie die alte `opponentEngine.ts::evaluateOutcome`. Das ist der Kernunterschied zu NC-L3-OPPONENT: NC-L3-SIM erdet das Debrief an der echten Analyse, nicht an geschätzten Gegner-Werten.
- `computeMarketComparison(finalOffer: number, layer2Snapshot: MarketDataContext): Pick<DebriefResult, 'vs_market_median' | 'market_comparison'>`
  — nur befüllt wenn `layer2Snapshot.available === true` und `data.market_median` vorhanden; sonst beide Felder `undefined`. Toleranzband für `market_comparison` ('below'/'at'/'above'): implementer's Ermessen, sinnvoller Default ±2%.
- `buildDebriefResult(pure: <Ergebnis der drei obigen Funktionen>, llmDerived: Pick<DebriefResult, 'tactics_used_well' | 'tactics_missed' | 'opponent_tactics_observed' | 'key_mistakes' | 'recommendations' | 'overall_score'>, outcome: Pick<DebriefResult, 'deal_reached' | 'final_offer' | 'walkaway_reason' | 'hidden_opponent_minimum' | 'hidden_opponent_target'>): DebriefResult`
  — reine Zusammenführung. **Die qualitativen LLM-Felder (`tactics_*`, `key_mistakes`, `recommendations`, `overall_score`) werden NICHT in Phase 2 berechnet** — laut Datenfluss (Abschnitt 3) braucht das einen Sonnet-Call ("LLM (Sonnet): qualitative Empfehlungen + key_mistakes"), das ist Phase-3-Scope (`simulationRoutes.ts`). `buildDebriefResult` nimmt sie als fertige Parameter entgegen, analog zu `buildScenarioObject`s additivem Zusammenführungs-Pattern aus Phase 1.

**`src/types/index.ts` — additive Erweiterung:**

- `DebriefResult`-Interface neu hinzufügen (vollständige Definition: Design-Doc Abschnitt 4)
- `SimulationTurn` additiv erweitern (bestätigt **toter Code, aktuell nirgends importiert** — A2-Discovery, siehe Abschnitt 2 — daher risikolos erweiterbar):
  ```typescript
  // vorher: role: 'user' | 'assistant';
  role: 'user' | 'assistant' | 'coach';
  offer_detected?: number;   // NEU
  coach_hint?: string;       // NEU
  ```

**Nicht Teil von Phase 2:** `simulationLoop.ts`, `simulationRoutes.ts`, jeglicher Anthropic-Client-Call, `opponentEngine.ts`-Refactor, Migration.

### 2. Exakt betroffene Dateien

| Datei | Art |
|---|---|
| `negotiationcoach-backend/src/layer3/debriefEngine.ts` | neu |
| `negotiationcoach-backend/src/types/index.ts` | additiv erweitert — `DebriefResult` neu, `SimulationTurn` additiv erweitert (kein bestehendes Feld entfernt/umbenannt) |

### 3. SIDE-EFFECT-CHECK (PFLICHT)

a) `grep -rn "SimulationTurn" src/` vor Implementierung durchführen und im Report bestätigen — laut A2-Discovery (2026-07-06) aktuell 0 Importe außerhalb der Definition selbst. Falls der Implementer einen Treffer findet, der bei der Planung nicht bekannt war: STOP, nicht einfach erweitern.
b) Kann die `SimulationTurn`-Erweiterung Verhalten für andere Caller verändern? Bei bestätigtem Befund aus (a): **Nein** — additive Felder, additiver Union-Wert, keine bestehenden Verwender.
c) `computeConcessionTimeline`/`computeOutcomeMetrics`/`computeMarketComparison`/`buildDebriefResult` sind neue, ungenutzte Exporte — keine bestehenden Caller.
d) DB-Schema-Änderung? Keine.
e) API-Contract-Änderung? Keine — keine Route in Phase 2.
f) `opponentEngine.ts`/`opponentSimulationRoutes.ts` weiterhin nicht angefasst — nicht importiert von `debriefEngine.ts`.

### 4. Tests

- `computeConcessionTimeline`: leeres Turn-Array, Turns ohne `offer_detected`, alternierende User/Gegner-Angebote, Prozent-Berechnung exakt geprüft
- `computeOutcomeMetrics`: alle drei `vs_monte_carlo_*`-Branches (above/at/below) je p50/p90, `final_vs_nash_direction` alle drei Werte, ZOPA-Perzentil-Randfälle (finalOffer außerhalb ZOPA)
- `computeMarketComparison`: `available: false` → beide Felder undefined; `available: true` alle drei `market_comparison`-Branches
- `buildDebriefResult`: Assemblierungs-Test — Ergebnis enthält alle Felder aus allen drei Quellen korrekt gemappt
- `npx tsc --noEmit` — 0 Fehler
- Bestehende Test-Suite (`npm test`) — keine Regression

### 5. Docs/Contracts

Keine — Contract-Update erst ab Phase 3 (neue Routen).

### 6. Rollback-Strategie

Eine neue Datei + additive Typ-Erweiterung ohne Downstream-Referenzen — Rollback = Datei löschen, Typ-Erweiterung revertieren. Kein DB-State, kein Deploy-Risiko.

### 7. Exakter Git-Commit-Befehl

```bash
cd ../negotiationcoach-backend && git add src/layer3/debriefEngine.ts src/types/index.ts && git commit -m "feat(layer3): NC-L3-SIM Phase 2 — debriefEngine (pure logic)"
```

**STOP — Phase-2-Plan steht. Wartet auf GO für Template 2b-DEV.**

---

## Phase-3-Plan (erweitert — absorbiert ehemalige Phase 4 + Phase 5)

**Erstellt:** 2026-07-21 — Backend-Plan, TARGET REPO negotiationcoach-backend
**Status:** PLANNED — wartet auf GO für Implementierung (Template 2b-DEV)
**Erzeugt via:** `/feature-plan NC-L3-SIM` (Schritte 1–4c durchlaufen, Schritt 4b explizit
bestätigt — siehe Konsequenz-Triage unten)

### Scope-Änderung ggü. Abschnitt 11 (Befund dieser Planungsrunde)

Die ursprüngliche Sequenz trennt Phase 3 (Routes), Phase 4 (Migration) und Phase 5
(`opponentEngine.ts`-Refactor). Beim Nachzeichnen des exakten Call-Graphs für diese
Phase wurden zwei Kopplungen gefunden, die diese Trennung nicht mehr sauber zulassen:

1. **Phase 3 hängt an Phase 5.** Der Datenfluss (Abschnitt 3) beschreibt die
   Opening-Message/Turn-Generierung bereits mit dem **erweiterten**
   `computeHiddenOpponentRange` (L1-ZOPA-Band) und `buildOpponentSystemPrompt`
   (ZOPA/Nash/MC-Grounding) — genau die additiven Parameter, die laut Abschnitt 11
   erst in Phase 5 entstehen sollen. Ohne diese Erweiterung würde Phase 3 den
   *alten*, nicht-L1-geerdeten Gegner ausliefern — das widerspricht dem gesamten
   Sinn von NC-L3-SIM ("mathematisch geerdete Simulation"). Der additive
   `opponentEngine.ts`-Refactor ist damit kein separierbarer Nachfolgeschritt,
   sondern eine Voraussetzung für funktionierende Phase-3-Turns.
2. **Phase 3 hängt an Phase 4 für sicheres Deployment.** `simulationRoutes.ts`
   schreibt gegen `simulation_sessions`/`simulation_turns`, die erst in Phase 4
   angelegt werden. Push nach `main` löst Auto-Deploy aus (Projekt-Konvention) —
   ohne die Migration wären die drei neuen Endpoints live, aber jeder Aufruf
   scheitert mit "relation does not exist". Entschärft durch den Tier-Gate-Befund
   unten (kein echter Nutzer erreicht die Endpoints ohnehin), aber es verletzt den
   Grundsatz "DB-Änderungen müssen in Produktion verifiziert werden" (siehe
   `tasks/lessons.md`, `feedback_migration_verification.md`), wenn Phase 3 isoliert
   als abgeschlossen gilt.

**Konsequenz:** Phase 3, Phase 4 (Migration) und Phase 5 (`opponentEngine.ts`-
Refactor) werden zu **einer** Implementierungseinheit zusammengefasst. Phase-
Nummern in Abschnitt 11 bleiben als historische Marker stehen; "Phase 5" entfällt
als eigener Schritt, ihr Inhalt ist Teil dieses Plans. Phase 6 (Frontend) und
Phase 7 (curl + manueller Acceptance-Test) bleiben unverändert eigene Schritte.

### Aus Schritt 4b bestätigt (GO 2026-07-21, keine Scope-Anpassung verlangt)

- **Tier-Gate-Lücke:** `requireTier('profi')` + die geplante RLS-Policy hängen von
  `auth.users.raw_user_meta_data.tier` ab. Verifiziert: kein Produktionspfad setzt
  dieses Feld je auf `'profi'` (kein Stripe-Webhook — AR-032 Paused; der
  Dev-Tier-Mock-Toggle schreibt nur `user_profiles.subscription_tier/persona_type`,
  ein anderes Feld). Kein echter Nutzer kann die neuen Endpoints heute erreichen.
  Bewusst akzeptiert — dieselbe Lücke wie bei NC-L3-OPPONENT, kein neues Problem.
- **Phase-3/4-Reihenfolge:** akzeptiert, gelöst durch die Scope-Zusammenfassung oben
  (Migration ist jetzt Teil derselben Implementierungseinheit, nicht nachgelagert).

### 1. Umfang

**Call-Graph (neu, Phase 3):**

```
routes.ts
  └─ simulationRoutes.ts (neu) — 3 Handler: POST /start, POST /turn, POST /debrief
       ├─ authMiddleware, requireTier('profi'), validateBody(Simulate*Schema)
       └─ layer3/index.ts (neu) — Orchestrierungs-Entrypoint
            ├─ smlParser.ts (Phase 1, unverändert) — buildScenarioObject, deriveUserBatnaStrength, computeRecommendedOpening
            ├─ promptBuilder.ts (Phase 1, unverändert) — buildMarketDataContext, buildIntakePromptSkeleton
            ├─ layer3/simulationLoop.ts (neu) — Turn-Orchestrierung, Offer-Detection, Terminierung
            ├─ opponentEngine.ts (additiv erweitert, siehe unten) — computeHiddenOpponentRange, buildOpponentSystemPrompt, computeSimulationWarning
            └─ debriefEngine.ts (Phase 2, unverändert) — computeConcessionTimeline, computeOutcomeMetrics, computeMarketComparison, buildDebriefResult
```

**`src/layer3/simulationLoop.ts` (neu):**
- `detectOffer(userMessage: string): number | undefined` — Regex-first (Lesson
  2026-06-19: LLM-Zahlenextraktion braucht Regex-Fallback), Beträge im Format
  `\d{1,3}(\.\d{3})*|\d+` vor Währungswörtern
- `lookupAcceptanceProbability(offer: number, layer1Snapshot: AnalysisResult): number`
  — nutzt bestehende `acceptance_curve` aus `layer1_snapshot`, keine Neuberechnung
- `computeDeadlineEscalation(turnNumber: number, deadlineDays: number | undefined, maxTurns: number): number`
  — Urgency-Faktor 0–1, steigt Richtung `max_turns`
- `checkTermination(turn: SimulationTurn, turnCount: number, maxTurns: number): 'active' | 'deal' | 'user_abort' | 'max_turns'`

**`src/layer3/index.ts` (neu) — Orchestrierung, ein Export pro Endpoint-Phase:**
- `runIntake(session, userMessage | undefined): { status: 'intake' | 'ready'; clarifying_questions?: string[]; opening_message?: string; scenario: ScenarioObject }`
  — LLM-Call 1 (Sonnet, neuer `TaskType` `l3_sim_intake`): Lückenanalyse bei erstem
  Aufruf, Extraktion bei Folgeaufrufen. Bei `intake_complete === true`:
  `computeHiddenOpponentRange` (erweitert) → `buildOpponentSystemPrompt` (erweitert)
  → LLM-Call (Opus, bestehender `TaskType` `opponent_simulation` — gleiche Aufgabe,
  gleiches Modell wie NC-L3-OPPONENT, kein neuer Router-Key nötig) → Opening Message
- `runTurn(session, userMessage, clientTurnId): { opponent_message: string; coach_hint?: string; offer_detected?: number; turn_number: number; status: string; idempotent?: true }`
  — Idempotenz-Check zuerst (client_turn_id), dann `detectOffer` →
  `lookupAcceptanceProbability` → `computeDeadlineEscalation` →
  `buildOpponentSystemPrompt` (per Turn, stateless) → LLM (Opus, `opponent_simulation`)
  → `checkTermination`
- `runDebrief(session, finalOffer?): DebriefResult`
  — lädt alle Turns → `computeConcessionTimeline` → `computeOutcomeMetrics` →
  `computeMarketComparison` → LLM-Call (Sonnet, neuer `TaskType` `l3_sim_debrief`):
  qualitative `tactics_used_well/missed`, `key_mistakes`, `recommendations`,
  `overall_score` → `buildDebriefResult`

**`src/layer3/opponentEngine.ts` (additiv erweitert — vormals Phase 5):**
- `computeHiddenOpponentRange` erhält optionale Parameter für L1-ZOPA-Band;
  bestehende Aufrufe ohne diese Parameter (aus `opponentSimulationRoutes.ts`)
  bleiben unverändert gültig (Design-Vorgabe Abschnitt 7, bereits Side-Effect-
  geprüft am 2026-07-07: genau ein Caller je Funktion)
- `buildOpponentSystemPrompt` erhält optionale Parameter für Nash-Referenz und
  Monte-Carlo-Pacing, gleiche Additiv-Regel

**`src/utils/modelRouter.ts` (additiv):**
- Zwei neue `TaskType`-Werte: `l3_sim_intake` (→ `MODELS.SONNET`), `l3_sim_debrief`
  (→ `MODELS.SONNET`). Opponent-Turn-Generierung nutzt den bestehenden
  `opponent_simulation`-Key (→ `MODELS.OPUS`) weiter — keine Duplikation eines
  bereits vorhandenen Routing-Eintrags.

**`src/types/index.ts` (additiv):**
- Request/Response-Typen für die drei Endpoints (vollständige Definitionen:
  Design-Doc Abschnitt 4, "Request/Response-Typen")
- Neuer `TaskType`-Union-Eintrag (s.o.)

**`src/api/validation.ts` (additiv, Pattern wie `StartOpponentSimulationSchema`/`TurnOpponentSimulationSchema`):**
- `SimulateStartSchema`, `SimulateTurnSchema`, `SimulateDebriefSchema` (Zod)

**`src/api/simulationRoutes.ts` (neu):**
- 3 Express-Handler, Fehlerbehandlung exakt nach Design-Doc Abschnitt 5
  (`MISSING_LAYER1_DATA`, `LLM_TIMEOUT`, `SIMULATION_ALREADY_FINISHED`,
  `LLM_RESPONSE_INVALID`, `UNAUTHORIZED_SESSION`)
- **Ergänzung ggü. Abschnitt 5 (in dieser Planungsrunde gefunden):** die Tabelle
  deckt "kein `layer1_result`" ab, aber nicht "`layer1_result` vorhanden, aber
  strukturell unvollständig" (z. B. ein älteres Analyse-Ergebnis mit
  `_debug.error`-Feld statt echter ZOPA/Nash-Werte). `/start` muss zusätzlich zur
  reinen Existenzprüfung die erwarteten numerischen Felder validieren, sonst
  bekommt `computeHiddenOpponentRange` `undefined`/`NaN`-Eingaben. Gleiches
  `MISSING_LAYER1_DATA`-Errorcode, erweiterte Prüfbedingung.

**Migration (`negotiationcoach-backend/supabase/migrations/`, vormals Phase 4):**
- `simulation_sessions` + `simulation_turns` + 2 RLS-Policies exakt wie Design-Doc
  Abschnitt 7 spezifiziert. Anwendung via `mcp__supabase__apply_migration`
  (Präzedenzfall: BUG-20260719-signup-trigger-tier-mismatch, 2026-07-21) plus
  Migrationsdatei im Repo — beides, nicht nur eines von beiden.

**Route-Registrierung in `routes.ts`:**
```typescript
router.post('/simulate/start', authMiddleware, requireTier('profi'), validateBody(SimulateStartSchema), async (req, res, next) => { ... });
router.post('/simulate/turn', authMiddleware, requireTier('profi'), validateBody(SimulateTurnSchema), async (req, res, next) => { ... });
router.post('/simulate/debrief', authMiddleware, requireTier('profi'), validateBody(SimulateDebriefSchema), async (req, res, next) => { ... });
```

**Nicht Teil dieser Phase:** `negotiation-buddy` (Phase 6, separates Item), curl-
Tests gegen den Live-Endpoint + manueller Acceptance-Test (Phase 7 — wird direkt im
Anschluss an diese Phase ausgeführt, da die Migration jetzt Teil derselben Einheit
ist), Deprecation von `/api/opponent-simulation/*` (nicht geplant).

### 2. Exakt betroffene Dateien

| Datei | Art |
|---|---|
| `negotiationcoach-backend/src/layer3/simulationLoop.ts` | neu |
| `negotiationcoach-backend/src/layer3/index.ts` | neu |
| `negotiationcoach-backend/src/layer3/opponentEngine.ts` | additiv erweitert (optionale Parameter, keine bestehende Signatur entfernt) |
| `negotiationcoach-backend/src/api/simulationRoutes.ts` | neu |
| `negotiationcoach-backend/src/api/routes.ts` | additiv — 3 neue Registrierungen |
| `negotiationcoach-backend/src/api/validation.ts` | additiv — 3 neue Zod-Schemas |
| `negotiationcoach-backend/src/utils/modelRouter.ts` | additiv — 2 neue `TaskType`-Werte |
| `negotiationcoach-backend/src/types/index.ts` | additiv — Request/Response-Typen, `TaskType`-Erweiterung |
| `negotiationcoach-backend/supabase/migrations/<timestamp>_create_simulation_sessions.sql` | neu |
| `shared-context/docs/contracts/frontend-backend.md` | neuer Abschnitt — 3 Endpoints |

### 3. SIDE-EFFECT-CHECK (PFLICHT)

a) `grep -rn "computeHiddenOpponentRange\|buildOpponentSystemPrompt\|computeSimulationWarning" src/` vor Implementierung erneut durchführen — Stand 2026-07-07 (Brief): genau ein Caller je Funktion (`opponentSimulationRoutes.ts`). Falls Implementer einen zweiten Caller findet: STOP, nicht einfach erweitern, erneut Side-Effect-Check.
b) Verändert die additive Erweiterung Verhalten für den bestehenden Caller (`opponentSimulationRoutes.ts`)? **Nein**, solange die neuen Parameter optional sind und bei Abwesenheit exakt das alte Verhalten reproduzieren — muss der Implementer per Unit-Test explizit beweisen (alter Aufruf ohne neue Parameter → identischer Output wie vor dem Refactor), nicht nur behaupten.
c) `opponentSimulationRoutes.ts` selbst wird nicht angefasst — bestätigen per `git diff --stat`.
d) DB-Schema-Änderung: 2 neue Tabellen, keine Änderung an bestehenden Tabellen (`opponent_simulation_sessions/turns` bleiben unverändert — per `git diff` gegen die Migration bestätigen, nicht nur behaupten).
e) API-Contract-Änderung: 3 neue Endpoints, keine bestehenden Endpoints verändert — `docs/contracts/frontend-backend.md` nur ergänzt, bestehende Abschnitte unverändert.
f) `modelRouter.ts`: neue `TaskType`-Werte sind additiv zur bestehenden Union — bestehende Task-Types/Routing-Einträge unverändert, per Diff bestätigen.

### 4. Tests

- Unit: `simulationLoop.ts` — `detectOffer` (Regex-Fälle inkl. Tausenderpunkt, kein Treffer, mehrere Zahlen im Text), `lookupAcceptanceProbability` (Randfälle: Angebot außerhalb ZOPA), `computeDeadlineEscalation` (ohne `deadline_days`, an `max_turns`-Grenze), `checkTermination` (alle 4 Zustände)
- Unit: `opponentEngine.ts` — Regressionstest: alter Call ohne neue Parameter → Output identisch zu vor dem Refactor (Pflicht, siehe SIDE-EFFECT-CHECK b)
- `npx tsc --noEmit` (negotiationcoach-backend) — 0 Fehler
- `npm test` — keine Regression, neue Tests in `scripts.test` verkabelt (holt die in Phase 1/2 als Minor-Finding vorgemerkte Lücke nach)
- **curl-Tests (Design-Doc Abschnitt 10, alle 6) gegen den Live-Endpoint** — jetzt
  möglich, da Migration Teil derselben Phase ist. Test 6 (Tier-Gate, 403) ist die
  einzige *tatsächlich* durchführbare Verifikation der Tier-Gate-Lücke von oben:
  ein `$KMU_JWT` bekommt 403, ein manuell geseedeter `$PROFI_JWT` (analog
  `seed-verify-user.ts`) müsste für Tests 1–5 verwendet werden, da kein echter
  Nutzer aktuell ein solches JWT organisch erhalten kann.

### 5. Docs/Contracts

- `docs/contracts/frontend-backend.md`: neuer Abschnitt nach dem bestehenden
  `/api/opponent-simulation/*`-Muster (Zeilen 480–597 als Vorlage) — 3 neue
  Endpoints mit Request/Response-Typen, Error-Codes
- `/contract-check` — Pflicht vor Merge (Design-Doc Abschnitt 12)
- `docs/ARCHITECTURE.md` Abschnitt 2 (Datenflüsse) + 3 (Service Boundaries) — laut
  Abschnitt 12 "nach Implementierung", nicht blockierend für diesen Plan

### 6. Rollback-Strategie

- Code (Routes, Orchestrierung, `modelRouter`/`types`/`validation`-Additive):
  Dateien löschen bzw. additive Erweiterungen revertieren, keine Downstream-
  Referenzen außerhalb dieses Features.
- `opponentEngine.ts`-Refactor: additive Parameter zurücknehmen — bestehender
  Caller unberührt, da er die neuen Parameter nie übergibt.
- Migration: `DROP TABLE simulation_turns, simulation_sessions CASCADE` — keine
  bestehenden Tabellen betroffen, kein Fremdschlüssel von außerhalb dieses
  Features zeigt auf diese beiden Tabellen.
- Da kein echter Nutzer die Endpoints heute erreichen kann (Tier-Gate-Lücke),
  ist ein Rollback nach Deploy praktisch risikolos — es gibt keine Produktions-
  Nutzungsdaten, die verloren gehen könnten.

### 7. Exakter Git-Commit-Befehl

```bash
cd ../negotiationcoach-backend && git add \
  src/layer3/simulationLoop.ts src/layer3/index.ts src/layer3/opponentEngine.ts \
  src/api/simulationRoutes.ts src/api/routes.ts src/api/validation.ts \
  src/utils/modelRouter.ts src/types/index.ts \
  supabase/migrations/ \
  && git commit -m "feat(layer3): NC-L3-SIM Phase 3 — simulate routes, opponent L1-grounding, migration"
```

**STOP — Phase-3-Plan steht. Wartet auf GO / HOLD / SPLIT / BACK TO DOCS.**
