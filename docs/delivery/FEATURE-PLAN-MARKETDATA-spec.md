# FEATURE-PLAN-MARKETDATA — Verhandlungsplan Marktdaten-Integration
## Spezifikation: MarketContext-Sektion im generierten Verhandlungsplan

**Erstellt:** 2026-05-22
**Status:** PROPOSED — Review durch Delivery Controller ausstehend
**Trigger:** Delivery Controller Entscheidung 2026-05-22
**Voraussetzung:** FEATURE-L2-CONTEXT-spec.md committed (`9f12bcb`), Option B entschieden

---

## Abschnitt 1 — IST-Analyse

### 1.1 Aktuelle PlanRequest-Struktur (Observed)

**Observed** — `docs/contracts/frontend-backend.md:73-81`:

```typescript
// POST /api/plan Request (Express Backend — aktiver Contract, inaktiver Pfad)
{
  messages?: ChatMessage[];
  extractedInputs: ExtractedInputs;
  zopaResult?: object;
  analysis?: object;    // AnalysisResult (Layer 1) — kein EnrichedAnalysisResult
}
```

`EnrichedAnalysisResult` (Layer 2) ist **kein Parameter** der PlanRequest-Struktur. **Missing.**

Das `analysis`-Feld ist als `object` typisiert — kein konkreter Typ.
Selbst wenn `EnrichedAnalysisResult` übergeben würde, wäre es strukturell nicht deklariert.

**Observed** — `src/lib/apiClient.ts:115-128` (UNUSED):
```typescript
export async function generatePlan(
  messages: { role: 'user' | 'assistant'; content: string }[],
  extractedInputs: ExtractedInputs,
  zopaResult?: ZopaToolResult | null,
  analysis?: AnalysisResult | null,
  accessToken?: string
): Promise<PlanResponse>
```
`enrichedAnalysis` fehlt auch hier. Dieser Pfad ist heute dead code (zero active callers).

### 1.2 Aktuelle PlanResponse-Struktur (Observed)

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

**Frontend — kanonischer Typ** (`src/components/StrategyTab.tsx:40-56`):
```typescript
export type NegotiationPlan = {
  summary: string;
  situationAnalysis: string;
  opening: string;
  objections: { title?: string; objection: string; response: string }[];
  recommendations: string[];
  nextStep: string;
  // Legacy fallback fields (Dead Code — never populated by active paths)
  executive_summary?: string;
  situation_analysis?: string;
  opening_script?: string;
  // EF-spezifisches Zusatzfeld — nicht im Backend PlanResponse-Interface:
  numbers?: {
    first_offer?: string;
    target?: string;
    compromise_zone?: string;
  };
};
```

**Frontend — apiClient.ts PlanResponse** (`src/lib/apiClient.ts:92-99`):
```typescript
export interface PlanResponse {
  summary: string;
  situationAnalysis: string;
  opening: string;
  objections: PlanObjection[];  // { objection: string; response: string } — title fehlt
  recommendations: string[];
  nextStep: string;
}
```

**Observed Drifts:**
- `NegotiationPlan` (StrategyTab) vs. `PlanResponse` (apiClient): `numbers?` nur in `NegotiationPlan`
- `PlanObjection.title`: in `planHelpers.ts` Pflicht, in `apiClient.ts` fehlt, in `StrategyTab` optional
- `StrategyTab.NegotiationPlan` ist der tatsächlich gerenderte Typ — nicht `PlanResponse`

**Marktdaten-Sektion:** In keiner der drei Deklarationen vorhanden. **Missing.**

### 1.3 Aktiver Generierungspfad — generate-plan Edge Function (Observed)

**Observed** — `supabase/functions/generate-plan/index.ts:49`:
```typescript
// EF Input heute:
const { session_id, progress_status, messages } = await req.json();
// Nicht empfangen: extractedInputs, zopaResult, analysis, enrichedAnalysis
```

**Observed** — EF Prompt-Aufbau (`generate-plan/index.ts:61-71`):
```typescript
const contextLines = points.map((key) => {
  const val = progress_status[key];
  const summary = typeof val === "object" ? val?.summary || "" : "";
  return `${key}: ${summary}`;
}).join("\n");
// Prompt-Kontext: NUR progress_status-Summaries + letzte 15 Messages
// Kein ZOPA, kein Score, KEIN Marktdaten-Block
```

