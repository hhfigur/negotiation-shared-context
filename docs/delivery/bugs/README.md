# docs/delivery/bugs/

Bug-Dateien für NegotiationCoach AI.

## Zweck
Jede Bug-Datei ist das einzige Übergabedokument zwischen:
- `/bug-report` Skill (Erfassung)
- Template 1-DEV (Plan)
- Template 2-DEV (Implement)
- `/close-task` Skill (Abschluss)

## Dateiname
`BUG-[YYYYMMDD]-[kurzname-kebab-case].md`

## Status-Werte
- `OPEN` — erfasst, noch kein Plan
- `PLANNED` — Template 1-DEV ausgeführt, Plan vorhanden
- `IN PROGRESS` — Template 2-DEV ausgeführt
- `DONE` — /close-task bestätigt

## Regeln
- Bug-Dateien werden nie manuell bearbeitet — nur durch Skills und Templates
- Eine Bug-Datei pro Bug — kein Zusammenfassen
- Abgeschlossene Bugs bleiben als Referenz erhalten, Status wird auf DONE gesetzt
