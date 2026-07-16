# ADR-011 — Verify-Loop als Pflicht-Gate für Feature-/Bug-Delivery

**Status:** PROPOSED — 2026-07-16
**Datum:** 2026-07-16
**Entscheider:** Maik Figur
**Klassifizierung:** Prozess-/Governance-Entscheidung, cross-repo

---

## Kontext

`docs/features/loop-coding-integration.md` (Master-PLAN, GO erteilt) plant
die Einführung eines mechanischen Verifikationsloops (`verify.sh`) als
Ersatz für "TypeScript kompiliert" als Fertigstellungskriterium. Der Loop
selbst (`.claude/skills/verify-loop/SKILL.md`) und der zugehörige Contract
(`docs/contracts/verify-harness.md`) sind mit diesem Delivery bereits
angelegt.

Offen ist die eigentliche Architekturfrage: **Wird ein rotes `verify.sh`
zu einem harten Blocker für DONE/DONE_WITH_CONCERNS, oder bleibt es
zunächst ein empfohlenes, aber nicht erzwungenes Werkzeug?**

## Entscheidungsfrage

Soll `verify-loop` als **Hard Gate** in `/feature-implement` und `/bug-fix`
verankert werden (kein DONE ohne grünes `verify.sh`), oder als **Soft/
Advisory**-Mechanismus eingeführt werden?

## Optionen

| Kriterium | Option A — Sofort Hard Gate | Option B — Pilot zuerst (Backend) | Option C — Advisory only |
|---|---|---|---|
| Beschreibung | `verify-loop` wird ab sofort in beiden Repos verbindlich — kein DONE ohne grünes `verify.sh` | Nur Backend (konkretes Orakel: `/api/enrich`) macht den Gate verbindlich; Frontend bleibt vorerst advisory bis `verify.sh` dort erprobt ist | Skill dokumentiert den Loop als empfohlenes Muster, aber kein Hard-Gate |
| Aufwand | Mittel — beide Repos brauchen `scripts/verify.sh` sofort funktionsfähig | Mittel, aber gestaffelt | Gering |
| Risiko | Delivery-Verzögerung falls `verify.sh` in einem Repo noch Lücken hat (siehe Backend: kein Lint-Setup, Layer3-Tests nicht verdrahtet) | Geringer — Frontend-Harness kann in Ruhe reifen, ohne Blocker für laufende Frontend-Deliveries | Geringstes Risiko, aber auch geringste Wirkung — widerspricht dem Zweck des Vorhabens (Loop Coding soll verbindlich werden) |
| ADR-Konformität | Konsistent mit "ADR-Entscheidungen vor Implementierung", sofern hier entschieden | Konsistent | Konsistent, aber schwächt den eigentlichen Zweck |
| Reversibilität | Leicht reversibel (Skill-Text zurücksetzen) | Leicht reversibel | Leicht reversibel |
| Empfehlung | Vorläufig empfohlen für den Zielzustand, aber siehe Interim-Maßnahme unten | Alternative, falls Backend-Lücken (Lint, Layer3-Tests) sich als größer herausstellen als erwartet | Nicht empfohlen |

## Interim-Maßnahme (bereits aktiv — unabhängig vom Ausgang dieser ADR)

Unabhängig davon, welche Option letztlich entschieden wird, gilt ab diesem
Delivery bereits: **SOFT-LAUNCH.**

- Der Mechanismus (`.claude/skills/verify-loop/SKILL.md`,
  `docs/contracts/verify-harness.md`, Template-2b-DEV-Ergänzung) ist ab
  sofort verfügbar und wird in `/feature-implement` Schritt 0 sowie
  `/bug-fix` Phase 1.5 referenziert.
- Er ist **nicht blockierend**: ein rotes `verify.sh` verhindert aktuell
  noch keine DONE-Meldung, muss aber transparent im Implementer-Report
  ausgewiesen werden (kein stiller Fail).
- Diese Interim-Maßnahme ist keine Vorwegnahme der Entscheidung A/B/C —
  sie stellt nur sicher, dass der Loop ab sofort geübt und mit echten Daten
  (tatsächliche PASS/FAIL-Quote über mehrere Deliveries) gefüllt wird,
  bevor über den Hard-Gate-Charakter entschieden wird.
- Promotion zu Hard Gate erfolgt ausschließlich über dieses ADR, Status
  PROPOSED → DECIDED (kein separater Skill-Edit nötig — die Skills
  referenzieren den ADR-Status bereits jetzt).

## Entscheidung

*Noch offen — wird nach mindestens einem vollständigen Soft-Launch-Zyklus
(≥ 1 Feature- oder Bug-Delivery pro Repo mit `verify.sh`-Lauf) und
User-Bestätigung eingetragen.*

## Konsequenzen

- Bei Option A: `/feature-implement` Schritt 3 und `/bug-fix` Phase 3
  müssten um einen echten Abbruch-Pfad ("STOP — verify.sh rot, kein DONE")
  ergänzt werden.
- Bei Option B: Backend- und Frontend-Skill-Referenzen müssten
  unterschiedliche Gate-Stufen ausweisen — höherer Pflegeaufwand in den
  Skill-Texten.
- Bei Option C: Kein weiterer Skill-Änderungsbedarf, aber die in
  `docs/features/loop-coding-integration.md` Abschnitt 4 dokumentierte
  Zielsetzung ("verify-loop als Pflicht-Gate") würde nicht erreicht.

## Betroffene Items

- `docs/features/loop-coding-integration.md` (Master-Plan, GO erteilt)
- `.claude/skills/verify-loop/SKILL.md`
- `.claude/skills/feature-implement/SKILL.md` (Schritt 0, Schritt 3)
- `.claude/skills/bug-fix/SKILL.md` (Phase 1.5, Persistenz-Ergänzung)
- `docs/contracts/verify-harness.md`
- Folge-Deliveries: Backend-Harness (`negotiationcoach-backend`),
  Frontend-Harness (`negotiation-buddy`)

## Referenzen

- `docs/features/loop-coding-integration.md` — Master-Plan (Abschnitt 4:
  ADR-Bedarf, Abschnitt 5: Contract-Skizze)
- `.claude/skills/adr-create/SKILL.md` — Format-Vorlage für dieses ADR
