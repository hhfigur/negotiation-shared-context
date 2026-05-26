# FEATURE-L2-CONTEXT — Implementation Plan

**Feature:** Layer 2 Marktdaten-Kontextualisierung via context_notes
**Strategy:** Option B — Kontext-Extraktion via Claude Pre-Processing
**Status:** DONE — implementiert 2026-05-26
**Spec:** `docs/delivery/FEATURE-L2-CONTEXT-spec.md` (9f12bcb)
**Impact Check:** PASSED — LOW risk, keine protected files, kein Contract-Change
**Plan erstellt:** 2026-05-26

---

## Design Gate Answers

### DGQ-1: extractMarketContext() — Prompt-Design

**Modell:** `MODELS.HAIKU`

Begründung: Die Aufgabe ist strukturierte JSON-Extraktion aus Freitext — keine Reasoning-Intensität.
Haiku ist schnell (~0.5s) und günstig (~0.01–0.02€ pro Call). Der Tier des Nutzers beeinflusst die
Extraktionsqualität nicht. `modelRouter.selectModel()` ist für nutzer-seitige LLM-Tasks — dieser
Schritt ist ein Backend-interner Pre-Processing-Step. Haiku ist die richtige Wahl.

**max_tokens:** 256 — JSON mit 4–5 Feldern à max. 50 Zeichen.

**System-Prompt:**
```
Du bist ein Daten-Extraktor für Verhandlungskontext.
Extrahiere strukturierte Felder aus dem gegebenen Freitext.
Antworte ausschließlich mit einem validen JSON-Objekt.
Fehlende Informationen: Feld weglassen. Keine leeren Strings. Kein null.
Keine Annahmen oder Erfindungen — nur explizit im Text enthaltene Informationen.
```

**User-Prompt (type-spezifisch — Beispiel `gehalt`):**
```
Verhandlungstyp: gehalt
Kontext-Text: "Senior Software Engineer, 5 Jahre Erfahrung, SaaS-Startup, ~200 Mitarbeiter, München"

Extrahiere folgende Felder wenn im Text enthalten:
- job_role: Berufsbezeichnung (max. 50 Zeichen)
- seniority_level: z. B. "Junior", "Mid", "Senior", "Principal"
- industry: Branche z. B. "SaaS", "Finanzwesen", "Pharma"
- company_size: Unternehmensgröße z. B. "Startup <50 MA", "KMU 200 MA"

Nur enthaltene Informationen. Keine Felder erfinden.
```

**Type-spezifische Feld-Hints per `FIELD_HINTS: Record<NegotiationType, string>`:**
```typescript
const FIELD_HINTS: Record<NegotiationType, string> = {
  gehalt:    '- job_role (Berufsbezeichnung)\n- seniority_level ("Junior"/"Mid"/"Senior"/"Principal")\n- industry (Branche)\n- company_size (Unternehmensgröße)',
  miete:     '- property_type (Wohnungstyp)\n- size_sqm_range (Größenkategorie)\n- location_type (Lage)',
  lieferant: '- product_category (Produktkategorie)\n- contract_volume_range (Jahresvolumen)\n- contract_duration (Vertragslaufzeit)',
  m_a:       '- target_industry (Branche des Zielunternehmens)\n- company_size_range (Größe)\n- deal_type (z. B. "Strategic Acquisition")',
  sonstige:  '- description (Kurzbeschreibung der Verhandlung, max. 200 Zeichen)',
};
```

**JSON-Response-Parsing:**
```typescript
// 1. Text-Block extrahieren
const textBlock = response.content.find(b => b.type === 'text');
if (!textBlock || textBlock.type !== 'text') return fallback;

// 2. JSON.parse in try/catch — Claude liefert gelegentlich Markdown-Fences
let raw: unknown;
try {
  // Strip ```json ... ``` fence if present
  const text = textBlock.text.trim().replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '');
  raw = JSON.parse(text);
} catch {
  console.warn('[extractMarketContext] JSON.parse failed — fallback to generic query');
  return fallback;
}

// 3. Zod-Validierung (alle Felder optional — passiert niemals hard-fail)
const parsed = MarketContextExtractedSchema.safeParse(raw);
if (!parsed.success) return fallback;

return { negotiation_type: negotiationType, region, ...parsed.data };
```

