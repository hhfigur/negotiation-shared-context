# Diagnosis Report — BUG-20260521-marktdaten-wrong-dialog

**Datum:** 2026-05-22
**Bug-ID:** BUG-20260521-marktdaten-wrong-dialog
**Status:** OPEN — Root Cause identifiziert, Fix-Scope minimal (1 Zeile)
**Klassifizierung:** UI-Bug / Copy-Paste-Fehler in Tool-Route-Definition

---

## 1. Bug Summary

Klick auf "Marktdaten" in der Sidebar navigiert zu `/strategy` — exakt dieselbe Route wie
"Strategie-Score". Beide Tools zeigen `StrategyGenerator.tsx`, das mit dem Strategy-Score
beginnt. Marktdaten-Inhalte erscheinen erst tiefer auf derselben Seite (wenn `enriched`
vorhanden). Der Nutzer erwartet ein differenziertes Verhalten für beide Buttons.

---

## 2. Observed — direkt im Code verifiziert

**O-001:** `TOOLS`-Array in `SessionSidebar.tsx` — beide Einträge haben `route: "/strategy"`:

```typescript
// SessionSidebar.tsx:87–109
{
    label: "Strategie-Score",
    route: "/strategy",      // ← Route A
    icon: <svg …/>,
},
{
    label: "Marktdaten",
    badge: "KMU",
    route: "/strategy",      // ← Route A — IDENTISCH (Copy-Paste-Fehler)
    icon: <svg …/>,
},
```

**O-002:** Click-Handler ist generisch für ALLE Tools — kein Tool-spezifisches Verhalten:

```typescript
// SessionSidebar.tsx:253
onClick={() => navigate(tool.route)}
```

→ Beide Buttons rufen `navigate("/strategy")` auf. Kein Unterschied im Verhalten.

**O-003:** `/strategy`-Route in `App.tsx:53` rendert ausschließlich `StrategyGenerator`:

```typescript
<Route path="/strategy" element={<ProtectedRoute><StrategyGenerator /></ProtectedRoute>} />
```

Keine separate `/marktdaten`-Route existiert im Router.

**O-004:** `StrategyGenerator.tsx` zeigt auf einer Seite:
1. Strategy-Score-Übersicht (immer gerendert, oben)
2. Marktdaten-Sektion (bedingt: `enriched && enriched.market_data_source !== 'none'`, ab Zeile 212)

**O-005:** Strategy Score wird NICHT on-demand berechnet in StrategyGenerator.
Er liest aus AnalysisContext: `strategyScore ?? analysis?.strategy_score ?? 0` (Zeile 63).
Kein `calculateStrategyScore()`-Aufruf bei Navigation.

**O-006:** Marktdaten-Card existiert AUCH inline in `Index.tsx:839–851` (kein Dialog, kein Route):
```tsx
{enriched && enriched.market_data_source !== 'none' && enriched.market_median != null && (
    <div className="shrink-0 px-4 py-2">
        <div className="rounded-lg border border-blue-200 bg-blue-50/60 …">
            📊 Marktlage …
        </div>
    </div>
)}
```
Diese Card ist immer im Chat sichtbar wenn Layer-2-Daten vorhanden — unabhängig von Navigation.

---

## 3. Inferred

**I-001:** Der `route: "/strategy"` für Marktdaten ist ein Copy-Paste-Fehler aus dem
Strategie-Score-Eintrag. Es gibt keine Evidenz für eine bewusste Design-Entscheidung,
beide auf dieselbe Route zu legen.

**I-002:** Das ursprüngliche Intent für "Marktdaten" war vermutlich:
entweder (a) eine eigene Route `/market` oder (b) `/strategy` mit einem Scroll-to-Anker
oder Query-Parameter der die Marktdaten-Sektion hervorhebt.

**I-003:** Da `StrategyGenerator` bereits beide Inhalte zeigt, wäre ein Scroll-to-Anker
(`/strategy?section=market` oder `navigate('/strategy', { state: { scrollTo: 'market' } })`)
die minimale korrekte Lösung ohne neue Seite erstellen zu müssen.

---

## 4. Missing

**M-001:** Product-Entscheidung: Soll "Marktdaten" eine eigene Seite bekommen,
oder reicht Scroll-to-Sektion auf `/strategy`? Bisher keine ADR-Entscheidung.

**M-002:** Tier-Gate für "Marktdaten" Tool: Soll der Button für free/privat-Tier
ausgeblendet oder disabled sein? Das KMU-Badge existiert, aber kein Code
prüft aktuell den Tier vor dem Rendern.

