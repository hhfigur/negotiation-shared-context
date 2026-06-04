---
name: adr-create
description: Erstellt einen neuen ADR in docs/decision-log/. Erzwingt
  Optionen-Analyse und explizite Entscheidung vor Implementierung.
trigger: wenn eine Architekturentscheidung getroffen werden muss — vor jeder
  Implementierung die ADR-pflichtig ist
---

# Skill: adr-create

## Eingabe (vom User)

- ADR-Nummer: [z.B. ADR-009]
- Entscheidungsfrage: [Was muss entschieden werden?]
- Kontext: [Warum jetzt? Was hat die Frage ausgelöst?]

## Schritt 1 — Bestehende ADRs prüfen

```bash
ls docs/decision-log/
```

Lies jeden ADR der die Entscheidungsfrage tangiert.

Gibt es einen bestehenden ADR der diese Frage bereits beantwortet?
- Falls ja: Zeige den relevanten ADR.
  Ist eine Ergänzung ausreichend statt einem neuen ADR?

STOP — warte auf Bestätigung vom User ob neuer ADR oder Ergänzung.

## Schritt 2 — Optionen erarbeiten

Erarbeite mindestens 2, maximal 4 Optionen.

Für jede Option:

| Kriterium | Option A | Option B | Option C |
|---|---|---|---|
| Aufwand | ... | ... | ... |
| Risiko | ... | ... | ... |
| ADR-Konformität | ... | ... | ... |
| Reversibilität | ... | ... | ... |
| Empfehlung | ... | ... | ... |

STOP — zeige mir die Optionen-Tabelle. Warte auf Entscheidung vom User.

## Schritt 3 — ADR-Entwurf erstellen

Erstelle: docs/decision-log/ADR-[NR]-[short-title].md

Format:

# ADR-[NR] — [Titel]
**Status:** PROPOSED
**Datum:** [DATUM]
**Entscheider:** Maik Figur

## Kontext
[Warum diese Entscheidung nötig ist]

## Entscheidungsfrage
[Exakte Frage]

## Optionen

[Tabelle aus Schritt 2]

## Entscheidung
[Noch offen — wird nach User-Bestätigung eingetragen]

## Konsequenzen
[Was sich durch diese Entscheidung ändert]

## Betroffene Items
[NC-xxx, RFB-xxx die von dieser Entscheidung abhängen]

STOP — zeige mir den ADR-Entwurf. Warte auf Entscheidung vom User.

## Schritt 4 — Entscheidung eintragen (nur nach User-Bestätigung)

- Status von PROPOSED auf DECIDED setzen
- Entscheidung eintragen
- Commit:

```bash
git add docs/decision-log/ADR-[NR]-[short-title].md
git commit -m "docs(adr): ADR-[NR] — [Titel] — DECIDED"
```

STOP — ADR abgeschlossen. Zeige Commit-Hash.
