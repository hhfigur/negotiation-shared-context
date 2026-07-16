# Verify-Harness Contract

**Owner:** Feature Delivery Controller (Claude)
**Status:** Active — SOFT-LAUNCH (siehe `docs/decision-log/ADR-011-verify-loop-gate.md`)
**Last updated:** 2026-07-16
**Skill:** `.claude/skills/verify-loop/SKILL.md`

---

## Zweck

`scripts/verify.sh` ist das ausführbare Orakel für jede Code-Delivery in
`negotiation-buddy` und `negotiationcoach-backend`. Es ersetzt die bisherige
Praxis, `npx tsc --noEmit` allein als Fertigstellungsnachweis zu akzeptieren.

Dieser Contract ist repo-agnostisch: beide Repos implementieren ihn, dürfen
aber Schritte weglassen, die für sie nicht zutreffen (siehe
"Repo-Spezialisierung" unten) — kein Schritt wird jedoch stillschweigend
übersprungen, ein fehlender Schritt muss explizit als `[SKIP] <Grund>`
ausgewiesen werden.

## Pflichtreihenfolge

Abbruch bei erstem Fehler (`exit != 0` propagiert, kein Weiterlaufen der
Folgeschritte):

```
1. tsc --noEmit
2. Testsuite (npm test / vitest run)
3. contract-check        (nur wenn API-/Contract-relevante Dateien geändert wurden)
4. curl-assert / smoke   (nur Backend — setzt laufenden lokalen Dev-Server voraus)
5. lint
```

## Health-Check vor Schritt 4 (nur Backend)

Bevor curl-Assertions laufen, muss `verify.sh` prüfen, ob der lokale
Dev-Server erreichbar ist (z.B. `curl -sf http://localhost:<PORT>/health`
oder ein äquivalenter leichter Endpoint). Ist der Server nicht erreichbar,
ist das ein eigener, klar benannter Fehlgrund ("server not running") — nicht
als curl-Assertion-Fehler getarnt.

## Ausgabeformat

Pro Schritt eine Zeile:

```
[PASS] <Schrittname>
[FAIL] <Schrittname> (exit <code>) — <erste Fehlerzeile>
[SKIP] <Schrittname> — <Grund>
```

Abschluss-Summary (maschinenlesbar, letzte Zeile des Scripts):

```
VERIFY_RESULT: PASS
```
oder
```
VERIFY_RESULT: FAIL (<n>/5 Schritte grün) — erster Fehlerschritt: <Name>
```

**Exit-Code des Gesamtscripts** = Anzahl fehlgeschlagener Schritte
(0 = alle grün).

## Repo-Spezialisierung

### negotiationcoach-backend

- Dev-Server: `npm run dev` (nodemon + ts-node, Port via `process.env.PORT`,
  Default `3001` — siehe `src/api/routes.ts`).
- `scripts/curl-assert.sh` (jq-basiert): POSTet Beispiel-Payloads an lokale
  Endpunkte, prüft erwartete JSON-Felder (z.B. `zopaExists`, `zopaMin`,
  `zopaMax`, `nashSolution`, `_debug.model`).
- `scripts/smoke-enrich.sh`: Smoke-Test für `/api/enrich` — prüft, dass
  `EnrichedAnalysisResult`-Felder vorhanden und plausibel sind.
  **Hinweis (Observed, 2026-07-16):** Layer 2 ist seit R-2026-05 (NC-L2-FIX)
  released und laut `product/roadmap.md`/`docs/features/layer3-simulation.md`
  verifiziert — dieser Smoke-Test wird auf sauberem `main` als **GREEN**
  erwartet, nicht als bekanntes RED-Orakel.
- Lint-Schritt: Kein `.eslintrc*`/`eslint.config.*` im Repo vorhanden
  (Observed, 2026-07-16). Bis ein Minimal-Setup existiert, ist Schritt 5
  `[SKIP] lint — kein Setup vorhanden` — kein stiller Erfolg vortäuschen.
- Testsuite: `npm test` deckt aktuell nur `tests/layer1/` und `tests/layer2/`
  ab; `tests/layer3/` existiert, ist aber nicht verdrahtet (Observed,
  2026-07-16) — wer diesen Contract für das Backend implementiert, sollte
  das beheben oder die Lücke explizit im Script kommentieren.

### negotiation-buddy

- Kein serverabhängiger Schritt — Schritt 4 (curl-assert) entfällt für
  dieses Repo.
- Testsuite: `vitest run`.
- Lint: `npm run lint` (eslint, vorhanden).
- Optional: `npm run build` als zusätzlicher Schritt, falls gewünscht (nicht
  Pflichtbestandteil dieses Contracts).

## Verweis

- Skill: `.claude/skills/verify-loop/SKILL.md`
- Eingebunden in: `.claude/skills/feature-implement/SKILL.md` Schritt 0/3
- Template: `docs/delivery/claude-code-prompt-templates-dev.md` Template
  2b-DEV, Acceptance-Abschnitt
- Architekturentscheidung: `docs/decision-log/ADR-011-verify-loop-gate.md`
