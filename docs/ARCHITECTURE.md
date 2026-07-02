# NegotiationCoach AI — Architektur

## Letzte Aktualisierung

| Datum | Geänderte Dateien / Anlass |
|-------|---------------------------|
| 2026-07-02 | Initiale Erstellung — analysiert: `negotiation-buddy/src/` (Frontend), `negotiationcoach-backend/src/` (Backend), `shared-context/docs/` (ADRs, Contracts, Edge Functions) |

---

## Systemüberblick

NegotiationCoach AI ist eine React-SPA (`negotiation-buddy`), gestützt durch zwei Laufzeit-Services: einen Express-Backend (Render.com) für LLM-Orchestrierung und Layer-1/2/3-Analysen sowie Supabase für Auth, PostgreSQL und Streaming-Edge-Functions (Deno). Der Haupt-Chat läuft als Server-Sent-Events (SSE) über eine Supabase Edge Function; alle strukturierten Analysen, Session-Persistenz und Business-Logik laufen über das Express-Backend. Eine `AnalysisContext`-Schicht im Browser (localStorage, 7-Tage-TTL) hält den globalen Session-State zwischen Tool-Navigationen konsistent.

---

## 1. User Flows

Die vier zentralen User-Journeys: Auth-Flow (Login, Signup, Password Reset), der Haupt-Verhandlungscoach-Flow (Guided Onboarding → Chat → Fortschrittsanalyse → Plan → Marktdaten), Tool-Navigation als nested-route Overlay (Index bleibt gemountet), und die Layer-3-Gegner-Simulation (Profi-Tier only).

```mermaid
flowchart TD
    Landing["/ — Landing Page"] --> Login["/login — Anmelden"]
    Landing --> Signup["/signup — Registrieren"]
    Landing --> ForgotPW["/forgot-password"]

    Login --> SupaSignIn["supabase.auth\n.signInWithPassword()"]
    Signup --> SupaSignUp["supabase.auth\n.signUp()"]
    SupaSignIn --> AuthEvent["INITIAL_SESSION Event\n(onAuthStateChange)"]
    SupaSignUp --> AuthEvent

    ForgotPW --> |"EF send-password-reset"| ResetEmail["Reset-E-Mail\n(via Resend)"]
    ResetEmail --> ResetPW["/reset-password"]
    ResetPW --> |"EF verify-reset-token"| SupaSignIn

    AuthEvent --> ProtectedRoute{"ProtectedRoute\nSession vorhanden?"}
    ProtectedRoute --> |"nein"| Login
    ProtectedRoute --> |"ja"| Index["/app — Index\nHaupt-Coach-Screen"]

    Index --> SessionList["SessionSidebar\n(loadSessions — Supabase direkt)"]
    Index --> GuidedFlow["GuidedFlowChips\n4-Step Onboarding\ngehalt / miete / auto / eigene"]

    GuidedFlow --> |"POST /api/sessions"| SessionCreated["Session erstellt\n(Backend API)"]
    SessionCreated --> ChatLoop["Chat Loop\n(EF chat — SSE-Stream)"]
    ChatLoop --> |"POST /api/sessions/:id/messages"| MessageSaved["Nachricht persistiert\n(Backend API)"]
    ChatLoop --> ProgressEngine["useProgressEngine"]

    ProgressEngine --> |"POST EF analyze-progress"| SixPoints["6-Punkte-Fortschritt\nsituation / ziel / gegenseite\nbatna / macht / strategie"]
    ProgressEngine --> |"POST /api/chat"| ExtractInputs["Strukturierte Inputs\nextrahieren\n(extractedInputs)"]

    SixPoints --> AllDone{"Alle 6 Punkte\nerfüllt?"}
    AllDone --> |"nein → weiter chatten"| ChatLoop
    AllDone --> |"ja"| PlanGen["POST EF generate-plan\n(max. 5 Versuche)"]
    PlanGen --> EnrichCall["POST /api/enrich\n(Layer 2 — kmu/profi Tier)"]
    EnrichCall --> PlanDisplay["Verhandlungsplan\n+ Marktdaten anzeigen"]

    Index --> ToolNav["Tool-Navigation\n(nested Routes — Index bleibt gemountet)"]
    ToolNav --> ZopaCalc["/app/zopa — ZOPA Calculator\nPOST /api/analyze-full"]
    ToolNav --> Canvas["/app/canvas — Negotiation Canvas\nAnalysisContext lesen"]
    ToolNav --> WhatIf["/app/what-if — What-If Simulator\nAnalysisContext lesen"]
    ToolNav --> Strategy["/app/strategy — Strategy Generator\nAnalysisContext lesen"]
    ToolNav --> Team["/app/team — Team Dashboard\n/api/teams + Supabase direkt"]

    Index --> Debrief["/debrief/:id — Debrief Dashboard"]
    Index --> Profile["/profile — Profil\n(user_profiles Supabase direkt)"]

    Index --> |"Profi-Tier only"| OpponentStart["POST /api/opponent-simulation/start\nGegner-Range wird verborgen berechnet"]
    OpponentStart --> OpponentTurn["POST /api/opponent-simulation/:id/turn\n(iterativ — max. N Runden)"]
    OpponentTurn --> |"max. Runden oder Nutzer beendet"| OpponentFinish["POST /api/opponent-simulation/:id/finish\nVerborgene Gegner-Range enthüllt"]

    Index --> |"supabase.auth.signOut()"| Logout["Logout → /login"]
```

