---
name: bug-fix
description: Strukturierter Bug-Fix-Workflow mit Diagnose-First. Verhindert
  Trial-and-Error. Erzwingt Lessons-Eintrag am Ende.
trigger: bei jedem Bug-Fix — vor jeder Code-Änderung ausführen
---

# Skill: bug-fix

Führe alle Phasen in dieser Reihenfolge aus.
STOP nach jeder Phase. Keine Phase überspringen.

## Eingabe (vom User)

- BUG-ID: [z.B. BUG-20260604-xyz]
- Symptom: [Was der User sieht]
- Betroffenes Repo: [negotiation-buddy | negotiationcoach-backend | beide]

## Phase 1 — Kontext laden

1. Lies: docs/delivery/bugs/[BUG-ID].md (falls bereits erstellt via /bug-report)
2. Lies: tasks/lessons.md — gibt es frühere Bugs in derselben Datei oder
   demselben Layer?
3. Suche nach früheren Fixes in diesem Bereich:
```bash
grep -r "[SYMPTOM-STICHWORT]" docs/delivery/bugs/ 2>/dev/null
```
Notiere: Wurde diese Stelle schon einmal gefixt? Was war die Ursache damals?

## Phase 2 — Diagnose (KEIN FIX IN DIESER PHASE)

Trace das Symptom Schicht für Schicht:
1. Wo tritt es auf? (Frontend-Komponente / API-Endpunkt / Layer / DB)
2. Wo liegt die Ursache? (muss nicht dieselbe Stelle sein)
3. Welche Dateien sind betroffen?
4. Kopplungsrisiken: was könnte ein Fix kaputt machen?

Klassifiziere jeden Befund:
- Observed — direkt im Code gesehen
- Inferred — logisch abgeleitet
- Missing — nicht einsehbar, Annahme nötig

Erstelle: docs/delivery/bugs/[BUG-ID]-diagnosis-report.md

Format:
# Diagnose-Report — [BUG-ID]
**Datum:** [DATUM]
**Symptom:** [Was der User sieht]
**Ursache:** [Observed/Inferred/Missing]
**Betroffene Dateien:** [Liste]
**Kopplungsrisiken:** [Was ein Fix kaputt machen könnte]
**Nicht einsehbar:** [Was fehlt für vollständige Diagnose]
**Empfohlener Fix-Scope:** [Minimal — nur was nötig ist]

STOP — zeige mir den Diagnose-Report. Warte auf GO vom User.

## Phase 3 — Fix (nur nach GO)

- Minimaler Fix — nur was die Diagnose als Ursache identifiziert hat
- Keine opportunistischen Verbesserungen
- Nach dem Fix: npx tsc --noEmit (falls TypeScript-Repo)
- Zeige git diff vor Commit

STOP — warte auf Bestätigung des Diffs vom User.

## Phase 4 — Abschluss (erzwungen — kein Überspringen)

1. Update docs/delivery/bugs/[BUG-ID].md:
   - Status auf **Status:** DONE setzen (Leerzeichen nach Doppelpunkt)
   - Abschluss-Block ausfüllen

2. Eintrag in tasks/lessons.md (PFLICHT):
## [DATUM] — [BUG-ID]
**Task:** [Was gefixt wurde]
**Problem:** [Was war falsch]
**Ursache:** [Warum nicht sofort erkannt]
**Regel:** [Was beim nächsten Mal anders machen]
**Folge-Risiko:** [Welche anderen Stellen könnten dasselbe Problem haben]

3. Commit:
```bash
git add docs/delivery/bugs/[BUG-ID].md
git add docs/delivery/bugs/[BUG-ID]-diagnosis-report.md
git add tasks/lessons.md
git add [geänderte Source-Dateien]
git commit -m "fix([LAYER]): [kurze Beschreibung] — closes [BUG-ID]"
```

4. Zwei-Repo-Regel prüfen (PFLICHT):
   Wurde shared-context ebenfalls aktualisiert?
   Ein Fix ist erst DONE wenn Commits in BEIDEN relevanten Repos
   existieren UND shared-context aktualisiert ist.

STOP — Abschluss bestätigen.
