# Delivery Brief: NC-L3-SIM-REALISM
## Opponent Simulation — Realismus-Fix (Eröffnungsformel + Warning)

**Release:** TBD (Wave 3)
**Status:** Qualified
**Affected repos:** negotiationcoach-backend (primary), negotiation-buddy (secondary)
**Tier impact:** profi only
**Created:** 2026-07-02
**Priority:** P1 — Simulation trivial unbrauchbar wenn Eröffnungsangebot über Nutzerziel
**Depends on:** NC-L3-OPPONENT (Released) + NC-L3-OPPONENT-UI (Released)
**ADR:** ADR-009 (keine Änderung)

---

## Problem (Observed)

Aufgedeckt bei Ersttest: Simulation mit Gehaltsverhandlung
(own_target=44000, own_minimum=42000, opponent_estimated_max=48000, kooperativ, mittel)
öffnet die KI-Gegenseite mit **47.400 €** — weit über dem Nutzerziel von 44.000 €.
Die Verhandlung ist trivial gewonnen, bevor der Nutzer einen Zug macht.

### Ursache 1: Falsche Formel in opponentEngine.ts (Zeile 40)

```typescript
// IST (falsch): Eröffnung nahe am Maximum
hidden_opponent_target = opponent_estimated_max - STYLE_ANCHOR_MARGIN * range;
// → 48000 - 0.10 * 6000 = 47.400

// SOLL: Eröffnung nahe am Minimum (Gegenseite startet niedrig/konservativ)
hidden_opponent_target = opponent_estimated_min + STYLE_OPENING_MARGIN * opponent_range;
// → 38000 + 0.15 * 10000 = 39.500
```

`opponent_range = opponent_estimated_max - opponent_estimated_min` (nicht ZOPA-Range!)
Dies modelliert korrekt: Gegenseite kennt ihre eigene Range und öffnet nahe ihrem
konservativen Ende.

### Ursache 2: Falsches Vorzeichen im System-Prompt (Zeile 75)

```
"Dein Mindestwert (du gehst nie darunter): 44700"
```

Für einen Arbeitgeber in einer Gehaltsverhandlung ist 44700 das **Maximum**, nicht
das Minimum. Die KI instruiert sich falsch und bietet möglicherweise mehr an als
sie sollte.

**Fix:** Richtungskorrektur im Prompt:
```
"Dein Budget-Maximum (du bietest NIE MEHR als): 44700"
```

---

## Scope (Phase 1 + 2 — dieses Item)

### Phase 1 — Backend: opponentEngine.ts

**Datei:** `negotiationcoach-backend/src/layer3/opponentEngine.ts`

**Fix 1 — STYLE_ANCHOR_MARGIN → STYLE_OPENING_MARGIN (neue Semantik, neue Werte):**

```typescript
// Ersetze STYLE_ANCHOR_MARGIN durch STYLE_OPENING_MARGIN
// Margin bezieht sich jetzt auf opponent_range (min→max), nicht ZOPA-range
const STYLE_OPENING_MARGIN: Record<OpponentStyle, number> = {
  kooperativ:  0.15,  // öffnet moderat über Minimum, gibt schnell nach
  sachlich:    0.08,  // öffnet konservativ, Zugeständnisse linear
  hart:        0.03,  // öffnet sehr nah am Minimum, gibt kaum nach
  manipulativ: 0.02,  // öffnet aggressiv niedrig, setzt Druck auf
};
```

**Fix 2 — computeHiddenOpponentRange:**

```typescript
export function computeHiddenOpponentRange(
  setup: OpponentSimulationSetup,
): HiddenOpponentRange {
  const zopa = calculateZopa(setup.own_minimum, setup.opponent_estimated_max);
  if (!zopa.zopa_exists) {
    return {
      hidden_opponent_minimum: setup.opponent_estimated_max,
      hidden_opponent_target:  setup.opponent_estimated_max,
    };
  }
  const zopa_range = zopa.zopa_max - zopa.zopa_min;
  const opp_range  = setup.opponent_estimated_max - setup.opponent_estimated_min;

  const offset  = DIFFICULTY_OFFSET[setup.scenario_difficulty];
  const opening = STYLE_OPENING_MARGIN[setup.opponent_style];

  return {
    // Gegner-Ceiling: wie weit die Gegenseite maximal zugesteht
    hidden_opponent_minimum: zopa.zopa_min + offset * zopa_range,
    // Gegner-Eröffnungsanker: nahe am konservativen Ende der Gegner-Range
    hidden_opponent_target:  setup.opponent_estimated_min + opening * opp_range,
  };
}
```

