# Wave 2 — Scope & Delivery-Sequenz

**Erstellt:** 2026-04-17
**Status:** Proposed — noch nicht freigegeben
**Basis:** Initial Setup Baseline (`docs/delivery/initial-setup-baseline.md`)
**Projekt:** NegotiationCoach AI — Feature Delivery Controller

---

## Voraussetzungen für Wave-2-Start

Folgende Bedingungen müssen erfüllt sein, bevor Feature-Delivery beginnt:

- [ ] ADR-007 erstellt und entschieden (VG-06-Entscheidung: EF engine retire / migrate / adapter)
- [ ] Layer-2-Diagnose durchgeführt (Fehlerursache in marketDataResolver/marketDataInterpreter bekannt)
- [ ] `docs/delivery/layer2-diagnosis-plan.md` erstellt

Ohne ADR-007 darf keine Implementierungsarbeit an Layer-2-Fix, Layer-3 oder EF-Pfad beginnen.

---

## Start-Gate — Sofort auszuführen

### Step 1 — ADR-007 erstellen (VG-06-Entscheidung)

**Klassifizierung:** Architecture Decision
**Priorität:** Blocker — Wave-2-Start-Gate
**Tool:** Claude Code in `shared-context`
**Repos betroffen:** shared-context (Dokument), negotiationcoach-backend (Umsetzung)

**Entscheidungsfrage:**
Was passiert mit der Edge Function `_shared/engine/` (doppelte Layer-1-Implementierung)?

| Option | Beschreibung | Auswirkung |
|---|---|---|
| A — Retire | EF engine löschen, EF delegiert an Railway | Sauberste Lösung, erfordert EF-Umbau |
| B — Migrate | EF engine an Railway-Schema anpassen | Mittlerer Aufwand, zwei Implementierungen bleiben kurzfristig |
| C — Adapter | Schema-Adapter an EF-Boundary | Geringster Aufwand, versteckt das Problem |

**Deferral-Regeln bis ADR-007 entschieden:**
- Keine neue Logik in Edge Function engine path
- EF batnaDetector.ts bleibt undeployed
- Railway Layer-1 ist kanonischer Execution-Path

**Spawns:** RFB-006-Umsetzung, RFB-026-Reparatur

---

### Step 2 — Layer-2-Diagnose

**Klassifizierung:** Bug — höchste Priorität
**Tool:** Claude Code in `negotiationcoach-backend`
**Repos betroffen:** negotiationcoach-backend (Diagnose + Fix)

**Betroffene Dateien:**
- `src/layer2/marketDataResolver.ts` — Cache vs. Web-Search-Entscheidungsweg
- `src/layer2/marketDataInterpreter.ts` — Claude API Tool Use für Marktdaten
- `src/layer2/knowledgeGraph.ts` — Supabase Cache Read/Write
- `src/layer2/realityScore.ts` — Abweichungsberechnung
- `src/layer2/index.ts` — `enrichWithMarketData()` Orchestrierung

**Diagnosepfad (Proposed):**
```
1. marketDataResolver: Trifft Cache-vs-Miss-Entscheidung korrekt?
2. knowledgeGraph: Liest/schreibt Cache ohne Fehler?
3. marketDataInterpreter: Antwortet Claude API Tool Use korrekt?
4. realityScore: Berechnet Abweichung korrekt?
5. EnrichedAnalysisResult: Output-Felder vollständig befüllt?
```

**Prompt-Vorlage für Diagnose:**
```
PLAN ONLY. DO NOT CHANGE CODE YET.

Context:
- Repo: negotiationcoach-backend
- Problem: Layer 2 enrichWithMarketData() liefert falsche Ergebnisse
- Betroffene Dateien: marketDataResolver.ts, marketDataInterpreter.ts,
  knowledgeGraph.ts, realityScore.ts, layer2/index.ts

Ziel: Fehlerursache lokalisieren. Kein Fix in diesem Schritt.

Analysiere:
1. Welcher Pfad wird bei Cache-Miss tatsächlich ausgeführt?
2. Gibt es unbehandelte Fehler in den Claude API Tool-Use-Calls?
3. Werden realityScore-Inputs korrekt aus AnalysisResult extrahiert?
4. Welche Felder in EnrichedAnalysisResult sind null/undefined?

Klassifiziere jede Aussage als Observed / Inferred / Missing.
Kein Code-Fix. Nur Diagnose-Report.
```

