---
name: session-end
description: Führe diesen Skill am Ende jeder Claude-Code-Session aus. Sichert
  den Session-Stand in MEMORY.md, prüft ob Lessons-Einträge fehlen, erkennt
  lange Sessions und bietet Session-Dump an.
trigger: am Ende jeder Session — vor dem Schließen von Claude Code
---

# Skill: session-end

Führe alle Schritte in dieser Reihenfolge aus. Nicht überspringen.

## Schritt 1 — Was wurde heute gemacht?

Führe aus:
```bash
git -C . log --oneline --since="6 hours ago"
git -C ../negotiation-buddy log --oneline --since="6 hours ago" 2>/dev/null
git -C ../negotiationcoach-backend log --oneline --since="6 hours ago" 2>/dev/null
```

Notiere: Welche Commits wurden heute gemacht? In welchen Repos?

## Schritt 2 — Offene Punkte prüfen

Prüfe:
1. Gibt es uncommitted Changes in einem der drei Repos?
```bash
git -C . status --short
git -C ../negotiation-buddy status --short 2>/dev/null
git -C ../negotiationcoach-backend status --short 2>/dev/null
```

2. Gibt es Tasks in tasks/todo.md die heute angefangen aber nicht abgeschlossen wurden?

3. Gibt es Bug-Fixes die heute committed wurden aber noch keinen Lessons-Eintrag
   in tasks/lessons.md haben?
   Vergleiche: git log --oneline --since="6 hours ago" | grep "fix("
   mit: letzten Einträgen in tasks/lessons.md

## Schritt 3 — Lessons-Check (PFLICHT)

Falls ein Bug-Fix heute committed wurde und kein korrespondierender
Lessons-Eintrag in tasks/lessons.md existiert:

Weise explizit darauf hin:
> LESSONS FEHLT — Bug-Fix [COMMIT] hat noch keinen Lessons-Eintrag.
> Bitte jetzt nachtragen oder in der nächsten Session als erstes erledigen.

Falls kein Bug-Fix heute: weiter mit Schritt 4.

## Schritt 4 — Session-Dauer einschätzen

Prüfe den ältesten Commit von heute:
```bash
git -C . log --oneline --since="6 hours ago" --format="%ar" | tail -1
```

Falls Session länger als 90 Minuten (Inferred aus Commit-Zeitstempeln):
> LANGE SESSION erkannt. Empfehle Session-Dump vor /clear.
> Soll ich einen Session-Dump erstellen? (Ja/Nein)

Falls Ja: Session-Dump erstellen (Schritt 5).
Falls Nein oder Session unter 90 Min.: direkt zu Schritt 6.

## Schritt 5 — Session-Dump (optional, bei langer Session)

Erstelle: shared-context/docs/delivery/session-dump-[DATUM].md

Format:
# Session-Dump — [DATUM]

## Was committed / erreicht
[Liste der Commits aus Schritt 1]

## Uncommitted Changes
[Falls vorhanden — welche Dateien, warum nicht committed]

## Offene Entscheidungen
[Was noch nicht entschieden ist]

## Nächster Schritt (exakt)
[Konkreter erster Schritt für die nächste Session]

## Ausstehende Acceptance Criteria
[Falls ein Fix oder Feature noch nicht vollständig verifiziert ist]

git add docs/delivery/session-dump-[DATUM].md
git commit -m "docs(session): session-dump [DATUM]"

## Schritt 6 — MEMORY.md updaten (PFLICHT)

Aktualisiere shared-context/MEMORY.md:

Ersetze den Abschnitt "## Letzte Session" mit:
## Letzte Session
Datum: [HEUTE]
Gemacht: [1-3 Sätze — was committed wurde]
Problem: [was nicht funktioniert hat oder offen blieb — oder: keins]

Ersetze den Abschnitt "## Nächster Schritt" mit:
## Nächster Schritt
[Konkreter erster Schritt für die nächste Session — so spezifisch wie möglich]

Max. 20 Zeilen total in MEMORY.md.

git add MEMORY.md
git commit -m "docs(memory): update session state [DATUM]"

## Ausgabe

SESSION END — [DATUM]
─────────────────────────────
Commits heute:    [Anzahl in allen Repos]
Uncommitted:      [Ja/Nein — welche Repos]
Lessons-Check:    [OK oder: FEHLT für [BUG-ID]]
Session-Dump:     [Erstellt / Nicht nötig]
MEMORY.md:        [Aktualisiert]
─────────────────────────────
Nächste Session beginnt mit: [konkreter Schritt]

STOP — Session kann geschlossen werden.