**Kein Marktdaten-Kontext im Prompt. Observed.**

**Typ-Alignment:** Die EF hat kein TypeScript-Interface für Input oder Output — native JSON-Deserialisierung via `await req.json()`. Das Response-Objekt (`plan`) wird inline zusammengebaut (Zeile 144-152) und entspricht näherungsweise `NegotiationPlan` inklusive `numbers`.

**Observed** — Vertrag in `docs/contracts/frontend-backend.md:540-565`:
Die EF empfängt `{ session_id?, progress_status, messages? }` und gibt `{ plan: {...} }` zurück.
`enrichedAnalysis` ist **nicht im Contract deklariert**. **Missing.**

### 1.4 Rendering in StrategyDialog.tsx und StrategyTab.tsx (Observed)

**Observed** — `src/components/StrategyTab.tsx:155-330` (Plan-Rendering-Hauptkomponente):
- Sektion 1: `summary` — Situationszusammenfassung
- Sektion 2: `situationAnalysis` — Detailanalyse der 6 Progress-Punkte
- Sektion 3: Zahlen/Angebote — `numbers.first_offer`, `numbers.target`, `numbers.compromise_zone`
- Sektion 4: `opening` — Eröffnungssatz
- Sektion 5: `objections` — Einwände & Antworten
- Sektion 6: `recommendations` — Empfehlungen
- Sektion 7: `nextStep` — Nächste Aktion

**Kein Platzhalter für Marktdaten. Missing.**

**Observed** — `src/components/StrategyDialog.tsx:57-78`: Rendert denselben Plan als Dialog-View. Nutzt `NegotiationPlan` aus `StrategyTab`.

**Observed** — `src/pages/Index.tsx:876`:
```typescript
plan={negotiationPlan}  // NegotiationPlan | null
```
`negotiationPlan` wird in `StrategyTab` via `BottomBar` als Prop übergeben.

**Observed** — `StrategyGenerator.tsx` rendert **nicht** `NegotiationPlan` — nur AnalysisContext-Daten (`analysis`, `enriched`, `zopaResult`). Kein Change dort nötig.

### 1.5 Tier-Gate aktuell (Observed)

**Observed** — `docs/contracts/frontend-backend.md:577`:
```
Tier Gate: Present, inactive — commented stub in `generate-plan/index.ts`.
Uncomment `if (tier === 'free') return 403` block to enforce a paid-tier requirement.
```

**Observed:** Die EF löst Tier via JWT auf (`personaType → tier`, Zeile 44-47), nutzt ihn aber für keinen Gate. Jeder authentifizierte User kann heute einen Plan generieren. **Tier-Gate ist inaktiv.**

**Implikation für Marktdaten-Integration:** Marktdaten im Plan sind Layer-2-Inhalte (kmu/profi). Das Tier-Gate muss für `marketContext` aktiviert oder neu implementiert werden. **Proposed:** `marketContext` wird nur befüllt wenn Tier `kmu` oder `profi` UND Layer-2-Daten vorhanden.

---

## Abschnitt 2 — Integration Design

### Empfehlung: **Option A — Neue dedizierte Sektion `marketContext`**

**Begründung (Proposed):**
1. **Testbarkeit:** `marketContext: null` vs. `marketContext: {...}` ist curl-testbar.
   Einweben in `summary`/`recommendations` wäre unsichtbar und schwer zu verifizieren.
2. **Tier-Gate-Klarheit:** `null` = "kein Zugang" (explizites Signal an Frontend für Upgrade-Hinweis).
   Fehlendes Feld = "Feature nicht implementiert" (andere Semantik).
3. **Frontend-Rendering:** `StrategyTab.tsx` kann eine eigene Sektion konditionell rendern
   und einen Upgrade-CTA zeigen wenn `marketContext === null`.
4. **Rückwärtskompatibilität:** `marketContext?` ist optional →
   bestehende Pfade ohne `enrichedAnalysis` brechen nicht.

Option B (Einweben ohne Contract-Change) wird **abgelehnt:** Marktdaten im Plan müssen
explizit und tier-gebunden sein — implizites Einweben macht das Tier-Gate unimplementierbar.

### 2.1 Prompt-Design (Option A)

**Proposed Erweiterung der EF und `buildPlanSystemPrompt()`:**

