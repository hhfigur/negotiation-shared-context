# Diagnosis Report — BUG-20260521-enrich-500

**Datum:** 2026-05-22
**Bug-ID:** BUG-20260521-enrich-500
**Status:** OPEN → Fix implementiert
**Root Cause:** inputs nicht in DB gespeichert → null-Zugriff in /api/enrich → TypeError → 500

---

## 1. Bug Summary

`POST /api/enrich` gibt HTTP 500 zurück. Layer-2-Marktdaten fehlen im Plan.
Ursache: `/api/analyze` und `/api/analyze-full` speichern `inputs` nicht in `negotiation_sessions`.
`/api/enrich` liest `session.inputs` aus der DB → `null` → `null.tier = req.tier` → TypeError → 500.

---

## 2. Observed — direkt im Code verifiziert

**O-001:** `negotiation_sessions.inputs` ist als JSONB-Spalte vorhanden (nullable).
Migration `20260408120000_add_analysis_columns_to_negotiation_sessions.sql:20`:
```sql
ADD COLUMN IF NOT EXISTS inputs JSONB
```
Kommentar: "NegotiationInputs payload passed to /api/analyze or /api/analyze-full" — war als
Speicherort vorgesehen, aber nie implementiert.

**O-002:** `/api/analyze` (routes.ts:162–169) speichert `inputs` NICHT:
```typescript
.insert({
    user_id:        req.user!.id,
    negotiation_id: ...,
    layer1_result:  result,
    // ← inputs fehlt!
})
```

**O-003:** `/api/analyze-full` (routes.ts:240–248) speichert `inputs` NICHT:
```typescript
.insert({
    user_id:        req.user!.id,
    negotiation_id: ...,
    layer1_result:  analysis,
    layer2_result:  enriched ?? null,
    // ← inputs fehlt!
})
```

**O-004:** `/api/enrich` (routes.ts:204–205) liest `session.inputs` und setzt sofort `.tier`:
```typescript
const inputs = (session as { inputs: NegotiationInputs }).inputs; // → null
inputs.tier = req.tier; // → TypeError: Cannot set properties of null
```
Kein null-Check vor dem Zugriff.

**O-005:** `EnrichRequestSchema` (validation.ts:70–73) akzeptiert nur `sessionId` + `region`,
kein `inputs` aus Request-Body — obwohl der Frontend-Client `inputs` mitschickt
(apiClient.ts: `{ sessionId, inputs }`). Die gesendeten `inputs` werden serverseitig ignoriert.

---

## 3. Inferred

**I-001:** Alle Sessions die über `/api/analyze` oder `/api/analyze-full` erstellt wurden,
haben `inputs = null` in der DB. Jeder Enrich-Versuch auf diese Sessions schlägt fehl.

**I-002:** Der Bug existiert seit der initialen Implementierung von `/api/enrich` —
die `inputs`-Spalte war als Speicherort geplant, wurde aber nie im Analyze-Insert befüllt.

**I-003:** `/api/analyze-full` ruft intern `enrichWithMarketData(analysis, inputs, region)`
direkt auf (ohne DB-Roundtrip) — dort funktioniert Enrich korrekt. Nur der separate
`/api/enrich`-Endpunkt (der aus der DB liest) ist broken.

---

## 4. Missing

Keine offenen Fragen — Root Cause vollständig aus Code-Lektüre bestimmbar.

---

## 5. Root Cause

**Beides fehlt:** weder speichern `/api/analyze` noch `/api/analyze-full` die `inputs` in der DB,
noch hat `/api/enrich` einen null-Check bevor es `session.inputs.tier` setzt.

**Call Chain:**
```
Frontend: ZopaCalculator.tsx → analyzeOnly() → /api/analyze → session erstellt (inputs=null)
Frontend: ZopaCalculator.tsx → enrich(sessionId, inputs) → /api/enrich
Backend:  session.inputs aus DB lesen → null
          null.tier = req.tier → TypeError
          next(err) → 500
```

---

## 6. Files Involved

| Datei | Repo | Rolle |
|---|---|---|
| `src/api/routes.ts` | negotiationcoach-backend | Fix: inputs in analyze + analyze-full speichern, null-Check in enrich |
| `supabase/migrations/20260408*.sql` | negotiationcoach-backend | inputs-Spalte vorhanden (kein Fix nötig) |
| `src/api/validation.ts` | negotiationcoach-backend | EnrichRequestSchema (kein Fix nötig) |

---

## 7. Recommended Fix

**Fix 1 — `/api/analyze` (routes.ts):** `inputs` zum Insert hinzufügen:
```typescript
.insert({
    user_id:        req.user!.id,
    negotiation_id: ...,
    layer1_result:  result,
    inputs:         inputs,   // NEU
})
```

**Fix 2 — `/api/analyze-full` (routes.ts):** `inputs` zum Insert hinzufügen:
```typescript
.insert({
    user_id:        req.user!.id,
    negotiation_id: ...,
    layer1_result:  analysis,
    layer2_result:  enriched ?? null,
    inputs:         inputs,   // NEU
})
```

**Fix 3 — `/api/enrich` (routes.ts):** null-Check vor Tier-Zuweisung:
```typescript
const rawInputs = (session as { inputs: NegotiationInputs | null }).inputs;
if (!rawInputs) {
    throw new ValidationError('Session hat keine gespeicherten Inputs — /api/analyze zuerst aufrufen');
}
const inputs = rawInputs;
inputs.tier = req.tier;
```

**Keine Migration nötig** — `inputs`-Spalte existiert bereits.

---

## 8. Acceptance Criteria

- AC-1: `npx tsc --noEmit` → 0 Fehler
- AC-2: `curl POST /api/analyze` → Session in DB mit `inputs != null` verifizierbar
- AC-3: `curl POST /api/enrich` mit dieser Session-ID → HTTP 200, `result.market_median` vorhanden
- AC-4: `/api/enrich` mit alter Session (inputs=null in DB) → 400 `VALIDATION_ERROR`, kein 500 mehr