**Fallback-Definition:**
```typescript
const fallback: MarketContext = { negotiation_type: negotiationType, region };
```

**Fehlerfall-Verhalten:**
- `context_notes` leer oder kürzer als 10 Zeichen → sofortiger Fallback, KEIN Claude-Call
- Claude-Call schlägt fehl (Timeout, API-Error) → Fallback, kein Error-Throw
- JSON.parse schlägt fehl → Fallback
- Zod-Validierung schlägt fehl → Fallback (praktisch unmöglich, da alle Felder optional)
- In allen Fallback-Fällen: `console.warn()` mit kurzem Kontext-String

**Invariante:** `extractMarketContext()` wirft nie. Upstream `resolveMarketData()` sieht immer
ein valides `MarketContext`-Objekt.

---

### DGQ-2: contextHash-Kollisionstoleranz

**Formel (aus Spec Abschnitt 4.2):**
```typescript
function buildContextHash(context: MarketContext): string {
  const normalized = [
    context.negotiation_type,
    (context.job_role ?? '').toLowerCase().trim().slice(0, 30),
    (context.seniority_level ?? '').toLowerCase().trim(),
    (context.industry ?? '').toLowerCase().trim().slice(0, 30),
  ]
    .filter(Boolean)
    .join(':');
  return normalized || context.negotiation_type;
}
```

**Beispiel-Hashes:**
```
"Senior Software Engineer, SaaS, München" → "gehalt:senior software engineer:senior:saas"
"Buchhalter, Junior, Bank"                → "gehalt:buchhalter:junior:finanzwesen"
"Product Manager, Mid, E-Commerce"        → "gehalt:product manager:mid:e-commerce"
Kein context_notes (Fallback)             → "gehalt"
```

**Kollisionsanalyse für `gehalt` + `München` (Beispiel):**

| Dimension    | Realistische Werte    | Anzahl |
|--------------|-----------------------|--------|
| job_role     | SWE, PM, Controller, Buchhalter, Marketing Mgr, Data Scientist, UX, DevOps, Sales, Jurist | ~10–15 |
| seniority    | junior, mid, senior, lead, principal | 5 |
| industry     | saas, finanzwesen, pharma, automobil, einzelhandel, logistik, consulting, pharma, medien, öffentlich | ~10 |

**Unique Hashes:** 12 × 5 × 10 = **600 distinct Kombinationen** pro Type+Region.

Verglichen mit Status quo (1 Hash pro Type+Region): **600× Verbesserung**.

**Erwünschte Kollisionen** (Cache-Sharing als Feature):
Zwei Senior SWEs bei SaaS-Startups in München teilen denselben Cache-Eintrag → korrekt,
ihre Marktdaten sind identisch. Cache-Sharing reduziert API-Calls ohne Qualitätsverlust.

**Unerwünschte Kollisionen** (falsche Daten):
Nach Implementierung: ~0% — Nutzer mit `context_notes` bekommen typ-spezifische Daten.
Ohne `context_notes` (Fallback): `category = "gehalt"` → identisches Verhalten wie heute.

**Bewertung:** 3 Kerndimensionen sind ausreichend. Weitere Dimensionen (company_size, remote_policy)
verbessern die Summary-Qualität, nicht die Cache-Granularität — bewusste Entscheidung aus Spec.

---

### DGQ-3: resolveMarketData() Rückwärtskompatibilität

**Alle bestehenden Aufrufer:**

| Datei | Aufruf | Anpassung nötig |
|---|---|---|
| `src/layer2/index.ts:51` | `resolveMarketData(inputs.negotiation_type, tier, region)` | Ja — 4. Arg `inputs.context_notes` hinzufügen (Schritt 6) |
| `tests/layer2/layer2.test.ts` | Kein direkter Aufruf — nur via `enrichWithMarketData()` | Nein |

