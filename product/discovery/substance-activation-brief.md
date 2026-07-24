# Delivery Brief (Draft) — Substance Activation

**Zweck:** Release-Klammer, die bereits implementierte quantitative Substanz
(Layer 1 + Layer 3) im Hauptpfad sichtbar und erklärt macht.
**Rolle bei Erstellung:** Planung, read-only. Keine Code-Änderungen in
negotiationcoach-backend oder negotiation-buddy vorgenommen. Ausführung nur in
shared-context.
**Grundlage:** `product/discovery/content-inventory-backend.md` (Commits
`fcfaadd` + `6304a94`), plus eigene Laufzeit-Verifikation (dieses Dokument).
**Datum:** 2026-07-24
**Klassifikation je Aussage:** Observed | Inferred | Missing | Proposed — UNKNOWN
wo nicht verifizierbar.
**Sandbox-Hinweis:** Die `.env*`-Deny-Regel hat die Laufzeit-Verifikation nicht
blockiert für Lesezugriffe; ein Subagent musste für den lokalen Dev-Server-Start
+ curl-Aufrufe den Sandbox-Override nutzen (kein Dateizugriff auf `.env`, nur
Prozessstart + Netzwerk zu `localhost`). Kein Datei wurde in den
Implementierungs-Repos verändert (`git status --short` leer, verifiziert).

---

## 0. Zentraler Befund vorab

**Observed, wichtigste Einzelerkenntnis dieser Analyse:** Weder der aktive
Produktionspfad (Supabase EF `generate-plan`) noch der inaktive Backend-Pfad
(`POST /api/plan`) verbinden heute tatsächlich ZOPA/Nash/Monte-Carlo-Werte mit
dem, was der Nutzer liest:

- `generate-plan` (aktiv, deployed, Version 5) generiert den Plan rein
  konversationell aus Chat-Verlauf + `progress_status` — es ruft nirgends eine
  Analyse-Engine auf, es gibt keine ZOPA/Nash/Monte-Carlo-Werte, die es
  einspeisen könnte.
- `/api/plan` (inaktiv, kein Frontend-Caller) ruft `buildPlanSystemPrompt()` auf,
  die zwar ZOPA/Nash-Werte in Prosa einbetten *kann* — aber nur, wenn der Caller
  sie im Request-Body mitliefert. Der Handler ruft `analyzeNegotiation()` selbst
  **nicht** auf (Observed, empirisch bestätigt: Request ohne `zopaResult`/
  `analysis` → `200 OK` mit Platzhalter-Prosa, keine Zahlen).

**Konsequenz:** A-1 ist kein reiner Routing-Wechsel, sondern erfordert
zusätzlich, dass der Caller vor dem Plan-Aufruf eine Layer-1-Analyse auslöst und
deren Ergebnis mitgibt. Das ändert Aufwand und Scope von A-1 grundlegend
gegenüber der ursprünglichen Annahme "Plan-Pfad umstellen" — siehe Phase 1.1
und Phase 2.1.

---

## Phase 0 — Statusabgleich `product/`

| Maßnahme | Vorhandene ID / Brief? | Release-Zuordnung | Delivery Brief vorhanden? | Telemetrie |
|---|---|---|---|---|
| A-1 (Plan-Pfad-Umstellung) | **NEU** — RFB-034/DCC-BE-02 (Observed, `docs/audits/refactor-backlog.md`) verlangt nur *Annotation als Migrationsziel*, keine Umsetzung. ADR-005 hat die Zielarchitektur bereits entschieden (2026-04-11), aber nie ausgeführt. | Kein aktiver Release enthält es. R-2026-09 ist Released und geschlossen. | Nein | Fehlt — kein Event für "Plan enthält begründeten Layer-1-Wert" |
| A-2 (Framework-Namen-Regel) | **NEU** — kein ID/Brief irgendwo (Observed, Volltextsuche). | — | Nein | Fehlt |
| A-3 (`/api/simulate/*` ans Frontend) | **Effektiv bereits vorhanden** — explizit als NC-L3-SIM "Phase 6" / "Nicht in Scope (dieses Item)" vorgemerkt (Observed, `product/briefs/NC-L3-SIM.md` + `feature-register.md`). Kein eigenständige ID vergeben. | NC-L3-SIM ist "In Delivery" (R-2026-10 vorgemerkt, siehe unten). | Teilweise — als Folgephase von NC-L3-SIM angekündigt, kein eigener Brief. | Vorhanden (`tool_opened` deckt Simulation-Tools ab, sofern UI existiert) |
| A-4 (`market_median`-Herkunft kennzeichnen) | **Teilweise NEU** — NC-L2-FIX/NC-L2-UI (beide Released) haben `market_data_source` bereits in den `/api/enrich`-Contract aufgenommen, aber kein Item verlangt dessen UI-Anzeige. | R-2026-09 (geschlossen, deckt A-4 nicht ab). | Nein für die UI-Kennzeichnung. | Fehlt für "Nutzer hat Herkunft gesehen" |

### 0.1 Aktueller Release
**Observed.** `product/releases/current.md`: Release-ID `R-2026-09`, Status
"Released — Review: product/release-reviews/R-2026-09.md". R-2026-05 ist
historisch (NC-L2-FIX), nicht mehr offen.

### 0.2 NC-L3-SIM Status
**Observed, keine kritische Drift.** `roadmap.md` sagt "Phase 1/2 von 7"
(`c00e719`, `2f163c8`) — das ist der Stand vor der letzten Aktualisierung.
`feature-register.md` ist aktueller: **Phase 3/7 implementiert**, Commits
`c00e719` (Phase 1), `2f163c8` (Phase 2), `007a6ee`+`b5bf2d7` (Phase 3 —
Simulate-Routes + Opponent-Engine-L1-Grounding + Migration; Task-Review fand 5
Important Findings, gefixt, Re-Review Approved).