```
// Marktdaten-Block — nur eingefügt wenn enrichedAnalysis vorhanden
// UND market_data_source !== 'none':

## Marktdaten-Kontext (kmu/profi)
Marktmedian: {market_median}€
Marktspanne: {market_range_min}€ – {market_range_max}€
Reality Score: {reality_score}% ({über/unter/auf Höhe des} Marktmedians)
Markteinordnung: {market_context_summary}
Datenquelle: {market_data_source}

Füge dem JSON-Output eine "marketContext"-Sektion hinzu:
"marketContext": {
  "market_position": "1 Satz: Position des Ziels relativ zum Median",
  "market_range_summary": "1-2 Sätze: Marktspanne + Kontext",
  "reality_assessment": "1-2 Sätze: Ist die Forderung marktgerecht?",
  "data_source": "{market_data_source}"
}
```

**Fallback wenn kein `enrichedAnalysis` oder `market_data_source === 'none'`:**
```
Keine Marktdaten verfügbar. Setze "marketContext": null im JSON-Output.
Halluziniere keine Marktwerte.
```

**Konkretes Beispiel — Gehalt Senior SWE München:**

*Prompt-Block mit Marktdaten:*
```
## Marktdaten-Kontext (kmu/profi)
Marktmedian: 88.000€
Marktspanne: 72.000€ – 105.000€
Reality Score: +5,9% (leicht über dem Marktmedian)
Markteinordnung: Senior Software Engineer, SaaS, München, 200 MA — Spanne 78–105k€ p.a.
Datenquelle: knowledge_graph
```

*Erwartetes Claude-Output:*
```json
"marketContext": {
  "market_position": "Ihr Ziel von 44.000€ liegt 50% unter dem Marktmedian von 88.000€ für Senior SWE in München.",
  "market_range_summary": "Typische Vergütung für Ihre Position: 72.000–105.000€ Jahresbrutto. Ihr aktuelles Gehalt und Ihr Ziel liegen deutlich darunter.",
  "reality_assessment": "Der Markt rechtfertigt eine Forderung von 75.000–88.000€. Ihre Verhandlungsposition ist stärker als gedacht.",
  "data_source": "knowledge_graph"
}
```

### 2.2 Tier-Gate-Design (Proposed)

**Proposed:** Tier-Gate sitzt im **Request-Aufbau** (Index.tsx) — nicht im Prompt-Builder.

```typescript
// Index.tsx — erweiterter generatePlan-Call (Proposed)
body: JSON.stringify({
  session_id: activeSessionId,
  progress_status: effectiveProgress,
  messages: messages.slice(-15).map(...),
  // enrichedAnalysis nur wenn kmu/profi UND Daten vorhanden:
  ...(enriched
    && enriched.market_data_source !== 'none'
    && (tier === 'kmu' || tier === 'profi')
    ? { enrichedAnalysis: enriched }
    : {}),
})
```

Der **Prompt-Builder** prüft nur ob `enrichedAnalysis` übergeben wurde:
- `enrichedAnalysis` vorhanden + `market_data_source !== 'none'` → Marktdaten-Block
- Sonst → Fallback-Block ("marketContext: null")

**Begründung:** Tier ist bereits im Frontend bekannt (aus JWT via useAnalysis/useAuth).
Redundante Backend-Prüfung ist optional — das bestehende `/api/enrich`-Gate
(`requireTier('kmu')`) stellt bereits sicher, dass `enriched` nur für kmu/profi befüllt ist.

**Observed** — `enriched: EnrichedData | null` ist bereits in `useAnalysis()` verfügbar
und in `Index.tsx:78` destrukturiert. Das Conditional braucht nur einen `tier`-Check.

### 2.3 Abhängigkeit zu FEATURE-L2-CONTEXT-spec.md

**Status: ENTSCHIEDEN** — FEATURE-L2-CONTEXT-spec.md committed `9f12bcb`, Option B gewählt.

**Felder aus `EnrichedAnalysisResult` die in den Plan-Prompt übergeben werden:**
```typescript
enriched.market_median         // Pflicht — Kern-Marktdatum
enriched.market_range_min      // Pflicht — Spanne
enriched.market_range_max      // Pflicht — Spanne
enriched.reality_score         // Pflicht — Positionierung
enriched.market_context_summary // Optional — AI-generierte Einordnung
enriched.market_data_source    // Pflicht — Quellen-Transparenz
```

