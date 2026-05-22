# FEATURE-PLAN-MARKETDATA — Verhandlungsplan Marktdaten-Integration
## Spezifikation: MarketContext-Sektion im generierten Verhandlungsplan

**Erstellt:** 2026-05-22
**Status:** PROPOSED — Review durch Delivery Controller ausstehend
**Voraussetzung:** FEATURE-L2-CONTEXT-spec.md committed (`9f12bcb`), Option B entschieden
**Repos:** negotiationcoach-backend (primary), negotiation-buddy (EF + Frontend), shared-context (Docs)

---

## Abschnitt 1 — IST-Analyse (Observed)

### 1.1 Aktuelle PlanRequest-Struktur

**Observed** — kein explizites `PlanRequest`-Interface im Backend-Code.
`buildPlanSystemPrompt()` in `src/api/planHelpers.ts` nimmt lose Parameter entgegen:

```typescript
// planHelpers.ts:1-6
export function buildPlanSystemPrompt(
  messages: { role: string; content: string }[],
  extractedInputs: Record<string, unknown>,
  zopaResult?: Record<string, unknown>,
  analysis?: Record<string, unknown>,    // AnalysisResult — Layer-1-Ergebnis
): string
```

`EnrichedAnalysisResult` ist **kein Parameter** von `buildPlanSystemPrompt()`. **Missing.**

Das Frontend-seitige `generatePlan()` in `src/lib/apiClient.ts:115-128` (UNUSED — zero
active callers) hat eine etwas präzisere Signatur:

```typescript
// apiClient.ts:115-128
export async function generatePlan(
  messages: { role: 'user' | 'assistant'; content: string }[],
  extractedInputs: ExtractedInputs,
  zopaResult?: ZopaToolResult | null,
  analysis?: AnalysisResult | null,
  accessToken?: string
): Promise<PlanResponse>
```

`enrichedAnalysis` fehlt auch hier. **Missing.** Die Funktion ist laut ADR-005-Kommentar der
Migrationsziel-Pfad (RFB-004 Phase C), aber heute nicht aktiv.

### 1.2 Aktuelle PlanResponse-Struktur

**Backend** (`src/api/planHelpers.ts:69-76`):
```typescript
export interface PlanResponse {
  summary: string;
  situationAnalysis: string;
  opening: string;
  objections: Array<{ title: string; objection: string; response: string }>;
  recommendations: string[];
  nextStep: string;
}
```

**Frontend** (`src/lib/apiClient.ts:86-99`):
```typescript
interface PlanObjection {
  objection: string;
  response: string;
  // DRIFT: title fehlt — Backend liefert title, Frontend-Typ ignoriert ihn
}
export interface PlanResponse {
  summary: string;
  situationAnalysis: string;
  opening: string;
  objections: PlanObjection[];
  recommendations: string[];
  nextStep: string;
}
```

**Observed Drift:** `PlanObjection.title` ist im Backend-Typ vorhanden, im Frontend-Typ nicht
deklariert. Pre-existing Drift, kein Blocker für dieses Feature.

**Marktdaten-Sektion:** In keiner der beiden Deklarationen vorhanden. **Missing.**

**Edge Function Response** (`supabase/functions/generate-plan/index.ts:144-152`):
```typescript
const plan = {
  summary: rawPlan.summary || rawPlan.executive_summary || "",
  situationAnalysis: rawPlan.situationAnalysis || rawPlan.situation_analysis || "",
  opening: rawPlan.opening || rawPlan.opening_script || "",
  objections: rawPlan.objections || [],
  recommendations: rawPlan.recommendations || [],
  nextStep: rawPlan.nextStep || "",
  numbers: rawPlan.numbers || {},   // Zusatzfeld — nicht in PlanResponse Backend-Typ
};
```

`numbers` ist ein Edge-Function-spezifisches Zusatzfeld das weder im Backend- noch im
Frontend-PlanResponse-Interface deklariert ist. **Observed Drift (pre-existing).**

