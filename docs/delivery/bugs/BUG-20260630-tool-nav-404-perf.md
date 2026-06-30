# BUG-20260630-tool-nav-404-perf

**Erstellt:** 2026-06-30
**Status:** DONE
**Risiko:** P1
**TARGET REPO:** negotiation-buddy
**Layer:** Layer 0 — Frontend State / Routing
**Bug-Typ:** Routing-Bug + Performance (UI-Freeze)
**Betroffene Tiers:** Alle
**ADR-Constraints:** keine

## Symptome

1. **404 bei Tool-Aufruf:** Klick auf Tool (ZOPA, What-If, Strategie …) in SessionSidebar
   oder Landing-Page führte zur NotFound-Seite. Console: `"404 Error: User attempted
   to access non-existent route: /zopa"`.

2. **Langsames Laden nach Tool-Rückkehr:** Nach Rückkehr aus Tool wurden Sessions und
   User-Profile neu von Supabase geladen (200–300ms), alle Chat-Nachrichten komplett
   neu gerendert (N×ReactMarkdown-Parse). Bei vielen Nachrichten führte dies zu
   spürbarer Verzögerung (mehrere Sekunden bei langen Sessions).

3. **Back-Button in Tools unsichtbar:** "← Zurück"-Button lag unter dem CoachHeader
   (z-index: 100). Overlay startete bei `inset: 0` (top: 0), CoachHeader verdeckte
   die ersten 64px des Tool-Inhalts.

## Root Causes

### RC-1: Veraltete Routen in SessionSidebar + Landing
Nach NC-NAV (Phase C, Commit `ff03384`) wurden Tool-Routen von `/zopa` auf `/app/zopa`
umbenannt. `SessionSidebar.tsx` und `Landing.tsx` wurden nicht mitaktualisiert —
beide navigierten weiterhin zu `/zopa`, was kein Match in der Route-Tabelle hatte.

**Dateien:** `src/components/SessionSidebar.tsx`, `src/pages/Landing.tsx`

### RC-2: Index unmounts bei jedem Tool-Wechsel (Flat Routing)
Mit Flat Routes (`/app`, `/app/zopa` als separate Top-Level-Routen) unmountete
`Index.tsx` bei jedem Tool-Nav. Beim Remount:
- `loadProfile` → Supabase-Query `user_profiles` (~227ms)
- `loadSessions` → Supabase-Query `negotiation_sessions` (~159ms)
- Alle ChatMessage-Komponenten neu erstellt → N×ReactMarkdown-Parse

**Fix:** Nested Routing — `/app/zopa` als Kind-Route unter `/app`. Index bleibt
permanent gemountet. Outlet rendert aktives Tool als Fixed-Overlay.

### RC-3: Overlay startete bei top: 0 statt top: 64
`CoachHeader` hat `position: fixed; z-index: 100`. Overlay mit `inset: 0; z-index: 40`
startete hinter dem Header — die ersten 64px Tool-Inhalt (inkl. "← Zurück") waren
unsichtbar.

## Fixes

### Fix 1 — Routen-Strings korrigiert
`SessionSidebar.tsx`: `/zopa` → `/app/zopa` für alle 6 Tools.
`Landing.tsx`: `/zopa` → `/app/zopa`, `/whatif` → `/app/what-if`, `/strategy` → `/app/strategy`.

### Fix 2 — Nested Routing + Outlet-Overlay
`App.tsx`: Tool-Routen als Kind-Routen unter `/app`.
`Index.tsx`: `useMatch('/app/:tool')` + bedingter Outlet-Div:
```tsx
{toolMatch && (
  <div style={{ position: 'fixed', top: 64, left: 0, right: 0, bottom: 0,
                zIndex: 40, overflowY: 'auto', background: '#FFFFFF' }}>
    <Outlet />
  </div>
)}
```
- `top: 64` → unter CoachHeader (z-100)
- `z-40` → BottomTabBar (z-50) bleibt auf dem Tool sichtbar
- Index: nie Unmount → kein Re-fetch, kein Message-Rerender

### Fix 3 — Performance (Streaming + Remount)
- `ChatMessage`: `React.memo` + `useMemo` für alle Parse-Operationen
  (parseStrategyBlocks, sanitizeAIContent, splitCompliance)
- `ChatInput`: `React.memo` (war vorher bei jedem Streaming-Token neu gerendert)
- `Index.tsx`: `startTransition` für Message-Restore (Browser malt zuerst)
- `Index.tsx`: `isLoading`-Guard verhindert per-Token AnalysisContext-Writes
- `TeamDashboard.tsx`: `AbortController` + 8s Timeout + `Promise.all`

### Fix 4 — ProtectedRoute-Tier-Gate entfernt
`ProtectedRoute.tsx` leitete bei `subscription_tier === "free"` zu `/` weiter —
Cold-Start-Lockout möglich wenn localStorage leer. Gate entfernt; Tier-Prüfung
erfolgt innerhalb Index.tsx nach DB-Laden.

## Abschluss

**Status:** DONE
Commit: `0810ab0` (negotiation-buddy) — 2026-06-30
Verified: tsc --noEmit clean ✓ | User-Bestätigung 404 behoben ✓ | ZOPA-Tool öffnet korrekt
API contract updated: no
DB delta: none
ADR created/amended: none
Docs updated: docs/delivery/bugs/BUG-20260630-tool-nav-404-perf.md
