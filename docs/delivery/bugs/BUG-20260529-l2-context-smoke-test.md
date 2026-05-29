# BUG-20260529-l2-context-smoke-test

**Erstellt:** 2026-05-29
**Status:** OPEN
**Risiko:** P3
**TARGET REPO:** negotiationcoach-backend
**Layer:** 2
**Bug-Typ:** Contract-Gap (Test-Gap — fehlende Live-Verifikation, kein Code-Defekt)
**Betroffene Tiers:** kmu, profi
**ADR-Constraints:** keine erkennbar

## Symptom

Die curl-basierten Acceptance Criteria AC-2, AC-3 und AC-4 aus dem FEATURE-L2-CONTEXT-Plan
konnten nicht gegen den Live-Render-Endpunkt verifiziert werden, da API-Keys und JWT-Tokens
in der Claude Code Umgebung nicht verfügbar sind. Kein Code-Fehler bekannt —
die Unit-Tests (Tests A/B/C, Layer2.test.ts) laufen durch. Live-Verhalten unbestätigt.

## Ort

- `/api/enrich` — Render.com Live-Endpunkt
- `src/layer2/marketContextExtractor.ts` — HAIKU-Extraction mit context_notes
- `src/layer2/marketDataResolver.ts` — contextHash als cache key (category-Spalte)
- Supabase `knowledge_graph` — Tabelle, category-Differenzierung zu verifizieren

## Reproduktion

Nicht reproduzierbar im klassischen Sinne — manuelle Verifikation erforderlich:

**AC-2 — Funktionaler Smoke-Test (context_notes vorhanden):**
```bash
curl -X POST https://[RENDER_URL]/api/enrich \
  -H "Authorization: Bearer [KMU_JWT]" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "[SESSION_ID_MIT_CONTEXT_NOTES]",
    "region": "München"
  }'
```
→ Erwartung: HTTP 200, `market_context_summary` nicht null/leer,
  `market_data_source`: `web_search` oder `knowledge_graph`

**AC-3 — Fallback-Verhalten (kein context_notes):**
```bash
curl -X POST https://[RENDER_URL]/api/enrich \
  -H "Authorization: Bearer [KMU_JWT]" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "[SESSION_ID_OHNE_CONTEXT_NOTES]",
    "region": "München"
  }'
```
→ Erwartung: HTTP 200 (kein Fehler), `market_data_source` nicht `none`
  (generische Query greift auch ohne context_notes)

**AC-4 — Cache-Key-Differenzierung:**
Zwei `/api/enrich`-Calls mit identischem `type+region` aber unterschiedlichem `context_notes`:
- Call A: Session mit `context_notes='Senior Software Engineer, SaaS'`
- Call B: Session mit `context_notes='Junior Buchhalter, Bank'`

→ Erwartung: `knowledge_graph`-Tabelle zeigt zwei unterschiedliche `category`-Werte
  (unterschiedliche contextHashes)

Supabase-Query zur Verifikation:
```sql
SELECT data_type, region, category, created_at
FROM knowledge_graph
WHERE data_type = 'gehalt' AND region = 'München'
ORDER BY created_at DESC LIMIT 5;
```

## Logs / Fehlermeldungen

Keine — kein Fehler bekannt. Unit-Tests (Tests A/B/C in `tests/layer2/layer2.test.ts`) PASS.
TypeCheck: 0 Fehler (tsc --noEmit).

## Verdacht

Kein Code-Defekt vermutet. Live-Verhalten entspricht wahrscheinlich der Spec,
aber unbestätigt. Risiko: HAIKU-Extraktion könnte auf dem Live-System anders
reagieren als in lokalen Tests (z.B. Modell-Antwortformat, Token-Limit-Grenzfälle).

## Plan

_Manuell durch Maik gegen Render-Backend ausführen. Kein /bug-plan erforderlich — nur Verifikation._

## Implement

_Kein Code-Fix erwartet. Falls AC-2/3/4 fehlschlagen: neu analysieren._

## Abschluss

_Nach erfolgreicher manueller Verifikation aller drei ACs: Status → CLOSED, Ergebnis hier dokumentieren._