### 1.3 Aktiver Generierungspfad (generate-plan Edge Function)

**Observed** — `src/pages/Index.tsx:441-473`:

```typescript
// Index.tsx:445-457 — aktiver Plan-Generierungsaufruf
const resp = await fetch(
  `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/generate-plan`,
  {
    method: "POST",
    headers: { Authorization: `Bearer ${token ?? VITE_SUPABASE_PUBLISHABLE_KEY}` },
    body: JSON.stringify({
      session_id: activeSessionId,
      progress_status: effectiveProgress,
      messages: messages.map((m) => ({ role: m.role, content: m.content })),
      // enriched ist NICHT enthalten obwohl es in useAnalysis() verfügbar ist
    }),
  }
);
```

Die Edge Function empfängt heute (`generate-plan/index.ts:49`):
```typescript
const { session_id, progress_status, messages } = await req.json();
```

**Nicht empfangen:** `extractedInputs`, `zopaResult`, `analysis`, `enrichedAnalysis`. **Missing.**

**Observed — Prompt-Aufbau in generate-plan/index.ts (kein Marktdaten-Kontext):**

```typescript
// generate-plan/index.ts:62-66 — aktueller Kontext-Aufbau
const contextLines = points.map((key) => {
  const val = progress_status[key];
  const summary = typeof val === "object" ? val?.summary || "" : "";
  return `${key}: ${summary}`;
}).join("\n");
```

Der Prompt nutzt ausschliesslich `progress_status`-Felder und die letzten 15 Chat-Messages.
Kein Marktdaten-Kontext. **Kein Marktdaten-Block im Prompt vorhanden. Missing.**

### 1.4 Rendering in StrategyGenerator.tsx

**Observed** — `StrategyGenerator.tsx` rendert **nicht** die `PlanResponse`. Es liest
ausschliesslich aus `AnalysisContext`:

| Sektion | Datenquelle | Rendering |
|---|---|---|
| ZOPA-Ergebnis | `zopaResult` aus AnalysisContext | Card mit ZOPA-Range, Nash, Score |
| Ausgangslage | `displayInputs` (inputs \|\| extractedInputs) | Card mit Zahlen |
| Markt-Vergleich | `enriched.reality_score` | Progress-Bar |
| Marktlage | `enriched.*` | Card mit Median, Range, Summary |
| Empfehlungen | `analysis.recommendations` | Liste |
| Strategie-Score | `analysis.strategy_score` | Card mit Score-Tiers |

**Kein Platzhalter für Plan-spezifische Marktdaten.** `PlanResponse` wird in
`StrategyGenerator.tsx` nicht importiert oder genutzt. **Observed.**

**Inferred:** Die `PlanResponse` (aus `negotiationPlan` State) wird in einer anderen
Komponente gerendert — wahrscheinlich `StrategyDialog.tsx` oder `StrategyTab.tsx`.
Die Marktdaten-Erweiterung muss dort ansetzen, nicht in `StrategyGenerator.tsx`.

### 1.5 Datenpfad EnrichedAnalysisResult → Frontend heute

**Observed** — `AnalysisContext.tsx:27`:
```typescript
enriched: EnrichedData | null;
```

`EnrichedData` wird aus `@/lib/types` importiert. **Inferred:** `EnrichedData` entspricht
`EnrichedAnalysisResult` aus dem Backend (selbe Felder: `market_median`, `reality_score`,
`market_data_source`, etc.) — zwei separate Typ-Deklarationen ohne Shared-Package.

**Observed** — `AnalysisContext.tsx:177,187`:
```typescript
// setResult() und setAnalysisResult() akzeptieren enriched:
enriched: e ?? null,
```

**Observed** — `Index.tsx:78`:
```typescript
const { ..., enriched, ... } = useAnalysis();
```

`enriched` ist im Index.tsx-Scope verfügbar. **Observed.**

