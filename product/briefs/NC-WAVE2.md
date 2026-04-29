# Brief: NC-WAVE2 — Wave 2 Scope-Dokument

**Status:** In Delivery
**Release:** R-2026-07
**Typ:** Enabler
**Priorität:** P0 — kein Wave-2-Delivery ohne dieses Item
**Erstellt:** 2026-04-29

---

## Lagebeurteilung

Wave 1 ist formal abgeschlossen (gate cleared 2026-04-16, alle carry-forwards
in R-2026-05 und R-2026-06 abgearbeitet). Die Wave-1-Gate-Datei definiert
konkrete Post-Gate-Actions, die als Wave-2-Startpunkte dienen.

**Quellen für den Wave-2-Scope:**
- `docs/audits/wave1-completion-gate.md` — Post-Gate-Actions #2, #3, #4, #5
- `product/strategy.md` — Strategic Focus 2 (Wave 2 Scope) + Focus 3 (Tier-Conversion)
- `product/roadmap.md` — Discovery queue (NC-TELEMETRY, NC-ONBOARDING)

---

## Ziel / Outcome

NC-WAVE2 liefert ein vollständig gefülltes Feature Register für Wave 2:
- Alle Wave-2-Items haben eine NC- oder AR-ID
- Jedes Item hat Status Qualified oder Planned
- Jedes Item hat einen Brief in `product/briefs/`
- `product/roadmap.md` "Now" ist auf Wave-2-Items aktualisiert
- `product/strategy.md` ist auf aktuellen Stand gebracht

NC-WAVE2 selbst produziert KEINEN Code. Alle Code-Deliverables folgen
in nachfolgenden Releases.

---

## Problem

Nach Wave-1-Abschluss gibt es keine definierten Wave-2-Items im Feature Register.
Die roadmap.md zeigt nur Platzhalter. Ohne dieses Scope-Dokument kann kein Wave-2-
Delivery beginnen — kein Brief, kein GO, kein Implement.

---

## Affected Repos

- `shared-context` (Docs only — alle Änderungen hier)

---

## Wave-2-Items (zu definieren + zu briefen)

### Tier 1 — Sicherheit + Compliance (höchste Priorität)

| ID (neu) | Titel | Typ | Herkunft |
|---|---|---|---|
| NC-SEC-01 | VG-01/VG-02: RLS-Audit in Produktion — teams und negotiation_sessions | Enabler | wave1-gate Post-Gate #2 |
| NC-SEC-02 | VG-05-A: JWT-Auth-Hardening in Edge Functions (tier enforcement) | Enabler | wave1-gate Post-Gate #3 |

**Hinweis NC-SEC-01:** VG-01 (teams RLS) und VG-02 (negotiation_sessions cross-user)
sind Critical/High-Risk aus Wave-1-Audit. Unverifizierten RLS in Produktion bedeutet
potenziell unzureichende Datentrennung zwischen Nutzern.

**Hinweis NC-SEC-02:** VG-05-A dokumentiert, dass Tier-Enforcement in Edge Functions
aktuell dekorativ ist (kein JWT, kein echtes Tier-Gate). Affects: kmu/profi Tier-Value-Promise.

### Tier 2 — Tier-Conversion + Revenue-Readiness

| ID (neu) | Titel | Typ | Herkunft |
|---|---|---|---|
| NC-TIER-01 | Stripe-Readiness-Check: was fehlt bis Stripe live? | Research | Strategy Focus 3 |
| AR-032 | Stripe Webhook Handler implementieren | Feature | existing (Paused) |

**Hinweis:** AR-032 kann erst beginnen wenn Stripe live ist (extern, nicht von uns kontrolliert).
NC-TIER-01 klärt zuerst, welche anderen Vorbedingungen (Frontend, DB, Emails) fehlen.

### Tier 3 — Observability + Onboarding

