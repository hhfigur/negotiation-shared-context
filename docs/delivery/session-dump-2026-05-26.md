# Session Dump — 2026-05-26

Context-Reset. Enthält alle Commits dieser Session.

---

## Was committed / erreicht

### Bug geschlossen

| Bug-ID | Titel | Commits | Repo |
|---|---|---|---|
| BUG-20260521-zopa-prefilled-values | ZOPA-Rechner zeigt vorbefüllte Werte ohne Nutzereingaben | `3d0cb31` (fix), `9b074ff` (diagnosis), `356a399` (close-stamp) | negotiation-buddy + shared-context |

**Diagnose (`9b074ff` — shared-context):**
- Root Cause: `handleNewSession()` ruft `setExtractedInputsFn({...nulls})` auf
- `setExtractedInputs`-Merge-Logik (`??`-Operator) ignoriert null-Werte still
- Wertequelle: `extractedInputs` aus AnalysisContext → aus localStorage deserialisiert
- Vorbefüllung aus extractedInputs ist intentionales Feature — Bug liegt im Reset-Pfad

**Fix-Details (`3d0cb31` — negotiation-buddy):**
- `AnalysisContext.tsx`: neue Action `clearExtractedInputs()` — setzt `extractedInputs: null` direkt, kein Merge
- `Index.tsx`: `clearExtractedInputs()` an 3 Stellen aufgerufen:
  - `handleNewSession` — ersetzt alten 11-Felder-null-Literal
  - `handleSelectSession` — erste Statement (Bleeding zwischen Sessions verhindert)
  - `handleUseCaseStart` — nach `startFlow(useCaseKey)`
- Alle 3 `useCallback`-Dep-Arrays aktualisiert

**Verifikation:**
- tsc --noEmit: 0 Fehler ✓
- Spec-Review: 10/10 PASS ✓
- Code-Quality: APPROVED_WITH_DEBT (D1: pre-existing Pattern — AnalysisContext-Funktionen nicht memoized)

**Close-Stamp (`356a399` — shared-context):**
- `docs/delivery/bugs/BUG-20260521-zopa-prefilled-values.md` auf DONE gestampt
- `docs/delivery/BUG-20260521-zopa-prefilled-values-diagnosis-report.md` committed

---

## Offene Entscheidungen (nicht committed)

| Thema | Status | Ausstehend |
|---|---|---|
| FEATURE-L2-CONTEXT | Spec reviewed, Status PROPOSED | GO-Entscheidung durch Delivery Controller — Option B bestätigt? |
| FEATURE-PLAN-MARKETDATA | Spec reviewed | Abhängig von FEATURE-L2-CONTEXT DONE |
| BUG-20260521-batna-lost-after-nav | OPEN | NC-CONTEXT Phase A löst Root Cause |
| AC-3 BUG-zopa (Auth-Reset nach Logout/Login) | Explizit ausgescoped | Separater Backlog-Eintrag empfohlen |
| D1 (AnalysisContext-Funktionen nicht memoized) | APPROVED_WITH_DEBT | Refactor-Kandidat, low severity, pre-existing |

---

## Nächster geplanter Schritt (exakt)

**Schritt 1 — FEATURE-L2-CONTEXT Phase A implementieren (P1, negotiationcoach-backend)**

Spec: `docs/delivery/FEATURE-L2-CONTEXT-spec.md` (Commit `9f12bcb`)
Entscheidung: Option B — Kontext-Extraktion aus `context_notes` in neuem `marketContextExtractor.ts`

Delivery-Sequenz laut Spec (Abschnitt 8):

| Schritt | Datei | Beschreibung |
|---|---|---|
| 2 | `src/layer2/types.ts` (neu) | `MarketContext`-Interface definieren |
| 3 | `src/layer2/marketContextExtractor.ts` (neu) | Claude-Call zur Extraktion aus context_notes |
| 4 | `src/layer2/marketDataInterpreter.ts` | Signatur: `(type, region?)` → `(context: MarketContext)` |
| 5 | `src/layer2/marketDataResolver.ts` | `contextNotes?` Parameter + `extractMarketContext()` aufrufen |
| 6 | `src/layer2/index.ts` | `inputs.context_notes` an `resolveMarketData` durchreichen (~1 Zeile) |
| 7 | `src/layer2/knowledgeGraph.ts` | Cache-Key: `contextHash` statt `negotiationType` in `category` |
| 8 | `tests/layer2/layer2.test.ts` | Tests mit Kontext-Parametern erweitern |
| 9 | Integration-Smoke-Test | Reale Beispiele pro Type (Gehalt/Miete/Lieferant) |