Die vom Auftrag befürchtete Drift ("nicht gestartet", "Design scoped", "GO
ausstehend") **existiert nicht** — beide Dokumente stimmen im Status "In
Delivery" überein, nur `roadmap.md` hinkt bei der Phasenzahl einen Schritt
hinterher (kosmetisch, kein Blocker).

**Bekannte, akzeptierte Lücke (Observed, `feature-register.md`):** kein
Produktionspfad setzt `tier='profi'` im JWT (kein Stripe-Webhook live) —
Endpoints nur mit manuell geseedetem Test-User erreichbar. Das betrifft A-3
direkt: selbst nach Frontend-Anschluss kann kein realer zahlender Nutzer den
Pfad heute erreichen.

### 0.3 Existierende IDs
Siehe Tabelle oben. Zusätzlich, load-bearing:

- **ADR-005** (`docs/decision-log/ADR-005-plan-generation-path.md`, Observed,
  wörtlich): *"Railway `POST /api/plan` is the canonical long-term path for
  plan generation. The Supabase Edge Function `generate-plan` is a temporary
  active path."* Konsequenz: *"`POST /api/plan` (Railway) must NOT be removed
  ... `generate-plan` Edge Function will be retired when the frontend migrates
  to Railway `/api/plan` (scoped under RFB-004 or a successor item)."*
  → A-1 braucht **kein neues ADR** — es setzt eine bereits getroffene
  Entscheidung um, die nie ausgeführt wurde.
- **docs/contracts/frontend-backend.md** zu `/api/plan` ist veraltet: es
  formuliert noch *"Decision required before Release 1: deprecate backend
  `/api/plan` or migrate Edge Function call"* — obwohl ADR-005 diese
  Entscheidung bereits getroffen hat (migrate, nicht deprecate). Docs-Drift,
  siehe Phase 2.2.
- **`/api/simulate/*` fehlt komplett** in `docs/contracts/frontend-backend.md`
  (Observed) — obwohl NC-L3-SIMs eigenes Akzeptanzkriterium AC-7 verlangt,
  dass der Contract die drei neuen Endpoints enthält. Dieses AC ist aktuell
  **nicht erfüllt**, trotz "In Delivery"-Status von Phase 3.

### 0.4 Release-Zuordnung
**Empfehlung (Proposed):** Substance Activation braucht einen eigenen Release,
kein Anhängen an R-2026-09 (bereits Released/geschlossen) und keine Vermischung
mit NC-L3-SIM (eigener, laufender Scope mit eigenem Phasenplan). Ein neuer
Release `R-2026-1x` mit A-1, A-2, A-4 als Kern-Scope; A-3 bleibt organisatorisch
Teil von NC-L3-SIM (Phase 6), sollte aber im selben Zeitfenster geplant werden,
weil beide denselben `apiClient.ts`-Bereich berühren (siehe 3.3).

### 0.5 Telemetrie
**Korrektur einer im Auftrag genannten Annahme (Observed, wichtig):** Die
Behauptung *"distinctId ist auf 'server' hardcodiert"* ist **nicht mehr
zutreffend** im aktuellen Code. `src/services/telemetry.ts:52-59` definiert
`trackEvent(event, properties, distinctId: string)` als Pflichtparameter; der
einzige Call-Site (`src/api/routes.ts:225-231`, `analyze_completed`) übergibt
`req.user!.id` als `distinctId` — nicht `'server'`. Das war offenbar ein
älterer Zustand, der im Rahmen von NC-TELEMETRY-C bereits behoben wurde, aber
nie explizit als "gefixt" vermerkt wurde (Docs-Drift, siehe Phase 4.5).

Trotzdem bleibt die Telemetrie für Substance Activation **unzureichend**:
keines der vier Events deckt "Nutzer hat einen Layer-1-/Layer-3-begründeten
Wert im Ergebnis gesehen" ab. Ohne neues Event lässt sich die Wirkung von A-1,
A-3, A-4 nicht messen. **Missing** — Empfehlung: neues Event
`plan_grounded_in_analysis` (o.ä.) als Teil des A-1-Delivery-Briefs vormerken.

---

## Phase 1 — Laufzeit-Verifikation

### 1.1 Funktioniert `/api/plan`?

**Observed, empirisch verifiziert** (lokaler Dev-Server, Port 3001,
`nodemon --exec ts-node src/api/routes.ts`):

- Route: `src/api/routes.ts:109-144`, geschützt durch
  `authMiddleware, validateBody(PlanRequestSchema)`. Code-Kommentar direkt über
  der Route (Zeilen 104-107, Observed, wörtlich): *"NOT currently called by the
  frontend — active path is the Supabase Edge Function generate-plan ... DO
  NOT REMOVE until RFB-004 Phase C frontend migration is complete."*
- Ohne Bearer-Token: `401`,
  `{"error":{"code":"AUTH_ERROR","message":"Nicht authentifiziert","statusCode":401}}`.
- Mit gültigem JWT, Body **ohne** `zopaResult`/`analysis`: `200 OK`, vollständiger
  Plan, aber Platzhalter-Prosa ("kein Minimalziel ... vorliegen") — **beweist**,
  dass der Handler `analyzeNegotiation()` nicht selbst aufruft, sondern nur
  weiterreicht, was mitgeliefert wird (`planHelpers.ts:1-31`, liest nur
  `zopaResult?.zopa_exists/.zopa_min/.zopa_max/.nash_solution`,
  `analysis?.strategy_score`).
- Response-Shape (Observed, vollständig): `summary`, `situationAnalysis`,
  `opening`, `objections[]`, `recommendations[]`, `nextStep`. **Keine**
  strukturierten Felder wie `zopaExists`, `zopaMin/Max`, `nashSolution`,
  `numbers.*`, `_debug.model` — ZOPA/Nash-Zahlen erscheinen nur als Prosa
  innerhalb von `summary`/`situationAnalysis`, nie maschinenlesbar.

**Ergebnis:** `/api/plan` ist erreichbar und funktioniert als reiner
Prompt-Formatter, ist aber **keine Analyse-Pipeline**. A-1 ist ein
Reparatur-/Verdrahtungs-Task, kein reiner Routing-Wechsel (siehe Phase 0,
zentraler Befund, und Phase 2.1).

### 1.2 Funktioniert `/api/simulate/{start,turn,debrief}`?

**Observed, vollständig durchlaufen** (profi-Tier-JWT via
`scripts/lib-jwt.sh`):

1. `POST /api/analyze` → `200`, echtes Layer-1-Ergebnis
   (`zopa_exists:true, zopa_min:58000, zopa_max:62000, nash_solution:65000,
   monte_carlo_p50:60011.43, monte_carlo_p90:61596.11, strategy_score:47`).
2. `POST /api/simulate/start {session_id}` → `201`, echter DB-Write in
   `simulation_sessions`.
3. Drei `POST /api/simulate/turn`-Aufrufe (Intake, Gegenangebot,
   Fait-accompli) → jeweils `200`, Angebotsverfolgung korrekt
   (58000 → 58800 → 59400).
4. `POST /api/simulate/debrief` → `200`, vollständiges Debrief.

**Debrief-Felder (Observed, exakte Namen aus Live-Response):**
`deal_reached`, `final_offer`, `hidden_opponent_minimum`,
`hidden_opponent_target`, `final_vs_zopa_percentile`,
**`final_vs_nash_distance`** (5600), `final_vs_nash_direction`,
**`vs_monte_carlo_p50`**, **`vs_monte_carlo_p90`**,
**`concession_timeline`** (`[{turn:2, user_offer:62000}, {turn:3,
user_offer:60000, user_concession_pct:-3.23}]`), plus
`total_user/opponent_concession_pct`, `tactics_used_well/missed`,
`opponent_tactics_observed`, `key_mistakes`, `recommendations`,
`overall_score`. **Alle vier gefragten Konzepte vorhanden, mit exakten
Feldnamen, nicht nur semantisch ähnlich.**

Tier-Gate empirisch bestätigt: gleicher Call mit `privat`-JWT → `403`,
`{"error":{"code":"TIER_ERROR","message":"Dieses Feature erfordert Tier: profi","statusCode":403}}`.

`/api/opponent-simulation/*` bleibt unberührt: eigene Tabelle
(`opponent_simulation_sessions`), eigener Router, eigene Prompt-Logik
(`layer3/opponentEngine.ts`) — deckungsgleich mit der Brief-Aussage "bleibt
unverändert lauffähig (verifiziert byte-identisch)".

**Ergebnis:** Backend-seitig ist A-3 ein echter, einfacher Routing-/
Verdrahtungs-Task — die einzige offene Lücke ist die bereits unter 0.2
dokumentierte fehlende Produktions-JWT-Tier-Auflösung (`profi` ohne Stripe).

### 1.3 Deployter Stand `generate-plan` vs. Repo

**Observed**, per `get_edge_function` (Projekt `gpllrgkuozytyrmpfwbb`, Slug
`generate-plan`, Status ACTIVE, Version 5, `verify_jwt: true`) abgeglichen:

- Framework-Namen-Regel **bestätigt vorhanden**, wörtlich zweimal im Prompt:
  *"Keine Framework-Namen (Harvard, BATNA etc.), nur Alltagssprache."* und in
  der Feldbeschreibung von `summary`: *"Keine Framework-Namen."* Das bestätigt
  A-2s Prämisse direkt am deployten Artefakt, nicht nur im Repo.
- Tier-Ermittlung: `persona_type` aus `user_profiles` → Mapping
  `pro→profi, kmu→kmu, private→privat, else→free`. Laut ADR-006 ist das die
  separate, gültige Funktion `personaTypeToTier()` (nicht die
  `subscription_tier`-Mapping, die ADR-006 primär regelt) — **kein Widerspruch
  zu ADR-006**, aber dieselbe Datenquelle (`user_profiles.persona_type`), die
  in BUG-20260719 (signup-trigger-tier-mismatch, **Status: DONE**, gefixt
  2026-07-21) fehlerhaft war. Der Fix betraf den Trigger, der `persona_type`
  setzt — nicht den EF-Code selbst. Das reduziert das Risiko für A-2, macht es
  aber nicht auf null: **Missing** — ob die drei anderen tier-lesenden EFs
  (`analyze-progress`, `summarize-session`, `analyze-document`) denselben
  Bugfix-Bedarf hatten, wurde in BUG-20260719 nie geprüft (offene
  Verifikationslücke, außerhalb dieses Scopes).
- Tier-Gate im EF-Code selbst: **"Present, inactive — commented stub"**
  (Observed, `docs/contracts/frontend-backend.md:712-713`). Für A-2 relevant,
  falls die Terminologie-Regel tier-abhängig gesteuert werden soll (P-1) —
  die Infrastruktur dafür (Tier bereits aufgelöst) existiert, der Gate-Stub
  ist nur nicht aktiviert.

### 1.4 Herkunft von `market_median`

**Observed, eindeutig geklärt — LLM-Schätzung, keine externe Quelle:**

- `src/layer2/marketDataResolver.ts:1-41`: für `tier` in
  (`privat`,`free`) sofortiger Short-Circuit zu `{source:'none', data:null}`.
  Sonst Supabase-Cache-Check (`knowledgeGraph.ts`), bei Cache-Miss Aufruf von
  `searchMarketData()`.
- `src/layer2/marketDataInterpreter.ts:37-105`: `claude.messages.create({
  model: MODELS.SONNET, tools:[{name:'extract_market_data'}],
  tool_choice:{type:'tool', name:'extract_market_data'} })`. System-Prompt
  wörtlich (Zeile 62): *"Nutze dein aktuellstes Wissen über typische Werte."*
  **Keine** Web-Search-Tool-Definition, kein HTTP-Call an eine externe
  Markt-API, keine statische Lookup-Tabelle. Code-Kommentar bestätigt die
  Grenze selbst: *"Known limitation: unit consistency (annual vs. monthly)
  relies on the prompt — not enforced at runtime."*
- Ergebnis-Zuweisung: `median: input.median` (aus dem geparsten
  Tool-Use-Response), dann `market_median: marketData.median`
  (`src/layer2/index.ts:96`), in Supabase gecacht.

**Definitive Aussage:** `market_median` ist eine LLM-generierte Schätzung aus
Claudes parametrischem Wissen (erzwungener Tool-Call, keine Recherche
angeschlossen), gecacht, **nicht** aus einer echten Markt-API und **nicht**
hardcodiert. Das ist direkt entscheidungsrelevant für P-2.

---

## Phase 2 — Design Gate

### A-1 — Plan-Pfad-Umstellung

**2.1 Datenfluss:** Aktuell läuft die Kette
`Chat-Fortschritt → generate-plan EF → Nutzer` ohne Analyse-Engine dazwischen.
Damit A-1 tatsächlich Substanz liefert, muss die Kette werden:
`Chat-Fortschritt → /api/analyze (Layer 1) → /api/plan (mit zopaResult+analysis
im Body) → Nutzer`. **Missing (zu klären vor Umsetzung, nicht in diesem Scope
gelöst):** Ruft das Frontend `/api/analyze` heute bereits automatisch bei
Abschluss der 6 Fortschrittspunkte auf (z. B. im Rahmen von NC-PLAN-FIX), oder
nur bei manuellem Öffnen von `ZopaCalculator`/`WhatIfSimulator`/
`StrategyGenerator`? Die Telemetrie-Events (`tool_opened` für diese drei Tools)
deuten auf manuellen Trigger hin, nicht automatischen — das ist Inferred, nicht
Observed, und muss vor der A-1-Implementierung geklärt werden, sonst entsteht
ein zusätzlicher, unsichtbarer `/api/analyze`-Call im Plan-Trigger-Pfad mit
eigenem Fehlerflächen-Risiko (Latenz, Kosten, Tier-Gates auf `/api/analyze`).

**2.2 Typ-/Vertragsänderungen:** `docs/contracts/frontend-backend.md` ist auf
`/api/plan` bereits veraltet (formuliert "Decision required", obwohl ADR-005
das entschieden hat) — muss vor oder mit A-1 aktualisiert werden. `apiClient.ts`
braucht einen neuen oder reaktivierten `generatePlan()`-Call gegen
`/api/plan` statt gegen die EF; laut ADR-005 existiert der Wrapper bereits als
totes, absichtlich erhaltenes Code-Ziel.

**2.3 Fehlerfälle:** Was passiert, wenn `analyzeNegotiation()` fehlschlägt
oder ZOPA nicht existiert (`zopa_exists:false`)? `planHelpers.ts` degradiert
bereits sauber zu Platzhalter-Prosa (empirisch bestätigt) — das ist ein
brauchbarer Fallback, muss aber explizit als Akzeptanzkriterium festgehalten
werden ("Plan bleibt nutzbar auch ohne ZOPA"), sonst könnte die Umsetzung das
stillschweigend anders lösen (z. B. Plan-Generierung ganz abbrechen).

**2.4 ENGB01:** Keine neue Business-Logik in der Edge Function nötig — A-1
verschiebt den Pfad zum Backend (Engine-Layer), das ist ENGB01-konform;
`generate-plan` EF wird dünner (irgendwann obsolet, siehe 3.4), nicht dicker.

### A-2 — Framework-Namen-Regel

**2.1** Kein neuer Datenfluss, nur Prompt-Textänderung in `generate-plan`
(oder in `buildPlanSystemPrompt`, falls A-1 zuerst kommt — Reihenfolge-Frage,
siehe Phase 4.1).

**2.2** Kein Contract-Impact — reine Textänderung im LLM-Output, keine
Schema-Änderung.

**2.3** Fehlerfall: falls tier-abhängig gesteuert (P-1), muss der
`else→'free'`-Fallback im Tier-Mapping (Phase 1.3) sauber auf "keine
Framework-Namen" abbilden, sonst sehen `free`-Nutzer versehentlich
Fachbegriffe, die für ihr Tier nicht vorgesehen sind.

**2.4** ENGB01: n/a (reine Prompt-Textänderung).

### A-3 — Layer-3-Debrief ans Frontend

**2.1** Datenfluss backend-seitig vollständig funktionsfähig (Phase 1.2).
Frontend-seitig: neue Komponente(n) analog `OpponentSimulator.tsx`, aber gegen
`/api/simulate/*` statt `/api/opponent-simulation/*`. Kein bestehender Caller.

**2.2** `docs/contracts/frontend-backend.md` muss um die drei neuen Endpoints
ergänzt werden — das ist bereits ein offenes, nicht erfülltes
Akzeptanzkriterium von NC-L3-SIM selbst (AC-7), unabhängig von A-3.

**2.3** Fehlerfälle bereits backend-seitig sauber (403 bei Tier-Unterdeckung,
empirisch bestätigt). Frontend muss diesen 403-Fall (Nicht-profi-Nutzer)
UI-seitig abfangen — insbesondere weil laut 0.2 aktuell **kein** Nutzer
produktiv `profi` via JWT erreicht (kein Stripe live). Ohne UI-Fallback zeigt
ein Feature-Release ein Feature, das niemand nutzen kann.

**2.4** ENGB01: konform, Logik bleibt im Backend.

### A-4 — `market_median`-Herkunft kennzeichnen

**2.1** Feld `market_data_source` existiert bereits im `/api/enrich`-Response
(`'web_search' | 'knowledge_graph' | 'none'`) — aber laut Phase 1.4 gibt es
aktuell **keinen** `'web_search'`-Pfad im Code; nur LLM-Schätzung
(am ehesten unter `'knowledge_graph'` oder einem vierten, fehlenden Wert
einzuordnen — **Missing**, muss geprüft werden, welchen Source-Wert der
LLM-Schätzungspfad tatsächlich zurückgibt, das wurde in Phase 1.4 nicht
explizit verifiziert). Reine UI-Anzeige-Ergänzung, kein neuer Backend-Call
nötig.

**2.2** Contract-Feld existiert, aber die Bedeutung von `market_data_source`
muss präzisiert werden — aktuell suggeriert `'web_search'` eine echte
Recherche, die es laut Phase 1.4 nicht gibt. Das ist mehr als reine
UI-Arbeit: **entweder** der Source-Enum-Wert wird korrigiert (z. B.
`'llm_estimate'` statt `'web_search'`), **oder** die UI labelt es unabhängig
vom Backend-Wert generisch als "geschätzt" — das ist P-2.

**2.3** Fehlerfall: `source:'none'` (bei `privat`/`free`-Tier) — UI muss dann
gar keine Herkunftskennzeichnung zeigen, da kein Wert vorhanden ist.

**2.4** ENGB01: n/a bzw. konform, falls Source-Enum-Korrektur nötig ist
(gehört zum Backend/Engine-Layer, nicht ins Frontend).

---

## Phase 3 — Constraints und Blast Radius

### 3.1 ADR-Konformität

| ADR | Relevanz | Befund |
|---|---|---|
| ADR-001 (System Boundaries) | Grundregel (Backend = kanonischer Layer-1/2-Owner) bleibt gültig für A-1/A-3 | **Observed, veraltet:** Dokument nutzt durchgehend "Railway"-Terminologie, keine Erwähnung von "Render" — stale relativ zu ADR-012 (2026-07-18, bestätigt Render.com). Docs-Hygiene-Flag, kein Blocker. |
| ADR-002 (ein Writer pro Entity) | Indirekt — A-1 konsolidiert Plan-Generierung auf einen Pfad | Konform, keine Konflikt |
| ADR-005 (Plan-Pfad) | Zentral für A-1 | Entscheidung bereits getroffen (siehe 0.3), A-1 vollzieht sie nach — **Drift-Rückbau**, kein neuer Entscheid nötig. Auch hier "Railway"-Terminologie, stale wie ADR-001. |
| ADR-006 (Tier-Mapping) | Relevant für A-2 (tier-abhängige Steuerung) | Kein Widerspruch — `personaTypeToTier()` ist explizit als separate, gültige Funktion neben der `subscription_tier`-Mapping vorgesehen. |
| ADR-009 (Opponent-Simulation-Routing) | Relevant für A-3 | Bereits erweitert gültig laut NC-L3-SIM-Brief ("Routing, unverändert gültig") — kein neues ADR für die Backend-Seite von A-3 nötig. Warnt aber selbst vor Verwechslungsgefahr durch parallele Pfade (`/api/opponent-simulation/*` vs. `/api/simulate/*`) — relevant für P-3. |
| ADR-012 (Anthropic-only) | Alle Maßnahmen | Konform — keine neue Modellwahl vorgesehen. |

**Für A-4 (externe Marktdatenquelle):** Falls P-2 zu "externe Datenquelle
beschaffen" führt, entsteht ADR-Bedarf (neue externe Service-Integration,
analog zu bestehenden ADR-Mustern für Supabase/Anthropic). **Nicht selbst
geschrieben** — nur als Bedarf festgestellt.

