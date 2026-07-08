# ADR-010 — NC-L3-SIM Intake-Strategie: dynamischer LLM-Intake vs. statische SML-Bibliothek

**Status:** DECIDED
**Datum:** 2026-07-08
**Entscheider:** Maik Figur

## Kontext

NC-L3-SIM (Design: `docs/features/layer3-simulation.md`) redesigned die Layer-3-Simulations-Engine und weicht dabei vom ursprünglichen ENGB01-Blueprint ab: statt einer statischen `ScenarioObject`-Bibliothek mit vordefinierten `ai_opponent.tactics`/`fallback_position`-Feldern nutzt das Design einen dynamischen LLM-Intake, der das Szenario zur Laufzeit aus der bestehenden Nego-Session ableitet und fehlende Informationen per gezielter Rückfrage ergänzt (Design-Doc Abschnitt 6, "ENGB01-Blueprint-Konformität", dort bereits als "empfohlen, nicht blockierend" für eine formale ADR vorgemerkt).

Phase 1 (`smlParser.ts`, commit `c00e719`) und Phase 2 (`debriefEngine.ts`, commit `2f163c8`) sind bereits implementiert und Task-Review-approved — beide bauen bereits auf dem dynamischen-Intake-Datenmodell auf (`ScenarioObject.intake_complete`, `clarifying_questions_asked`, `buildScenarioObject(intakeResult, ...)`). Vor Phase 3 (`simulationRoutes.ts` — erste echte Intake-Orchestrierung, erster LLM-Call) soll die Strategie formal entschieden sein, statt implizit durch bereits geschriebenen Code festzustehen.

## Entscheidungsfrage

Soll NC-L3-SIM das Verhandlungsszenario für die Simulation (a) dynamisch per LLM-Intake aus der realen Nego-Session ableiten, (b) aus einer statischen, kuratierten Szenario-Bibliothek beziehen, oder (c) einen Hybrid aus beidem nutzen?

## Optionen

| Kriterium | A: Dynamischer LLM-Intake | B: Statische SML-Bibliothek | C: Hybrid (Template + dynamische Lückenfüllung) |
|---|---|---|---|
| Beschreibung | Szenario wird zur Laufzeit aus der Nego-Session + gezielten LLM-Rückfragen abgeleitet, kein vordefiniertes Set | Vordefinierte `ScenarioObject`-Bibliothek (Original-ENGB01-Blueprint), Nutzer wählt aus kuratierten Szenarien statt Freitext | Grobe kuratierte Basis-Templates pro `negotiation_type`, Feinwerte (BATNA, Deadline, Ziele) weiterhin dynamisch aus Session/Intake |
| Aufwand | Mittel — Intake-Loop + Extraction-Parsing (Phase 3) | Hoch — Bibliothek muss inhaltlich kuratiert und gepflegt werden | Mittel-Hoch — beide Systeme + Auswahl-Logik nötig |
| Risiko | Mittel — LLM-Extraktion kann fehlschlagen (bekanntes Muster, Lesson 2026-06-19: user-only messages + 3-Tier-Regex-Fallback nötig) | Niedrig technisch, aber geringerer Realismus (Szenario passt nie exakt zur echten Session-Situation) | Mittel — Komplexität durch zwei parallele Pfade |
| ADR-/Blueprint-Konformität | Weicht vom ENGB01-Blueprint ab (Begründung: Design-Doc Abschnitt 6) | Volle Blueprint-Konformität | Teilweise |
| Reversibilität | — | Niedrig — Phase 1+2 sind bereits exakt auf Option A zugeschnitten; ein Wechsel würde diese Arbeit größtenteils verwerfen | Mittel — Template-Layer wäre Zusatzarbeit auf Option-A-Fundament, kein Verwurf |
| Produkt-Fit | Passt zu `product/strategy.md`: kein belegter Nutzer-Bedarf für Szenario-Bibliothek (Marketplace explizit "kein aktiver Nutzer-Bedarf") | — | Overkill ohne belegten Bedarf |
| Empfehlung | ✅ | ❌ | Vorgemerkt als spätere Erweiterung, nicht jetzt |

## Entscheidung

**Option A — dynamischer LLM-Intake.**

Formalisiert den bereits in Phase 1+2 implementierten Ansatz. `ScenarioObject` bleibt ein zur Laufzeit befülltes Objekt (Intake-Ergebnisse + Layer-1/2-Snapshot), keine statische Bibliothek.

**Option C (Hybrid) wird explizit als möglicher späterer Schritt vorgemerkt, nicht verworfen.** Trigger-Bedingung für eine Revision dieser ADR: entweder (a) Telemetrie/Nutzer-Feedback zeigt, dass der offene Intake-Dialog eine signifikante Abbruch-Hürde ist (vgl. `simulation_abandoned`-Event, Design-Doc Abschnitt 8), oder (b) eine konkrete Produkt-Anforderung nach kuratierten Übungsszenarien entsteht (aktuell laut `product/strategy.md` nicht belegt). Ohne einen dieser Trigger bleibt Option A der alleinige Ansatz — kein spekulativer Vorbau.

## Konsequenzen

- `smlParser.ts`/`buildScenarioObject` (Phase 1) und `debriefEngine.ts` (Phase 2) benötigen **keine** Anpassung — sie waren bereits konform mit dieser Entscheidung.
- Phase 3 (`simulationRoutes.ts`) implementiert den Intake-Dialog als LLM-Rückfrage-Loop, nicht als Szenario-Auswahl-UI.
- Kein neues DB-Schema für eine Szenario-Bibliothek nötig (spart die in Option B/C sonst anfallende Kurations-/Pflege-Infrastruktur).
- Das ENGB01-Blueprint gilt für NC-L3-SIM als bewusst und dokumentiert abgewichen, nicht als unvollständig umgesetzt.
- Bei Aktivierung von Option C in einer späteren Iteration: neue ADR (Nachfolger dieser ADR) statt stillschweigender Erweiterung, da sich das Datenmodell (`ScenarioObject`) und der Intake-Flow ändern würden.

## Betroffene Items

- NC-L3-SIM (Phase 1 ✅, Phase 2 ✅, Phase 3 offen — direkt betroffen)
- NC-MARKETPLACE (Idea, kein aktiver Bedarf) — falls je aktiviert, wäre das der wahrscheinlichste Auslöser für eine Revision Richtung Option C
