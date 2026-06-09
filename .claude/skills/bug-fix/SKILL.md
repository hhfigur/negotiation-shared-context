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
→ Bei GO: weiter mit Phase 1.5 (Laufzeit-Evidenz-Gate) — kein Fix-Prompt ohne Laufzeit-Evidenz.

## Phase 1.5 — Laufzeit-Evidenz-Gate (Pflicht vor Fix-Freigabe)

**Zweck:** Hypothesen aus Phase 2 müssen durch beobachtbares Laufzeitverhalten
bestätigt werden, bevor ein Fix-Prompt ausgegeben wird.
TypeScript-Compilation-Erfolg (`npx tsc --noEmit`) ist kein Laufzeitbeweis.

### Gate-Bedingung

Mindestens EINE der folgenden Evidenzquellen muss dokumentiert sein:

- [ ] **Tatsächlicher Laufzeit-Output dokumentiert** — curl-Aufruf,
      Test-Script oder manuelle Ausführung mit konkreten Inputs und konkretem Output
- [ ] **Supabase `get_logs` oder `execute_sql` Output ausgewertet** — falls
      DB-Pfad, RLS oder Supabase-Tabelle betroffen
- [ ] **Fehler-Pfad isoliert** — konkrete Zeile / konkreter Funktionsaufruf
      mit beobachtetem Fehlverhalten benannt — Beweis, nicht Inferenz
- [ ] **Abweichung dokumentiert** — erwarteter vs. tatsächlicher Output,
      Zeile für Zeile

### Klassifizierungsregel

Jede Aussage über Fehlerursachen muss mit einem dieser Labels versehen sein:

| Label | Bedeutung |
|-------|-----------|
| **Observed** | Direkt aus Laufzeit-Output |
| **Inferred** | Aus Code-Lesen erschlossen — kein Laufzeitbeweis |
| **Missing** | Information fehlt für Bestätigung |

**`Inferred` allein ist kein ausreichender Grund für einen Fix-Prompt.**

### Wenn kein Gate erfüllt → Logging-Instruktionen ausgeben

Status der Hypothese: **Inferred** (nicht Confirmed). Kein Fix-Prompt.

Stattdessen: temporäre Debug-Logs einfügen — markiert mit `// DEBUG-TEMP`.
Diese werden **nicht** committed.

**Debugging-Instruktions-Template:**

```
Datei/Funktion: [aus Phase 2 Hypothese — konkret benennen]

Logging-Ziele:
1. Welcher Branch / Pfad tatsächlich ausgeführt wird
2. Tatsächliche Werte der relevanten Variablen an der Verdachtsstelle
3. Ob ein Error geworfen und still geschluckt wird

Ausführen mit diesen Inputs: [aus Phase 2 Diagnose-Report befüllen]

Nach Logging → Output dokumentieren → Phase 1.5 Gate erneut prüfen.
```

### Wenn Gate erfüllt → Evidenz-Report erstellen

```
# Evidenz-Report — [BUG-ID]
**Evidenzquelle:** [welche der vier Quellen oben]
**Tatsächlicher Output:** [wörtlich — nicht paraphrasiert]
**Bestätigte Fehlerursache:** [Observed — Label zwingend]
```

STOP — Evidenz-Report zeigen. Warte auf GO für Fix-Prompt.

## Phase 3 — Fix (nur nach Evidenz-GO aus Phase 1.5)

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
