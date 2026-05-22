# FEATURE-L2-CONTEXT — Layer 2 Market Context Specification
## Kontextualisierung von Marktdaten in Layer 2

**Erstellt:** 2026-05-22
**Status:** PROPOSED — Review durch Delivery Controller ausstehend
**Trigger:** Delivery Controller Entscheidung 2026-05-22
**Repos:** negotiationcoach-backend (primary), shared-context (Docs)
**Empfehlung:** Option B (Kontext-Extraktion aus context_notes — kein API-Contract-Change)

---

## Abschnitt 1 — IST-Analyse

### 1.1 Was übergibt enrichWithMarketData() heute an resolveMarketData()?

**Observed** — `src/layer2/index.ts:51`

```typescript
// Signatur enrichWithMarketData:
async function enrichWithMarketData(
  analysisResult: AnalysisResult,
  inputs: NegotiationInputs,   // enthält context_notes, batna_description, etc.
  region?: string,
): Promise<EnrichedAnalysisResult>

// Tatsächlich übergeben an resolveMarketData:
resolveMarketData(inputs.negotiation_type, tier, region)
//                ^ type: 'gehalt'        ^ kmu  ^ 'München'
```

**Verlust:** Von `NegotiationInputs` wird ausschliesslich `negotiation_type` weitergegeben.
Alle anderen Felder — `context_notes`, `batna_description`, `deadline_days`, `own_target`,
`own_minimum` — werden in Layer 2 nie an den Marktdaten-Lookup übergeben.
Das `region`-Feld kommt aus dem HTTP-Request-Body von `/api/enrich` direkt, nicht aus
`NegotiationInputs`.

### 1.2 Was übergibt resolveMarketData() an searchMarketData()?

**Observed** — `src/layer2/marketDataResolver.ts:26`

```typescript
// Signatur resolveMarketData:
async function resolveMarketData(
  negotiationType: NegotiationType,  // 'gehalt'
  tier: Tier,                        // 'kmu' — nur für Tier-Gate, nicht weitergereicht
  region?: string,                   // 'München'
): Promise<MarketDataResolution>

// Tatsächlich übergeben an searchMarketData:
searchMarketData(negotiationType, region)
//               'gehalt'         'München'
```

**Informationsverlust beim Übergang resolveMarketData → searchMarketData:**
- `tier` wird für den Tier-Gate verwendet (privat/free → early return), aber nicht weitergegeben
- Keine weiteren NegotiationInputs-Felder sind in resolveMarketData verfügbar

**Kumulierter Verlust** von `enrichWithMarketData` bis `searchMarketData`:
`inputs.context_notes`, `inputs.batna_description`, `inputs.deadline_days`,
`inputs.own_target`, `inputs.own_minimum` — alle ungenutzt.

### 1.3 Welche Felder in NegotiationInputs enthalten implizit Kontext?

**Observed:**
- `context_notes?: string` — Freitext-Notizen des Nutzers. In der Chat-basierten Extraktion
  (useProgressEngine.ts) enthält dieses Feld typischerweise strukturierte Informationen wie
  Jobrolle, Branche, Unternehmensgröße — als natürlichsprachiger Text, z. B.:
  `"Senior Software Engineer, 5 Jahre Erfahrung, SaaS-Startup, ~200 Mitarbeiter, München"`
- `batna_description?: string` — beschreibt Alternativoptionen. Implizit: Marktkenntnis des
  Nutzers (z. B. "Konkurrenzangebot von Firma X: 70.000€"). **Inferred:** Enthält oft implizit
  Marktdaten die als Plausibilitäts-Check dienen könnten.
- `deadline_days?: number` — Inferred: kurze Deadlines (< 14 Tage) deuten auf wenig
  Verhandlungsspielraum hin, was die Marktdaten-Gewichtung beeinflussen könnte.

**Inferred:** `context_notes` ist der primäre Träger von Kontext-Informationen die für
belastbare Marktdaten notwendig wären — wird aber von Layer 2 komplett ignoriert.

