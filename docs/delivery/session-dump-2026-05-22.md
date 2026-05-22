# Session Dump — 2026-05-22

Context-Reset nach einer langen Debug-Session (2 Tage).
Enthält alle Commits seit session-dump-2026-05-21b.md.

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

## Offene Entscheidungen (nicht committed)

| Thema | Status | Ausstehend |
|---|---|---|
| NC-CONTEXT Phase A | Qualified, kein Plan | Max. Re-Extraction-Count pro Session (Vorschlag: 5×) |
| NC-CONTEXT Phase C | Qualified | Guided Flow via Lovable oder CC? |
| executedRef.current | Offen | Boolean → Set of unfilled fields? (eleganter) |
| BUG-20260521-batna-lost-after-nav | OPEN | Root Cause: Claude 529 verhindert Erkennung → NC-CONTEXT Phase A löst das |
| BUG-20260521-zopa-prefilled-values | OPEN P2 | Vorbefüllte ZOPA-Werte (eigenem Angebot) |
| BUG-20260521-marktdaten-wrong-dialog | OPEN P2 | Routing-Bug: falscher Dialog öffnet |

---

## Nächster geplanter Schritt (exakt)

**Empfehlung: P2-Bugs zuerst (schnell), dann NC-CONTEXT Phase A**

**Schritt 1 — BUG-20260521-marktdaten-wrong-dialog (P2, einfach)**
`/bug-report` → Diagnose → Fix in `SessionSidebar.tsx`
Symptom: Marktdaten-Tool öffnet falschen Dialog/Route

**Schritt 2 — BUG-20260521-zopa-prefilled-values (P2)**
`/bug-report` → Diagnose → Fix in `ZopaCalculator.tsx`
Symptom: ZOPA-Rechner zeigt vorbefüllte Werte aus vorheriger Session

**Schritt 3 — NC-CONTEXT Phase A (P1)**
Brief: `product/briefs/NC-CONTEXT.md`
Template 1-DEV → Plan → GO → Template 2b-DEV
Scope: `useProgressEngine.ts` (one-shot → retry-on-failure) + Regex-Fallback

---

## Dateien aktuell geändert (alle committed, clean)

### negotiation-buddy (main, committed, up-to-date mit origin)
- `src/pages/Index.tsx` — Session Guard + AbortController (967475d, b2dea9e)
- `src/pages/WhatIfSimulator.tsx` — useCallback dep fix (001a3d0)
- `src/hooks/useSessionManager.ts` — session_history + status filter (dc40096)
- `src/lib/apiClient.ts` — 30s Timeout (b2dea9e)
- `src/components/SessionSidebar.tsx` — isLoadingSessions Spinner (b2dea9e)
- `supabase/migrations/20260522120000_add_missing_backend_columns.sql` — (1377104)
- `CLAUDE.md` — Side-Effect-Check (43eefc7)
- `MEMORY.md` — Session State (5fd40c7)

### negotiationcoach-backend (main, committed, up-to-date mit origin)
- `src/api/routes.ts` — inputs in DB + null-guard enrich (96ccc4d)
- `MEMORY.md` — Session State (b7aec5e)

### shared-context (main, committed, up-to-date mit origin)
- `docs/delivery/bugs/BUG-20260521-session-save-retry-loop.md` — DONE
- `docs/delivery/bugs/BUG-20260521-whatif-analyze-loop.md` — DONE
- `docs/delivery/bugs/BUG-20260521-enrich-500.md` — DONE
- `docs/delivery/BUG-20260521-session-save-retry-loop-diagnosis-report.md`
- `docs/delivery/BUG-20260521-enrich-500-diagnosis-report.md`
- `docs/delivery/claude-code-prompt-templates-dev.md` — Side-Effect-Check (1e22ead)
- `product/briefs/NC-CONTEXT.md` — neu (ad12dea)
- `product/feature-register.md` — NC-CONTEXT Qualified
- `product/roadmap.md` — NC-CONTEXT in Next

---

## Ausstehende Acceptance Criteria (R-2026-09)

| Kriterium | Status | Anmerkung |
|---|---|---|
| Verhandlungsplan erscheint nach Chat-Flow | ✅ | effectiveProgress-Trigger gefixt (frühere Session) |
| Market-Data-Werte im UI sichtbar | ⚠️ | enrich-500 gefixt, aber UI-Anzeige noch nicht end-to-end verifiziert |
| TypeCheck negotiation-buddy: 0 Fehler | ✅ | verifiziert nach jedem Fix |
| Session-Save ohne Fehler | ✅ | inputs-Migration applied, session_history korrekt |
| BATNA aus Chat erkannt | ⚠️ | Claude 529 verhindert zuverlässige Erkennung → NC-CONTEXT Phase A nötig |
| Sessions nach Re-Login sichtbar | ✅ | BUG-session-reload-after-auth gefixt (e813f42, frühere Session) |

---

## Kontext für nächste Session

```
TARGET REPO: negotiation-buddy (primär für P2-Bugs + NC-CONTEXT)
TARGET REPO: negotiationcoach-backend (NC-CONTEXT Phase A — useProgressEngine.ts)
```

Supabase: `gpllrgkuozytyrmpfwbb` (eigenes Projekt, fully migrated)
Test-User: `hhfigur@gmx.net` — `persona_type=kmu`, `tier=kmu` im JWT
Backend: `https://negotiationcoach-backend.onrender.com` (Render.com, auto-deploy)
Frontend: `https://negotiation-buddy.onrender.com` (Render.com, auto-deploy)
Lokale Dev: `npm run dev` (Port 8080, VITE_API_URL nicht gesetzt → Production Backend)

**Wichtige Erkenntnisse aus dieser Session:**
- Side-Effect-Check ist jetzt Pflicht (Memory + Templates + CLAUDE.md)
- Backend-Migrations MÜSSEN im Frontend-Repo dupliziert + `supabase db push` ausgeführt werden
- React Context-Funktionen ohne `useCallback` als useCallback/useEffect-Dep → Endlos-Loop
- Render.com Free Tier: Cold Starts 30–60s → 30s-Timeout in apiCall schützt davor