### 3.2 Kopplung A-2 ↔ HIGH-03

**Befund (Observed, wichtig):** BUG-20260719 (der konkrete
`persona_type`-Bug hinter einem der drei HIGH-03-Systeme) ist **Status: DONE**,
gefixt am 2026-07-21 per Migration. HIGH-03 selbst (die ursprüngliche
"drei-Tier-Systeme"-Architekturfeststellung) ist laut
`docs/audits/current-state-report.md` bereits **RESOLVED** seit 2026-04-10
(RFB-009). `AGENTS.md`s Quick-Reference-Tabelle listet HIGH-03 aber weiterhin
unqualifiziert als offen — das ist eine reine Docs-Drift zwischen zwei
verschiedenen Ären desselben Symptoms (ursprüngliches Architekturproblem vs.
neu entdeckter, strukturell anderer Signup-Trigger-Bug), nicht ein weiterhin
offenes Risiko.

**Empfehlung:** A-2 ist **nicht** blockiert von einem offenen HIGH-03 — beide
zugrundeliegenden Probleme sind gefixt. Die einzige verbleibende, echte Lücke
ist **Missing**: ob die drei anderen `persona_type`-lesenden Edge Functions
(`analyze-progress`, `summarize-session`, `analyze-document`) denselben
Bugfix-Bedarf hatten, wurde nie geprüft. Für A-2 selbst (betrifft nur
`generate-plan`) ist das irrelevant, da `generate-plan` explizit Teil des
BUG-20260719-Fixes war (Trigger-Fix wirkt auf `user_profiles.persona_type`
global, unabhängig davon, welche EF liest). **A-2 kann ohne Vorbedingung
starten.** Empfehlung an AGENTS.md: HIGH-03-Zeile in der Quick-Reference-Tabelle
korrigieren/historisieren (separates Docs-Housekeeping-Item, nicht Teil dieser
Klammer).