### 1.4 Wie ist der Cache-Key in knowledgeGraph.ts heute aufgebaut?

**Observed** — `src/layer2/marketDataResolver.ts:19-20` + `knowledgeGraph.ts:4-18`

```typescript
// Cache-Key-Variable in resolveMarketData:
const cacheKey = negotiationType;  // Wert: 'gehalt', 'miete', etc.

// saveMarketData-Aufruf:
saveMarketData(cacheKey, fresh, region, negotiationType, fresh.source);
// Parameter:   dataType  data   region  category         source

// DB-Lookup in getMarketData:
.eq('data_type', dataType)          // = negotiationType ('gehalt')
.eq('region', region)               // = 'München' oder IS NULL
.eq('category', category)           // = negotiationType ('gehalt') — Duplikat!
```

**Effektiver Composite-Key:** `data_type=negotiationType AND region=region AND category=negotiationType`

Da `data_type` und `category` beide `negotiationType` enthalten, ist der funktionale Cache-Key:
**`negotiationType + region`**

**Problem:** Zwei Nutzer mit Gehaltsverhandlung in München — ein Senior SWE bei einem
SaaS-Startup, ein Junior-Buchhalter bei einer Bank — würden denselben Cache-Eintrag bekommen:
`data_type='gehalt' AND region='München'`. Der SWE erhält Buchhalter-Marktdaten und umgekehrt.
**Observed:** Cache-Kollision zwischen inhaltlich völlig unterschiedlichen Kontexten.

**Zusätzlich beobachtet:** `category` wird mit dem identischen Wert wie `data_type` befüllt
— das ist redundant und deutet darauf hin, dass `category` ursprünglich für Kontext-Differenzierung
vorgesehen war, aber nie implementiert wurde.

---

## Abschnitt 2 — Kontextparameter pro Negotiation-Type

### gehalt

- **Pflichtparameter** (ohne diese ist market_median nicht belastbar):
  - `job_role`: Berufsbezeichnung, z. B. "Software Engineer", "Product Manager", "Buchhalter"
  - `seniority_level`: Erfahrungsstufe, z. B. "Junior (0-2J)", "Senior (5-8J)", "Principal (10J+)"
  - `industry`: Branche, z. B. "SaaS/Tech", "Finanzen", "Einzelhandel", "Pharma"
- **Optionale Parameter** (verbessern Präzision):
  - `company_size`: Unternehmensgröße, z. B. "Startup (<50 MA)", "KMU (50-500 MA)", "Konzern (500+ MA)"
  - `remote_policy`: z. B. "Remote-first", "Hybrid", "Vollzeit vor Ort"
  - `region`: bereits vorhanden
- **Datenquelle im Kontext:** `context_notes` (Freitext) — strukturierte Extraktion nötig
- **Beispiel-Query mit Kontext:**
  `"Liefere aktuelle Marktdaten für Gehalt: Senior Software Engineer, SaaS-Startup 200 MA, München, Hybrid. Zeitraum: aktuell."`
  Erwartetes Ergebnis: median ~85.000–95.000€ p.a.
- **Beispiel-Query ohne Kontext (heute):**
  `"Liefere aktuelle Marktdaten für: Gehälter / Vergütung in München. Zeitraum: aktuell."`
  Erwartetes Ergebnis: Querschnitt aller Berufe, München, ~50.000–65.000€ — **für SWE wertlos**

### miete

- **Pflichtparameter:**
  - `property_type`: Wohnungstyp, z. B. "1-Zimmer-Wohnung", "3-Zimmer-Wohnung", "Haus", "Gewerbe"
  - `size_sqm_range`: Größenkategorie, z. B. "40-60qm", "80-100qm", "120-150qm"
  - `location_type`: Lage, z. B. "Innenstadt", "Stadtrand", "Peripherie/Umland"