---

## 2. Datenflüsse

Vier kritische Datenflüsse: (A) der Chat-Nachricht-Flow mit SSE-Streaming, (B) der Fortschritts- und Plan-Generierungs-Flow, (C) der Layer-1+2-Analyse-Flow (ZOPA Calculator), und (D) der Layer-3-Gegner-Simulations-Flow. Alle Flows nutzen Supabase-JWT als Bearer-Token für Backend und Edge-Function-Calls.

### A — Chat-Nachricht-Flow (SSE-Streaming)

```mermaid
sequenceDiagram
    participant Browser as Browser (React SPA)
    participant EF as Supabase EF: chat
    participant Anthropic as Anthropic API (Haiku)
    participant Backend as Express Backend
    participant DB as Supabase PostgreSQL

    Browser->>EF: POST /functions/v1/chat<br/>{messages, persona} + Bearer JWT (optional)
    EF->>EF: JWT prüfen → Tier auflösen (free fallback)
    EF->>Anthropic: createMessage(stream=true)<br/>model: claude-haiku-4-5-20251001
    Anthropic-->>EF: SSE stream (OpenAI-Format)
    EF-->>Browser: SSE stream: data: {choices:[{delta:{content}}]}<br/>...data: [DONE]
    Browser->>Browser: useChat akkumuliert Tokens → setzt message state

    Browser->>Backend: POST /api/sessions/:id/messages<br/>{role, content} + Bearer JWT
    Backend->>Backend: authMiddleware → JWT validieren
    Backend->>DB: INSERT session_history (max 50/session via DB-Trigger)
    DB-->>Backend: {id, created_at}
    Backend-->>Browser: {id, created_at}
```

### B — Fortschritts- und Plan-Generierungs-Flow

```mermaid
sequenceDiagram
    participant Browser as Browser (React SPA)
    participant ProgEF as Supabase EF: analyze-progress
    participant BackendChat as Express /api/chat
    participant PlanEF as Supabase EF: generate-plan
    participant Anthropic as Anthropic API (Haiku)
    participant DB as Supabase PostgreSQL

    Browser->>ProgEF: POST /functions/v1/analyze-progress<br/>{session_id, messages} + Bearer JWT
    ProgEF->>Anthropic: 6-Punkte-Prompt (user-only messages)
    Anthropic-->>ProgEF: {situation, ziel, gegenseite, batna, macht, strategie}
    ProgEF->>DB: UPDATE negotiation_sessions.progress_status
    ProgEF-->>Browser: {progress: {...6 Punkte...}}

    Browser->>BackendChat: POST /api/chat<br/>{messages, previousInputs} + Bearer JWT
    BackendChat->>Anthropic: extract-Prompt (user-only messages)
    Anthropic-->>BackendChat: JSON {extractedInputs}
    BackendChat->>BackendChat: parseChatResponse (3-Tier Regex Fallback)
    BackendChat-->>Browser: {message, extractedInputs, isComplete}
    Browser->>Browser: AnalysisContext.setExtractedInputs()

    Note over Browser: Alle 6 Punkte erfüllt? → Plan generieren

    Browser->>PlanEF: POST /functions/v1/generate-plan<br/>{session_id, progress_status, messages} + Bearer JWT
    PlanEF->>Anthropic: Plan-Prompt
    Anthropic-->>PlanEF: {plan: {summary, opening, objections, ...numbers}}
    PlanEF->>DB: UPDATE negotiation_sessions (plan gespeichert)
    PlanEF-->>Browser: {plan}

    Browser->>BackendChat: POST /api/enrich<br/>{sessionId} + Bearer JWT
    Note right of BackendChat: nur kmu / profi Tier
    BackendChat->>DB: SELECT negotiation_sessions (layer1_result)
    BackendChat->>BackendChat: Layer 2 Market Data Resolver<br/>knowledgeGraph Cache-Check → Web-Suche → Sonnet Summary
    BackendChat->>DB: UPDATE negotiation_sessions (layer2_result)
    BackendChat-->>Browser: {EnrichedAnalysisResult}
```