**Inferred:** Nach FEATURE-L2-CONTEXT-Implementierung (Option B: Kontext-Extraktion
aus `context_notes`) werden diese Felder präziser und kontext-spezifischer befüllt.
Die Plan-Marktdaten werden dadurch automatisch qualitativ hochwertiger — kein weiterer
Code-Change in FEATURE-PLAN-MARKETDATA nötig.

---

## Abschnitt 3 — Contract-Änderungen

### 3.1 PlanRequest-Erweiterung (Proposed)

```typescript
// Proposed — neue PlanRequest-Struktur (Backend + EF)
interface PlanRequest {
  messages?: ChatMessage[];
  extractedInputs: ExtractedInputs;
  zopaResult?: object;
  analysis?: object;               // AnalysisResult (Layer 1) — unverändert
  enrichedAnalysis?: EnrichedAnalysisResult;  // NEU — optional, rückwärtskompatibel
}
```

**Rückwärtskompatibel:** `optional` → Callers ohne `enrichedAnalysis` brechen nicht.

**Import:** `EnrichedAnalysisResult` aus `src/types/index.ts` (negotiationcoach-backend)
bzw. als lokaler Typ in `src/lib/apiClient.ts` (negotiation-buddy, kein shared package).

### 3.2 PlanResponse-Erweiterung (Option A) — alle drei Deklarationen

**Neues Interface:**
```typescript
// Proposed — neu in planHelpers.ts oder types.ts
interface MarketContextSection {
  market_position: string;       // "Ihr Ziel liegt X% über/unter dem Marktmedian."
  market_range_summary: string;  // "Typische Spanne: 72–105k€ für diese Position."
  reality_assessment: string;    // "Die Forderung ist marktgerecht/aggressiv/..."
  data_source: 'web_search' | 'knowledge_graph' | 'none';
}
```

**Backend — `src/api/planHelpers.ts` (Proposed):**
```typescript
export interface PlanResponse {
  summary: string;
  situationAnalysis: string;
  opening: string;
  objections: Array<{ title: string; objection: string; response: string }>;
  recommendations: string[];
  nextStep: string;
  marketContext?: MarketContextSection | null;  // NEU
}
```

**Frontend — `src/components/StrategyTab.tsx:NegotiationPlan` (Proposed):**
```typescript
export type NegotiationPlan = {
  summary: string;
  situationAnalysis: string;
  opening: string;
  objections: { title?: string; objection: string; response: string }[];
  recommendations: string[];
  nextStep: string;
  numbers?: { first_offer?: string; target?: string; compromise_zone?: string };
  marketContext?: MarketContextSection | null;  // NEU
  // Legacy fields unverändert...
};
```

**Frontend — `src/lib/apiClient.ts:PlanResponse` (Proposed):**
```typescript
export interface PlanResponse {
  summary: string;
  situationAnalysis: string;
  opening: string;
  objections: PlanObjection[];
  recommendations: string[];
  nextStep: string;
  marketContext?: MarketContextSection | null;  // NEU
}
```

**Warum kein shared package:** Observed — kein shared package in dieser Architektur.
Typ wird in beiden Repos separat deklariert. Vorhandener Präzedenzfall: `PlanResponse`
existiert bereits in zwei Repos unabhängig (documented in frontend-backend.md:101).

### 3.3 generate-plan Edge Function Contract (Proposed)

**Delta Request:**
```
Vorher: { session_id?, progress_status, messages? }
Nachher: { session_id?, progress_status, messages?, enrichedAnalysis?: EnrichedAnalysisResult }
```

**Delta Response:**
```
Vorher:  { plan: { summary, situationAnalysis, opening, objections, recommendations, nextStep, numbers? } }
Nachher: { plan: { ..., marketContext?: MarketContextSection | null } }
```

**Rückwärtskompatibilität:** Alle neuen Felder optional — Clients ohne `enrichedAnalysis`
erhalten `marketContext: null`.

### 3.4 frontend-backend.md Update-Anforderungen

**POST /api/plan (Express Backend — kanonisch, ADR-005):**

Delta Request — hinzufügen:
```typescript
enrichedAnalysis?: EnrichedAnalysisResult;  // optional — Layer 2 Output für Marktdaten-Sektion
```