- **Optionale Parameter:**
  - `furnishing`: "möbliert", "unmöbliert", "teilmöbliert"
  - `condition`: "Neubau", "renoviert", "Altbau unrenoviert"
  - `floor_level`: "Erdgeschoss", "Obergeschoss", "Dachgeschoss"
- **Datenquelle:** `context_notes` (Freitext)
- **Beispiel mit Kontext:**
  `"Marktdaten für Miete: 3-Zimmer-Wohnung, 80-90qm, Innenstadt, unrenoviert, Hamburg."`
  Erwartetes Ergebnis: ~1.500–2.200€/Monat
- **Ohne Kontext (heute):**
  `"Mietpreise / Immobilien in Hamburg."` → Durchschnitt aller Wohnungstypen, ~1.200–1.800€/Monat — **für spezifische Verhandlung zu ungenau**

### lieferant

- **Pflichtparameter:**
  - `product_category`: Produktkategorie, z. B. "IT-Hardware", "Büromaterial", "Logistik-Dienstleistungen"
  - `contract_volume_range`: Jahresvolumen, z. B. "10.000–50.000€", "50.000–200.000€"
  - `contract_duration`: z. B. "Einmalig", "12 Monate", "3 Jahre"
- **Optionale Parameter:**
  - `exclusivity`: "exklusiv", "nicht exklusiv"
  - `payment_terms`: "30 Tage netto", "sofortige Zahlung", "Vorkasse"
  - `delivery_frequency`: "einmalig", "quartalsweise", "monatlich"
- **Datenquelle:** `context_notes`
- **Beispiel mit Kontext:**
  `"B2B-Marktpreise: IT-Hardware, Jahresvolumen 50.000–100.000€, 2-Jahresvertrag, nicht exklusiv, Deutschland."`
- **Ohne Kontext (heute):**
  `"Lieferantenkonditionen / B2B-Preise in Deutschland."` → bedeutungsloser Querschnitt

### m_a

- **Pflichtparameter:**
  - `target_industry`: Branche des Zielunternehmens, z. B. "B2B SaaS", "E-Commerce", "Pharma"
  - `company_size_range`: Größe, z. B. "1–5M€ ARR", "5–20M€ ARR", "50–100M€ Umsatz"
  - `deal_type`: z. B. "Strategic Acquisition", "Financial Buyout", "Merger", "Asset Deal"
- **Optionale Parameter:**
  - `synergy_type`: "Technologie-Akquisition", "Marktanteil", "Talente"
  - `geographic_scope`: "DACH", "EU", "Global"
- **Datenquelle:** `context_notes`
- **Beispiel mit Kontext:**
  `"M&A Bewertungen: B2B SaaS, 5–15M€ ARR, DACH, Strategic Acquisition. Zeitraum: 2024–2025."`
  Erwartetes Ergebnis: EV/ARR Multiple 4–8×
- **Ohne Kontext (heute):**
  `"M&A Unternehmensbewertungen in Deutschland."` → wertlos, da Multiples stark nach Branche/Größe variieren

### sonstige

- **Pflichtparameter:**
  - `description`: Freitext-Beschreibung der Verhandlung, min. 20 Zeichen
- **Optionale Parameter:** Alle verfügbaren NegotiationInputs-Felder werden vollständig in den Prompt eingebettet
- **Fallback-Strategie:** Claude nutzt `context_notes` vollständig als Kontext-Quelle

---

## Abschnitt 3 — Extraktionsstrategie

### Option A — Strukturierte Felder in NegotiationInputs

Neue optionale Felder je negotiation_type:
```typescript
interface NegotiationInputs {
  // ... bestehende Felder ...
  job_role?: string;
  seniority?: string;
  industry?: string;
  company_size?: string;
  property_type?: string;
  size_sqm_range?: string;
  product_category?: string;
  contract_volume_range?: string;
}
```