**Resultat:** Genau ein Aufrufer. Der neue Parameter `contextNotes?: string` ist der
letzte Parameter (optional) → vollständig rückwärtskompatibel. Bestehender Aufruf
ohne 4. Argument kompiliert weiterhin korrekt (TypeScript: `contextNotes = undefined`).

---

### DGQ-4: Tests — layer2.test.ts Erweiterung

**Status bestehende Tests:**
```typescript
// NOTE: These tests are execution-proof only — no assertions.
```
Die bestehenden Tests sind reine Smoke-Tests (run-and-log, keine Assertions).

**Bestehende Tests nach Implementierung:**
- Kompilieren ohne Änderung: `enrichWithMarketData(layer1Result, testInputs, 'München')` —
  Signatur bleibt unverändert ✓
- Exercieren automatisch den neuen Extraction-Pfad, da `testInputs.context_notes` bereits
  `'Senior Software Engineer, 5 Jahre Erfahrung...'` enthält und `tier: 'profi'` ✓
- Kein Update nötig für bestehende Test-Infrastruktur ✓

**Neue Test-Cases (Schritt 8):**

| Test | Input | Expected Output |
|---|---|---|
| `extractMarketContext` — reich | `negotiation_type: 'gehalt', contextNotes: 'Senior SWE, SaaS, München, ~200 MA'` | Objekt mit `job_role`, `seniority_level`, `industry` gesetzt |
| `extractMarketContext` — leer | `contextNotes: undefined` | `{ negotiation_type: 'gehalt' }` — nur Pflichtfelder |
| `extractMarketContext` — zu kurz | `contextNotes: 'Gehalt'` (< 10 Zeichen) | Fallback ohne Claude-Call |
| `searchMarketData` — mit Kontext | `MarketContext { negotiation_type: 'gehalt', job_role: 'Software Engineer', seniority_level: 'Senior', industry: 'SaaS', region: 'München' }` | `median > 70000` (kontextspezifisch) |
| Cache-Key-Differenzierung | Gleicher `type+region`, unterschiedlicher `job_role` → `buildContextHash()` | Unterschiedliche Hash-Strings |

**Signatur-Impact auf Tests:**
`searchMarketData(type, region?)` → `searchMarketData(context: MarketContext)`:
Tests rufen `searchMarketData` nie direkt auf → 0 bestehende Tests brechen.

---

### DGQ-5: ENGB01-Check — Architekturkonformität

| Kriterium | Status |
|---|---|
| `extractMarketContext.ts` liegt in `src/layer2/` | ✓ Layer-2-intern |
| Einziger Aufrufer: `marketDataResolver.ts` (Layer 2) | ✓ Kein Layer-Boundary-Crossing |
| Nutzt `claudeClient` (Utility, layer-agnostisch) | ✓ |
| Kein direkter Supabase-Zugriff (bleibt in `knowledgeGraph.ts`) | ✓ |
| Kein Import aus Layer 0, Layer 1, Layer 3 | ✓ |
| Kein neuer externer HTTP-Client | ✓ |
| Tier-Gate bleibt in `resolveMarketData()` — nicht verschoben | ✓ |
| `enrichWithMarketData()` Signatur unverändert → ADR-001 konform | ✓ |

**ENGB01: PASS.** Keine Layer-Boundary-Verletzung.

---

## Implementierungsplan — Schritte 2–9

---

### SCHRITT 2: MarketContext Interface

**Datei(en):**
- `src/layer2/types.ts` — NEU
- `src/layer2/schemas.ts` — GEÄNDERT (1 neues Schema hinzugefügt)

**Änderungstyp:** neu (types.ts) / geändert (schemas.ts)

**Abhängig von:** — (standalone, keine Abhängigkeit)

**Was genau ändert sich:**
- Neue Datei `src/layer2/types.ts` mit `MarketContext`-Interface (alle Felder aus Spec 5.1)
- `src/layer2/schemas.ts`: `MarketContextExtractedSchema` hinzufügen (Zod, alle Felder optional)
- Kein Änderung an `src/types/index.ts` (domain interface — protected)

