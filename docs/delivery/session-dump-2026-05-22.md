# Session Dump — 2026-05-22 (aktualisiert — zweiter Reset)

Context-Reset. Enthält alle Commits seit session-dump-2026-05-21b.md
inkl. Nachträge aus der zweiten Session-Hälfte 2026-05-22.

---

## Was committed / erreicht

### Bugs geschlossen

| Bug-ID | Titel | Commit | Repo |
|---|---|---|---|
| BUG-20260521-session-save-retry-loop | createSession Fan-Out in Index.tsx | `967475d` | negotiation-buddy |
| BUG-20260521-whatif-analyze-loop | updateAnalysis unstable dep → infinite /api/analyze | `001a3d0` | negotiation-buddy |
| BUG-20260521-enrich-500 | inputs nicht in DB gespeichert → null deref in /api/enrich | `96ccc4d` | negotiationcoach-backend |

**Fix-Details BUG-session-save-retry-loop (`967475d` — Index.tsx):**
- `isCreatingSession: useRef<boolean>` — concurrent guard
- `sessionCreateFailed: useRef<boolean>` — retry nach Fehler verhindern
- `createSessionAbortRef: useRef<AbortController|null>` — Cleanup bei Unmount

**Fix-Details BUG-whatif-analyze-loop (`001a3d0` — WhatIfSimulator.tsx):**
- `runAnalysis useCallback([updateAnalysis])` → `useCallback([])` — unstable dep entfernt
- Root Cause: updateAnalysis in AnalysisContext nicht memoized → neue Identität nach jedem setSession → Loop

**Fix-Details BUG-enrich-500 (`96ccc4d` — routes.ts):**
- `/api/analyze`: `inputs: inputs` zu Insert hinzugefügt
- `/api/analyze-full`: `inputs: inputs` zu Insert hinzugefügt
- `/api/enrich`: null-Guard vor `inputs.tier = req.tier` (400 statt 500 für alte Sessions)

### Schema-Migration (Prod-DB)

| Commit | Repo | Inhalt |
|---|---|---|
| `1377104` | negotiation-buddy | `inputs`-Spalte + `knowledge_graph`-Tabelle auf Prod-DB applied via `supabase db push` |

**Root Cause der Migration-Lücke:** Backend-Migrations (`20260408`, `20260421`) waren nur im
`negotiationcoach-backend`-Repo — nie auf das Frontend-Supabase-Projekt (`gpllrgkuozytyrmpfwbb`)
angewendet. Render-Logs zeigten `Could not find the 'inputs' column` → erst nach 2 Tagen gefunden.

### Performance-Fixes

| Commit | Repo | Inhalt |
|---|---|---|
| `dc40096` | negotiation-buddy | `session_messages` → `session_history` (richtiger Tabellenname); Status-Filter `.eq("status","active")`; column trim statt `select("*")` |
| `b2dea9e` | negotiation-buddy | `AbortSignal.timeout(30_000)` in `apiCall`; `isLoadingSessions`-Spinner in SessionSidebar |

### Docs / Process

| Commit | Repo | Inhalt |
|---|---|---|
| `5775d86` / `9b96e3d` | buddy + backend | Railway → Render.com / Express Backend Naming Cleanup (95+ Vorkommen) |
| `1e22ead` | shared-context | Mandatory Side-Effect-Check in alle Delivery-Templates (Template 1-DEV, 2-DEV, 2b-DEV) |
| `43eefc7` | negotiation-buddy | CLAUDE.md: impact-check als Pflicht vor JEDEM Edit |
| `ad12dea` | shared-context | NC-CONTEXT Feature Brief (Qualified, 3 Phasen) |
| Memory | Claude-System | feedback_unstable_context_deps, feedback_migration_verification, feedback_side_effect_check |

---

## Zusätzlich committed in zweiter Session-Hälfte (2026-05-22)

### Bug geschlossen

| Bug-ID | Titel | Commits | Repo |
|---|---|---|---|
| BUG-20260521-marktdaten-wrong-dialog | Marktdaten öffnet falschen Dialog | `298ea87` + `a566a4c` | negotiation-buddy |

**Fix-Details:**
- `SessionSidebar.tsx:101`: `route: "/strategy"` → `route: "/strategy?section=market"`
- `StrategyGenerator.tsx`: `useLocation` + `useEffect([location.search, enriched])` → scrollt zu `id="market-data-section"`
- Diagnosis Report: `3dbd50a` (shared-context)
- Close-Stamp: `41b21a2` (shared-context)

### Feature-Spezifikationen (Docs-only)

| Dokument | Commit | Inhalt |
|---|---|---|
| `FEATURE-L2-CONTEXT-spec.md` | `9f12bcb` | Layer-2-Marktdaten-Kontextualisierung — Option B entschieden (Extraktion aus context_notes) |
| `FEATURE-PLAN-MARKETDATA-spec.md` | `c9af220` | Marktdaten-Integration in Verhandlungsplan — neue `marketContext`-Sektion in PlanResponse/NegotiationPlan |

### Navigation Review
- Gestartet, dann bewusst zurückgestellt bis Weiterentwicklung beginnt

---

## Offene Entscheidungen (nicht committed)