**Vorteil:** Typsicher, explizit, Cache-Key eindeutig, keine Extraktion nötig.
**Nachteil:**
- `NegotiationInputs` als zentrales Interface propagiert durch: `types/index.ts`, `routes.ts`,
  `/api/analyze`, `/api/enrich`, `frontend-backend.md`, alle Layer-1-Kalkulationen
- API-Contract ändert sich für `/api/analyze` UND `/api/enrich`
- Frontend (`useProgressEngine.ts`, `ZopaCalculator.tsx`, Guided Flow) muss neue Felder
  erfassen und senden
- Guided Flow Erweiterung für jede `negotiation_type` nötig (bereits als NC-CONTEXT geplant)
- Voluminöseste Änderung — hoher Blast-Radius

**Impact-Schätzung:** 8–12 Dateien in 2 Repos.

---

### Option B — Kontext-Extraktion aus context_notes via Claude (Pre-Processing)

Vor `searchMarketData()` einen dedizierten Claude-Call einführen, der `context_notes`
in strukturierte `MarketContext`-Parameter zerlegt. Das Ergebnis wird nur für den
aktuellen Request genutzt — nicht persistiert in NegotiationInputs.

```
enrichWithMarketData()
  → resolveMarketData(negotiationType, tier, region, context_notes)  ← context_notes NEU
    → extractMarketContext(negotiationType, context_notes)            ← NEU
      → MarketContext { job_role, seniority, industry, ... }
    → searchMarketData(context: MarketContext)                        ← Signatur erweitert
```

**Vorteil:**
- Kein API-Contract-Change — `/api/analyze` und `/api/enrich` bleiben unverändert
- Kein Frontend-Change — `context_notes` wird bereits befüllt
- Kein TypeScript-Interface-Change in `NegotiationInputs`
- Blast-Radius minimal: `marketDataResolver.ts` + neues `marketContextExtractor.ts` + `marketDataInterpreter.ts`
- `context_notes` enthält in der Chat-Extraction bereits Jobrolle, Branche etc. als Freitext

**Nachteil:**
- Zusätzlicher Claude-Call pro Enrich-Request: +0.5–1s Latenz, ~0.01–0.03€ pro Call
- Qualität der Extraktion abhängig von User-Input in `context_notes`
- Falls `context_notes` leer: Fallback auf Type-only Query (Status quo)
- Cache-Key muss gehashed werden (Freitext nicht direkt als Key nutzbar)

**Impact-Schätzung:** 2–3 Dateien, ausschließlich `negotiationcoach-backend`.

---

### Empfehlung: **Option B**

**Begründung (Proposed):**

1. **Minimaler Blast-Radius:** Nur Backend-Layer-2 betroffen. Keine API-Contract-Änderung,
   kein Frontend-Change, kein ADR für Typänderungen nötig.

2. **`context_notes` enthält bereits den benötigten Kontext:** Die Chat-basierte Extraktion
   (useProgressEngine.ts → `sendChatMessage` → `/api/chat`) schreibt Jobrolle, Branche,
   Unternehmensgröße bereits als Freitext in `context_notes`. Die Information liegt vor —
   sie muss nur strukturiert ausgewertet werden.

3. **Phased Approach:** Option B liefert sofortigen Mehrwert. Option A kann später
   als NC-CONTEXT Phase B (Tool-Backwrite + neue strukturierte Felder) ergänzt werden,
   wenn der gesamte Context-Memory-Lifecycle implementiert ist.

4. **Kein ADR erforderlich:** Da kein Interface-Change und kein API-Contract-Change,
   fällt die Änderung in den Backend-internen Layer-2-Scope. Dokumentation in
   `service-catalog.md` ausreichend.

**ADR-Bedarf:** Kein ADR. Service-Catalog-Update nach Implementierung.

---

## Abschnitt 4 — Cache-Key-Strategie

### 4.1 Aktueller Cache-Key (Observed)

**Effektiver Composite-Lookup** in `getMarketData()`:
```
data_type = negotiationType   (z. B. 'gehalt')
region    = region || NULL    (z. B. 'München')
category  = negotiationType   (Duplikat von data_type)
valid_until > now()
```