**Observed GAP** — `Index.tsx:453-457`: `enriched` wird im `generatePlan`-Aufruf
NICHT in den Request-Body aufgenommen. Die Daten sind vorhanden — sie werden nur
nicht weitergeleitet. **Kein Blocker — einfach behebbar (1-2 Zeilen).**

---

## Abschnitt 2 — Entschiedene Integrationsstrategie

### 2.1 Gewählte Integrationsstrategie — neue optionale Sektion `marketContext`

**Begründung für neue explizite Sektion trotz Option-B-Analogie (Proposed):**

Option B in FEATURE-L2-CONTEXT war: "Kontext intern extrahieren, kein API-Contract-Change".
Für den Verhandlungsplan gilt eine andere Abwägung:

1. **Testbarkeit:** Eine explizite `marketContext`-Sektion im Plan ist curl-testbar und
   reviewbar. Implizites Einweben in `recommendations` wäre unsichtbar.
2. **Tier-Gate:** Null-Signal muss explizit möglich sein — `marketContext: null` sagt
   "keine Marktdaten" eindeutig, `marketContext: undefined` (Feld fehlt) sagt
   "Feature nicht implementiert". Der Unterschied ist semantic.
3. **Frontend-Rendering:** StrategyDialog/StrategyTab muss wissen ob Marktdaten vorhanden
   sind um eine eigene Sektion zu rendern oder einen Upgrade-Hinweis zu zeigen.
4. **Rückwärtskompatibilität:** `marketContext?: MarketContextSection | null` ist optional →
   bestehende Code-Pfade ohne `enrichedAnalysis` brechen nicht.

**Proposed Interface:**

```typescript
// Neu — in planHelpers.ts oder types/index.ts
interface MarketContextSection {
  market_position_summary: string;
  // z.B. "Ihr Ziel liegt 5,9% über dem Marktmedian für Senior SWE in München."
  market_range_summary: string;
  // z.B. "Typische Spanne: 78.000–105.000€ Jahresbrutto für diese Position."
  reality_assessment: string;
  // z.B. "Ihre Forderung ist für Senior-Level mit 5J Erfahrung im SaaS-Markt realistisch."
  data_source: 'web_search' | 'knowledge_graph' | 'none';
}

// Erweitertes PlanResponse
interface PlanResponse {
  summary: string;
  situationAnalysis: string;
  opening: string;
  objections: Array<{ title: string; objection: string; response: string }>;
  recommendations: string[];
  nextStep: string;
  marketContext?: MarketContextSection | null;
  // Optional: rückwärtskompatibel mit Code ohne enrichedAnalysis
  // Nullable: explizit "keine Marktdaten" vs. "Feld nicht vorhanden"
}
```

**Warum `optional AND nullable`:**
- `undefined` (Feld fehlt): Backend hat Feature noch nicht implementiert oder
  kein `enrichedAnalysis` übergeben → UI rendert nichts, kein Upgrade-Hinweis
- `null` (Feld explizit gesetzt): Backend hat geprüft, Tier reicht nicht oder
  market_data_source === 'none' → UI kann Upgrade-Hinweis zeigen

### 2.2 Erweitertes PlanRequest

**Proposed:**

```typescript
// planHelpers.ts — Parameter-Erweiterung
interface PlanRequest {
  messages?: ChatMessage[];
  extractedInputs: ExtractedInputs;
  zopaResult?: object;
  analysis?: object;
  enrichedAnalysis?: EnrichedAnalysisResult;  // NEU — optional, rückwärtskompatibel
}
```

**Begründung für optional:** Plan wird auch ohne vorherigen Enrich-Call generiert —
z. B. für free/privat-Tier oder wenn Enrich fehlschlägt. `enrichedAnalysis: undefined`
bedeutet `marketContext: null` im Response.

### 2.3 Prompt-Design — Marktdaten-Block