### C — Layer-1+2-Analyse-Flow (ZOPA Calculator)

```mermaid
sequenceDiagram
    participant Browser as Browser (/app/zopa)
    participant Backend as Express Backend
    participant L1 as Layer 1 Engine (TypeScript)
    participant L2 as Layer 2 Engine
    participant Anthropic as Anthropic API (Sonnet)
    participant PostHog as PostHog (EU)
    participant DB as Supabase PostgreSQL

    Browser->>Backend: POST /api/analyze-full<br/>{NegotiationInputs} + Bearer JWT
    Backend->>Backend: authMiddleware → Tier ermitteln
    Backend->>L1: analyzeNegotiation()
    L1->>L1: parallel: calculateZopa + detectBatna + deadlineEffect
    L1->>L1: calculateNash (Nash Bargaining Solution)
    L1->>L1: runMonteCarlo (P50/P90, nur wenn ZOPA existiert)
    L1->>L1: calculateStrategyScore
    L1-->>Backend: AnalysisResult
    Backend->>PostHog: trackEvent(analyze_completed, {tier, layer2_used, success})
    Backend->>DB: upsertAnalysisSession → negotiation_sessions

    alt Tier = kmu oder profi
        Backend->>L2: enrichWithMarketData()
        L2->>DB: knowledgeGraph Cache-Check (market_data Tabelle)
        alt Cache Miss
            L2->>L2: searchMarketData() (externe Web-Suche)
            L2->>DB: saveMarketData() (Cache befüllen)
        end
        L2->>Anthropic: Market Context Summary (claude-sonnet-4-6)
        Anthropic-->>L2: 2-3 Satz Summary
        L2->>L2: realityScore = (own_target - market_median) / market_median × 100
        L2-->>Backend: EnrichedAnalysisResult
    end

    Backend-->>Browser: {sessionId, result: AnalysisResult | EnrichedAnalysisResult}
    Browser->>Browser: AnalysisContext setzen (zopaResult, analysis, enriched)
```

### D — Layer-3-Gegner-Simulations-Flow (Profi-Tier)

```mermaid
sequenceDiagram
    participant Browser as Browser (React SPA)
    participant Backend as Express Backend
    participant L3 as Layer 3 Engine
    participant Anthropic as Anthropic API (Opus)
    participant DB as Supabase PostgreSQL

    Browser->>Backend: POST /api/opponent-simulation/start<br/>{negotiation_type, opponent_style, own_target, ...} + Bearer JWT
    Backend->>Backend: requireTier('profi') → 403 für andere Tiers
    Backend->>L3: computeHiddenOpponentRange()<br/>(ZOPA-basiert + difficulty/style Offsets)
    Note right of L3: Verborgene Range wird NICHT an Browser gesendet
    Backend->>DB: INSERT opponent_simulation_sessions
    Backend->>L3: buildOpponentSystemPrompt()
    L3->>Anthropic: Opening Message (claude-opus-4-8)
    Anthropic-->>L3: Eröffnungsangebot des Gegners
    Backend->>DB: INSERT turn 0 (opening message)
    Backend-->>Browser: {simulation_session_id, opening_message, max_turns}

    loop Verhandlungsrunden
        Browser->>Backend: POST /api/opponent-simulation/:id/turn<br/>{content, client_turn_id} + Bearer JWT
        Backend->>DB: Idempotenz-Check (client_turn_id)
        Backend->>DB: Gesamt-History laden (alle Turns)
        Backend->>L3: buildOpponentSystemPrompt() (stateless, per Turn)
        L3->>Anthropic: Full History → Gegner-Antwort (claude-opus-4-8, 30s Timeout)
        Anthropic-->>L3: Gegner-Reaktion
        Backend->>DB: UPSERT user_turn + assistant_turn (ON CONFLICT DO NOTHING)
        Backend->>DB: UPDATE turn_count
        Backend-->>Browser: {assistant_message, turn_count, max_turns, finished}
    end

    Browser->>Backend: POST /api/opponent-simulation/:id/finish<br/>{final_offer} + Bearer JWT
    Backend->>L3: evaluateOutcome()\n(Nash-Perzentil, ZOPA-Perzentil, tactic_assessment)
    Backend->>DB: UPDATE status=finished, final_outcome, evaluation
    Backend-->>Browser: {evaluation, hidden_opponent_minimum, hidden_opponent_target}
    Note right of Browser: Verborgene Range erstmals sichtbar
```

