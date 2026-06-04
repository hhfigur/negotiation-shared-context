# Delivery Brief: NC-L2-FIX
## Layer 2 Market Data Diagnose + Reparatur

**Release:** R-2026-05
**Status:** Released
**Affected repos:** negotiationcoach-backend
**Tier impact:** kmu, profi (Layer 2 is gated at requireTier('kmu'))
**Created:** 2026-04-20

---

## Goal / Outcome
`enrichWithMarketData()` liefert ein vollständig befülltes `EnrichedAnalysisResult`
für kmu/profi-Nutzer ohne Fehler. Layer 2 ist der einzige Wert-Beweis für bezahlte
Tiers — solange es defekt ist, gibt es kein KMU-Wertversprechen.

---

## Problem
Das gesamte Layer-2-Subsystem liefert aktuell falsche oder unvollständige Ergebnisse.
Alle vier Module sind als fehlerhaft klassifiziert (Observed):

| Modul | Status |
|---|---|
| `src/layer2/marketDataResolver.ts` | ⚠️ Fehlerhaft |
| `src/layer2/marketDataInterpreter.ts` | ⚠️ Fehlerhaft |
| `src/layer2/knowledgeGraph.ts` | ⚠️ Fehlerhaft |
| `src/layer2/realityScore.ts` | ⚠️ Fehlerhaft |

Die Fehlerursache ist undiagnostiziert. Kein Fix darf vor Diagnose beginnen.

---

## Affected Repos
- `negotiationcoach-backend` — alle Änderungen und die Diagnose
- `shared-context` — Diagnose-Report (`docs/delivery/layer2-diagnosis-plan.md`)
  und `source-of-truth-matrix.md` Update nach Abschluss

---

## Scope

### Step A — Diagnose (PLAN ONLY, NO CODE CHANGES)
Lokalisiere die Fehlerursache in `enrichWithMarketData()` anhand folgender Pfade:

1. `marketDataResolver.ts` — trifft die Cache-vs-Miss-Entscheidung korrekt?
2. `knowledgeGraph.ts` — liest/schreibt der Supabase-Cache ohne Fehler?
3. `marketDataInterpreter.ts` — antwortet Claude API Tool Use korrekt?
4. `realityScore.ts` — werden Inputs korrekt aus `AnalysisResult` extrahiert?
5. `EnrichedAnalysisResult` — welche Output-Felder sind null/undefined?

Klassifiziere jede Aussage als Observed / Inferred / Missing.
Output: `docs/delivery/layer2-diagnosis-plan.md` in shared-context.

### Step B — Fix (nach Diagnose, Scope kann sich anpassen)
Fix in den identifizierten Modulen aus Step A.
Richtet sich nach dem Diagnoseergebnis — Scope hier ist ein Rahmen, kein Vollumfang:
- `marketDataResolver.ts` und/oder `marketDataInterpreter.ts`
- `knowledgeGraph.ts` (Cache-Fehler, falls gefunden)
- `realityScore.ts` (Input-Extraktion, falls fehlerhaft)
- `src/layer2/index.ts` — `enrichWithMarketData()` Orchestrierung falls nötig

Nach Fix:
- `source-of-truth-matrix.md` — Layer-2-Status von ⚠️ auf ✅ aktualisieren
- `docs/audits/refactor-backlog.md` — NC-L2-FIX als DONE schließen

---

## Non-goals
- Kein Austausch von `marketDataInterpreter.ts` durch externe Marktdaten-API
  (nutzt Claude-Trainingsdaten — strukturell veraltet, kein Fix in R-2026-05)
- Keine Layer-1-Änderungen (AnalysisResult bleibt unverändert)
- Keine Frontend-Änderungen
- Kein ADR-007 / Dual Layer 1 (separate Entscheidung, deferred)
- Kein Telemetrie-Setup (Wave 2 Backlog)
- Keine neuen API-Endpunkte

---

## Acceptance Criteria

### Step A
- [ ] Diagnose-Report `docs/delivery/layer2-diagnosis-plan.md` erstellt
- [ ] Fehlerursache für jeden der 4 Module als Observed / Inferred / Missing klassifiziert
- [ ] Mindestens eine Root Cause als Observed identifiziert

### Step B
- [ ] `enrichWithMarketData()` gibt `EnrichedAnalysisResult` mit befüllten Feldern zurück
      (kein null/undefined auf `marketData`, `realityScore`, `summary`)
- [ ] Manueller Live-Test: ein kmu/profi-Nutzer mit bekanntem Input erhält realityScore-Wert
- [ ] `npx tsc --noEmit` in negotiationcoach-backend: 0 Fehler
- [ ] Layer-1-Regression: `POST /api/analyze` für free/privat unverändert funktionsfähig
- [ ] `source-of-truth-matrix.md` Layer-2-Status aktualisiert

---

## Telemetry / Measurement

**Gap (UNKNOWN):** Kein produktives Telemetrie-Setup vorhanden. Layer-2-Fehlerrate
kann nicht automatisch gemessen werden.

**Ersatz-Verifikation für R-2026-05:**
- Manueller Live-Test mit echtem kmu/profi-User-Token gegen Backend API
- `EnrichedAnalysisResult`-Felder per `console.log` / Render.com logs verifiziert

Telemetrie-Setup ist Wave-2-Backlog (NC-TELEMETRY).

---

## Risks / Open Questions

| Risk | Severity | Mitigation |
|---|---|---|
| Fehlerursache unbekannt — Diagnose könnte Scope von Step B erheblich verändern | High | Step A zuerst, kein Fix ohne Diagnose-Report |
| `marketDataInterpreter.ts` nutzt Claude-Trainingsdaten, nicht externe API — Marktdaten können veraltet sein | Medium | Strukturell akzeptiert für R-2026-05; ADR für externe API-Integration ist Wave-3-Kandidat |
| Keine automatisierten Assertions in bestehenden tests/layer2/ Tests | Medium | Manuelle Verifikation als AC-Ersatz; Test-Assertions als Follow-up |
| Render.com-Umgebungsvariablen (ANTHROPIC_API_KEY, SUPABASE_SERVICE_KEY) für Live-Test erforderlich | Low | Sind in Render.com-Deployment bereits gesetzt |

---

## Architecture references
- `docs/wiki/WIKI---Repo-Profile-negotiationcoach-backend.md` — Layer-2-Modul-Status
- `docs/delivery/wave2-scope.md` — Step 2 (Layer-2-Diagnose) und Step 3 (Layer-2-Fix)
- `docs/decision-log/ADR-001-system-boundaries.md` — Backend kanonischer Layer-2-Execution-Path
- `docs/decision-log/ADR-002-data-ownership.md` — Schreib-Pfad nach DB