**Proposed Erweiterung von `buildPlanSystemPrompt()` und EF-Prompt:**

```
// Wird eingefügt wenn enrichedAnalysis vorhanden UND market_data_source !== 'none':

## Marktdaten-Kontext (kmu/profi-Tier)
Marktmedian: {market_median}€
Marktspanne: {market_range_min}€ – {market_range_max}€
Reality Score: {reality_score}% ({über/unter/im Bereich des} Marktmedians)
Markteinordnung: {market_context_summary}
Datenquelle: {market_data_source}

Ergänze deine Antwort um eine "marketContext"-Sektion im JSON:
"marketContext": {
  "market_position_summary": "1 präziser Satz: Wie liegt das Ziel (own_target) zum Marktmedian?",
  "market_range_summary": "1 Satz: Typische Marktspanne für diesen Kontext.",
  "reality_assessment": "1-2 Sätze: Ist die Forderung realistisch gemessen am Markt?",
  "data_source": "{market_data_source}"
}
```

**Fallback wenn kein enrichedAnalysis oder market_data_source === 'none':**

```
// Im Prompt:
Keine Marktdaten verfügbar. Setze "marketContext": null im JSON-Output.
Halluziniere keine Marktwerte.
```

**Konkretes Beispiel — Gehalt Senior SWE:**

*Prompt mit Marktdaten:*
```
## Marktdaten-Kontext (kmu/profi-Tier)
Marktmedian: 88.000€
Marktspanne: 72.000€ – 105.000€
Reality Score: +5,9% (über dem Marktmedian)
Markteinordnung: Senior SWE in SaaS-Unternehmen mit 200 MA in München
  liegen typischerweise zwischen 78.000 und 105.000€ Jahresbrutto.
  Ihr Ziel von 44.000€ liegt deutlich unter dem Marktmedian.
Datenquelle: knowledge_graph
```

*Erwartetes Claude-Output:*
```json
"marketContext": {
  "market_position_summary":
    "Ihr Zielgehalt von 44.000€ liegt 50% unter dem Marktmedian von 88.000€ für Senior Software Engineer in München.",
  "market_range_summary":
    "Die typische Vergütungsspanne für Ihre Position beträgt 72.000–105.000€ Jahresbrutto.",
  "reality_assessment":
    "Ihr aktuelles Gehalt von 40.000€ und das Ziel von 44.000€ liegen weit unter dem Markt. Das stärkt Ihre Verhandlungsposition erheblich — der Markt rechtfertigt eine Forderung von mindestens 75.000€.",
  "data_source": "knowledge_graph"
}
```

### 2.4 Tier-Gate-Design

**Proposed — Tier-Gate sitzt im Request-Aufbau (Index.tsx), nicht im Prompt-Builder:**

```typescript
// Index.tsx — generatePlan-Aufruf (Proposed)
body: JSON.stringify({
  session_id: activeSessionId,
  progress_status: effectiveProgress,
  messages: messages.map(...),
  // enrichedAnalysis nur wenn Tier kmu/profi UND Daten vorhanden:
  ...(enriched && enriched.market_data_source !== 'none' && isKmuOrProfi
    ? { enrichedAnalysis: enriched }
    : {}),
})
```

Der **Prompt-Builder** prüft nur ob `enrichedAnalysis` übergeben wurde — keine Tier-Logik
im Backend. Die Tier-Prüfung bleibt im Frontend (Caller-seitig), wie bei bestehenden
Tier-Gates im Chat-Path.

**Begründung:** Die Tier-Prüfung ist redundant mit dem bestehenden `/api/enrich`-Gate
(`requireTier('kmu')`). Wenn `enrichedAnalysis` vorhanden ist, hat die Tier-Prüfung
bereits stattgefunden. Doppelte Prüfung im Backend ist optional (defensive Programmierung),
aber kein Muss für MVP.

---

## Abschnitt 3 — Betroffene Artefakte