---

## 3. Architektur & Service Boundaries

Alle drei Laufzeit-Services kommunizieren über HTTPS/JSON (Backend) oder HTTPS/SSE (Edge Functions). Das Frontend ist der einzige Initiator von Calls — es gibt keine Service-to-Service-Kommunikation außer Backend → Supabase (service_role) und Backend → Anthropic. Der Browser hält keinen direkten Kontakt zur Anthropic API; alle LLM-Calls werden entweder über das Express-Backend oder die Supabase-Edge-Functions proxied.

```mermaid
graph LR
    subgraph Browser["Browser — negotiation-buddy.onrender.com"]
        ReactSPA["React 18 SPA\nVite / TypeScript strict"]
        AnalysisCtx["AnalysisContext\nlocalStorage 7d TTL"]
        PostHogFE["PostHog Client\n(memory, kein Cookie)"]
        ReactSPA <--> AnalysisCtx
    end

    subgraph SupabasePlatform["Supabase Platform"]
        SupaAuth["Supabase Auth\nJWT-Ausstellung\nToken-Refresh"]
        SupaDB["PostgreSQL\n+ RLS Policies\nservice_role für Backend"]
        subgraph EdgeFunctions["Edge Functions (Deno)"]
            EF_chat["chat EF\nSSE-Streaming\nHaiku"]
            EF_progress["analyze-progress EF\nHaiku"]
            EF_plan["generate-plan EF\nHaiku"]
            EF_doc["analyze-document EF\nHaiku Streaming"]
            EF_summary["summarize-session EF\nHaiku"]
            EF_pwreset["send-password-reset EF\nkein LLM"]
            EF_verify["verify-reset-token EF\nkein LLM"]
        end
    end

    subgraph Backend["Express Backend — Render.com\nnegotiationcoach-backend"]
        AuthMW["authMiddleware\nJWT → supabase.auth.getUser()"]
        TierMW["requireTier()\n403 für unzureichenden Tier"]
        Layer1["Layer 1 Engine\nZOPA · Nash · Monte Carlo\nDeadline · StrategyScore"]
        Layer2["Layer 2 Engine\nMarket Data Resolver\nknowledgeGraph Cache\nRealityScore"]
        Layer3["Layer 3 Engine\nOpponent Simulation\nHidden Range · Evaluation"]
        ErrHandler["Global ErrorHandler\nAppError-Hierarchie\n401 · 403 · 400 · 500"]
    end

    subgraph ExternalAPIs["Externe APIs"]
        AnthropicAPI["Anthropic API\nHaiku / Sonnet / Opus"]
        PostHogSrv["PostHog EU\nServer-side Telemetrie"]
        ResendAPI["Resend\nPassword-Reset-E-Mail"]
        MarketSearch["Market Data Search\n%% TODO: nicht eindeutig aus Code ableitbar — Web-Suche-Mechanismus"]
    end

    %% Browser → Supabase Auth
    ReactSPA -->|"HTTPS supabase.auth.signIn/Out\nAnon Key"| SupaAuth
    SupaAuth -->|"JWT + onAuthStateChange"| ReactSPA

    %% Browser → Edge Functions
    ReactSPA -->|"HTTPS SSE — Bearer JWT optional\nAnon Key"| EF_chat
    ReactSPA -->|"HTTPS JSON — Bearer JWT\nAnon Key"| EF_progress
    ReactSPA -->|"HTTPS JSON — Bearer JWT\nAnon Key"| EF_plan
    ReactSPA -->|"HTTPS JSON — Bearer JWT"| EF_doc
    ReactSPA -->|"HTTPS JSON — Bearer JWT"| EF_summary
    ReactSPA -->|"HTTPS JSON — public"| EF_pwreset
    ReactSPA -->|"HTTPS JSON — public"| EF_verify

    %% Browser → Backend (Express)
    ReactSPA -->|"HTTPS JSON — Bearer JWT\nPort 443 (Render.com)"| AuthMW
    AuthMW --> TierMW
    TierMW --> Layer1
    TierMW --> Layer2
    TierMW --> Layer3

    %% Browser → Supabase DB (architectural debt)
    ReactSPA -->|"HTTPS — Anon Key + RLS\nDIREKT: negotiation_sessions SELECT\nsession_history SELECT\nuser_profiles UPDATE\nteam_members SELECT\nteam_training_tasks SELECT+INSERT"| SupaDB

    %% Backend → Supabase DB
    Layer1 -->|"service_role Key\nbypasst RLS"| SupaDB
    Layer2 -->|"service_role Key"| SupaDB
    Layer3 -->|"service_role Key"| SupaDB
    AuthMW -->|"supabase.auth.getUser(token)"| SupaAuth

    %% Edge Functions → Supabase DB
    EF_progress -->|"service_role"| SupaDB
    EF_plan -->|"service_role"| SupaDB
    EF_summary -->|"service_role"| SupaDB
    EF_pwreset -->|"service_role"| SupaDB
    EF_verify -->|"service_role"| SupaDB

    %% Edge Functions → Anthropic
    EF_chat -->|"HTTPS — API Key"| AnthropicAPI
    EF_progress -->|"HTTPS — API Key"| AnthropicAPI
    EF_plan -->|"HTTPS — API Key"| AnthropicAPI
    EF_doc -->|"HTTPS — API Key"| AnthropicAPI
    EF_summary -->|"HTTPS — API Key"| AnthropicAPI

    %% Backend → External
    Layer1 -->|"HTTPS"| AnthropicAPI
    Layer2 -->|"HTTPS"| AnthropicAPI
    Layer2 -->|"HTTPS"| MarketSearch
    Layer3 -->|"HTTPS — 30s Timeout"| AnthropicAPI
    Layer1 -->|"server-side Events"| PostHogSrv
    ReactSPA -->|"client-side Events"| PostHogFE
    EF_pwreset -->|"HTTPS — API Key"| ResendAPI
```