### 3.3 Blast-Radius-Triage (7 Punkte)

| Punkt | A-1 | A-2 | A-3 | A-4 |
|---|---|---|---|---|
| Callers | `apiClient.ts` neuer/reaktivierter `generatePlan()`-Call; alle UI-Stellen, die aktuell EF-Plan konsumieren (`StrategyDialog`, `Index.tsx`, `BottomBar` laut Contract-Doc) | Nur `generate-plan`-Prompt-Text | Neue Frontend-Komponente(n), kein bestehender Caller | Anzeige-Layer in `Strategy Report` o.ä. (wo laut NC-L2-UI Market Data bereits angezeigt wird) |
| Signaturänderungen | `/api/plan` Request braucht `zopaResult`+`analysis` — Frontend muss diese aus einem vorherigen `/api/analyze`-Call mitgeben | Keine | Neue Request/Response-Typen für `/api/simulate/*` | Ggf. Korrektur von `market_data_source`-Enum-Wert (P-2) |
| Vertragsabdeckung | `frontend-backend.md` muss aktualisiert werden (aktuell stale) | Keine Änderung nötig | `frontend-backend.md` fehlt komplett für diese Endpoints (AC-7 von NC-L3-SIM) | Enum-Bedeutung muss präzisiert werden |
| Logikduplikation | Reduziert sie sogar (ein Plan-Pfad statt zwei) | Keine | Keine — `/api/opponent-simulation/*` bleibt unabhängig bestehen (bewusste Parallelität, kein Duplikat-Risiko laut ADR-009) | Keine |
| Layer-Abhängigkeiten (0→3) | Erzwingt korrekte Reihenfolge: Layer 1 muss vor Plan-Generierung laufen — aktuell nicht sichergestellt (siehe 2.1) | n/a | Layer 3 baut korrekt auf Layer 1 auf (bereits laut Debrief-Feldern bestätigt) | Layer 2 unverändert |
| Tier-Gates | `/api/plan` hat `authMiddleware`, aber (ungeprüft in diesem Scope) kein sichtbares Tier-Gate — **Missing**, zu prüfen vor Rollout, da EF aktuell auch keins hat (Tier-Gate-Stub inaktiv) | Tier-abhängige Steuerung selbst ist der Kern von P-1 | `requireTier('profi')` bereits empirisch bestätigt aktiv (Phase 1.2) | `source:'none'` bei `privat`/`free` bereits vorhandenes Gate |
| Breaking Changes | Für bestehende EF-Nutzer: Umstellung muss ohne sichtbaren Ausfall erfolgen (Rollback-Pfad, Phase 4.3) | Keine (reiner Text) | Kein Breaking Change, da neuer Pfad additiv | Kein Breaking Change, additive UI-Info |