### 3.1 negotiationcoach-backend

**`src/api/planHelpers.ts`**
- `buildPlanSystemPrompt()`: Parameter `enrichedAnalysis?: EnrichedAnalysisResult` hinzufügen
- Marktdaten-Block in Prompt einweben (Abschnitt 2.3)
- `parsePlanResponse()`: `marketContext` aus Claude-Response extrahieren,
  `null` als expliziter Fallback wenn nicht vorhanden
- `PlanResponse` Interface: `marketContext?: MarketContextSection | null` hinzufügen
- `MarketContextSection` Interface: neu definieren
- **Änderungsumfang: ~40 Zeilen**

**`src/lib/types.ts` (negotiationcoach-backend)**
- Kein `PlanRequest`-Interface vorhanden — kein Change nötig
- `EnrichedAnalysisResult` wird bereits in `src/types/index.ts` exportiert — kein neues Interface

**`src/api/routes.ts`** (POST /api/plan Handler)
- `enrichedAnalysis` aus Request-Body lesen
- An `buildPlanSystemPrompt()` weitergeben
- **Änderungsumfang: ~5 Zeilen**

### 3.2 negotiation-buddy — Edge Function (aktiver Pfad)

**`supabase/functions/generate-plan/index.ts`**

**Observed:** Heute empfängt die EF: `{ session_id, progress_status, messages }`.
Plan-Prompt nutzt nur `progress_status`-Summaries und letzte 15 Messages.

**Proposed Änderungen:**

1. Input-Typ erweitern: `enrichedAnalysis?: EnrichedAnalysisResult` aus Body lesen
2. Marktdaten-Block analog zu `buildPlanSystemPrompt()` in den Claude-Prompt einbauen
   (wenn `enrichedAnalysis` vorhanden und `market_data_source !== 'none'`)
3. Response-Parsing: `marketContext` aus `rawPlan` extrahieren, Fallback `null`
4. `plan`-Objekt um `marketContext` ergänzen

**ADR-005-Hinweis (Observed):** Die EF ist der "temporäre Pfad" — `apiClient.ts:generatePlan()`
ist der Migrations-Ziel-Pfad (RFB-004 Phase C). Die EF-Änderung ist notwendig weil der
Backend-Pfad heute inactive ist. Wenn RFB-004 Phase C implemented wird, ist die EF zu
retire — die EF-Änderung hat dann begrenzte Lebensdauer.

**Änderungsumfang: ~50 Zeilen**

### 3.3 negotiation-buddy — Frontend

**`src/lib/apiClient.ts`**
- `generatePlan()` (UNUSED, ADR-005 Migrationsziel): Parameter `enrichedAnalysis?` hinzufügen
- `PlanResponse` Frontend-Typ: `marketContext?: MarketContextSection | null` hinzufügen
- `MarketContextSection` Interface lokal definieren (kein shared package vorhanden)
- `PlanObjection` Drift (pre-existing): `title?: string` hinzufügen — optional, nicht blockierend
- **Änderungsumfang: ~20 Zeilen**

**`src/pages/Index.tsx`**
- `enriched` aus `useAnalysis()` wird bereits destrukturiert (Zeile 78) — **Observed, kein neues Feld nötig**
- Im `generatePlan`-Fetch-Call: `enrichedAnalysis: enriched` conditional hinzufügen
- Tier-Gate Prüfung vor Übergabe (Abschnitt 2.4)
- **Änderungsumfang: ~8 Zeilen**

**`src/pages/StrategyGenerator.tsx`**
- **Observed:** StrategyGenerator rendert keine PlanResponse. Kein Change hier nötig.
- `enriched` aus AnalysisContext wird bereits gerendert (Marktlage-Card, reality_score)
- **Änderungsumfang: 0 Zeilen (kein Change erforderlich)**

