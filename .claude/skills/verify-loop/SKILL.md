---
name: verify-loop
description: Definiert den inneren Verifikationsloop (Innerer Loop = Maschine,
  Äußerer Loop = Mensch). Kein DONE ohne grünes Orakel — TypeScript-Kompilierung
  allein reicht nicht.
trigger: bei jeder Code-Delivery in /feature-implement und /bug-fix — vor jeder
  DONE/DONE_WITH_CONCERNS-Meldung
---

# Skill: verify-loop

## Gate-Status (PFLICHT-Hinweis)

**SOFT-LAUNCH** — siehe `docs/decision-log/ADR-011-verify-loop-gate.md`
(Status: PROPOSED, nicht DECIDED).

Solange ADR-011 nicht DECIDED ist:
- Der Loop selbst (Ausführung von `verify.sh`, Iteration bis Exit 0) ist
  Pflicht-Praxis — er wird immer ausgeführt.
- Ein rotes Ergebnis blockiert NICHT automatisch die DONE-Meldung — es MUSS
  aber transparent im Report als `verify.sh: FAIL — [Schritt]` ausgewiesen
  werden, nicht verschwiegen oder umgangen werden.
- Sobald ADR-011 auf DECIDED gesetzt wird, wird ein rotes `verify.sh`
  automatisch zum Hard-Blocker für DONE — ohne dass dieser Skill dafür
  erneut geändert werden muss.

## Regel

Definiere das ausführbare Orakel ZUERST — bevor Code geschrieben wird, muss
klar sein, welches Kommando (`verify.sh`) den Erfolg mechanisch beweist.

**TypeScript-Kompilierung allein (`tsc --noEmit` grün) ist KEIN DONE.** Sie
ist ein Teilschritt im `verify.sh`-Contract, nicht der Contract selbst.

## Ablauf (Innerer Loop = Maschine)

1. Vor Implementierungsbeginn prüfen: Existiert `scripts/verify.sh` im
   Ziel-Repo? Falls nein — das Definieren dieses Scripts ist selbst Teil der
   Delivery (siehe Contract, Abschnitt "Verweis" unten).
2. Nach Implementierung: `./scripts/verify.sh` lokal ausführen.
3. Bei Fehler: Fehler lesen, am Code iterieren (nicht am Orakel — Tests
   werden nicht passend gemacht, damit sie grün werden), erneut ausführen.
4. Wiederholen bis Exit 0 — ODER bis ein Blocker außerhalb des eigenen
   Scopes erkannt wird (Server nicht startbar, fehlende Env-Variable) → dann
   BLOCKED melden, nicht DONE.
5. Erst nach grünem (oder, im Soft-Launch, transparent als FAIL
   ausgewiesenem) `verify.sh` geht der Report an den Spec-Reviewer.

## Abgrenzung: Was NICHT als Orakel zählt

- `npx tsc --noEmit` allein — Typkorrektheit ist kein Verhaltensbeweis.
- "Sieht plausibel aus" / Code-Lektüre ohne Ausführung.
- Ein Test, der während der Implementierung an das aktuelle (fehlerhafte)
  Verhalten angepasst wurde, statt das Verhalten am Test zu korrigieren.

## Verweis

- Contract: `docs/contracts/verify-harness.md` — Pflichtschritte,
  Exit-Code-Semantik, PASS/FAIL-Summary-Format.
- Eingebunden in: `.claude/skills/feature-implement/SKILL.md` Schritt 0,
  `.claude/skills/bug-fix/SKILL.md` Phase 1.5 (Persistenz-Ergänzung).
- Architekturentscheidung: `docs/decision-log/ADR-011-verify-loop-gate.md`.
