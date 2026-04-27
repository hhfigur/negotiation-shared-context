---
name: bug-report
description: Interaktive Bug-Erfassung für NegotiationCoach AI. Führt durch 6 Fragen und generiert einen fertigen Plan-Prompt (CC-RP-01 + CC-HEADER-v1) für Claude Code.
---

# Skill: bug-report

Wenn dieser Skill aufgerufen wird, führe exakt die folgenden Schritte durch.

---

## Schritt 1 — Begrüßung

Gib aus:

```
BUG REPORT — NegotiationCoach AI
Ich stelle dir 6 Fragen. Danach erstelle ich den fertigen Plan-Prompt.
Frage 1 von 6:
```

---

## Schritt 2 — Interaktive Abfrage

Stelle die Fragen **eine nach der anderen**. Warte nach jeder Frage auf die Antwort, bevor du die nächste stellst.

**Frage 1:** "Beschreibe den Bug in eigenen Worten. Was passiert, was sollte passieren?"

**Frage 2:** "Wo tritt der Bug auf? (z.B. Screen-Name, API-Endpunkt, Layer, Funktion)"

**Frage 3:** "Ist der Bug reproduzierbar? Wenn ja: welche Schritte führen dazu?"

**Frage 4:** "Welche Tiers sind betroffen? (free / privat / kmu / profi / alle / unbekannt)"

**Frage 5:** "Gibt es Fehlermeldungen, Logs oder auffällige Outputs? Wenn ja: einfügen oder beschreiben."

**Frage 6:** "Hast du eine Vermutung, wo die Ursache liegt? (Datei, Funktion, Layer — oder 'unbekannt')"

---

## Schritt 3 — Klassifizierung (intern — nicht ausgeben)

Leite aus den Antworten ab:

- **TARGET REPO:** `negotiationcoach-backend` | `negotiation-buddy` | `shared-context` | `cross-repo`
  - Backend-Signale: API-Endpunkt, Layer 1/2/3, Railway, Algorithmus, DB, Auth-Middleware
  - Frontend-Signale: Screen-Name, UI-Komponente, Edge Function, Supabase direkt
  - Cross-repo: wenn Bug beide Repos betrifft
- **Betroffener Layer:** `0` | `1` | `2` | `3` | `API` | `Frontend` | `unbekannt`
- **Bug-Typ:** `Logic-Bug` | `Boundary-Violation` | `Contract-Gap` | `Auth-Bug` | `Data-Bug` | `UI-Bug` | `unbekannt`
- **Risiko:**
  - `P0` — Datenverlust, Auth-Bypass, Silent-Data-Corruption
  - `P1` — Falsche Berechnungsergebnisse, Layer-Output-Fehler
  - `P2` — UX-Probleme, nicht-kritische Fehler
  - `P3` — Kosmetisch, Typos, Minor-Layout
- **ADR-Constraints:** Prüfe ob ADR-001 bis ADR-007 relevant sind:
  - ADR-001: System-Boundaries (Browser vs Railway vs Supabase)
  - ADR-002: Data-Ownership (wer schreibt welche Tabelle)
  - ADR-003: AI-Provider-Strategy (Railway → Anthropic, EF → Gemini)
  - ADR-004: Edge Function Tier Enforcement
  - ADR-006: Tier-Mapping
  - ADR-007: Dual Layer-1 (wenn Layer 1 betroffen)

---

## Schritt 4 — Klassifizierung ausgeben und bestätigen

Gib aus:

```
KLASSIFIZIERUNG:
- TARGET REPO: [Wert]
- Layer: [Wert]
- Bug-Typ: [Wert]
- Risiko: [Wert]
- ADR-Constraints: [relevante ADRs nennen, oder 'keine erkennbar']

Ist die Klassifizierung korrekt? (ja / korrigiere: [Korrektur])
```

Warte auf Bestätigung oder Korrektur. Bei Korrektur: übernehme die korrigierten Werte und fahre fort.

---

## Schritt 5 — Fertigen Plan-Prompt ausgeben

Nach Bestätigung gib exakt den folgenden Plan-Prompt aus — befüllt mit den gesammelten Informationen.

Hinweise zur Befüllung:
- `Bug-ID`: Format `BUG-[YYYYMMDD]-[max-3-wörter-kebab-case]` — Kurzname aus Symptombeschreibung ableiten
- `TARGET PATH`: Aus Antwort Frage 2 ableiten; wo kein konkreter Pfad erkennbar: `[konkreter Pfad — aus Prompt-Inhalt ableiten]`
- `Active rules` und `Git commits`: je nach TARGET REPO anpassen (Varianten siehe unten)
- `[relevante ADRs]`: durch konkrete ADR-Dateinamen aus Klassifizierung ersetzen, oder Zeile weglassen wenn keine

**Active rules — Varianten je nach TARGET REPO:**
- `negotiationcoach-backend`: `shared-context/CLAUDE.md + ../negotiationcoach-backend/CLAUDE.md + ../negotiationcoach-backend/AGENTS.md`
- `negotiation-buddy`: `shared-context/CLAUDE.md + ../negotiation-buddy/CLAUDE.md + ../negotiation-buddy/AGENTS.md`
- `shared-context`: `shared-context/CLAUDE.md + shared-context/AGENTS.md`
- `cross-repo`: `shared-context/CLAUDE.md + ../negotiationcoach-backend/CLAUDE.md + ../negotiation-buddy/CLAUDE.md`

**Git commits — Varianten je nach TARGET REPO:**
- `negotiationcoach-backend`: `cd ../negotiationcoach-backend && git add [files] && git commit -m "[type(scope): msg]"`
- `negotiation-buddy`: `cd ../negotiation-buddy && git add [files] && git commit -m "[type(scope): msg]"`
- `shared-context`: `git add [files] && git commit -m "[type(scope): msg]"`

---

**Ausgabe-Template:**

```
BUG REPORT. PLAN ONLY. DO NOT CHANGE CODE YET.

SESSION CONTEXT:
- Working directory: shared-context/
- Available repos: negotiation-buddy (../negotiation-buddy), negotiationcoach-backend (../negotiationcoach-backend)
- TARGET REPO: [aus Klassifizierung]
- TARGET PATH: [aus Antwort Frage 2 ableiten]
- Active rules: [Variante je nach TARGET REPO]
- Git commits: [Variante je nach TARGET REPO]

Bug-ID: BUG-[YYYYMMDD]-[kurzname-kebab-case]
Risiko: [P0 | P1 | P2 | P3]
Layer: [Wert]
Betroffene Tiers: [Antwort Frage 4]

Symptom:
[Antwort Frage 1]

Ort:
[Antwort Frage 2]

Reproduktion:
[Antwort Frage 3]

Logs / Fehlermeldungen:
[Antwort Frage 5]

Verdacht:
[Antwort Frage 6]

Aufgabe:
Lies die relevanten Dateien im TARGET REPO.
Lese zusätzlich:
- shared-context/docs/audits/refactor-backlog.md
- shared-context/docs/contracts/frontend-backend.md
- [relevante ADRs]

Erstelle einen Planungsvorschlag:
1. Wahrscheinliche Fehlerursache (mit Dateiname und Funktion)
2. Kleinste sichere Fix-Scope
3. Exakt betroffene Dateien
4. Seiteneffekte
5. Tests die danach laufen müssen
6. Docs/Contracts die zu updaten sind
7. Rollback-Strategie
8. Exakter Git-Commit-Befehl
```

---

Schreibe danach:

```
Plan-Prompt bereit. In Claude Code eingeben oder hier reviewen?
```