**Plan-Display-Komponente (StrategyDialog.tsx oder StrategyTab.tsx — zu verifizieren)**
- **Inferred:** `negotiationPlan` State wird in einer dieser Komponenten gerendert
- Neue Sektion "Markteinordnung" wenn `negotiationPlan.marketContext !== null`
- Tier-Gate Upgrade-Hinweis wenn `marketContext === null` und Tier < kmu
- Position: nach ZOPA & Strategie-Score, vor Empfehlungen
- **Änderungsumfang: ~40 Zeilen — Datei muss vor Implementierung verifiziert werden**

### 3.4 shared-context

**`docs/contracts/frontend-backend.md`**
- POST /api/plan: Request-Body um `enrichedAnalysis?` ergänzen
- POST /api/plan: Response-Shape um `marketContext?` ergänzen
- POST /functions/v1/generate-plan: analog
- **Änderungsumfang: ~30 Zeilen**

**Kein ADR erforderlich.** Option-B-Analogie: keine neue Systemgrenze, kein neues
externes System. Erweiterung bestehender Interfaces innerhalb etablierter Pfade.

### 3.5 Supabase

**Kein Schema-Change.**
`negotiation_sessions.layer2_result` (JSONB) enthält bereits `EnrichedAnalysisResult`.
`progress_status._plan` (JSONB, gesetzt von generate-plan EF Zeile 163-165) wird um
`marketContext` erweitert — JSONB-Spalte ist schema-agnostisch, kein Migration nötig.

---

## Abschnitt 4 — Offene Abhängigkeiten

### 4.1 EnrichedAnalysisResult in AnalysisContext (Observed — kein Blocker)

**Observed:** `enriched: EnrichedData | null` ist in AnalysisContext vorhanden.
`enriched` wird in Index.tsx destrukturiert und ist im `generatePlan`-Scope verfügbar.

**Observed GAP:** Im `generatePlan`-Fetch-Call wird `enriched` nicht übergeben.
Das ist ein **1-Zeilen-Fix** — kein struktureller Blocker.

**Nicht Missing, nicht Blocked.** Die Abhängigkeit ist erfüllt — nur der Weiterleitungs-Code
fehlt (Abschnitt 3.3, Index.tsx).

### 4.2 Aufruf-Reihenfolge im UI

**Observed:** Heute triggert `useProgressEngine.ts` `generatePlan()` wenn alle 6
Progress-Punkte completed sind (`effectiveProgress` alle `true`). Die Reihenfolge
`/api/analyze` → `/api/enrich` → `generatePlan()` ist heute **nicht erzwungen**.

**Observed:** `/api/enrich` wird aus `ZopaCalculator.tsx` nach der ZOPA-Berechnung
aufgerufen — nicht automatisch nach `/api/analyze`. Ein Nutzer kann `generatePlan()`
ohne vorherigen Enrich-Call erreichen.

**Inferred:** In diesem Fall ist `enriched === null` in AnalysisContext →
`enrichedAnalysis` wird nicht übergeben → `marketContext: null` im Response.
Das ist **korrektes Verhalten** — kein Blocker. Der Plan wird generiert, nur ohne
Marktdaten-Sektion.

**Proposed:** Keine Änderung der Aufruf-Reihenfolge nötig. Das `enriched`-Conditional
in Index.tsx (Abschnitt 2.4) handelt beide Fälle korrekt:
- `enriched !== null`: Plan mit Marktdaten
- `enriched === null`: Plan ohne Marktdaten (marketContext: null)

### 4.3 Plan-Display-Komponente (zu verifizieren vor Implementierung)

**Inferred:** `negotiationPlan` State aus `useProgressEngine` wird in einer Komponente
gerendert die aktuell noch nicht identifiziert ist. **Muss vor Schritt 4 (Abschnitt 5)
verifiziert werden.**

Kandidaten: `StrategyTab.tsx`, `StrategyDialog.tsx`, `BottomBar.tsx`.