**Gesamtscope:** 4–5 Dateien geändert, 2 neu, ausschließlich `negotiationcoach-backend`.
Kein API-Contract-Change, kein Frontend-Change, keine Migration.

**Schritt 2 — FEATURE-PLAN-MARKETDATA (nach FEATURE-L2-CONTEXT DONE)**
Brief: `docs/delivery/FEATURE-PLAN-MARKETDATA-spec.md`
Abhängig von FEATURE-L2-CONTEXT DONE.

---

## Dateien aktuell geändert (alle committed, clean)

### negotiation-buddy (main, committed, up-to-date mit origin)
- `src/contexts/AnalysisContext.tsx` — `clearExtractedInputs()` hinzugefügt (`3d0cb31`)
- `src/pages/Index.tsx` — 3 Aufrufstellen `clearExtractedInputs()` (`3d0cb31`)

### negotiationcoach-backend (main, committed, up-to-date mit origin)
- keine Änderungen in dieser Session

### shared-context (main, committed — Stand nach 356a399)
- `docs/delivery/bugs/BUG-20260521-zopa-prefilled-values.md` — DONE-Stamp (`356a399`)
- `docs/delivery/BUG-20260521-zopa-prefilled-values-diagnosis-report.md` — neu (`9b074ff`)
- Diverse andere Dateien aus Vorsession (AGENTS.md, CLAUDE.md, docs/…) — noch uncommitted (pre-existing dirty state)

---

## Ausstehende Acceptance Criteria (R-2026-09)

| Kriterium | Status | Anmerkung |
|---|---|---|
| Verhandlungsplan erscheint nach Chat-Flow | ✅ | effectiveProgress-Trigger gefixt (Vorsession) |
| Market-Data-Werte im UI sichtbar | ⚠️ | enrich-500 gefixt; end-to-end noch nicht verifiziert; FEATURE-L2-CONTEXT verbessert Qualität |
| TypeCheck negotiation-buddy: 0 Fehler | ✅ | verifiziert nach BUG-fix (`3d0cb31`) |
| ZOPA-Felder leer nach neuer Session | ✅ | BUG-20260521 gefixt (`3d0cb31`) |
| ZOPA-Felder leer nach Logout/Login | ⚠️ | Ausgescoped — separater Backlog-Eintrag empfohlen |
| BATNA aus Chat erkannt | ⚠️ | NC-CONTEXT Phase A nötig |

---

## Kontext für nächste Session

```
TARGET REPO: negotiationcoach-backend (FEATURE-L2-CONTEXT Implementierung)
```

Supabase: `gpllrgkuozytyrmpfwbb` (eigenes Projekt, fully migrated)
Supabase MCP: PERMANENT WRONG PROJECT (`ivrfsjxdfzxrimexvoft`) — NIEMALS für DB-Ops verwenden
Test-User: `hhfigur@gmx.net` — `persona_type=kmu`, `tier=kmu` im JWT
Backend: `https://negotiationcoach-backend.onrender.com` (Render.com, auto-deploy auf main-Push)
Frontend: `https://negotiation-buddy.onrender.com` (Render.com, auto-deploy)

**Key Layer-2-Dateien (lesen vor Implementierung):**
- `src/layer2/index.ts` — `enrichWithMarketData()` — Einstiegspunkt
- `src/layer2/marketDataResolver.ts` — `resolveMarketData()` + `buildContextHash()` (neu)
- `src/layer2/marketDataInterpreter.ts` — `searchMarketData()` — Signatur ändert sich
- `src/layer2/knowledgeGraph.ts` — Cache-Layer (`getMarketData`, `saveMarketData`)

**Kritische Implementation-Details aus Spec:**
- `MarketContext`-Interface: Neue Datei `src/layer2/types.ts` (oder `src/types/index.ts`)
- `contextHash`-Formel: `[negotiation_type, job_role.slice(0,30), seniority, industry.slice(0,30)].filter(Boolean).join(':')`
- `category`-Spalte in knowledge_graph übernimmt contextHash — kein Schema-Change nötig
- Fallback: leeres context_notes → generische Query (Status quo)
- Claude-Call in extractMarketContext: strukturiertes JSON-Extraction-Prompt