### 3.4 Wird `generate-plan` EF nach A-1 obsolet?

**Ja, absehbar** — aber laut ADR-005 erst *nach* vollzogener Frontend-Migration
zu retiren, nicht vorher. **Als DCC-Kandidat vormerken** (Schema-Vorschlag:
`DCC-EF-03`, analog zu `DCC-EF-02` für die bereits gelöschte `chat`-Gemini-EF).
**Nicht in dieser Klammer löschen.**

---

## Phase 4 — Lieferplan

### 4.1 Repo-Aufteilung und Reihenfolge

1. **shared-context (docs-only, zuerst):** `frontend-backend.md` auf aktuellen
   Stand bringen (`/api/plan`-Entscheidungsstatus korrigieren, `/api/simulate/*`
   ergänzen — letzteres schließt gleichzeitig NC-L3-SIMs offenes AC-7).
2. **negotiationcoach-backend:** A-1s fehlende Verdrahtung
   (`analyzeNegotiation()`-Aufruf vor Plan-Generierung, ODER explizite
   Vertragsklärung, dass der Frontend-Caller die Analyse selbst vorher
   ausführt und mitgibt — Entscheidung Teil des A-1-Delivery-Briefs, nicht
   hier). Tier-Gate-Prüfung für `/api/plan` (Blast-Radius-Punkt oben).