**TypeScript-Interfaces:**
```typescript
// src/layer2/types.ts (NEU)
import { NegotiationType } from '../types/index';

export interface MarketContext {
  negotiation_type: NegotiationType;
  region?: string;
  // gehalt
  job_role?: string;
  seniority_level?: string;
  industry?: string;
  company_size?: string;
  // miete
  property_type?: string;
  size_sqm_range?: string;
  location_type?: string;
  // lieferant
  product_category?: string;
  contract_volume_range?: string;
  contract_duration?: string;
  // m_a
  target_industry?: string;
  company_size_range?: string;
  deal_type?: string;
  // fallback
  extracted_context?: string;
}
```

```typescript
// src/layer2/schemas.ts (ERGÄNZUNG)
export const MarketContextExtractedSchema = z.object({
  job_role:               z.string().max(50).optional(),
  seniority_level:        z.string().optional(),
  industry:               z.string().max(30).optional(),
  company_size:           z.string().optional(),
  property_type:          z.string().optional(),
  size_sqm_range:         z.string().optional(),
  location_type:          z.string().optional(),
  product_category:       z.string().optional(),
  contract_volume_range:  z.string().optional(),
  contract_duration:      z.string().optional(),
  target_industry:        z.string().optional(),
  company_size_range:     z.string().optional(),
  deal_type:              z.string().optional(),
  description:            z.string().max(200).optional(),
});
```

**Fehlerfall / Fallback:** Nicht zutreffend — reine Typdefinition.

**Rückwärtskompatibilität:** Rein additiv — keine bestehenden Importe betroffen.

**Test-Abdeckung:** Kein eigener Test. Wird durch Schritt 3 und 4 indirekt verifiziert.

---

### SCHRITT 3: marketContextExtractor.ts

**Datei(en):** `src/layer2/marketContextExtractor.ts` — NEU

**Änderungstyp:** neu

**Abhängig von:** Schritt 2 (MarketContext, MarketContextExtractedSchema)

**Was genau ändert sich:**
- Neue Datei mit zwei Exports:
  1. `extractMarketContext(negotiationType, contextNotes?, region?): Promise<MarketContext>`
  2. `buildContextHash(context: MarketContext): string`
- `extractMarketContext()` führt Claude-Call (HAIKU) zur Kontext-Extraktion durch
- Frühzeitiger Fallback wenn `contextNotes` fehlt oder kürzer als 10 Zeichen
- `buildContextHash()` normalisiert 3 Kerndimensionen zu Cache-Key-String

**TypeScript-Signaturen (neu):**
```typescript
export async function extractMarketContext(
  negotiationType: NegotiationType,
  contextNotes?: string,
  region?: string,
): Promise<MarketContext>

export function buildContextHash(context: MarketContext): string
```

**Implementierungsdetails `extractMarketContext`:**
```typescript
// Frühzeitiger Fallback — kein Claude-Call
if (!contextNotes || contextNotes.trim().length < 10) {
  return { negotiation_type: negotiationType, region };
}

// Claude-Call (HAIKU, max_tokens: 256)
// System: Daten-Extraktor, nur JSON, keine Erfindungen
// User: Verhandlungstyp + contextNotes + type-spezifische Feld-Hints

// Parse + Zod-Validate → Fallback bei jedem Fehler
// Return: { negotiation_type, region, ...extractedFields }
```

**Implementierungsdetails `buildContextHash`:**
```typescript
// Dimensions: [negotiation_type, job_role.slice(0,30), seniority_level, industry.slice(0,30)]
// Normalisierung: toLowerCase().trim()
// Filter: filter(Boolean) — fehlende Felder werden ausgelassen
// Join: ':'
// Fallback wenn kein Kontext: negotiation_type alleine → Status-quo-Verhalten
```

**Fehlerfall / Fallback:**
- Jeder Fehler in `extractMarketContext` → `console.warn` + Fallback-Return `{ negotiation_type, region }`
- Kein Error-Throw. Invariante: Funktion wirft nie.
- `buildContextHash` ist synchron und deterministisch — kein Fehlerfall.

