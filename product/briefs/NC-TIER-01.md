# Brief: NC-TIER-01 — Stripe-Readiness-Check

**Status:** Qualified
**Release:** TBD (Wave 2 — Tier 2)
**Typ:** Research
**Priorität:** P1 — Prerequisite für Revenue-Aktivierung
**Erstellt:** 2026-04-29

---

## Lagebeurteilung

Stripe ist nicht live. AR-032 (Stripe Webhook Handler) ist formal Paused.
Bevor AR-032 sinnvoll gestartet werden kann, muss bekannt sein, welche
weiteren Vorbedingungen fehlen — Frontend-Flows, Preisseiten, DB-Felder,
Email-Bestätigungen, Dankeschön-Seiten etc.

Ohne diesen Check riskiert AR-032, nur den Webhook zu implementieren
während ein Dutzend andere Gaps den tatsächlichen Checkout blockieren.

---

## Ziel / Outcome

Vollständige Checkliste aller Voraussetzungen für einen funktionierenden
Stripe-Checkout-Flow in NegotiationCoach AI. Priorisierte Liste der Gaps.
Input für Planung von AR-032 und begleitenden NC- Items.

---

## Problem

- Stripe-Readiness ist unbekannt
- AR-032 allein reicht nicht für funktionierenden Abo-Flow
- Kein Conversion-Tracking bis NC-TELEMETRY aktiv

---

## Affected Repos

- `shared-context` (Deliverable: `docs/delivery/stripe-readiness.md`)
- `negotiation-buddy` und `negotiationcoach-backend` — READ ONLY für Analyse

---

## Scope

Research-Aufgabe. Keine Code-Änderungen.

Zu prüfen:
1. **Frontend**: Gibt es eine Pricing-Page? Einen "Upgrade"-CTA? Eine Checkout-Seite?
2. **Backend**: Ist der Stripe-API-Key konfiguriert (als Env Var)? In welchem Env?
3. **Webhook**: Was muss nach erfolgreichem Checkout passieren?
   (Tier updaten, Email senden, Session erneuern)
4. **DB**: Welche Felder müssen gesetzt werden? Wer schreibt sie?
5. **Email**: Gibt es Bestätigungs-Emails? Wo ausgelöst?
6. **ADR**: Braucht AR-032 eine ADR-Ergänzung (wer schreibt welche DB-Felder)?

Deliverable: `docs/delivery/stripe-readiness.md` mit:
- Checkliste aller Gaps (Observed)
- Priorisierung (was muss zuerst, was kann parallel)
- Geschätzter Aufwand pro Gap
- Empfehlung: Wann ist Stripe-Launch realistisch?

---

## Non-Goals

- Stripe-Integration implementieren
- Pricing-Page bauen
- AR-032 (Webhook) implementieren

---

## Acceptance Criteria

1. `docs/delivery/stripe-readiness.md` existiert mit Observed-Befunden
2. Alle Gaps klassifiziert (Observed / Inferred / Missing)
3. Empfehlung für Reihenfolge der Gap-Schließung vorhanden
4. AR-032 Status in Feature Register aktualisiert basierend auf Findings

---

## Telemetry / Measurement

Nicht anwendbar — Research-Item.

---

## Risks / Open Questions

| Risiko | Bewertung |
|---|---|
| Lovable-verwaltetes Frontend erschwert Analyse | Medium — nur Read-Zugriff auf Codebase |
| Stripe-Konto existiert möglicherweise nicht | Unbekannt — zu klären |
| Viele Gaps könnten mehrere Releases benötigen | Akzeptiert — Ziel ist Klarheit, nicht sofortige Lösung |