| ID (neu) | Titel | Typ | Herkunft |
|---|---|---|---|
| NC-TELEMETRY | Telemetrie-Setup — Konversions- und Nutzungsdaten | Feature | Discovery queue |
| NC-ONBOARDING | Guest Mode / Free-Tier Onboarding-Optimierung | Feature | Discovery queue |

**Hinweis NC-TELEMETRY:** Baselines für alle Metriken sind UNKNOWN. Kein datengetriebenes
Produkt-Entscheidungen möglich ohne Telemetrie. Sollte vor NC-ONBOARDING umgesetzt werden.

---

## Scope — exakt was sich in R-2026-07 ändert

| # | Datei | Änderung |
|---|---|---|
| 1 | `product/feature-register.md` | NC-SEC-01, NC-SEC-02, NC-TIER-01 als neue Items eintragen (Status: Qualified) |
| 2 | `product/feature-register.md` | NC-TELEMETRY, NC-ONBOARDING formal eintragen (Status: Qualified) |
| 3 | `product/feature-register.md` | AR-020b, AR-020c → Released |
| 4 | `product/briefs/NC-SEC-01.md` | Brief erstellen |
| 5 | `product/briefs/NC-SEC-02.md` | Brief erstellen |
| 6 | `product/briefs/NC-TIER-01.md` | Brief erstellen |
| 7 | `product/briefs/NC-TELEMETRY.md` | Brief erstellen |
| 8 | `product/briefs/NC-ONBOARDING.md` | Brief erstellen |
| 9 | `product/roadmap.md` | "Now" auf Wave-2-Items aktualisieren |
| 10 | `product/strategy.md` | Stale Constraints entfernen, neuen Fokus |

---

## Non-Goals

- Implementierung von NC-SEC-01, NC-SEC-02, NC-TIER-01, NC-TELEMETRY, NC-ONBOARDING
- Jeglicher Code in negotiationcoach-backend oder negotiation-buddy
- AR-032 (Stripe) implementieren — Stripe ist nicht live
- Layer 3 Simulation Engine
- Scenario Marketplace UI

---

## Implementierungsreihenfolge

1. Feature Register: NC-SEC-01, NC-SEC-02, NC-TIER-01, NC-TELEMETRY, NC-ONBOARDING eintragen
2. Feature Register: AR-020b, AR-020c → Released
3. Briefs für alle 5 neuen Items erstellen
4. Strategy.md aktualisieren
5. Roadmap "Now" aktualisieren
6. Commit + /close-task NC-WAVE2

---

## Acceptance Criteria

1. `product/feature-register.md` enthält alle 5 neuen Items mit ID, Typ, Status=Qualified, Affected Repos
2. `product/briefs/NC-SEC-01.md` bis `NC-ONBOARDING.md` existieren und sind gefüllt
3. AR-020b und AR-020c haben Status=Released im Feature Register
4. `product/strategy.md` ist aktuell (keine stale Constraints)
5. `product/roadmap.md` "Now" enthält Wave-2-Items in Prioritätsreihenfolge
6. Kein Code in negotiation-buddy oder negotiationcoach-backend geändert

---

## Telemetry / Measurement

Nicht anwendbar — reine Dokumentationsänderung.
NC-TELEMETRY wird nach diesem Item die Messlücken schließen.

---

## Risks / Open Questions

| Risiko | Bewertung |
|---|---|
| VG-01/VG-02 könnten bei Audit kritische Lücken aufdecken | Wahrscheinlich — NC-SEC-01 Brief muss Audit-Scope klar abgrenzen |
| NC-SEC-02 (VG-05-A) könnte ADR erfordern (welcher EF-Pfad, welches JWT-Schema) | Möglich — Brief muss ADR-Bedarf explizit markieren |
| NC-TIER-01 könnte ergeben dass viele Vorbedingungen für Stripe fehlen | Akzeptiert — Research-Item, Ergebnis fließt in R-2026-08+ |
| AR-032 bleibt extern blockiert | Bekannt — Paused-Status bleibt |