### Model-Routing nach Layer und Tier

| Layer / Endpoint | Haiku | Sonnet | Opus |
|-----------------|-------|--------|------|
| EF chat (alle Tiers) | ✓ | — | — |
| EF analyze-progress | ✓ | — | — |
| EF generate-plan | ✓ | — | — |
| EF analyze-document | ✓ (Streaming) | — | — |
| Backend /api/chat (free fallback) | ✓ | — | — |
| Backend /api/chat (standard) | — | ✓ | — |
| Backend Layer 2 Market Summary | — | ✓ (immer) | — |
| Backend /api/opponent-simulation | — | ✓ (Fallback) | ✓ (profi) |
| Backend /api/plan (inaktiv) | — | ✓ | — |

---

## 4. Error Handling

Jeder kritische Flow hat eine eigene Fehlerbehandlungs-Schicht. Grundprinzip: LLM-Calls und externe Abhängigkeiten sind isoliert (Failure → Fallback/Silent), Auth-Fehler sind hart (401/403), Session-Loads haben Timeouts gegen PostgREST-Hänger, und Plan-Generierung hat einen dedizierten Retry-Mechanismus.

### A — Chat-Fehler und SSE-Fehler

```mermaid
flowchart TD
    ChatCall["useChat.sendMessage()\nPOST EF chat — SSE"] --> FetchErr{"fetch() Fehler?"}
    FetchErr --> |"nein"| StreamOK["SSE-Stream akkumulieren"]
    FetchErr --> |"ja: Netzwerk / Timeout"| ChatErrorState["error state setzen"]
    ChatErrorState --> ToastDestructive["Toast: 'Verbindungsfehler'\n(useToast, destructive)"]

    StreamOK --> ParseErr{"JSON-Parse-Fehler\nin Delta?"}
    ParseErr --> |"nein"| RenderMsg["Nachricht rendern"]
    ParseErr --> |"ja"| SilentSkip["Delta überspringen\n(kein UI-Feedback)"]

    EF_Internal["EF — Anthropic API Fehler"] --> |"catch → 500 JSON"| BrowserReceives500["Browser: Response status 500"]
    BrowserReceives500 --> ChatErrorState

    EF_RateLimit["EF — Rate Limit (429)"] --> |"429 JSON"| BrowserReceives429["Browser: Response status 429"]
    BrowserReceives429 --> ToastRateLimit["Toast: Rate Limit\n(wenn implementiert)"]
```