**Funktionaler Key:** `(negotiationType, region)` — z. B. `('gehalt', 'München')`.
Kontext-Parameter fließen nicht ein. Zwei Nutzer mit identischem Type+Region aber
völlig unterschiedlichem Verhandlungskontext teilen denselben Cache-Eintrag.

### 4.2 Proposed Cache-Key-Struktur

**Proposed:**
```
data_type = negotiationType                          (z. B. 'gehalt')
region    = region || NULL                           (z. B. 'München')
category  = contextHash                              (NEU — normalisierter Hash)
```

**contextHash-Berechnung:**
```typescript
function buildContextHash(context: MarketContext): string {
  const normalized = [
    context.negotiation_type,
    (context.job_role ?? '').toLowerCase().trim().slice(0, 30),
    (context.seniority ?? '').toLowerCase().trim(),
    (context.industry ?? '').toLowerCase().trim().slice(0, 30),
  ]
    .filter(Boolean)
    .join(':');
  return normalized || context.negotiation_type;
}
```

**Normalisierungsstrategie:**
- `toLowerCase()` — "Senior SWE" = "senior swe"
- `trim()` — Whitespace-invariant
- `slice(0, 30)` — verhindert zu granulare Keys durch lange Freitexte
- Fehlende Felder werden gefiltert (`filter(Boolean)`) — kein "" im Hash
- Fallback auf `negotiationType` wenn kein Kontext verfügbar → Status-quo-Verhalten

**Beispiel-Hash:**
- "Senior Software Engineer, SaaS, München" → `gehalt:senior software engineer:seniority unbekannt:saas`
- "Buchhalter, Bank" → `gehalt:buchhalter::finanzwesen`
- Keine context_notes → `gehalt` → selber Cache wie bisher

**Granularität:** Bewusst auf 3 Kerndimensionen beschränkt (role, seniority, industry)
um Cache-Nutzbarkeit zu erhalten. Company-Size, Remote-Policy etc. gehen nicht in den
Hash ein — diese verfeinern den Summary-Text, führen aber nicht zu separaten Cache-Einträgen.

### 4.3 TTL-Implikationen

**Proposed:** TTL bleibt 7 Tage — keine Änderung empfohlen.

**Begründung:** Marktdaten für "Senior SWE, SaaS, München" ändern sich ebenso
langsam wie generische München-Gehaltsdaten. Der kürzere Refresh-Zyklus würde
keinen Mehrwert bringen und die Cache-Hit-Rate reduzieren. Die Kontext-Spezifität
der Daten ändert die Volatilität nicht — nur ihre Präzision.

### 4.4 Migration bestehender Cache-Einträge

**Proposed:** Koexistenz + schrittweise Verdrängung — keine explizite Invalidierung.

**Strategie:**
1. Bestehende Einträge haben `category = negotiationType` (z. B. `'gehalt'`).
   Neue Einträge haben `category = contextHash` (z. B. `'gehalt:senior software engineer:saas'`).
2. Cache-Miss tritt auf wenn contextHash ≠ negotiationType — neuer Claude-Call und
   neuer Eintrag werden erstellt.
3. Alte Einträge laufen nach 7 Tagen via `valid_until` natürlich ab.
4. Nach 7 Tagen: alle Einträge haben neues Format.

**Kein Migrations-Script nötig.** Die TTL übernimmt die Bereinigung.
Einziges Risiko: in den ersten 7 Tagen nach Deployment könnten Nutzer ohne
spezifischen Kontext (leeres context_notes) auf alte generische Einträge treffen —
das ist das Status-quo-Verhalten und akzeptabel.

---

## Abschnitt 5 — Interface-Definitionen (Proposed)

### 5.1 MarketContext Interface (neu)