**Output:** `docs/delivery/layer2-diagnosis-plan.md` in shared-context

---

## Wave-2-Delivery-Sequenz

Nach Abschluss der Start-Gates folgt diese geordnete Reihenfolge. Kein Schritt beginnt, bevor der vorherige abgeschlossen und verifiziert ist.

### Step 3 — Layer-2-Fix

**Klassifizierung:** Bug Fix
**Abhängigkeit:** Step 2 (Diagnose abgeschlossen)
**Tool:** Claude Code in `negotiationcoach-backend`
**Tier-Auswirkung:** KMU, Profi
**ADR-Referenz:** ADR-001 (Railway kanonisch), ADR-002 (Schreib-Pfad)

**Scope (nach Diagnose zu verfeinern):**
- Fix in `marketDataResolver.ts` oder `marketDataInterpreter.ts` (oder beide)
- Regression-Tests für `enrichWithMarketData()` mit bekannten Inputs
- Verifikation `EnrichedAnalysisResult`-Felder vollständig befüllt
- `source-of-truth-matrix.md` — Entity Layer-2-Status updaten

**Pflichtartefakte:**
- Change Summary
- Betroffene Dateien
- Test-Ergebnisse
- Docs-Updates

---

### Step 4 — RFB-006: Layer-1-Unification

**Klassifizierung:** Architecture / Refactoring
**Abhängigkeit:** ADR-007 entschieden (Step 1)
**Tool:** Claude Code in `negotiationcoach-backend`
**Repos betroffen:** negotiationcoach-backend (EF + Node.js)

**Scope (abhängig von ADR-007-Option):**
- Option A (Retire): `supabase/functions/_shared/engine/` löschen, EF delegiert an Railway-Endpunkt
- Option B (Migrate): EF engine auf Railway-Schema (`own_target/own_minimum`) migrieren
- Option C (Adapter): Schema-Adapter an EF-Boundary einbauen

**Verifikation:**
- `npx tsc --noEmit` clean
- Layer-1-Tests gegen kanonisches Schema
- `bounded-contexts.md` BC-02 CRIT-01 als resolved markieren
- `source-of-truth-matrix.md` Entity 5 updaten
- `frontend-backend.md` Type Drift Register updaten (CRITICAL DRIFT schließen)

---

### Step 5 — RFB-026: batnaDetector EF Reparatur

**Klassifizierung:** Bug Fix
**Abhängigkeit:** Step 4 (RFB-006) abgeschlossen
**Tool:** Claude Code in `negotiationcoach-backend`
**Repos betroffen:** negotiationcoach-backend (EF)

**Scope:**
- Import-Pfad in `supabase/functions/_shared/engine/batnaDetector.ts` reparieren
- `NegotiationTier` auf `'free'` erweitern
- Schema an Node.js-Kopie angleichen (oder löschen, falls Option A in ADR-007)
- Deno type check
- `docs/dead-code-candidates.md` DCC-EF-01 auflösen

---

### Step 6 — Layer-3-Vorbereitung

**Klassifizierung:** Feature / Architecture
**Abhängigkeit:** Step 3 (Layer-2-Fix) abgeschlossen
**Tool:** Claude Code in `negotiationcoach-backend` (Planung), dann Implementierung
**Tier-Auswirkung:** Privat (Basis), KMU (Mittel), Profi (Voll)