3. **negotiation-buddy:** `apiClient.ts` auf `/api/plan` umstellen (A-1),
   neue Simulate-UI (A-3), `market_data_source`-Anzeige (A-4).
4. **A-2** kann unabhängig und parallel laufen (reine Prompt-Textänderung in
   `generate-plan`), sollte aber inhaltlich mit A-1 abgestimmt werden, falls
   A-1 zuerst landet und die Prompt-Logik dann in `buildPlanSystemPrompt`
   statt in der EF liegt (Reihenfolge-Entscheidung, siehe P-1).

**Abhängigkeit A-1 → A-2:** Falls A-1 vor A-2 umgesetzt wird, muss die
Framework-Namen-Regel in `buildPlanSystemPrompt` (Backend) statt in
`generate-plan` (EF) geändert werden — sonst wird eine Regel geändert, die der
neue aktive Pfad gar nicht mehr nutzt. **Reihenfolge-Empfehlung: A-1 zuerst,
A-2 danach, im selben oder direkt folgenden Delivery.**

### 4.2 Akzeptanzkriterien (konkret)

- **A-1:** *"Der vom Nutzer empfangene Plan enthält mindestens einen aus ZOPA,
  Nash oder Monte Carlo abgeleiteten Wert, und dieser Wert ist im Plantext als
  solcher erkennbar begründet."* Konkreter curl-Test: `POST /api/plan` mit
  echtem `zopaResult`/`analysis` aus einem vorherigen `/api/analyze`-Call →
  Response-Text enthält den konkreten `nash_solution`-Wert oder eine ZOPA-Range
  als Zahl, nicht nur Prosa-Platzhalter.