---

## 5. Root Cause — falscher Handler oder falscher Dialog-State-Wert?

**Root Cause: Falscher Route-Wert (Copy-Paste-Fehler) — kein Dialog-State involviert.**

Es gibt keinen Modal/Dialog-State. Die Navigation erfolgt via React Router `navigate()`.
Der Fehler liegt in `SessionSidebar.tsx:101` — `route: "/strategy"` statt einer
Marktdaten-spezifischen Route oder Scroll-Anchor.

Kein komplexes State-Management betroffen. Fix ist 1-zeilig (Route-Wert ändern)
plus optional 5–10 Zeilen für Scroll-to-Anker in StrategyGenerator.

---

## 6. BUG-05b Assessment — Strategie-Score-Berechnung eigenständig?

**NEIN — kein separater Bug.**

`StrategyGenerator` berechnet den Score nicht on-demand. Er liest
`strategyScore ?? analysis?.strategy_score ?? 0` aus AnalysisContext (pre-computed durch
`/api/analyze` oder `/api/analyze-full`). Kein Aufruf von `calculateStrategyScore()` bei
Navigation zur Seite.

Falls der Score fehlt oder falsch ist, liegt das an der Analyse-Pipeline (Layer 1),
nicht am UI-Routing. Das ist bereits durch BUG-20260521-enrich-500 und den Extractions-
Problemen bekannt und wird durch NC-CONTEXT adressiert.

**BUG-05b: geschlossen — kein eigenständiger Bug.**

---

## 7. Files Involved

| Datei | Rolle | Fix erforderlich |
|---|---|---|
| `src/components/SessionSidebar.tsx:101` | Route-Definition Marktdaten | **Ja** — Route-Wert ändern |
| `src/pages/StrategyGenerator.tsx:212–244` | Marktdaten-Sektion | Optional — Scroll-to-Anker |
| `src/App.tsx:53` | Router-Definition | Nein (kein neuer Route nötig) |
| `src/pages/Index.tsx:839–851` | Marktdaten-Card inline | Nicht betroffen |

---

## 8. Recommended Fix Scope (Proposed — nicht implementieren)

**Minimal-Fix (Option A — 1 Zeile, empfohlen):**

```typescript
// SessionSidebar.tsx:101 — vorher:
route: "/strategy",

// SessionSidebar.tsx:101 — nachher:
route: "/strategy?section=market",
```

**Ergänzung StrategyGenerator (Option A — ~8 Zeilen):**

```typescript
// StrategyGenerator.tsx — nach bestehenden useEffects
const location = useLocation();
const marktdatenRef = useRef<HTMLDivElement>(null);

useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('section') === 'market' && marktdatenRef.current) {
        marktdatenRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}, [location.search]);

// + ref={marktdatenRef} auf die Marktdaten-Sektion-Div (Zeile ~212)
```

**Alternativ-Fix (Option B — minimaler, ohne Scroll):**

Marktdaten-Button aus TOOLS-Array entfernen, da die Marktdaten bereits inline
auf der Chat-Seite (Index.tsx:839) sichtbar sind wenn Layer-2-Daten vorhanden.
Keine Navigation nötig.

**Nicht empfohlen:** Neue Route `/marktdaten` mit eigener Seite — zu viel Scope für P2-Bug.

---

## 9. Acceptance Criteria — Bewertung

| AC | Kriterium | Bewertbar? | Anmerkung |
|---|---|---|---|
| AC-1 | `npx tsc --noEmit` → 0 Fehler | ✓ prüfbar | Baseline 0 Fehler |
| AC-2 | Kein curl-Test sinnvoll | — | Rein Frontend-seitiger UI-Bug, kein API involviert |
| AC-3 | Layer-1-Tests grün | ⚠️ eingeschränkt | Testcoverage minimal; visueller Test nötig |
| AC-4 | Output-Nachweis | ✓ prüfbar | Screenshot: "Marktdaten" öffnet Marktdaten-Sektion, nicht Score |

**Ergänzende AC:**
- AC-5: Klick "Strategie-Score" → `/strategy` → Seite beginnt mit Score-Übersicht ✓
- AC-6: Klick "Marktdaten" → `/strategy?section=market` → Seite scrollt zu Marktdaten-Sektion ✓
- AC-7: Kein Scroll wenn `enriched`-Daten fehlen (Seite zeigt dann "keine Marktdaten" Hinweis)