```typescript
// src/layer2/types.ts (neue Datei) oder src/types/index.ts — Proposed

/**
 * Strukturierter Kontext für Marktdaten-Abfragen.
 * Wird von extractMarketContext() aus NegotiationInputs.context_notes extrahiert
 * und an searchMarketData() übergeben. Nicht persistiert.
 */
export interface MarketContext {
  // Pflicht — immer vorhanden
  negotiation_type: NegotiationType;
  region?: string;

  // Gehalt — extrahiert aus context_notes
  job_role?: string;           // z. B. "Software Engineer", "Buchhalter"
  seniority_level?: string;    // z. B. "Junior", "Senior", "Principal"
  industry?: string;           // z. B. "SaaS", "Finanzwesen", "Pharma"
  company_size?: string;       // z. B. "Startup <50 MA", "KMU 50-500 MA"

  // Miete — extrahiert aus context_notes
  property_type?: string;      // z. B. "3-Zimmer-Wohnung", "Büro"
  size_sqm_range?: string;     // z. B. "80-100qm"
  location_type?: string;      // z. B. "Innenstadt", "Stadtrand"

  // Lieferant — extrahiert aus context_notes
  product_category?: string;   // z. B. "IT-Hardware", "Logistik"
  contract_volume_range?: string; // z. B. "50.000-100.000€/Jahr"
  contract_duration?: string;  // z. B. "2 Jahre"

  // M&A — extrahiert aus context_notes
  target_industry?: string;    // z. B. "B2B SaaS"
  company_size_range?: string; // z. B. "5-15M€ ARR"
  deal_type?: string;          // z. B. "Strategic Acquisition"

  // Fallback — rohes context_notes wenn Extraktion nicht möglich
  extracted_context?: string;  // Max. 200 Zeichen normalisiert
}
```

**Felder Pflicht vs. Optional:**
- `negotiation_type` — immer Pflicht
- Alle typspezifischen Felder — optional; fehlende Felder bedeuten weniger präzise Query
- `extracted_context` — Fallback wenn keine strukturierten Felder extrahiert werden konnten

### 5.2 Aktualisierte Signaturen (Proposed)

```typescript
// marketContextExtractor.ts (neue Datei) — Proposed
async function extractMarketContext(
  negotiationType: NegotiationType,
  contextNotes?: string,
  region?: string,
): Promise<MarketContext>

// marketDataInterpreter.ts — Proposed (Signatur-Erweiterung)
// VORHER:
async function searchMarketData(
  negotiationType: NegotiationType,
  region?: string,
): Promise<MarketSearchResult>

// NACHHER:
async function searchMarketData(
  context: MarketContext,
): Promise<MarketSearchResult>

// marketDataResolver.ts — Proposed (context_notes als neuer Parameter)
// VORHER:
async function resolveMarketData(
  negotiationType: NegotiationType,
  tier: Tier,
  region?: string,
): Promise<MarketDataResolution>

// NACHHER:
async function resolveMarketData(
  negotiationType: NegotiationType,
  tier: Tier,
  region?: string,
  contextNotes?: string,    // NEU — aus NegotiationInputs.context_notes
): Promise<MarketDataResolution>

// layer2/index.ts — enrichWithMarketData() gibt context_notes durch
// Keine Signaturänderung — inputs.context_notes bereits verfügbar
```

### 5.3 Claude Tool-Use-Prompt — Vergleich mit vs. ohne Kontext

**Heute (ohne Kontext):**
```
System: Du bist ein Marktdaten-Analyst. Suche aktuelle Marktdaten...

Tool: extract_market_data
Description: "Extrahiere aktuelle Marktdaten für Gehälter / Vergütung in München."

User: "Liefere aktuelle Marktdaten für: Gehälter / Vergütung in München. Zeitraum: aktuell."
```
→ Claude liefert Querschnitt aller Berufe in München: ~50.000–65.000€ p.a.