- **A-2:** curl/Prompt-Test: Plan-Output enthält mindestens einen Fachbegriff
  (z. B. "ZOPA" oder "BATNA") für Tiers, für die das freigegeben ist (P-1
  abhängig), und keinen für `free`, falls tier-differenziert.
- **A-3:** UI-Zustand: `/api/simulate/debrief` wird nach vollständigem
  Simulationsdurchlauf im Frontend angezeigt, inkl. `final_vs_nash_distance`
  und `concession_timeline` als sichtbare UI-Elemente (nicht nur im
  Netzwerk-Tab).
- **A-4:** UI-Zustand: wo `market_median` angezeigt wird, steht daneben ein
  Kennzeichnungstext (z. B. "geschätzt" oder Quellenangabe), der korrekt
  wiedergibt, dass es sich um eine LLM-Schätzung handelt (kein "Live-Marktdaten"
  o. ä. Wording, das eine externe Quelle suggeriert).
- Für alle: `tsc --noEmit` allein ist **kein** Abnahmekriterium
  (`verify-loop`-Skill-Konvention).

### 4.3 Risiken und Rollback

- **A-1 (höchstes Risiko, Hauptpfad für alle Nutzer):** Rollback = Feature-Flag
  oder schneller Revert von `apiClient.ts` zurück auf die EF, da `generate-plan`
  laut ADR-005 explizit *nicht* gelöscht werden darf, solange Migration läuft.
  Größtes Einzelrisiko: falls die Frontend-Analyse-Vorbedingung (2.1) übersehen
  wird, degradiert der Plan für alle Nutzer stillschweigend zu
  Platzhalter-Prosa — das ist schlechter als der Status quo (EF liefert
  wenigstens konversationell kohärenten Text). **Muss vor Rollout getestet
  werden.**
- **A-3:** Niedriges Risiko (additiv, kein bestehender Pfad wird ersetzt) —
  aber Gefahr von Nutzerverwirrung, wenn `profi`-Tier-UI sichtbar ist, aber
  praktisch niemand sie erreichen kann (0.2). Empfehlung: UI erst sichtbar
  machen, wenn Stripe/Tier-Auflösung für echte Nutzer erreichbar ist, oder
  klar als "Preview"/Beta kennzeichnen.
- **A-4:** Niedriges Risiko, reine Text-/Label-Änderung.
- **A-2:** Niedriges Risiko, aber Reihenfolge-Fehler (siehe 4.1) würde die
  Änderung wirkungslos machen.

### 4.4 Testansatz

`verify.sh`-Harness (bereits vorhanden im Backend) um `/api/plan` und
`/api/simulate/*` erweitern (aktuell laut Runtime-Check nur `/api/analyze` +
`/api/enrich` abgedeckt) — das ist selbst ein kleiner, sinnvoller Vorlauf-Task
vor A-1/A-3, damit die neuen Pfade ein Orakel haben, bevor sie zum Hauptpfad
werden.

### 4.5 Dokumentationsbedarf

- `docs/contracts/frontend-backend.md`: `/api/plan`-Abschnitt korrigieren,
  `/api/simulate/*` ergänzen (schließt NC-L3-SIM AC-7).
- `docs/decision-log/ADR-001` und `ADR-005`: Terminologie "Railway" →
  "Render.com" nachziehen (Docs-Hygiene, unabhängig von dieser Klammer, aber
  auffällig genug, um hier zu vermerken).
- `AGENTS.md`: HIGH-03-Zeile historisieren/korrigieren (zwei Ären
  unterscheiden).
- `product/roadmap.md`: NC-L3-SIM-Phasenzahl auf "Phase 3/7" nachziehen.
- Nach Umsetzung: `docs/ARCHITECTURE.md` Update-Trigger greift (Routing-Änderung
  an `/api/plan`, neue Endpunkte `/api/simulate/*` bereits vorhanden aber ggf.
  Frontend-Datenfluss-Diagramm ergänzen).

### 4.6 Skill-Update-Bedarf

Keiner zwingend — `impact-check`, `contract-check`, `pm-prepare-delivery`
decken den Bedarf bereits ab (siehe Skill-Checklisten-Zusammenfassung unten).
Einzige Beobachtung: ein `/contract-check`-Lauf auf diese Klammer würde
vermutlich bereits allein wegen der Docs-Staleness (4.5) mit HOLD reagieren,
bevor er den eigentlichen Code bewertet — das ist beabsichtigtes
Skill-Verhalten, kein Skill-Defizit.