Delta Response — hinzufügen:
```typescript
marketContext?: {
  market_position: string;
  market_range_summary: string;
  reality_assessment: string;
  data_source: 'web_search' | 'knowledge_graph' | 'none';
} | null;
// null wenn Tier < kmu oder market_data_source === 'none'
```

**POST /functions/v1/generate-plan (Edge Function — aktiver Pfad):**

Delta Request — hinzufügen:
```typescript
enrichedAnalysis?: {
  market_median: number;
  market_range_min: number;
  market_range_max: number;
  reality_score: number;
  market_context_summary?: string;
  market_data_source: 'web_search' | 'knowledge_graph' | 'none';
};
```

Delta Response — `plan`-Objekt um `marketContext` erweitern (wie oben).

---

## Abschnitt 4 — Frontend-Integration

### 4.1 Datenpfad zu generate-plan (Observed)

```
/api/enrich Response
  → setAnalysisResult(sessionId, analysis, enrichedData)  [ZopaCalculator.tsx]
  → AnalysisContext.enriched: EnrichedData | null          [Observed]
  → Index.tsx: const { enriched } = useAnalysis()          [Observed, Zeile 78]
  → Index.tsx: generatePlan() closure                       [Zeile 441-473]
     → aktuell: enriched NICHT übergeben                   [Observed GAP]
     → proposed: enrichedAnalysis: enriched (conditional)
```

**Observed:** `enriched` ist in Index.tsx im Scope und bereits für die Marktdaten-Card
(Zeile 841-850) genutzt. Es ist **kein neues State-Feld** nötig — nur Weitergabe.

### 4.2 generatePlan()-Erweiterung in Index.tsx und apiClient.ts (Proposed)

**Index.tsx — Fetch-Call (aktiver Pfad, Proposed):**
```typescript
// Tier prüfen vor Übergabe (enriched ist nur für kmu/profi befüllt,
// da /api/enrich requireTier('kmu') hat — defensives Conditional):
const marketData = enriched?.market_data_source !== 'none' ? enriched : null;

body: JSON.stringify({
  session_id: activeSessionId,
  progress_status: effectiveProgress,
  messages: messages.slice(-15).map((m) => ({ role: m.role, content: m.content })),
  ...(marketData ? { enrichedAnalysis: marketData } : {}),
})
```

**apiClient.ts generatePlan() (Migrationsziel-Pfad, Proposed):**
```typescript
export async function generatePlan(
  messages: ChatMessage[],
  extractedInputs: ExtractedInputs,
  zopaResult?: ZopaToolResult | null,
  analysis?: AnalysisResult | null,
  enrichedAnalysis?: EnrichedAnalysisResult | null,  // NEU
  accessToken?: string
): Promise<PlanResponse>
```

### 4.3 StrategyTab.tsx Rendering (Proposed — Option A)

**Neue Sektion nach Sektion 7 (nextStep), vor oder nach Empfehlungen:**

```tsx
// Proposed — neue Sektion in StrategyTab.tsx
{plan.marketContext !== undefined && (
  <section>
    <h3>Markteinordnung</h3>
    {plan.marketContext === null ? (
      // Tier-Gate UI: Upgrade-Hinweis für privat/free
      <UpgradeHint feature="Marktdaten" requiredTier="kmu" />
    ) : (
      <MarketContextCard context={plan.marketContext} />
    )}
  </section>
)}
// marketContext === undefined → kein Feature implementiert → Sektion nicht anzeigen
```

**ADR-001 Hinweis:** Frontend-Gate ist UI-only — primäres Gate ist das Server-seitige Conditional
beim Aufbau des Prompts (enrichedAnalysis wird nur für kmu/profi übergeben). Das Frontend zeigt
`null` als Upgrade-Hinweis, verlässt sich aber auf das Backend als autoritären Gate.

### 4.4 UX-Verhalten bei fehlenden Marktdaten (Proposed)