**Proposed (mit Kontext "Senior SWE, SaaS, München"):**
```
System: Du bist ein Marktdaten-Analyst. Suche aktuelle Marktdaten...

Tool: extract_market_data
Description: "Extrahiere aktuelle Marktdaten für Gehälter / Vergütung in München
             für: Senior Software Engineer | SaaS-Branche | Unternehmen 100-300 MA."

User: "Liefere aktuelle Marktdaten für:
      Berufsfeld: Senior Software Engineer
      Branche: SaaS / Software
      Unternehmensgröße: 100-300 Mitarbeiter
      Standort: München
      Zeitraum: 2024-2025."
```
→ Claude liefert präzise SWE-SaaS-Daten für München: ~80.000–105.000€ p.a.
→ Delta zum Nutzer-Ziel (44.000€) wäre sofort als unrealistisch erkennbar

**Proposed (Extraktion-Prompt für extractMarketContext):**
```
User: "Extrahiere die relevanten Marktkontext-Parameter aus diesem Text
      für eine Gehaltsverhandlung:
      [context_notes: 'Senior Software Engineer, 5J Erfahrung, SaaS-Startup,
      ~200 Mitarbeiter, München, Hybrid-Arbeitsmodell']

      Antworte mit JSON: { job_role, seniority_level, industry, company_size }"
```

---

## Abschnitt 6 — Impact Assessment

### 6.1 Backend (negotiationcoach-backend) — Option B

| Datei | Änderung | Typ |
|---|---|---|
| `src/layer2/marketContextExtractor.ts` | Neu — Claude-Call zur Kontext-Extraktion | Neue Datei |
| `src/layer2/marketDataInterpreter.ts` | Signatur: `(type, region?)` → `(context: MarketContext)` | Geändert |
| `src/layer2/marketDataResolver.ts` | Parameter `contextNotes?` hinzufügen, extractMarketContext aufrufen | Geändert |
| `src/layer2/index.ts` | `inputs.context_notes` an `resolveMarketData` durchreichen | Geändert (~1 Zeile) |
| `src/layer2/types.ts` | Neues `MarketContext`-Interface | Neue Datei oder types/index.ts-Erweiterung |
| `tests/layer2/layer2.test.ts` | Test-Inputs um Kontext-Parameter erweitern | Geändert |

**Schätzung:** 4–5 Dateien geändert, 1–2 neu. Backend-Only.

### 6.2 API-Contract (Option B — kein Contract-Change)

**Keine Änderung an:**
- `POST /api/analyze` — Request-Body unverändert
- `POST /api/enrich` — Request-Body unverändert
- `docs/contracts/frontend-backend.md` — kein Update nötig

`context_notes` wird bereits in `NegotiationInputs` gesendet und vom Backend empfangen.
Die Layer-2-interne Verarbeitung von `context_notes` ist ein Backend-Implementierungsdetail.

### 6.3 Frontend (negotiation-buddy) — Option B

**Keine Änderungen erforderlich.**

`context_notes` wird bereits vom Chat-Extraction-Pfad (useProgressEngine → `/api/chat`)
befüllt und via `/api/analyze` an das Backend gesendet. Das Frontend muss keine neuen
Felder erfassen.

**Inferred:** Die Qualität der Marktdaten verbessert sich automatisch sobald
`context_notes` reichhaltiger wird — z. B. durch NC-CONTEXT Phase A (bessere Extraktion).

### 6.4 Supabase

- **knowledge_graph-Tabelle:** Kein Schema-Change erforderlich.
  `category`-Spalte (bereits vorhanden, `TEXT`) nimmt den `contextHash` auf.
  Keine Migration nötig — bestehende Einträge laufen via TTL ab (7 Tage).
- **RLS:** Bestehende Policies bleiben gültig.

### 6.5 ADR-Bedarf

**Option B: Kein ADR erforderlich.**
Änderung ist Backend-intern (Layer 2 Implementierungsdetail). Keine Systemgrenz-Überschreitung,
kein Interface-Contract-Change, keine neue externe Abhängigkeit.

