---
name: impact-check
description: Prüft Auswirkungen einer geplanten Änderung auf alle drei Repos.
  Erzwingt Contract-, ADR- und Supabase-Prüfung vor Cross-Repo-Änderungen.
trigger: vor jeder Änderung die shared state, API-Vertrag, DB-Schema oder
  mehr als ein Repo betrifft — nie überspringen
---

# Skill: impact-check

## Eingabe (vom User)

- Geplante Änderung: [Was soll geändert werden?]
- Primäres TARGET REPO: [negotiation-buddy | negotiationcoach-backend | shared-context]
- Layer: [0 | 1 | 2 | 3 | UI]

## Schritt 1 — Kontext laden

Lies:
- CLAUDE.md (Repo-Mapping + Architekturregeln)
- docs/contracts/frontend-backend.md — aktuelle API-Verträge und Type-Drift-Register
- Relevante ADRs in docs/decision-log/ die diesen Layer betreffen

Notiere:
- Welche Architekturregeln sind für diese Änderung relevant?
- Gibt es eine ADR die diesen Bereich regelt?

## Schritt 2 — Impact-Tabelle erstellen

Bewerte für jede Dimension:

| Dimension | Betroffen? | Betroffene Dateien / Endpunkte | Risiko |
|---|---|---|---|
| negotiation-buddy (Frontend) | Ja / Nein / Unklar | ... | Niedrig / Mittel / Hoch |
| negotiationcoach-backend (Backend) | Ja / Nein / Unklar | ... | Niedrig / Mittel / Hoch |
| shared-context (Docs) | Ja / Nein / Unklar | ... | Niedrig / Mittel / Hoch |
| API-Vertrag (frontend-backend.md) | Ja / Nein / Unklar | ... | Niedrig / Mittel / Hoch |
| Supabase Schema / RLS / Migrations | Ja / Nein / Unklar | ... | Niedrig / Mittel / Hoch |
| Tier-Gates | Ja / Nein / Unklar | ... | Niedrig / Mittel / Hoch |
| Layer-Abhängigkeit (0→1→2→3) | Ja / Nein / Unklar | ... | Niedrig / Mittel / Hoch |

## Schritt 3 — ADR-Konfliktprüfung

Prüfe jeden relevanten ADR:

| ADR | Titel | Konflikt mit geplanter Änderung? |
|---|---|---|
| ADR-001 | System Boundaries | Ja / Nein |
| ADR-002 | Data Ownership | Ja / Nein |
| ADR-003 | AI Provider Strategy | Ja / Nein |
| [weitere relevante ADRs] | ... | ... |

Falls Konflikt: BACK TO DOCS — ADR-Entscheidung erforderlich bevor Implementierung.

STOP — zeige mir Impact-Tabelle und ADR-Konfliktprüfung.
Warte auf GO / HOLD vom User.

## Schritt 4 — Empfehlung ausgeben

**GO** wenn:
- Kein ADR-Konflikt
- Alle High-Risiko-Dimensionen haben einen bekannten Fix-Plan
- Layer-Abhängigkeiten eingehalten

**HOLD** wenn:
- ADR-Konflikt ohne Resolution
- Supabase-Migration nötig ohne Migrations-File
- Tier-Gate-Änderung ohne serverseitige Enforcement

**BACK TO DOCS** wenn:
- Neue ADR-Entscheidung erforderlich

---
**OUTPUT-SIGNAL:**
> IMPACT CHECK — [DATUM]
> Änderung: [kurze Beschreibung]
> Betroffene Repos: [Liste]
> ADR-Konflikte: [Anzahl oder: keine]
> Empfehlung: GO / HOLD / BACK TO DOCS
> Warte auf Bestätigung vom User bevor Implementierung beginnt.
