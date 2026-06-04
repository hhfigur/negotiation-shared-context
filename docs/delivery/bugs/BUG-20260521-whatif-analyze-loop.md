# BUG-20260521-whatif-analyze-loop

**Erstellt:** 2026-05-21
**Status:** DONE
**Risiko:** P1
**TARGET REPO:** negotiation-buddy
**Layer:** Frontend (React useCallback / Context Identity)
**Bug-Typ:** Logic-Bug
**Betroffene Tiers:** Alle
**ADR-Constraints:** keine direkt (Frontend-intern)

## Symptom

WhatIfSimulator löst einen Endlos-Loop von `/api/analyze`-Calls aus. Im Browser Network-Tab
erscheinen 15+ gleichzeitige `analyze`-Requests an `negotiationcoach-backend.onrender.com`,
alle von `apiClient.ts:27`. Die App friert ein und reagiert nur noch mit massiver Verzögerung
oder gar nicht mehr.

**Soll-Verhalten:** `runAnalysis` wird einmal aufgerufen wenn sich `debouncedInputs` ändert
(Slider-Bewegung oder initialer Mount). Kein automatischer Re-Trigger nach Abschluss.

## Ort

- `src/pages/WhatIfSimulator.tsx:99` — `runAnalysis` useCallback mit `[updateAnalysis]` als Dep
- `src/pages/WhatIfSimulator.tsx:101–103` — useEffect `[debouncedInputs, runAnalysis]`
- `src/contexts/AnalysisContext.tsx` — `updateAnalysis` ist NICHT in `useCallback` gewrappt

## Reproduktion

1. Chat-Session starten, Verhandlungsdaten eingeben
2. WhatIfSimulator öffnen (Tool-Navigation)
3. Simulator startet → `runAnalysis` wird ausgeführt → `analyzeOnly` Response kommt zurück
4. `updateAnalysis(result)` wird aufgerufen → AnalysisContext re-rendert
5. `updateAnalysis` bekommt neue Funktionsidentität (kein useCallback in AnalysisContext)
6. `runAnalysis` useCallback wird neu erstellt (Dep `updateAnalysis` hat sich geändert)
7. useEffect `[debouncedInputs, runAnalysis]` feuert erneut
8. → Schritt 3–7 wiederholen sich endlos

## Logs / Fehlermeldungen

- Browser Network-Tab: 15+ `analyze`-Requests (grün, je 1–5s) in schneller Folge
- Alle von `apiClient.ts:27`
- Kein expliziter Fehler — App friert durch akkumulierende offene Fetch-Promises ein
- Konsole: keine Fehlermeldung, nur `console.error` wenn einzelne Calls fehlschlagen

## Verdacht

**Root Cause (Observed — Code gelesen):**

`runAnalysis` in `WhatIfSimulator.tsx` ist als `useCallback` mit `[updateAnalysis]` als
Dependency definiert (Zeile 99). `updateAnalysis` wird aus `useAnalysis()` (AnalysisContext)
bezogen und ist dort NICHT in `useCallback` gewrappt — es ist eine inline Arrow-Function:

```typescript
// AnalysisContext.tsx — updateAnalysis ist NICHT memoized:
const updateAnalysis = (a: AnalysisResult) =>
    setSession(prev => ({ ...prev, analysis: a, ... }));
```

Jedes Mal wenn `setSession` aufgerufen wird (z.B. durch `updateAnalysis` selbst),
re-rendert der AnalysisProvider und alle darin definierten Funktionen bekommen neue
Referenzen. `updateAnalysis` ist damit jedes Mal ein neues Objekt. Das triggert
`runAnalysis`'s useCallback-Neukreation, was wiederum den useEffect auslöst.

**Loop-Pfad (Observed):**
```
runAnalysis(debouncedInputs)
  → analyzeOnly() → res.result
  → updateAnalysis(res.result)          ← AnalysisContext setSession
  → AnalysisProvider re-rendert
  → updateAnalysis bekommt neue Identität
  → runAnalysis useCallback neu erstellt  ← [updateAnalysis] dep geändert
  → useEffect [debouncedInputs, runAnalysis] feuert
  → runAnalysis(debouncedInputs)        ← Loop
```

**Proposed Fix (1 Zeile, nur WhatIfSimulator.tsx):**
```typescript
// Zeile 99 — vorher:
}, [updateAnalysis]);

// Zeile 99 — nachher:
// eslint-disable-next-line react-hooks/exhaustive-deps
}, []);
```

`setSession` aus React `useState` hat stabile Identität über Re-renders hinweg.
`updateAnalysis` als Dep ist unnötig — es ruft intern nur `setSession(prev => ...)` auf,
was keine externe Abhängigkeit zur Laufzeit darstellt.

**Verwandte Issues:**
- Gleiches Muster potenziell in ZopaCalculator.tsx (prüfen ob ähnliche Deps vorhanden)
- AGENTS.md warnt: "Do not refactor AnalysisContext.tsx localStorage logic without full session restore testing" — Fix in WhatIfSimulator.tsx umgeht diese Einschränkung

## Plan

Root Cause (Observed — Code gelesen, Network-Tab bestätigt):
`runAnalysis useCallback([updateAnalysis])` in WhatIfSimulator.tsx.
`updateAnalysis` aus AnalysisContext ist nicht memoized → neue Identität nach jedem
AnalysisContext-Re-render → Loop. Fix: `updateAnalysis` aus Dep-Array entfernen.

## Implement

Commit: `001a3d0` (negotiation-buddy) — 2026-05-21
Datei: `src/pages/WhatIfSimulator.tsx` — 2 Insertions, 1 Deletion

```diff
- }, [updateAnalysis]);
+ // eslint-disable-next-line react-hooks/exhaustive-deps
+ }, []); // updateAnalysis wraps setSession which has stable identity — listing it causes infinite loop
```

## Abschluss

**Status:** DONE
Commit: `001a3d0` (negotiation-buddy) — 2026-05-21
Verified: `npx tsc --noEmit` exit 0 ✓
API contract updated: no
DB delta: none
ADR created/amended: none
Docs updated: BUG-20260521-whatif-analyze-loop.md, MEMORY.md (feedback_unstable_context_deps.md)
