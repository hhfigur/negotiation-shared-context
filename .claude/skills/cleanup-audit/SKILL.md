---
name: cleanup-audit
description: Read-only Audit im TARGET REPO. Sucht Dead Code, verwaiste Dateien
  und doppelte Logik. Schreibt Findings als Kandidaten nach shared-context/.
trigger: bei technischen Schulden, Dead-Code-Verdacht oder vor größeren Refactors —
  macht keine Änderungen, nur Analyse
---

# Skill: cleanup-audit

## Voraussetzung (PFLICHT)

Dieser Skill macht KEINE Änderungen im TARGET REPO.
Alle Schreiboperationen gehen ausschließlich nach shared-context/.

## Eingabe (vom User)

- TARGET REPO: [negotiation-buddy | negotiationcoach-backend]
- Fokusbereich: [optional — z.B. src/hooks/, src/api/, oder: gesamtes Repo]
- Auslöser: [warum jetzt? z.B. "vor NC-xxx Refactor", "Dead-Code-Verdacht in X"]

## Schritt 1 — Kontext laden

Lies:
- docs/audits/refactor-backlog.md — bereits bekannte offene Items
- tasks/lessons.md — frühere Findings die diesen Bereich betreffen

```bash
# Letzte Änderungen im Fokusbereich
git -C ../[TARGET-REPO] log --oneline -10 -- [FOKUSBEREICH]
```

Notiere: Welche Items sind bereits im Backlog? Was wurde zuletzt angefasst?

## Schritt 2 — Dead Code suchen

```bash
# Ungenutzte Exports (TypeScript)
cd ../[TARGET-REPO] && npx ts-unused-exports tsconfig.json 2>/dev/null | head -30

# Dateien die nirgends importiert werden
grep -rL "import" src/ --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "index\|types\|\.d\.ts"

# TODO-Kommentare ohne Issue-Referenz
grep -rn "TODO\|FIXME\|HACK\|@deprecated" src/ 2>/dev/null
```

Klassifiziere jeden Fund:
- **Observed** — direkt im Code gesehen
- **Inferred** — logisch abgeleitet (z.B. keine bekannten Aufrufer)

## Schritt 3 — Doppelte Logik suchen

```bash
# Gleiche Funktionsnamen in verschiedenen Dateien
grep -rn "export.*function\|export const" src/ 2>/dev/null | \
  awk -F: '{print $3}' | sort | uniq -d | head -20

# Gleiche Typ-Definitionen
grep -rn "type.*=\|interface " src/ 2>/dev/null | grep -v "\.d\.ts" | \
  awk '{print $2}' | sort | uniq -d | head -20
```

Bekannte Drift-Kandidaten aus docs/contracts/frontend-backend.md (Section 4):
- `ExtractedInputs` — in beiden Repos parallel definiert
- `ChatMessage` — in beiden Repos parallel definiert
- `PlanResponse` — in beiden Repos parallel definiert

## Schritt 4 — Verwaiste Dateien suchen

```bash
# Dateien die zuletzt vor >90 Tagen angefasst wurden
git -C ../[TARGET-REPO] log --diff-filter=M --name-only \
  --since="90 days ago" --pretty=format: | sort -u > /tmp/recently_changed.txt

find ../[TARGET-REPO]/src -name "*.ts" -o -name "*.tsx" | \
  xargs ls -la | sort -k6 | head -20
```

STOP — zeige mir alle Findings aus Schritten 2–4.
Warte auf GO vom User bevor Schritt 5 (Report schreiben).

## Schritt 5 — Report schreiben (nur nach GO)

Erstelle: docs/audits/cleanup-[TARGET-REPO]-[DATUM].md

Format:
```
# Cleanup Audit — [TARGET-REPO] — [DATUM]
**Fokusbereich:** [Bereich]
**Auslöser:** [Warum jetzt]

## Dead Code Kandidaten
| Datei / Symbol | Befund | Klassifikation | Backlog-Kandidat? |
|---|---|---|---|
| ... | ... | Observed/Inferred | Ja / Nein |

## Doppelte Logik
| Symbol | Ort 1 | Ort 2 | Empfehlung |
|---|---|---|---|
| ... | ... | ... | Zusammenführen / Behalten |

## Verwaiste Dateien
| Datei | Letzter Commit | Noch gebraucht? |
|---|---|---|
| ... | ... | Ja / Nein / Unklar |

## Empfohlene Backlog-Kandidaten
| Kandidat | Priorität | Begründung |
|---|---|---|
| ... | P1/P2/P3 | ... |
```

STOP — zeige mir den Report. Warte auf Bestätigung vom User.

## Schritt 6 — Backlog aktualisieren (nur nach Bestätigung)

Für jeden bestätigten Backlog-Kandidaten:
- Prüfe ob bereits ein offenes Item in docs/audits/refactor-backlog.md existiert
- Falls nein: neues Item vorschlagen (kein automatisches Eintragen)
- User entscheidet welche Kandidaten als RFB-xxx eingetragen werden

```bash
git add docs/audits/cleanup-[TARGET-REPO]-[DATUM].md
git commit -m "docs(audit): cleanup-audit [TARGET-REPO] — [DATUM] — [Anzahl] Kandidaten"
```

STOP — Audit abgeschlossen. Zeige Commit-Hash.

---
**OUTPUT-SIGNAL:**
> CLEANUP AUDIT — [TARGET-REPO] — [DATUM]
> Dead Code Kandidaten: [Anzahl]
> Doppelte Logik: [Anzahl]
> Verwaiste Dateien: [Anzahl]
> Backlog-Kandidaten vorgeschlagen: [Anzahl]
> Report: docs/audits/cleanup-[TARGET-REPO]-[DATUM].md
> Warte auf Bestätigung vom User bevor Backlog-Update.