**Rückwärtskompatibilität:** Neue Datei — keine bestehenden Importer.

**Test-Abdeckung:**
Schritt 8 ergänzt:
- `extractMarketContext` mit reichhaltigem `context_notes` → Felder gesetzt
- `extractMarketContext` mit `contextNotes: undefined` → nur Pflichtfelder
- `buildContextHash` mit vollständigem Kontext → erwarteter Hash-String

---

### SCHRITT 4: marketDataInterpreter.ts — Signatur auf MarketContext

**Datei(en):** `src/layer2/marketDataInterpreter.ts` — GEÄNDERT

**Änderungstyp:** geändert

**Abhängig von:** Schritt 2 (MarketContext)

**Was genau ändert sich:**
- Import `MarketContext` aus `./types`
- Signatur `searchMarketData(negotiationType, region?)` → `searchMarketData(context: MarketContext)`
- Tool-Description und User-Message werden mit Kontext-Feldern angereichert
- `NEGOTIATION_TYPE_LABELS` bleibt als Label-Quelle (kein struktureller Umbau)
- Interne Hilfsfunktion `buildContextDetail(context: MarketContext): string` (privat) für
  die Anreicherung des Tool-Description-Strings

**TypeScript-Signaturen:**
```typescript
// VORHER:
export async function searchMarketData(
  negotiationType: NegotiationType,
  region?: string,
): Promise<MarketSearchResult>

// NACHHER:
export async function searchMarketData(
  context: MarketContext,
): Promise<MarketSearchResult>
```

**Prompt-Anreicherung (Beispiel `gehalt` mit Kontext):**
```typescript
// Tool description — VORHER:
`Extrahiere aktuelle Marktdaten für Gehälter / Vergütung in München.`

// Tool description — NACHHER:
`Extrahiere aktuelle Marktdaten für Gehälter / Vergütung in München
 für: Senior Software Engineer | SaaS-Branche | Unternehmen ~200 MA.`

// User message — VORHER:
`Liefere aktuelle Marktdaten für: Gehälter / Vergütung in München. Zeitraum: aktuell.`

// User message — NACHHER:
`Liefere aktuelle Marktdaten für:
Berufsfeld: Senior Software Engineer
Erfahrungsstufe: Senior
Branche: SaaS / Software
Unternehmensgröße: ~200 Mitarbeiter
Standort: München
Zeitraum: aktuell.`
```

**Fallback wenn kein Kontext (nur `negotiation_type` + `region`):**
- `buildContextDetail(context)` gibt `''` zurück
- Tool-Description und User-Message: identisch mit Status quo

**Fehlerfall / Fallback:** Keine Änderung am bestehenden Fehlerverhalten.

**Rückwärtskompatibilität:**
Einziger Aufrufer: `marketDataResolver.ts:26` — wird in Schritt 5 angepasst.
Test-Datei: kein direkter Aufruf → kein Test bricht.

**Test-Abdeckung:**
Schritt 8: `searchMarketData` mit `MarketContext` (Job-Rolle + Industry gesetzt) →
Smoke-Test: `median > 0` und kontextspezifisches `summary` enthält Rollenbezeichnung.

---

### SCHRITT 5+7: marketDataResolver.ts — contextNotes + contextHash

*(Spec trennt Schritt 5 und 7, beide landen in derselben Datei — zusammengeführt.
Spec-Notiz: `buildContextHash` liegt lt. Spec in `knowledgeGraph.ts`; tatsächlich
gehört es in `marketDataResolver.ts` wo es verwendet wird. `knowledgeGraph.ts` braucht
keine Änderung — die `category`-API bereits vorhanden.)*

**Datei(en):** `src/layer2/marketDataResolver.ts` — GEÄNDERT

**Änderungstyp:** geändert

**Abhängig von:** Schritt 3 (extractMarketContext, buildContextHash), Schritt 4 (MarketContext)

