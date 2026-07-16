---
name: feature-implement
description: Implementierungsworkflow nach GO-Entscheidung aus /feature-plan.
  Gibt Template 2b-DEV aus, erzwingt TypeCheck und close-task-dev am Ende.
trigger: nur nach expliziter GO-Entscheidung aus /feature-plan — nie ohne
  vorherigen /feature-plan ausführen
---

# Skill: feature-implement

## Voraussetzung (PFLICHT)

Dieser Skill darf nur nach einer expliziten GO-Entscheidung aus
/feature-plan ausgeführt werden.

Falls kein GO vorliegt:
STOP — zuerst /feature-plan ausführen.

## Eingabe (vom User)

- NC-ID: [z.B. NC-042]
- Genehmigter Plan: [Verweis auf Template-1-DEV-Output oder Zusammenfassung]
- Ziel-Repo: [negotiation-buddy | negotiationcoach-backend]

## Schritt 0 — verify-loop-Hook (Pflicht)

Vor jeder Weitergabe von Template 2b-DEV an den Implementer-Subagenten gilt
zusätzlich (siehe `.claude/skills/verify-loop/SKILL.md`):

- `/verify-loop` MUSS Teil des Subagent-Auftrags sein (siehe Template 2b-DEV
  Acceptance-Abschnitt in `docs/delivery/claude-code-prompt-templates-dev.md`).
- Der Implementer MUSS `scripts/verify.sh` (falls im Ziel-Repo vorhanden)
  selbst ausführen und bei Fehlern iterieren, BEVOR er
  DONE/DONE_WITH_CONCERNS meldet.
- **TypeScript-Kompilierung allein ist KEIN DONE-Kriterium.**
- Spec-Reviewer prüft dabei auch, ob ein tatsächlicher `verify.sh`-Lauf
  stattgefunden hat — nicht nur ob er behauptet wurde.
- Gate-Status: solange `docs/decision-log/ADR-011-verify-loop-gate.md`
  PROPOSED ist (Soft-Launch), blockiert ein rotes verify.sh nicht automatisch
  die DONE-Meldung — es MUSS aber transparent im Report ausgewiesen werden.
  Sobald ADR-011 DECIDED ist, wird ein rotes verify.sh automatisch zum
  Hard-Blocker, ohne dass dieser Skill erneut geändert werden muss.

Falls `scripts/verify.sh` im Ziel-Repo noch nicht existiert: dies explizit
im Report vermerken — kein stiller Skip.

## Schritt 1 — Re-Triage (Code kann sich seit Planung geändert haben)

Da zwischen /feature-plan und /feature-implement Zeit vergangen
sein kann und sich der Code geändert haben könnte:

1. Prüfe: Hat sich seit dem genehmigten Plan etwas an den betroffenen
   Dateien geändert?
```bash
git log --oneline -5 -- [betroffene Dateien aus dem Plan]
```

2. Falls Änderungen seit der Planung vorhanden:
   Wiederhole die Konsequenz-Triage aus /feature-plan Schritt 4b
   für den aktuellen Code-Stand.

3. Falls neue Treffer entstanden sind die im ursprünglichen Plan
   nicht berücksichtigt wurden:
   STOP — zeige die neuen Konsequenzen.
   Frage: "Der Code hat sich seit der Planung geändert. Neue
   Konsequenz: [X]. Tragbar, oder Plan anpassen?"
   Warte auf Bestätigung bevor Template 2b-DEV ausgegeben wird.

4. Falls keine Änderungen oder keine neuen Treffer:
   weiter zu Schritt 2, keine Nachfrage.

## Schritt 2 — Template 2b-DEV ausgeben

Lies: docs/delivery/claude-code-prompt-templates-dev.md

Fülle Template 2b-DEV mit NC-ID und genehmigtem Plan.
Gib das vollständige ausgefüllte Template aus —
bereit zum Einfügen in Claude Code im Ziel-Repo.

STOP — warte auf Bestätigung vom User dass Template übergeben wurde.

## Schritt 3 — Verifikation nach Implementierung

Nach Rückmeldung des Implementers prüfe:

1. verify.sh-Nachweis (siehe Schritt 0): Liegt ein PASS/FAIL-Summary pro
   verify.sh-Schritt im Implementer-Report? Falls `scripts/verify.sh` im
   Ziel-Repo existiert und kein Nachweis vorliegt: STOP — Nachweis nachfordern,
   nicht als DONE akzeptieren.

2. TypeCheck:
```bash
npx tsc --noEmit
```
Muss clean sein — keine neuen Fehler. (Ersetzt nicht den verify.sh-Nachweis
aus Punkt 1 — TypeScript-Kompilierung allein ist kein DONE-Kriterium.)

3. Diff-Review:
```bash
git diff --stat HEAD
```
Wurden nur die im Plan genannten Dateien geändert?
Falls unerwartete Dateien geändert: STOP — User informieren.

STOP — warte auf Bestätigung des Diffs vom User.

## Schritt 4 — close-task-dev ausführen

Führe /close-task-dev aus für NC-ID.

Zwei-Repo-Regel (PFLICHT):
Ein Feature ist erst DONE wenn:
- Commits im Ziel-Repo existieren
- shared-context aktualisiert ist (Docs, feature-register.md, Brief)
- Beide Punkte durch Commit-Hashes belegt sind

STOP — Abschluss bestätigen.