**Blocking für Schritt 4:** Die Rendering-Komponente muss bekannt sein bevor
`marketContext` dort hinzugefügt werden kann.

---

## Abschnitt 5 — Delivery-Sequenz (Proposed)

| Schritt | Beschreibung | Repo | Abhängig von | Scope | Template |
|---|---|---|---|---|---|
| 0 | FEATURE-L2-CONTEXT implementieren | negotiationcoach-backend | DONE (Spec committed) | 4–5 Dateien | 2b-DEV |
| 1 | Plan-Display-Komponente identifizieren | negotiation-buddy | — | read-only | Investigate |
| 2 | Backend: planHelpers.ts + MarketContextSection | negotiationcoach-backend | Schritt 0 DONE | ~40 Zeilen | 2b-DEV |
| 3 | Backend: routes.ts enrichedAnalysis durchreichen | negotiationcoach-backend | Schritt 2 | ~5 Zeilen | 2b-DEV |
| 4 | EF: generate-plan/index.ts erweitern | negotiation-buddy | Schritt 2 | ~50 Zeilen | 2b-DEV |
| 5 | Frontend: apiClient.ts + Index.tsx enrichedAnalysis übergeben | negotiation-buddy | Schritt 4 | ~28 Zeilen | 2b-DEV |
| 6 | Frontend: Plan-Display-Komponente um marketContext erweitern | negotiation-buddy | Schritt 1 + 5 | ~40 Zeilen | 2b-DEV |
| 7 | Contract-Docs Update | shared-context | Schritt 6 DONE | ~30 Zeilen | 2-DEV (Docs) |

**Schritt 0 ist Voraussetzung:** Ohne FEATURE-L2-CONTEXT liefert `enrichedAnalysis`
generische Marktdaten ohne Kontext → die Plan-Marktdaten wären so unspezifisch wie heute.

**Schritt 1 ist Voraussetzung für Schritt 6:** Plan-Display-Komponente muss bekannt sein.

**Acceptance Criteria (global):**

```
[ ] npx tsc --noEmit clean — backend + frontend, 0 Fehler

[ ] curl POST /functions/v1/generate-plan mit enrichedAnalysis:
    {
      "session_id": "...",
      "progress_status": {...},
      "messages": [...],
      "enrichedAnalysis": {
        "market_median": 88000,
        "market_range_min": 72000,
        "market_range_max": 105000,
        "reality_score": 5.9,
        "market_context_summary": "Senior SWE, SaaS, München",
        "market_data_source": "knowledge_graph"
      }
    }
    → Response: plan.marketContext.market_position_summary !== ""
    → Response: plan.marketContext.data_source === "knowledge_graph"

[ ] curl POST /functions/v1/generate-plan OHNE enrichedAnalysis:
    → Response: plan.marketContext === null

[ ] curl POST /functions/v1/generate-plan mit enrichedAnalysis.market_data_source === "none":
    → Response: plan.marketContext === null

[ ] Layer-1-Tests grün (Regression)
[ ] Output-Nachweis im Report (beide curl Response Bodies)
```

---

## Offene Entscheidungen für den Delivery Controller

| Entscheidung | Optionen | Empfehlung |
|---|---|---|
| Tier-Gate Ort | Frontend (Index.tsx) vs. Backend (planHelpers.ts) | **Frontend** — Analogie zu bestehenden Tier-Gates |
| EF-Lebensdauer | EF ändern (ADR-005: temporär) vs. EF überspringen | **EF ändern** — Backend-Pfad heute inactive |
| PlanObjection Drift | Sofort fixen (title hinzufügen) vs. separater Task | **Separater Task** — pre-existing, kein Blocker |
| Plan-Display-Komponente | Zu identifizieren vor Implementierung | **Schritt 1 zuerst** |
| marketContext Upgrade-Hinweis | Im Plan anzeigen wenn null + Tier < kmu | **Ja** — Conversion-Pfad für kmu-Upgrade |