**Was genau ändert sich:**
- Neuer Parameter `contextNotes?: string` (4. optionaler Parameter)
- Import `extractMarketContext`, `buildContextHash` aus `./marketContextExtractor`
- Import `MarketContext` aus `./types`
- `cacheKey` (für `data_type`) bleibt `negotiationType`
- `category` für Cache-Lookup/-Insert: war `negotiationType`, wird `contextHash`
- `searchMarketData` erhält `MarketContext` statt `(negotiationType, region)`

**TypeScript-Signaturen:**
```typescript
// VORHER:
export async function resolveMarketData(
  negotiationType: NegotiationType,
  tier: Tier,
  region?: string,
): Promise<MarketDataResolution>

// NACHHER:
export async function resolveMarketData(
  negotiationType: NegotiationType,
  tier: Tier,
  region?: string,
  contextNotes?: string,
): Promise<MarketDataResolution>
```

**Interne Änderungen:**
```typescript
// VORHER:
const cacheKey = negotiationType;
const cached = await getMarketData(cacheKey, region, negotiationType);
// ...
const fresh = await searchMarketData(negotiationType, region);
await saveMarketData(cacheKey, fresh, region, negotiationType, fresh.source);

// NACHHER:
const marketContext = await extractMarketContext(negotiationType, contextNotes, region);
const contextHash = buildContextHash(marketContext);
const cacheKey = negotiationType;  // data_type bleibt unverändert
const cached = await getMarketData(cacheKey, region, contextHash);  // category = contextHash
// ...
const fresh = await searchMarketData(marketContext);  // MarketContext statt (type, region)
await saveMarketData(cacheKey, fresh, region, contextHash, fresh.source);  // category = contextHash
```

**Tier-Gate:** Bleibt unverändert in Position (vor extractMarketContext-Call):
```typescript
if (tier === 'privat' || tier === 'free') {
  return { source: 'none', data: null };
}
// Erst danach: extractMarketContext aufrufen
```

**Cache-Migrations-Verhalten:**
- Alte Einträge: `category = negotiationType` (z. B. `'gehalt'`)
- Neue Einträge: `category = contextHash` (z. B. `'gehalt:senior software engineer:senior:saas'`)
- Cache-Miss bei erstem Aufruf mit Kontext → neuer Claude-Call, neuer Eintrag → korrekt
- Alte Einträge laufen via `valid_until` (7-Tage-TTL) aus → kein Migrations-Script nötig

**Fehlerfall / Fallback:**
`extractMarketContext` wirft nie (DGQ-1) → `contextHash` ist immer ein valider String.
Bestehender saveMarketData-Fehlerfall (log + proceed) bleibt unverändert.

**Rückwärtskompatibilität:**
- `contextNotes` ist letzter, optionaler Parameter → bestehender Aufruf ohne 4. Arg weiterhin gültig
- Einziger Aufrufer: `src/layer2/index.ts:51` → wird in Schritt 6 aktualisiert

**Test-Abdeckung:**
Indirekt via Schritt 8 + Schritt 9 (Integration-Smoke-Test).

---

### SCHRITT 6: layer2/index.ts — context_notes durchreichen

**Datei(en):** `src/layer2/index.ts` — GEÄNDERT

**Änderungstyp:** geändert (~1 Zeile)

**Abhängig von:** Schritt 5 (neue resolveMarketData-Signatur)

**Was genau ändert sich:**
- Zeile 51: 4. Argument `inputs.context_notes` zu `resolveMarketData()`-Call hinzufügen
- Keine weiteren Änderungen in dieser Datei

**Diff:**
```typescript
// VORHER (Zeile 51):
resolveResult = await resolveMarketData(inputs.negotiation_type, tier, region);

// NACHHER:
resolveResult = await resolveMarketData(inputs.negotiation_type, tier, region, inputs.context_notes);
```

**Signatur `enrichWithMarketData()`:** Bleibt vollständig unverändert — ADR-001 gewahrt.

**Fehlerfall / Fallback:**
`inputs.context_notes` ist `string | undefined` — TypeScript akzeptiert beides als 4. optionalen Param.
Fallback-Kette bereits in Schritt 3 und 5 implementiert.

**Rückwärtskompatibilität:**
`enrichWithMarketData()` Signatur identisch → `/api/enrich` unverändert → Frontend unverändert.