| Fall | `enrichedAnalysis` übergeben? | `marketContext` in Response | UX |
|---|---|---|---|
| Tier `privat`/`free` | Nein | `null` | Sektion "Markteinordnung" mit Upgrade-Hinweis sichtbar |
| Tier `kmu`/`profi`, Layer 2 noch nicht aufgerufen | Nein (`enriched === null`) | `null` | Gleicher Upgrade-Hinweis ODER kein Hinweis (TBD — offene Entscheidung) |
| Tier `kmu`/`profi`, Layer 2 aufgerufen, market_data_source = 'none' | Nein (Conditional) | `null` | Gleicher Hinweis |
| Tier `kmu`/`profi`, Layer 2 erfolgreich | Ja | `{ market_position, ... }` | Marktdaten-Sektion vollständig sichtbar |
| Feature nicht deployed (alt) | — | `undefined` (Feld fehlt) | Sektion komplett ausgeblendet |

**Offene Entscheidung:** Fall 2 — soll ein kmu-User der noch keinen Enrich-Call gemacht hat,
einen Upgrade-Hinweis sehen (verwirrend) oder gar keinen Hinweis (Marktdaten-Sektion komplett hidden)?
**Empfehlung (Proposed):** Kein Hinweis wenn `marketContext === null` und `enriched === null` —
Plan-Generierung ohne Layer 2 ist der normale privat/free-Pfad. Upgrade-Hinweis nur wenn
Tier < kmu (explizites Feature-Gate-Signal).

---

## Abschnitt 5 — Impact Assessment

### 5.1 Backend (negotiationcoach-backend)

| Datei | Änderung | Scope |
|---|---|---|
| `src/api/planHelpers.ts` | `buildPlanSystemPrompt()` um `enrichedAnalysis?` erweitern, Marktdaten-Block einweben; `parsePlanResponse()` um `marketContext` erweitern | ~40 Zeilen |
| `src/api/routes.ts` | `enrichedAnalysis` aus Request-Body lesen, an `buildPlanSystemPrompt()` übergeben | ~5 Zeilen |
| Neues Interface `MarketContextSection` | In `planHelpers.ts` oder neuem `src/lib/planTypes.ts` | ~10 Zeilen |
| **Gesamt** | 3 Dateien, ~55 Zeilen | — |

### 5.2 Edge Function (negotiation-buddy/supabase/functions/generate-plan)

| Datei | Änderung | Scope |
|---|---|---|
| `generate-plan/index.ts` | Input-Parsing um `enrichedAnalysis?` erweitern; Prompt-Aufbau um Marktdaten-Block; Response-Parsing um `marketContext` | ~50 Zeilen |

**Observed** — Tier ist in der EF bereits verfügbar (Zeile 44-47, `tier`-Variable).
**Proposed:** Kein Aktivieren des kommentierten Tier-Gate-Stubs für Plan-Generierung.
Marktdaten-Gate sitzt im Prompt (enrichedAnalysis-Conditional) — kein 403 für privat-Tier.

**ADR-005-Implikation (Proposed):**
ADR-005 sagt: EF ist temporär, Express Backend ist kanonisch. Änderungen an der EF
sind akzeptabel für MVP, da:
1. Der Express-Pfad (`/api/plan`) heute inaktiv ist (zero active callers)
2. Die EF-Änderung ist defensiv und rückwärtskompatibel
3. Bei Migration zu Express (RFB-004 Phase C) wird die EF-Änderung retired —
   aber `planHelpers.ts`-Erweiterung bleibt und wird dann aktiv

**Kein neues ADR erforderlich** — Änderung liegt innerhalb des bestehenden ADR-005-Rahmens
("EF ist temporary, änderbar bis Migration").

### 5.3 Frontend (negotiation-buddy)

| Datei | Änderung | Scope |
|---|---|---|
| `src/lib/apiClient.ts` | `generatePlan()` Signatur + `PlanResponse` Typ + `MarketContextSection` Interface | ~20 Zeilen |
| `src/pages/Index.tsx` | `enrichedAnalysis` conditional in Fetch-Call übergeben | ~8 Zeilen |
| `src/components/StrategyTab.tsx` | `NegotiationPlan` Typ + neue Rendering-Sektion | ~40 Zeilen |
| `src/components/StrategyDialog.tsx` | `marketContext`-Sektion in Dialog-View | ~20 Zeilen |
| **Gesamt** | 4 Dateien, ~88 Zeilen | — |

**Kein neues State-Feld in AnalysisContext erforderlich** — `enriched` ist bereits vorhanden.

### 5.4 Supabase