### B — Session-Load mit Timeout (PostgREST-Schutz)

```mermaid
flowchart TD
    LoadSessions["useSessionManager.loadSessions()\nbeim Mount / Session-Wechsel"] --> CacheCheck{"module-level Cache\nfür userId vorhanden?"}
    CacheCheck --> |"ja → sofort"| SetSessionsFromCache["setSessions(cache)\nSpinner bleibt aus"]
    CacheCheck --> |"nein"| AbortCtrl["AbortController erstellen\n6s Timeout"]
    SetSessionsFromCache --> DBQuery["Supabase SELECT\nnegotiation_sessions\n(user_id, status, updated_at)"]
    AbortCtrl --> DBQuery

    DBQuery --> QueryOK{"Query OK\ninnerhalb 6s?"}
    QueryOK --> |"ja"| UpdateCache["Cache aktualisieren\nsetSessions(fresh)"]
    QueryOK --> |"nein: Timeout (6s)"| AbortFired["AbortController.abort()\nQuery abgebrochen"]
    AbortFired --> CacheOrEmpty["Cache-Daten behalten\noder leere Liste"]
    AbortFired --> ConsoleError["console.error(timeout)\nkein User-Toast"]

    QueryOK --> |"ja: anderer Fehler"| DBError["Supabase-Fehler\n(RLS-Verletzung etc.)"]
    DBError --> ConsoleError2["console.error\nkein Retry — nächster Mount"]
```

### C — Auth-Token-Refresh-Fehler

```mermaid
flowchart TD
    TokenRefresh["Supabase Token-Refresh\n(automatisch alle ~55 Min)"] --> RefreshOK{"Refresh erfolgreich?"}
    RefreshOK --> |"ja"| NewToken["Neues JWT aktiv\nkein User-Impact"]
    RefreshOK --> |"nein: TOKEN_REFRESH_FAILED"| ImmediateSignOut["supabase.auth.signOut()\nSOFORT — kein Retry"]
    ImmediateSignOut --> AuthContextNull["AuthContext: user=null, session=null"]
    AuthContextNull --> ProtectedRedirect["ProtectedRoute → /login\nModule-level Cache bleibt\n(wird bei nächstem Mount invalidiert)"]

    BackendJWT["Backend-Call mit abgelaufenem JWT"] --> Auth401["authMiddleware → 401 AuthError"]
    Auth401 --> GlobalHandler["Global ErrorHandler\n{error: {code: UNAUTHORIZED}}"]
    GlobalHandler --> |"Browser: Response 401"| ApiClientThrows["apiClient.ts: throw ApiError(401)"]
    ApiClientThrows --> ComponentCatch["Component catch → Toast oder Error State"]
```

### D — Plan-Generierungs-Retry-Logik

```mermaid
flowchart TD
    AllSixDone["Alle 6 Fortschrittspunkte erfüllt"] --> PlanAttempt["POST EF generate-plan\n(Attempt 1 von max. 5)"]
    PlanAttempt --> PlanOK{"Plan-Response\nvalides JSON?"}
    PlanOK --> |"ja"| PlanStored["Plan in AnalysisContext\n+ UI anzeigen"]
    PlanOK --> |"nein: HTTP-Fehler"| HTTPErr["HTTP-Fehler → kein Retry-Versuch verbraucht\n(transient failure guard)"]
    HTTPErr --> WaitNextProgress["Warten auf nächste\nFortschritts-Änderung"]
    WaitNextProgress --> PlanAttempt

    PlanOK --> |"nein: JSON-Parse-Fehler"| ParseFail["Versuch +1\n(max. 5 gesamt)"]
    ParseFail --> MaxReached{"Versuche >= 5?"}
    MaxReached --> |"nein"| PlanAttempt
    MaxReached --> |"ja"| PlanToast["Toast: Plan-Generierung fehlgeschlagen\n(planFailToastedRef — max. 1 Toast/Session)"]
    PlanToast --> Stopped["Kein weiterer Retry in dieser Session"]
```