**Test-Abdeckung:**
Bestehender Test in `layer2.test.ts` exerciert diesen Pfad automatisch
(bereits `tier: 'profi'` und reichhaltiges `context_notes` in `testInputs`).

---

### SCHRITT 8: Tests — layer2.test.ts erweitern

**Datei(en):** `tests/layer2/layer2.test.ts` — GEÄNDERT

**Änderungstyp:** geändert

**Abhängig von:** Schritt 6 (alle Implementierungsschritte abgeschlossen)

**Was genau ändert sich:**
- Import: `extractMarketContext`, `buildContextHash` aus `../../src/layer2/marketContextExtractor`
- Import: `searchMarketData` aus `../../src/layer2/marketDataInterpreter`
- 3 neue Test-Funktionen in `run()`:

```typescript
// Test A: extractMarketContext mit reichhaltigem Kontext
async function testExtractionWithContext(): Promise<void> {
  console.log('\n=== Test A: extractMarketContext mit Kontext ===');
  const ctx = await extractMarketContext(
    'gehalt',
    'Senior Software Engineer, 5 Jahre Erfahrung, SaaS-Startup, ~200 Mitarbeiter, München',
    'München',
  );
  console.log('Extracted:', JSON.stringify(ctx, null, 2));
  // Execution-proof: kein Fehler + job_role gesetzt
  if (!ctx.job_role) throw new Error('Test A: job_role not extracted');
}

// Test B: extractMarketContext ohne Kontext → Fallback
async function testExtractionFallback(): Promise<void> {
  console.log('\n=== Test B: extractMarketContext Fallback ===');
  const ctx = await extractMarketContext('miete', undefined, 'Hamburg');
  console.log('Fallback result:', JSON.stringify(ctx));
  // Nur negotiation_type und region — keine weiteren Felder
  if (ctx.job_role || ctx.property_type) throw new Error('Test B: unexpected fields in fallback');
}

// Test C: buildContextHash Differenzierung
function testContextHashDifferentiation(): void {
  console.log('\n=== Test C: contextHash Differenzierung ===');
  const hashSWE = buildContextHash({ negotiation_type: 'gehalt', job_role: 'Software Engineer', seniority_level: 'Senior', industry: 'SaaS' });
  const hashBuchhalter = buildContextHash({ negotiation_type: 'gehalt', job_role: 'Buchhalter', seniority_level: 'Junior', industry: 'Finanzwesen' });
  const hashEmpty = buildContextHash({ negotiation_type: 'gehalt' });
  console.log('Hash SWE:        ', hashSWE);
  console.log('Hash Buchhalter: ', hashBuchhalter);
  console.log('Hash leer:       ', hashEmpty);
  if (hashSWE === hashBuchhalter) throw new Error('Test C: Hash-Kollision SWE vs. Buchhalter');
  if (hashEmpty !== 'gehalt') throw new Error('Test C: Fallback-Hash ungleich negotiationType');
}
```

**Bestehende Tests:**
Alle laufen ohne Anpassung. `enrichWithMarketData`-Signatur unverändert.
Der bestehende Test exerciert jetzt automatisch den Extraction-Pfad (Kontext bereits vorhanden).

**Fehlerfall / Fallback:** Test A–C werfen bei Assertion-Fehler explizit — keine stillen Fails.

**Test-Abdeckung nach Schritt 8:**
- Extraction (happy path + fallback + empty input) ✓
- Hash-Differenzierung ✓
- End-to-End enrichment (bestehend) ✓

---

### SCHRITT 9: Integration Smoke Test

**Datei(en):** `tests/layer2/layer2.test.ts` — GEÄNDERT (Erweiterung)

**Änderungstyp:** geändert

**Abhängig von:** Schritt 8 (alle Tests laufen)

**Was genau ändert sich:**
- Zweiten `testInputs`-Datensatz hinzufügen: `negotiation_type: 'miete'` + reichhaltiges `context_notes`
- Optional: `negotiation_type: 'lieferant'` für dritten Pfad

