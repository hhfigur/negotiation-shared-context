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

## Schritt 1 — Template 2b-DEV ausgeben

Lies: docs/delivery/claude-code-prompt-templates-dev.md

Fülle Template 2b-DEV mit NC-ID und genehmigtem Plan.
Gib das vollständige ausgefüllte Template aus —
bereit zum Einfügen in Claude Code im Ziel-Repo.

STOP — warte auf Bestätigung vom User dass Template übergeben wurde.

## Schritt 2 — Verifikation nach Implementierung

Nach Rückmeldung des Implementers prüfe:

1. TypeCheck:
```bash
npx tsc --noEmit
```
Muss clean sein — keine neuen Fehler.

2. Diff-Review:
```bash
git diff --stat HEAD
```
Wurden nur die im Plan genannten Dateien geändert?
Falls unerwartete Dateien geändert: STOP — User informieren.

STOP — warte auf Bestätigung des Diffs vom User.

## Schritt 3 — close-task-dev ausführen

Führe /close-task-dev aus für NC-ID.

Zwei-Repo-Regel (PFLICHT):
Ein Feature ist erst DONE wenn:
- Commits im Ziel-Repo existieren
- shared-context aktualisiert ist (Docs, feature-register.md, Brief)
- Beide Punkte durch Commit-Hashes belegt sind

STOP — Abschluss bestätigen.