### E — Layer-2-Enrichment-Fehler (Silent Failure by Design)

```mermaid
flowchart TD
    EnrichCall["POST /api/enrich\n(nach Plan-Generierung)"] --> TierCheck{"Tier = kmu\noder profi?"}
    TierCheck --> |"nein (free/privat)"| SilentSkip["kein Enrich-Call\n(Frontend ignoriert 403)"]
    TierCheck --> |"ja"| BackendEnrich["Backend: enrichWithMarketData()"]

    BackendEnrich --> MarketOK{"Market Data\nverfügbar?"}
    MarketOK --> |"ja"| EnrichResult["layer2_result gesetzt\nRealityScore berechnet"]
    MarketOK --> |"nein: Suche fehlgeschlagen"| IsolatedFail["Layer 2 isoliert fehlgeschlagen\n→ market_data_source: 'none'\nkein 500 — Backend antwortet normal"]
    IsolatedFail --> NoMarketUI["Frontend: Marktdaten-Sektion\nbleibt leer (kein Fehler-Toast)"]

    BackendEnrich --> SonnetFail{"Sonnet-Summary\nFehlgeschlagen?"}
    SonnetFail --> |"ja"| EmptySummary["market_context_summary: ''\nkein 500"]
    EmptySummary --> EnrichResult

    FrontendCall["Frontend: await enrich()"] --> NetworkErr{"Netzwerk-/HTTP-Fehler?"}
    NetworkErr --> |"ja"| SilentIgnore["catch → silent ignore\n(non-critical — kein Toast)"]
```

### F — Opponent-Simulation: Idempotenz und Fehlerisolation

```mermaid
flowchart TD
    TurnCall["POST /api/opponent-simulation/:id/turn\n{content, client_turn_id}"] --> OwnerCheck{"Owner + Status\n= in_progress?"}
    OwnerCheck --> |"nein"| Return403["403 / 404"]
    OwnerCheck --> |"ja"| IdempotencyCheck{"client_turn_id\nschon in DB?"}
    IdempotencyCheck --> |"ja"| ReturnCached["200: {idempotent: true,\nassistant_message: cached}"]
    IdempotencyCheck --> |"nein"| TurnLimitCheck{"turn_count\n>= max_turns?"}
    TurnLimitCheck --> |"ja"| AutoFinish["auto-finish: {finished: true,\nreason: turn_limit_reached}"]
    TurnLimitCheck --> |"nein"| OpusCall["Claude Opus API\n30s Timeout"]

    OpusCall --> OpusOK{"API-Antwort\ninnerhalb 30s?"}
    OpusOK --> |"ja"| UpsertTurns["UPSERT user_turn + assistant_turn\n(ON CONFLICT DO NOTHING)"]
    UpsertTurns --> UpdateCount["UPDATE turn_count"]
    UpdateCount --> TurnResponse["200: {assistant_message, turn_count, finished}"]
    OpusOK --> |"nein: Timeout"| Timeout500["500 — kein Auto-Retry\n(Client kann erneut senden\nmit gleicher client_turn_id)"]
```

---

## Anhang: Bekannte Architektur-Schulden

| ID | Severity | Beschreibung | Status |
|----|----------|-------------|--------|
| HIGH-01 | High | Frontend schreibt `user_profiles` noch direkt via Supabase (Profile.tsx) | Offen |
| HIGH-01 | High | `team_members`, `team_training_tasks` noch direkt via Supabase gelesen (TeamDashboard.tsx) | Offen |
| HIGH-01 | High | `negotiation_sessions` / `session_history` noch direkt via Supabase gelesen (useSessionManager) | Offen |
| MED-01 | Medium | `modelRouter` in `/api/chat` und `/api/plan` bypassed — kein Tier-basiertes Model-Routing | Offen |
| MED-02 | Medium | CORS-Wildcard-Header überschreibt Allowlist in Express-Backend | Offen |
| — | Info | `/api/plan` (Backend) deklariert aber inaktiv — aktiver Pfad: EF `generate-plan` (ADR-005) | Dokumentiert |

Vollständiger Befund: `docs/audits/current-state-report.md`