---

## Produktentscheidungen — nicht selbst getroffen

### P-1 — A-2: Framework-Namen-Terminologie

| Option | Vorteil | Nachteil |
|---|---|---|
| Generell freigeben (alle Tiers) | Einfachste Umsetzung, keine Tier-Abhängigkeit | Widerspricht der bestehenden `chat`-EF-Konvention (Block M-10 steuert Terminologie bereits tier-abhängig) — inkonsistentes Nutzererlebnis zwischen Chat und Plan |
| Tier-abhängig steuern (analog Block M-10) | Konsistent mit bestehendem `chat`-Verhalten; nutzt bereits vorhandene Tier-Infrastruktur (Tier-Gate-Stub existiert bereits, siehe 1.3) | Mehr Implementierungsaufwand; hängt an derselben `persona_type`-Datenquelle wie BUG-20260719 (gefixt, aber ein weiteres Abhängigkeitsglied) |
| Fachbegriff + Erklärung in Klammern (z. B. "Verhandlungsspielraum (ZOPA)") | Bildet Nutzer, ohne Fachjargon vorauszusetzen; funktioniert tier-unabhängig | Kein bestehendes Präzedenz-Muster im Code; müsste neu definiert werden |

**Empfehlung:** Tier-abhängig steuern, konsistent mit Block M-10 im
`chat`-Prompt — vermeidet ein viertes, inkonsistentes Terminologie-Verhalten
neben `chat`, `generate-plan` (aktuell) und einem möglichen neuen `/api/plan`.

### P-2 — A-4: Marktdatenquelle

| Option | Vorteil | Nachteil |
|---|---|---|
| Externe Marktdatenquelle beschaffen | Löst das strukturelle Problem (LLM-Schätzung ist bereits von NC-L2-FIX als "kann veraltet sein" geflaggt) | Neue externe Integration, ADR-Bedarf, Kosten/Wartung, laut `strategy.md` "kein aktiver Fokus" für Wave 3 |
| Zahl als Schätzung kennzeichnen | Sofort umsetzbar, kein neuer Backend-Aufwand, ehrliche Nutzerkommunikation | Reduziert wahrgenommene Werthaltigkeit des "Reality Score"-Kernversprechens |
| Reality Score vorerst zurückbauen | Vermeidet Irreführung vollständig | Verliert ein bereits beworbenes/gebautes Kernfeature (NC-L2-FIX/NC-L2-UI, beide Released) — hoher Sunk-Cost-Verlust |

**Empfehlung:** Als Schätzung kennzeichnen (Option 2) — geringster Aufwand,
größte Übereinstimmung mit dem bereits in NC-L2-FIX dokumentierten,
akzeptierten Risiko ("kann veraltet sein, ADR für externe API ist
Wave-3-Kandidat"). Externe Quelle bleibt ein späterer Wave-3-Kandidat, kein
Blocker für diese Klammer.

### P-3 — A-3: `/api/opponent-simulation/*` ablösen oder parallel betreiben?

**Beobachtung:** ADR-009 warnt bereits explizit vor Verwechslungsgefahr durch
zwei parallele "Chat-artige" Backend-Pfade. NC-L3-SIMs eigener Brief sagt
"ersetzt NICHT" — das ist bereits eine Vorentscheidung für Parallelbetrieb,
zumindest kurzfristig.

| Option | Vorteil | Nachteil |
|---|---|---|
| Parallel betreiben (bestätigt bereits Konvention) | Kein Migrations-Risiko für bestehende `OpponentSimulator.tsx`-Nutzer | Zwei UI-Einstiegspunkte für ähnliche Funktion — Verwechslungsgefahr laut ADR-009 selbst antizipiert |
| Ablösen (`/api/opponent-simulation/*` schrittweise retiren) | Ein Pfad, ein UX, weniger Wartungslast langfristig | Widerspricht der bereits kommunizierten NC-L3-SIM-Zusage ("ersetzt NICHT"); Migrations-Aufwand für bestehende Nutzer |

**Empfehlung:** Kurzfristig parallel betreiben (wie bereits zugesagt), aber
`/api/opponent-simulation/*` explizit als DCC-Kandidat für einen späteren
Wave vormerken, sobald `/api/simulate/*` produktiv erprobt ist — analog zum
Umgang mit `generate-plan` in 3.4.

---

## Zusammenfassung — Klassifikations-Nachweis

Alle Laufzeit-Behauptungen in Phase 1 sind **Observed** (empirisch per curl
oder direktem Code-/Deployment-Lesen bestätigt). Alle Aufwandsschätzungen in
Phase 4 basieren ausschließlich auf diesen Observed-Befunden. Als **Missing**
markiert und ausdrücklich nicht in dieser Klammer gelöst:

- Ob das Frontend heute bereits automatisch `/api/analyze` bei
  Chat-Flow-Abschluss aufruft (kritisch für A-1s tatsächlichen Aufwand).
- Ob `analyze-progress`, `summarize-session`, `analyze-document` denselben
  `persona_type`-Bugfix-Bedarf hatten wie `generate-plan`.
- Welchen `market_data_source`-Enum-Wert der LLM-Schätzungspfad aktuell
  tatsächlich zurückgibt.
- Ob `/api/plan` selbst ein Tier-Gate braucht (aktuell nur `authMiddleware`
  beobachtet, kein Tier-Check geprüft).

---

**STOP. Warte auf GO / HOLD / SPLIT / BACK TO DOCS.**
Kein Code, keine Migration, keine Prompt-Änderung ohne GO.
