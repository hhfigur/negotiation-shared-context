# Brief: NC-ONBOARDING — Guest Mode / Free-Tier Onboarding-Optimierung

**Status:** Qualified
**Release:** TBD (Wave 2 — Tier 3, nach NC-TELEMETRY)
**Typ:** Feature
**Priorität:** P2 — Conversion-Pfad; abhängig von Telemetrie-Daten
**Erstellt:** 2026-04-29

---

## Lagebeurteilung

Der aktuelle Guest-Mode funktioniert (Chat ohne Login möglich), aber
der Übergang von Guest → Free → Paid ist nicht optimiert. Es fehlen:
- Ein klarer Wert-Moment vor dem Login-Gate
- Sichtbarer Upgrade-CTA wenn Tier-Features geblockt sind
- Onboarding-Sequenz die Nutzer zum ersten vollständigen Analyse-Abschluss führt

Ohne NC-TELEMETRY sind Abbruchpunkte nicht bekannt — daher ist
NC-TELEMETRY eine Voraussetzung für die datengetriebene Ausgestaltung
dieses Items.

---

## Ziel / Outcome

Messbar mehr Nutzer die den Chat-Flow vollständig abschließen (isComplete=true
mit Layer-1-Ergebnis) — als Indikator für Produkt-Fit und Conversion-Readiness.

---

## Problem

- Onboarding-Friction unbekannt (kein Telemetrie)
- Kein sichtbarer Upgrade-Pfad für Guest-Nutzer
- "What-If Machine" zeigt Profi-Badge ohne Erklärung was Profi-Upgrade bringt
- Kein strukturierter erster Schritt nach Login

---

## Affected Repos

- `negotiation-buddy` (Frontend — Chat-Flow, Upgrade-CTAs, Onboarding-Dialogs)
- `shared-context` (Docs: design decisions wenn relevant)

---

## Scope

**Erst nach NC-TELEMETRY-Daten definierbar.** Dieser Brief ist vorläufig.

**Hypothetischer Minimal-Scope (zu validieren mit Telemetrie):**

1. **Wert-Moment vor Login-Gate**: Guest-User sieht erstes Analyse-Ergebnis
   BEVOR sie zum Login aufgefordert werden (aktuell: nach erstem AI-Response)
2. **Upgrade-CTA**: Bei gesperrten Profi-Features klar kommunizieren was
   Upgrade bringt (konkrete Beispiele: Marktdaten, What-If Simulator vollständig)
3. **Erster-Schritt-Guidance**: Nach Login/Signup: kurze Orientierung
   ("Starten Sie mit Gehaltsverhandlung" etc.)

**Kein Full-Onboarding-Wizard** — zu aufwändig ohne Telemetrie-Validierung.

---

## Non-Goals

- Vollständiges Onboarding-Redesign
- Neue Screens ohne Telemetrie-Evidenz
- Stripe-Checkout (NC-TIER-01 / AR-032)
- Änderungen an Backend-Logik

---

## Acceptance Criteria

**Vorläufig — wird nach NC-TELEMETRY-Daten präzisiert:**

1. Mindestens eine Telemetrie-gestützte Verbesserung am Onboarding-Flow
2. Chat-Flow-Abschlussrate nach Änderung messbar (via NC-TELEMETRY)
3. TypeCheck negotiation-buddy: 0 Fehler
4. Kein Rückgang in bestehenden Funktionen (Chat, Tools)

---

## Telemetry / Measurement

**Abhängig von NC-TELEMETRY.** Erst nach Telemetrie-Setup werden
konkrete Targets gesetzt:

- Target: Abschlussrate Chat-Flow (isComplete=true) ↑ X% (TBD nach Baseline)
- Guardrail: Kein Rückgang bei Session-Starts

**Gap:** Ohne NC-TELEMETRY ist kein quantitatives Target möglich.

---

## Risks / Open Questions

| Risiko | Bewertung |
|---|---|
| Lovable-verwaltetes Frontend: EF-Änderungen und UI-Änderungen komplex | Medium — Abhängigkeit von Lovable-Deployment |
| Ohne Telemetrie-Daten: Änderungen könnten am falschen Ort ansetzen | **Blocker** — NC-TELEMETRY muss zuerst Daten liefern |
| ADR erforderlich? | Nein — reine UX/Frontend-Arbeit |

**Blockierender Hinweis:**
Dieser Brief ist NICHT bereit für Delivery bis NC-TELEMETRY mindestens
2 Wochen Daten geliefert hat. Status bleibt Qualified bis dann.