| Thema | Status | Ausstehend |
|---|---|---|
| NC-CONTEXT Phase A | Qualified, kein Plan | Max. Re-Extraction-Count (Vorschlag: 5×); executedRef → Set of unfilled fields? |
| NC-CONTEXT Phase C | Qualified | Guided Flow via Lovable oder CC? |
| FEATURE-L2-CONTEXT | Spec reviewed | Implementierung noch ausstehend (Schritt 0 für FEATURE-PLAN-MARKETDATA) |
| FEATURE-PLAN-MARKETDATA | Spec reviewed | Plan-Display-Komponente = StrategyTab.tsx — Implementierung ausstehend |
| BUG-20260521-batna-lost-after-nav | OPEN | Claude 529 verhindert Erkennung → NC-CONTEXT Phase A löst Root Cause |
| BUG-20260521-zopa-prefilled-values | OPEN P2 | Vorbefüllte ZOPA-Werte aus vorheriger Session |
| Navigation Review | Zurückgestellt | Wird als Dialog geführt wenn Weiterentwicklung beginnt |

---

## Nächster geplanter Schritt (exakt)

**Empfehlung: BUG-zopa-prefilled-values, dann Feature-Implementierung in Reihenfolge**

**Schritt 1 — BUG-20260521-zopa-prefilled-values (P2)**
`/bug-report` → Diagnose → Fix in `ZopaCalculator.tsx`
Symptom: ZOPA-Rechner zeigt vorbefüllte Werte aus vorheriger Session

**Schritt 2 — FEATURE-L2-CONTEXT Phase A implementieren (P1)**
Brief: `docs/delivery/FEATURE-L2-CONTEXT-spec.md`
Spec `9f12bcb` — Option B: Kontext-Extraktion aus context_notes in `marketContextExtractor.ts`
Template 2b-DEV, nur negotiationcoach-backend

**Schritt 3 — FEATURE-PLAN-MARKETDATA implementieren**
Brief: `docs/delivery/FEATURE-PLAN-MARKETDATA-spec.md`
Abhängig von Schritt 2 DONE
5 Schritte: Backend planHelpers → EF generate-plan → Frontend apiClient + Index + StrategyTab

---

## Dateien aktuell geändert (alle committed, clean)

### negotiation-buddy (main, committed, up-to-date mit origin)
- `src/components/SessionSidebar.tsx` — Marktdaten-Route fix (`298ea87`)
- `src/pages/StrategyGenerator.tsx` — Scroll-Anker + enriched dep (`298ea87`, `a566a4c`)
- *(Alle Fixes aus erstem Dump-Stand unverändert)*

### negotiationcoach-backend (main, committed, up-to-date mit origin)
- `tasks/lessons.md` — L-006 ergänzt (`d0e10af`)
- *(Alle Fixes aus erstem Dump-Stand unverändert)*

### shared-context (main, committed, up-to-date mit origin)
- `docs/delivery/bugs/BUG-20260521-marktdaten-wrong-dialog.md` — DONE (`41b21a2`)
- `docs/delivery/BUG-20260521-marktdaten-wrong-dialog-diagnosis-report.md` (`3dbd50a`)
- `docs/delivery/FEATURE-L2-CONTEXT-spec.md` — neu (`9f12bcb`)
- `docs/delivery/FEATURE-PLAN-MARKETDATA-spec.md` — neu, final (`c9af220`)

---

## Ausstehende Acceptance Criteria (R-2026-09)

| Kriterium | Status | Anmerkung |
|---|---|---|
| Verhandlungsplan erscheint nach Chat-Flow | ✅ | effectiveProgress-Trigger gefixt |
| Market-Data-Werte im UI sichtbar | ⚠️ | enrich-500 gefixt; end-to-end noch nicht verifiziert |
| TypeCheck negotiation-buddy: 0 Fehler | ✅ | verifiziert nach jedem Fix |
| Session-Save ohne Fehler | ✅ | inputs-Migration applied, session_history korrekt |
| BATNA aus Chat erkannt | ⚠️ | NC-CONTEXT Phase A nötig |
| Sessions nach Re-Login sichtbar | ✅ | e813f42 gefixt |
| Marktdaten-Tool öffnet korrekte Sektion | ✅ | `298ea87` + `a566a4c` |

---

## Kontext für nächste Session

```
TARGET REPO: negotiation-buddy (P2-Bug zopa-prefilled-values)
TARGET REPO: negotiationcoach-backend (FEATURE-L2-CONTEXT Implementierung)
```

Supabase: `gpllrgkuozytyrmpfwbb` (eigenes Projekt, fully migrated)
Test-User: `hhfigur@gmx.net` — `persona_type=kmu`, `tier=kmu` im JWT
Backend: `https://negotiationcoach-backend.onrender.com` (Render.com, auto-deploy)
Frontend: `https://negotiation-buddy.onrender.com` (Render.com, auto-deploy)
Lokale Dev: `npm run dev` (Port 8080, VITE_API_URL nicht gesetzt → Production Backend)

**Plan-Display-Komponente (geklärt in dieser Session):**
`NegotiationPlan` aus `StrategyTab.tsx` ist der kanonische Frontend-Typ.
Plan wird gerendert in `StrategyTab.tsx` (Haupt-View) + `StrategyDialog.tsx` (Dialog).
`StrategyGenerator.tsx` rendert NUR AnalysisContext-Daten — nicht NegotiationPlan.

**EF generate-plan Input (heute):** `{ session_id, progress_status, messages }` — kein enrichedAnalysis.
`enriched` in Index.tsx bereits verfügbar — nur noch 1-Zeilen-Conditional für Übergabe.