**Dateien zu implementieren (aus ENGB01, Interfaces bereits definiert):**
- `src/layer3/smlParser.ts` — SML-Format parsen
- `src/layer3/promptBuilder.ts` — Simulations-Prompts aufbauen
- `src/layer3/simulationLoop.ts` — Simulations-Schleife
- `src/layer3/opponentEngine.ts` — KI-Gegner
- `src/layer3/debriefEngine.ts` — Debrief-Auswertung
- `src/layer3/index.ts` — Orchestrierung

**Voraussetzung vor Implementierung:**
- `docs/features/layer3-simulation.md` in shared-context erstellen (aus ENGB01 ableiten)
- ADR für Layer-3-API-Endpunkte (Proposed: POST /api/simulate, POST /api/debrief)

---

### Step 7 — RFB-020: Index.tsx Dekompositon

**Klassifizierung:** Refactoring / UX
**Abhängigkeit:** kein Blocker
**Tool:** Lovable in `negotiation-buddy`
**Priorität:** P3 — kann parallel zu anderen Steps laufen

**Scope:**
- `src/pages/Index.tsx` (~929 Zeilen) in logische Sub-Komponenten aufteilen
- Keine funktionale Änderung
- `tsc --noEmit` clean nach Änderung

---

### Step 8 — Feature-Docs: Layer-3 / Scenario Marketplace / PDF Export

**Klassifizierung:** Documentation
**Abhängigkeit:** Step 6 gestartet
**Tool:** Claude Code in `shared-context`

**Zu erstellende Dokumente:**
- `docs/features/layer3-simulation.md`
- `docs/features/scenario-marketplace.md`
- `docs/features/pdf-export.md`

---

### Step 9 — RFB-032: Stripe Webhook Handler

**Klassifizierung:** Feature / Infrastructure
**Abhängigkeit:** Stripe live geschaltet
**Tool:** Claude Code in `negotiationcoach-backend`
**Status:** Deferred — kein Handlungsbedarf bis Stripe-Entscheidung

**Wenn Stripe live:**
- `POST /api/webhooks/stripe` implementieren
- Schreibt `subscription_tier` (Railway Tier-Werte) in Supabase `user_profiles`
- Schreibt `app_metadata.tier` in Supabase Auth JWT
- Webhook-Secret-Verifikation zwingend
- RFB-032 in refactor-backlog.md schließen

---

## Abhängigkeitsgraph

```
ADR-007 (Step 1) ─────────────────┐
                                   ↓
                              RFB-006 (Step 4)
                                   ↓
                              RFB-026 (Step 5)

Layer-2-Diagnose (Step 2) ────────┐
                                   ↓
                              Layer-2-Fix (Step 3) ──────┐
                                                          ↓
                                                   Layer-3-Prep (Step 6)
                                                          ↓
                                                   Feature-Docs (Step 8)

RFB-020 (Step 7) ──── kein Blocker, parallel möglich

RFB-032 (Step 9) ──── Deferred, Stripe-abhängig
```

---

## Pflichtartefakte bei jedem Step

Bei jedem Step ist vor Freigabe zu prüfen:

- [ ] `npx tsc --noEmit` clean
- [ ] `npm test` bestanden (oder bekannte Broken-Tests dokumentiert)
- [ ] Relevante Docs in shared-context aktualisiert
- [ ] `refactor-backlog.md` Item geschlossen oder Status aktualisiert
- [ ] `close-task`-Skill ausgeführt
- [ ] Commit-Message beschreibt "why", nicht nur "what"

---

## Noch nicht in Wave 2 — Backlog für Wave 3+

| Feature | Grund |
|---|---|
| Knowledge Pipeline | ADR-016a erforderlich vor Implementierung |
| Scenario Marketplace UI | Abhängig von Layer-3-Abschluss |
| PDF Export (vollständig) | Abhängig von Profi-Tier-Fertigstellung |
| Guest Mode (vollständig) | Abhängig von Layer-3-Simulation |

---

*Dieses Dokument ist nach Abschluss jedes Steps zu reviewen und ggf. zu aktualisieren.*