**Fix 3 — buildOpponentSystemPrompt, Zeile 75-76:**

```typescript
// Ersetze:
`- Dein Mindestwert (du gehst nie darunter): ${hiddenRange.hidden_opponent_minimum.toFixed(2)}`,
`- Dein Zielwert (Anker für dein erstes Angebot): ${hiddenRange.hidden_opponent_target.toFixed(2)}`,

// Mit:
`- Dein Budget-Maximum (du bietest NIE MEHR als diesen Betrag an): ${hiddenRange.hidden_opponent_minimum.toFixed(2)}`,
`- Dein Eröffnungsangebot (starte mit diesem Wert und verhandle von hier): ${hiddenRange.hidden_opponent_target.toFixed(2)}`,
```

**Fix 4 — computeSimulationWarning (neue exportierte Funktion):**

```typescript
// Gibt einen Warntext zurück wenn das berechnete Eröffnungsangebot
// bereits über oder nahe dem Nutzerziel liegt.
export function computeSimulationWarning(
  setup: OpponentSimulationSetup,
  hiddenRange: HiddenOpponentRange,
): string | null {
  if (hiddenRange.hidden_opponent_target >= setup.own_target) {
    return `Hinweis: Das berechnete Eröffnungsangebot der Gegenseite (${Math.round(hiddenRange.hidden_opponent_target).toLocaleString('de-DE')} €) liegt bereits über Ihrem Ziel (${Math.round(setup.own_target).toLocaleString('de-DE')} €). Die Simulation bietet wenig Verhandlungsspielraum — erhöhen Sie Ihr Ziel für eine realistischere Übung.`;
  }
  return null;
}
```

### Phase 2 — Backend: opponentSimulationRoutes.ts

In `POST /api/opponent-simulation/start`, nach `computeHiddenOpponentRange`:

```typescript
const warning = computeSimulationWarning(setup, hiddenRange);
```

Response um optionales Feld erweitern:

```typescript
res.status(201).json({
  simulation_session_id: session.id,
  status:    session.status,
  max_turns: session.max_turns,
  opening_message: opening,
  warning: warning ?? undefined,   // nur wenn vorhanden
});
```

### Phase 3 — Frontend: src/pages/OpponentSimulator.tsx

In der Playing-Phase (nach erfolgreichem Start): wenn `warning` in der Response
vorhanden ist, ein dismissibles Info-Banner über der Message-Liste anzeigen.
Pattern: bestehender Toast-Mechanismus oder simples Inline-Banner.

Außerdem: `StartOpponentSimulationResponse` in `src/lib/types.ts` um
`warning?: string` erweitern.

---

## Nicht in Scope (Phase 3 — separates Item)

- Marktdaten-Kalibrierung: `/api/enrich`-Ergebnisse zur automatischen Kalibrierung
  von `opponent_estimated_min/max` basierend auf Branche, Inflation, letzter Erhöhung
- Neue Pflichtfelder im Setup: `current_salary`, `time_since_last_raise`
- Sektorspezifische Inflationsdaten-Integration

---

## Acceptance Criteria

- AC-1: Mit Werten (own_target=44000, own_minimum=42000, opponent_max=48000,
  opponent_min=38000, kooperativ, mittel) öffnet die Gegenseite UNTER 44000
  (erwartete Eröffnung ca. 39.500 €)
- AC-2: System-Prompt enthält "Budget-Maximum" und "Eröffnungsangebot" — nicht
  "Mindestwert" und "Zielwert"
- AC-3: `computeSimulationWarning` gibt null zurück wenn Eröffnung < own_target
- AC-4: `/start`-Response enthält `warning`-Feld wenn Eröffnung >= own_target,
  `undefined` sonst (kein leerer String)
- AC-5: Frontend zeigt Warning-Banner wenn Response.warning vorhanden
- AC-6: tsc --noEmit 0 Fehler in beiden Repos

---

## Dateien

| Datei | Repo | Art |
|---|---|---|
| `src/layer3/opponentEngine.ts` | negotiationcoach-backend | 4 Fixes (Formel + Prompt + Warning-Funktion) |
| `src/api/opponentSimulationRoutes.ts` | negotiationcoach-backend | Warning aufrufen + in Response |
| `src/pages/OpponentSimulator.tsx` | negotiation-buddy | Warning-Banner in Playing-Phase |
| `src/lib/types.ts` | negotiation-buddy | `warning?: string` in StartOpponentSimulationResponse |