Erforderlich nach Implementierung:
- Update `service-catalog.md` (oder neues Dokument): dokumentiert `extractMarketContext()`
  als neuen internen Layer-2-Schritt
- Update `docs/db-map.md`: `knowledge_graph.category` nutzt jetzt `contextHash` statt `negotiationType`

---

## Abschnitt 7 — ADR-Entwurf

**Nicht anwendbar** — Option B empfohlen. Kein ADR erforderlich.

Falls der Delivery Controller stattdessen Option A entscheidet, ist ADR-008 zu erstellen mit:
- Status: PROPOSED
- Context: Layer-2-Marktdaten ohne Kontext unbelastbar für kmu/profi-Tier-Versprechen
- Decision: Strukturierte Kontext-Felder in NegotiationInputs
- Consequences (positiv): typsichere Extraktion, deterministischer Cache-Key
- Consequences (negativ): API-Contract-Change, Frontend-Change, höherer Blast-Radius
- Betroffene ADRs: ADR-001 (System Boundaries), ADR-002 (Data Ownership), ADR-003 (AI Provider)

---

## Abschnitt 8 — Delivery-Plan (Proposed)

| Schritt | Beschreibung | Repo | Abhängig von | Scope (Dateien) | Template |
|---|---|---|---|---|---|
| 1 | Dieses Dokument — Review Delivery Controller | shared-context | — | 1 | Docs |
| 2 | `MarketContext`-Interface definieren | negotiationcoach-backend | Schritt 1 GO | 1 (types.ts) | 2b-DEV |
| 3 | `marketContextExtractor.ts` — Claude-Call zur Extraktion | negotiationcoach-backend | Schritt 2 | 1 (neu) | 2b-DEV |
| 4 | `marketDataInterpreter.ts` — Signatur auf MarketContext umstellen | negotiationcoach-backend | Schritt 3 | 1 | 2b-DEV |
| 5 | `marketDataResolver.ts` — contextNotes durchreichen + extractMarketContext aufrufen | negotiationcoach-backend | Schritt 4 | 1 | 2b-DEV |
| 6 | `layer2/index.ts` — context_notes an resolveMarketData übergeben | negotiationcoach-backend | Schritt 5 | 1 | 2b-DEV |
| 7 | Cache-Key-Migration: contextHash in saveMarketData | negotiationcoach-backend | Schritt 5 | 1 (knowledgeGraph.ts) | 2b-DEV |
| 8 | Tests: `layer2.test.ts` mit Kontext-Parametern erweitern | negotiationcoach-backend | Schritt 6+7 | 1 | 2b-DEV |
| 9 | Integration-Test: reale Beispiele pro Type (Gehalt/Miete/Lieferant) | negotiationcoach-backend | Schritt 8 | smoke test | Template 1-DEV |

**Gesamtscope:** 6–7 Dateien geändert, 1–2 neu, ausschließlich `negotiationcoach-backend`.
**Keine Frontend- oder Supabase-Migration-Schritte erforderlich (Option B).**

**Optionaler Folgeschritt (nach NC-CONTEXT Phase A):**
Wenn NC-CONTEXT Phase A (bessere Extraktion + retry) implementiert ist, wird `context_notes`
reichhaltiger → Marktdaten-Präzision verbessert sich automatisch ohne weiteren Code-Change.

---

## Offene Entscheidungen für den Delivery Controller

| Entscheidung | Optionen | Empfehlung |
|---|---|---|
| Option A vs. Option B | Strukturierte Felder vs. Kontext-Extraktion | **Option B** |
| Cache-Granularität | 3 Kerndimensionen vs. alle Felder | **3 Kerndimensionen** (job_role, seniority, industry) |
| Extraktion-Fallback | Fehler → Abbruch vs. Fehler → generische Query | **generische Query** (Status quo) |
| Delivery-Sequenz | Alles in einem PR vs. schrittweise | **schrittweise** (Schritt 2-9 einzeln) |
