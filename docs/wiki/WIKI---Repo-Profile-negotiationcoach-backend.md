WIKI — Repo Profile: negotiationcoach-backend (Backend & Engine)
Klassifikation: Observed | Inferred | Missing | Proposed Erstellt: 2026-04-17 | Ablageort: shared-context/docs/wiki/ Basis: Audit-Dokumente (current-state-report.md, audit-findings.md, refactor-backlog.md), ADRs 001–007, PDFs (ENGB01, IMP01–04, IMP03), initial-setup-baseline.md Korrespondierende Seite: WIKI — Repo Profile: negotiation-buddy (Frontend)

1. Zweck und Scope
Fachliche Rolle
negotiationcoach-backend ist der kanonische Execution-Path für alle Business-Logik in NegotiationCoach AI (ADR-001). Es ist kein API-Proxy — es trägt die gesamte Engine-Intelligenz: quantitative Verhandlungsanalyse, Marktdaten-Enrichment, LLM-Orchestrierung und Session-Persistenz.
Verantwortlichkeiten
Layer    Scope
Layer 0    Supabase-DB-Client (service role), TypeScript-Interfaces
Layer 1    Verhandlungsalgorithmen: ZOPA, Nash Bargaining, Monte Carlo, Deadline Effect, Strategy Score, BATNA
Layer 2    Marktdaten-Enrichment: Cache-first via knowledge_graph, Claude Tool Use, Reality Score
Layer 3 (API)    Express-Routing, Auth-Middleware, Tier-Gates, Session-Persistenz
Supabase-Schema    Alle Migrations als versionierte .sql-Files in supabase/migrations/
Abgrenzung zum Frontend
Backend-Eigentum ✅    Frontend-Eigentum ❌
Alle Algorithmen und LLM-Calls    UI-Komponenten, Routing, State
Supabase-Schema und RLS-Policies    Chat-Streaming (Edge Function via Gemini)
Tier-Enforcement serverseitig    apiClient.ts — reiner HTTP-Wrapper
Session-Persistenz in DB    AnalysisContext (localStorage)
Plangeneration, Chat-Fallback    Lovable-Prompts, Tailwind-Styling
2. Architektur
2.1 Request-Flow
Request → src/api/routes.ts (Express, Port 3001 / $PORT)
  ↓
authMiddleware — JWT-Validation, 401 bei fehlendem/ungültigem Token (seit fd68e1e)
  ↓ optional
requireTier(x) — explizites Gate nur auf /api/enrich: kmu+
  ↓
Layer 1 — src/layer1/
  zopaCalculator → nashBargaining → monteCarlo
  → deadlineEffect → strategyScore → batnaDetector (async Claude)
  Output: AnalysisResult
  ↓ wenn kmu/profi
Layer 2 — src/layer2/
  marketDataResolver → knowledgeGraph (Cache-Hit)
                     → marketDataInterpreter (Cache-Miss, Claude Tool Use)
  → realityScore → LLM-Summary (Claude)
  Output: EnrichedAnalysisResult
  ↓
Supabase INSERT/UPDATE (service role key — RLS bypassed, Ownership via app code)
2.2 Modul-Status
Layer    Modul    Status
0    supabaseClient.ts    ✅ Observed
1    zopaCalculator.ts    ✅ Observed
1    nashBargaining.ts    ✅ Observed
1    monteCarlo.ts    ✅ Observed
1    deadlineEffect.ts    ✅ Observed
1    strategyScore.ts    ✅ Observed
1    batnaDetector.ts    ✅ Node.js-Kopie; EF-Kopie: undeployable (broken import, Schema-Drift)
2    marketDataResolver.ts    ⚠️ Fehlerhaft — Fehlerursache undiagnostiziert
2    marketDataInterpreter.ts    ⚠️ Fehlerhaft
2    knowledgeGraph.ts    ⚠️ Fehlerhaft
2    realityScore.ts    ⚠️ Fehlerhaft
API    routes.ts    ✅
API    middleware.ts    ✅ (Auth-Enforcement seit RFB-001, fd68e1e)
API    errors.ts    ✅
Utils    modelRouter.ts    ✅ (vollständig nach fixes 60848db, d0b2bff)
Types    src/types/index.ts (domain)    ✅
Types    src/lib/types.ts (API shapes)    ✅
EF    supabase/functions/negotiate/index.ts    ⚠️ Dupliziert Layer 1, inkompatibles Schema — FREEZE bis ADR-007
Layer 3    smlParser.ts, promptBuilder.ts, simulationLoop.ts etc.    ❌ Nicht begonnen
2.3 Externe Integrationen
Service    Zweck    Bindung
Anthropic Claude API    LLM-Inference (haiku / sonnet / opus)    @anthropic-ai/sdk, via modelRouter.selectModel()
Supabase PostgreSQL    Session-Persistenz, Knowledge Graph Cache    service role key — RLS bypassed
Supabase Auth    JWT-Validation (getUser)    in authMiddleware.ts
Nicht vorhanden (Observed): Stripe-Integration, externe Web-Search-API, echte Marktdaten-Feeds.
⚠️ marketDataInterpreter.ts (ehem. webSearch.ts) nutzt Claude-Trainingsdaten, keine externe API. Der Name ist irreführend. Marktdaten können veraltet sein.