**Kein Schema-Change.**
`negotiation_sessions.layer2_result` (JSONB) enthält `EnrichedAnalysisResult` bereits.
`negotiation_sessions.progress_status._plan` (JSONB) wird um `marketContext` erweitert —
JSONB ist schema-agnostisch, keine Migration nötig.

### 5.5 ADR-Bedarf

**Kein neues ADR.** Begründung (Proposed):
- Keine neue Systemgrenze
- Kein neues externes System
- EF-Änderung innerhalb ADR-005-Rahmen
- Interface-Erweiterung ohne Contract-Breaking-Change

**Benötigte Docs-Updates nach Implementierung:**
- `docs/contracts/frontend-backend.md` — Request/Response Delta (Abschnitt 3.4)
- Optional: `docs/service-catalog.md` — `buildPlanSystemPrompt()` Signatur

---

## Abschnitt 6 — Delivery-Plan (Proposed)

| Schritt | Beschreibung | Repo | Abhängig von | Dateien | Template |
|---|---|---|---|---|---|
| 0 | FEATURE-L2-CONTEXT implementieren | negotiationcoach-backend | **Voraussetzung** (Spec `9f12bcb`) | 4–5 | 2b-DEV |
| 1 | Dieses Dokument reviewed + GO | shared-context | Schritt 0 DONE | — | — |
| 2 | Backend: `MarketContextSection` + `PlanResponse`-Erweiterung + `planHelpers.ts` | negotiationcoach-backend | Schritt 1 | ~3 | 2b-DEV |
| 3 | Backend: `routes.ts` enrichedAnalysis durchreichen | negotiationcoach-backend | Schritt 2 | 1 | 2b-DEV |
| 4 | EF: `generate-plan/index.ts` erweitern | negotiation-buddy | Schritt 2 | 1 | 2b-DEV |
| 5 | Frontend: `apiClient.ts` + `Index.tsx` enrichedAnalysis übergeben | negotiation-buddy | Schritt 4 | 2 | 2b-DEV |
| 6 | Frontend: `StrategyTab.tsx` + `StrategyDialog.tsx` Rendering | negotiation-buddy | Schritt 5 | 2 | 2b-DEV |
| 7 | Integration-Test: alle Tier-Kombinationen + beide Plan-Pfade | beide | Schritt 6 | smoke test | Template 1-DEV |
| 8 | Contract-Docs Update | shared-context | Schritt 7 DONE | 1–2 | 2-DEV (Docs) |

**Acceptance Criteria (global):**

```
[ ] npx tsc --noEmit — negotiationcoach-backend: 0 Fehler
[ ] npx tsc --noEmit — negotiation-buddy: 0 Fehler

[ ] curl POST /functions/v1/generate-plan mit enrichedAnalysis (kmu-Tier):
    → plan.marketContext.market_position !== ""
    → plan.marketContext.data_source === "knowledge_graph"

[ ] curl POST /functions/v1/generate-plan ohne enrichedAnalysis (privat-Tier):
    → plan.marketContext === null

[ ] curl POST /functions/v1/generate-plan mit enrichedAnalysis.market_data_source === "none":
    → plan.marketContext === null

[ ] Layer-1-Tests grün (Regression — planHelpers.ts parsePlanResponse)
[ ] Output-Nachweis: beide curl Response Bodies im Report dokumentiert
```

**Zwei-Location-Closure je Schritt:**
- Impl-Commit in Target-Repo
- Docs-Stamp in shared-context (`docs/delivery/bugs/` oder Spec-Update)

---

## Offene Entscheidungen für den Delivery Controller

| Entscheidung | Optionen | Empfehlung |
|---|---|---|
| Tier-Gate Ort | Frontend (Index.tsx) vs. Backend | **Frontend** — Tier bereits bekannt, enriched nur für kmu/profi befüllt |
| UX bei kmu + kein Enrich | Upgrade-Hinweis vs. kein Hinweis | **Kein Hinweis** — Plan ohne Marktdaten ist normaler Fall |
| `NegotiationPlan` vs. `PlanResponse` Drift | Sofort vereinheitlichen vs. separater Task | **Separater Task** — pre-existing, kein Blocker |
| Schritt 0 (L2-CONTEXT) als Voraussetzung | Strikt vs. mit generischen Marktdaten beginnen | **Strikt** — ohne Kontext sind Marktdaten im Plan unbrauchbar |