```typescript
const testInputsMiete: NegotiationInputs = {
  negotiation_type: 'miete',
  own_target: 1800,
  own_minimum: 1500,
  opponent_estimated_max: 2200,
  opponent_estimated_min: 1600,
  context_notes: '3-Zimmer-Wohnung, 85qm, Innenstadt, Altbau unrenoviert, Hamburg',
  tier: 'kmu',
};
```

**Verifikation:**
- `market_data_source` ≠ `'none'` (Tier-Gate passiert)
- `market_median` > 0 und `< 5000` (plausibel für Monatsmiete)
- `market_context_summary` enthält Wohnungstyp-Begriff

**Ziel:** Bestätigen dass Kontext-angereicherte Marktdaten für unterschiedliche Types
korrekt und plausibel sind. Kein Mock — echter Claude-Call mit echtem context_notes.

---

## Dateiübersicht — vollständiger Scope

| Datei | Typ | Schritt | Änderung |
|---|---|---|---|
| `src/layer2/types.ts` | NEU | 2 | `MarketContext` interface |
| `src/layer2/schemas.ts` | GEÄNDERT | 2 | `MarketContextExtractedSchema` hinzufügen |
| `src/layer2/marketContextExtractor.ts` | NEU | 3 | `extractMarketContext()` + `buildContextHash()` |
| `src/layer2/marketDataInterpreter.ts` | GEÄNDERT | 4 | Signatur → `(context: MarketContext)`, Prompt-Anreicherung |
| `src/layer2/marketDataResolver.ts` | GEÄNDERT | 5+7 | `contextNotes?` Param, contextHash als category |
| `src/layer2/index.ts` | GEÄNDERT | 6 | `inputs.context_notes` durchreichen (~1 Zeile) |
| `tests/layer2/layer2.test.ts` | GEÄNDERT | 8+9 | 3 neue Tests + 2. Datensatz |

**NICHT berührt:** `src/types/index.ts`, `src/layer1/*`, `src/api/routes.ts`,
`src/layer2/knowledgeGraph.ts`, `supabase/functions/negotiate/`

**Post-Implementierung (nicht im Code-Scope):**
- `docs/service-catalog.md` — Layer-2-Sektion aktualisieren (extractMarketContext hinzufügen)
- `docs/db-map.md` — `knowledge_graph.category`: Semantik-Änderung dokumentieren (contextHash statt negotiationType)

---

## Risiken

| Risk | Classification | Schwere | Mitigation |
|---|---|---|---|
| Claude-Haiku liefert kein valides JSON | Inferred | LOW | JSON.parse in try/catch + Markdown-Fence-Strip + Fallback implementiert |
| context_notes enthält keine extrahierbaren Felder | Observed (häufig in frühen Sessions) | LOW | Fallback auf generische Query (Status quo) — kein Qualitätsverlust vs. heute |
| Cache-Kollision in ersten 7 Tagen (alte Einträge mit `category=negotiationType`) | Inferred | LOW | Nutzer ohne Kontext (leeres context_notes) treffen auf alte generische Einträge — explizit akzeptiertes Risiko in Spec 4.4 |
| extractMarketContext erhöht Latenz bei Cache-Miss | Observed (Spec: +0.5–1s) | LOW | Haiku ist schnell; tritt nur bei Cache-Miss auf; Fallback ist instant |
| Tests sind execution-proof only — neue Assertions könnten bei flaky Claude-Responses fehlschlagen | Inferred | MEDIUM | Test A/B/C haben klar definierte Assertions die nicht von konkreten Claude-Werten abhängen (Schritt A: nur ob job_role gesetzt ist; Schritt B: ob Fallback-Objekt leer ist; Schritt C: deterministischer Hash) |

---

## Offene Punkte

**Keine Blocker — bereit für GO.**

Alle Design-Gate-Fragen beantwortet. Kein ADR erforderlich (Option B, Backend-intern).
Impact Check PASSED. Protected Files nicht berührt. API-Contract unverändert.

Empfehlung: Schritte 2→3→4→5+7→6→8→9 sequenziell — jeder Schritt in eigenem Commit.