3. API-Oberfläche
3.1 Endpunkte
Method    Pfad    Layer    Auth    Tier-Gate
GET    /api/health    —    Public    —
POST    /api/analyze    Layer 1    JWT (401)    keines
POST    /api/enrich    Layer 2    JWT (401)    requireTier('kmu') — explizit
POST    /api/analyze-full    L1 + L2    JWT (401)    L2 implizit übersprungen bei < kmu
GET    /api/sessions/:id    —    JWT (401)    user_id check (app-level)
POST    /api/plan    Plan    JWT (401)    keines
POST    /api/chat    Chat    JWT (401)    keines
POST    /api/teams/*    Teams    JWT (401)    admin-check serverseitig
3.2 Tier-Gate-Lücken (Observed)
* /api/plan und /api/chat: kein explizites Tier-Gate — Model-Routing via modelRouter.ts ist einziges Differenzierungsmittel
* /api/analyze: BATNA via Claude auch für free-Tier (kein explizites Gate)
* Tier-Gates auf /api/analyze-full sind implizit (Layer-2-Bypass) — kein 403, nur stilles Überspringen
3.3 Key-Interfaces
Type    Zweck
Tier    'free' | 'privat' | 'kmu' | 'profi'
NegotiationType    'gehalt' | 'miete' | 'lieferant' | 'm_a' | 'sonstige'
NegotiationInputs    Input zu Layer 1 und Layer 2
AnalysisResult    Output Layer 1
EnrichedAnalysisResult    Output Layer 2 (extends AnalysisResult)
4. Supabase-Nutzung
4.1 Instanz und Zugriffsmuster
* Instanz: Railway-Instanz (service role key) — getrennt von Lovable-Frontend-Instanz
* SERVICE_ROLE_KEY bypasses RLS vollständig
* Ownership-Enforcement ausschließlich via Application Code: .eq('user_id', req.user.id) und assertSessionOwner()
4.2 Tabellen
Tabelle    Operations    RLS    Ownership-Enforcement
negotiation_sessions    INSERT, SELECT, UPDATE    ✅ Aktiviert (pre-existing, confirmed 2026-04-09)    user_id via app code
session_history    — (war als session_messages falsch referenziert — RFB-031)    ✅ Aktiviert    —
knowledge_graph    SELECT (cache hit), INSERT (cache miss)    Inferred    rein serverseitig
teams, team_members, team_training_tasks    CRUD via team endpoints    Inferred    admin_user_id serverseitig
4.3 Migration-Disziplin
* Append-only .sql-Files in supabase/migrations/
* Naming: YYYYMMDDHHMMSS_beschreibung.sql
* Bekannte Migration: 20260320162431_add_model_routing_columns.sql (task_type, model_used, model_degraded)
* Nach jeder Migration: TypeScript-Types via MCP regenerieren (generate_typescript_types)

5. Auth-Fluss
Frontend → supabase.auth.signIn() → JWT (Lovable Supabase-Instanz)
     ↓
Railway authMiddleware → supabase.auth.getUser(token)
     → tier aus user.user_metadata.tier / app_metadata.tier
     → req.user = { id, tier }
     → 401 bei fehlendem/ungültigem Token (seit fd68e1e, 2026-04-03)
⚠️ Kein Stripe-Webhook-Handler implementiert — Tier ist nach Signup immutabel (RFB-032 deferred). Bezahlende User erhalten derzeit keine Tier-Upgrades.

6. Risikoübersicht
ID    Risiko    Klassifikation    Schwere    Status
R-01    Dual Layer-1-Implementierung — EF und Railway Schema inkompatibel, Tests broken    Observed (CRIT-01)    🔴 KRITISCH    Deferred → ADR-007 Blocker
R-02    Layer 2 liefert falsche Ergebnisse — Fehlerursache undiagnostiziert    Observed    🔴 KRITISCH    Höchste Priorität Wave 2
R-03    marketDataInterpreter.ts nutzt Claude-Trainingsdaten — Marktdaten potenziell veraltet    Observed    🟡 MITTEL    Strukturell, kein Fix geplant
R-04    CORS: Wildcard-Header überschreibt cors()-Allowlist — alle Origins erlaubt    Observed    🟡 MITTEL    Unbehandelt
R-05    Kein Input-Validation via Zod — zod installiert aber nirgendwo importiert    Observed    🟡 MITTEL    Unbehandelt
R-06    Kein Rate Limiting auf LLM-Endpunkten    Missing    🟡 MITTEL    Kein Fix geplant
R-07    Stripe-Webhook-Handler nicht implementiert — Tier-Gating ohne echtes Billing    Observed    🔴 HOCH (Business)    Deferred RFB-032
R-08    SESSION INSERT-Fehler werden geschluckt — sessionId: null ohne Caller-Feedback möglich    Observed    🟢 LOW    Unbehandelt
R-09    negotiation_id FK-Quelle unklar — möglicher silent INSERT-Fehler    Suspected    🟢 LOW    Unbehandelt
R-10    EF batnaDetector.ts: broken import, excludes 'free' — undeployable    Observed    🟡 MITTEL    Deferred → RFB-026 nach ADR-007
Bereiche mit hohem Änderungsrisiko
* src/layer2/ — gesamtes Layer-2-Subsystem fehlerhaft, Fehlerursache unbekannt → höchstes Risiko
* supabase/functions/negotiate/ — parallele Layer-1-Implementierung, inkompatibles Schema → jede Layer-1-Änderung muss in beiden Orten bewertet werden bis ADR-007 entschieden
* src/api/routes.ts — monolithische Routendatei ohne Subrouter-Struktur
* src/types/index.ts — Typ-Änderungen hier propagieren sofort in alle Layer; kein automatischer Drift-Check mit EF-Schema

7. Skill- und Pattern-Inventar
7.1 Installierte Skills
Skill    Pfad    Zweck
session-start    .claude/skills/session-start/    Session-Initialisierung für Claude Code Workloads
impact-check    .claude/skills/impact-check/    Cross-Repo Impact Assessment vor Änderungen
contract-check    .claude/skills/contract-check/    API-Contract-Verifikation
cleanup-audit    .claude/skills/cleanup-audit/    Redundanz- und Dead-Code-Checks
close-task    .claude/skills/close-task/    Task-Abschluss mit Docs-Update
7.2 Rule-Files
File    Inhalt
.claude/rules/architecture.md    Layer-Ordering, ADR-Konformität
.claude/rules/protected-files.md    Nicht änderbare Dateien
.claude/rules/api-contracts.md    Contract-Stabilität, Breaking Changes
.claude/rules/db-boundaries.md    Migration-Only für Schema, RLS-Pflicht
7.3 Wiederverwendbare Muster
Pattern    Wo    Beschreibung
assertSessionOwner()    src/api/routes.ts    User-Ownership-Check vor Session-Operationen
selectModel(task, tier)    src/utils/modelRouter.ts    Task-Tier-Matrix → haiku / sonnet / opus
requireTier(minTier)    src/api/middleware.ts    Express-Middleware für Tier-Gate
AppError / TierError / AuthError    src/utils/errors.ts    Typisiertes Error-Handling mit HTTP-Status-Codes
Cache-first mit TTL    src/layer2/knowledgeGraph.ts    Supabase als 7-Tage-Cache für Marktdaten
7.4 Lücken
* Kein Zod-basiertes Request-Validation-Pattern — installiert, nicht genutzt
* Kein Rate-Limiting-Pattern
* Keine Test-Coverage für Layer-2 Cache-Hit-Pfad (FINDING-T04)
* Keine Test-Coverage für modelRouter.ts (FINDING-T05)
* Kein standardisiertes Logging-Pattern (nur console.error)

8. Repo-Governance-Regeln
Diese Regeln sind in CLAUDE.md und .claude/rules/ verankert oder sollten dort ergänzt werden.
Bestehend (schärfen)
1. Layer-Ordering ist absolut — Kein neuer Layer-2/3-Code ohne vollständige Layer-0/1-Grundlage. Verstöße erfordern explizite ADR-Genehmigung.
2. Migrations sind append-only — Niemals bestehende Migration-Files editieren. Jede neue Tabelle erfordert RLS-Policy im gleichen Migration-File.
3. Service Role Key — Jede neue DB-Schreiboperation muss über assertSessionOwner() oder äquivalentes Ownership-Pattern abgesichert sein.
Neu hinzuzufügen (Proposed)
1. Kein neuer LLM-Call ohne modelRouter.selectModel() — Direkte Modell-Strings (z.B. 'claude-sonnet-4-6') sind verboten. Alle Claude-Calls laufen über modelRouter.
2. Zod-Validation ist Pflicht für neue Endpunkte — Jeder neue Express-Endpunkt muss Request-Body via Zod validieren. Kein as NegotiationInputs Cast ohne Schema-Check.
3. EF _shared/engine/ ist eingefroren — Bis ADR-007 entschieden: keine neue Logik in der Edge-Function-Engine.
4. Layer-2-Änderungen erfordern EnrichedAnalysisResult-Feldverifikation — Alle Output-Felder müssen vollständig befüllt sein (market_median, reality_score, market_context_summary ≠ undefined/null).
5. CORS — Nach Bereinigung: Neue Origins nur explizit in der Allowlist, kein Wildcard.

9. Ausstehende Dokumentation in shared-context
Dokument    Was fehlt / muss ergänzt werden    Auslöser
source-of-truth-matrix.md — Entity 6 (Layer 2)    Status-Update nach Layer-2-Fix    Wave 2 Step 3
bounded-contexts.md — BC-02    CRIT-01 als resolved markieren    Nach RFB-006 / ADR-007
contracts/frontend-backend.md — Type Drift Register    CRITICAL DRIFT EF vs. Railway schließen    Nach RFB-006
docs/delivery/layer2-diagnosis-plan.md    Neu erstellen — Diagnose-Ergebnisse Layer-2-Bug    Wave 2 Step 2
db-map.md — knowledge_graph    RLS-Status verifizieren (aktuell: Inferred)    Missing
docs/wiki/ (dieses Dokument)    Layer-3-Module ergänzen wenn Layer 3 beginnt    Bei Layer-3-Start
Backend docs/service-catalog.md    Team-Endpoints Phase C (Task-Erstellung)    Pending Lovable Phase C
decision-log/ADR-007-dual-layer1.md    Erste und dringendste Aufgabe Wave 2 — VG-06-Entscheidung    Sofort — Blocker
10. Referenzen
Dokument    Pfad
ADR-001 System Boundaries    docs/decision-log/ADR-001-system-boundaries.md
ADR-002 Data Ownership    docs/decision-log/ADR-002-data-ownership.md
ADR-003 AI Provider Split    docs/decision-log/ADR-003-ai-provider-strategy.md
ADR-006 Tier Mapping    docs/decision-log/ADR-006-tier-mapping.md
ADR-007 Dual Layer 1 (⚠️ fehlt)    docs/decision-log/ADR-007-dual-layer1.md
API-Vertrag Frontend ↔ Backend    docs/contracts/frontend-backend.md
Bounded Contexts    docs/bounded-contexts.md
Source of Truth Matrix    docs/source-of-truth-matrix.md
Audit Findings Backend    negotiationcoach-backend/docs/audit-findings.md
Refactor Backlog    docs/audits/refactor-backlog.md
Wave 2 Scope    docs/delivery/wave2-scope.md
Engine Blueprint    ENGB01 (PDF)
Dieses Dokument wird nicht automatisch aktualisiert. Nach jedem Wave-Abschluss und nach jeder wesentlichen Architekturentscheidung reviewen und aktualisieren.
