---
name: bug-report
description: Strukturierte Bug-Erfassung für NegotiationCoach AI. Erstellt docs/delivery/bugs/BUG-[ID].md als einzigen Input für Template 1-DEV (Plan) und Template 2-DEV (Implement).
---

# Skill: /bug-report

## Zweck
Strukturierte Bug-Erfassung. Erzeugt eine Bug-Datei unter `docs/delivery/bugs/BUG-[ID].md`.
Diese Datei ist der einzige Input für Template 1-DEV (Plan) und Template 2-DEV (Implement).
Der Skill selbst führt keinen Code aus und erzeugt keine Prompts.

## Verhalten bei Aufruf

### Schritt 1 — Begrüßung
Gib aus:
"BUG REPORT — NegotiationCoach AI
Ich stelle dir 6 Fragen und erstelle danach docs/delivery/bugs/BUG-[ID].md.
Diese Datei verwendest du als Input für /bug-plan (Template 1-DEV).
Frage 1 von 6:"

### Schritt 2 — Interaktive Abfrage (eine Frage nach der anderen, auf Antwort warten)

Frage 1: "Beschreibe den Bug in eigenen Worten. Was passiert, was sollte passieren?"
Frage 2: "Wo tritt der Bug auf? (Screen-Name, API-Endpunkt, Layer, Funktion)"
Frage 3: "Ist der Bug reproduzierbar? Wenn ja: welche Schritte führen dazu?"
Frage 4: "Welche Tiers sind betroffen? (free / privat / kmu / profi / alle / unbekannt)"
Frage 5: "Gibt es Fehlermeldungen, Logs oder auffällige Outputs? Einfügen oder beschreiben."
Frage 6: "Hast du eine Vermutung zur Ursache? (Datei, Funktion, Layer — oder 'unbekannt')"

### Schritt 3 — Klassifizierung (intern ableiten, nicht ausgeben)

- TARGET REPO: negotiationcoach-backend | negotiation-buddy | shared-context | cross-repo
- Layer: 0 | 1 | 2 | 3 | API | Frontend | unbekannt
- Bug-Typ: Logic-Bug | Boundary-Violation | Contract-Gap | Auth-Bug | Data-Bug | UI-Bug | unbekannt
- Risiko: P0 (Datenverlust/Auth) | P1 (falsche Ergebnisse) | P2 (UX) | P3 (kosmetisch)
- Bug-ID: BUG-[YYYYMMDD]-[kurzname-kebab-case] — Datum = heute, Kurzname aus Symptom ableiten

### Schritt 4 — Klassifizierung bestätigen

Gib aus:
"KLASSIFIZIERUNG:
- Bug-ID: [Wert]
- TARGET REPO: [Wert]
- Layer: [Wert]
- Bug-Typ: [Wert]
- Risiko: [Wert]
- ADR-Constraints: [relevante ADRs nennen oder 'keine erkennbar']

Ist die Klassifizierung korrekt? (ja / korrigiere: [Korrektur])"

Warte auf Bestätigung oder Korrektur. Passe bei Korrektur die Werte an.

### Schritt 5 — Bug-Datei erstellen

Erstelle `docs/delivery/bugs/[Bug-ID].md` mit folgendem Inhalt:

```
# [Bug-ID]

**Erstellt:** [Datum]
**Status:** OPEN
**Risiko:** [P0 | P1 | P2 | P3]
**TARGET REPO:** [Wert]
**Layer:** [Wert]
**Bug-Typ:** [Wert]
**Betroffene Tiers:** [Wert]
**ADR-Constraints:** [Wert]

## Symptom
[Antwort Frage 1]

## Ort
[Antwort Frage 2]

## Reproduktion
[Antwort Frage 3]

## Logs / Fehlermeldungen
[Antwort Frage 5]

## Verdacht
[Antwort Frage 6]

## Plan
_Wird durch Template 1-DEV befüllt._

## Implement
_Wird durch Template 2-DEV befüllt._

## Abschluss
_Wird durch /close-task befüllt._
```

### Schritt 6 — Abschluss

Führe aus:
```bash
git add docs/delivery/bugs/[Bug-ID].md
git commit -m "docs(bugs): [Bug-ID] erstellt"
```

Gib aus:
"Bug-Datei erstellt: docs/delivery/bugs/[Bug-ID].md
Commit: [Hash]

Nächster Schritt:
Öffne Template 1-DEV in docs/delivery/claude-code-prompt-templates-dev.md.
Setze BUG_FILE: docs/delivery/bugs/[Bug-ID].md
und führe den Plan-Prompt in Claude Code aus."

STOP. Kein weiterer Code. Kein Plan. Kein Implement.
