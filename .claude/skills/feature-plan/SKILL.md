---
name: feature-plan
description: Planungsworkflow für neue Features. Erzwingt Impact-Check,
  ADR-Prüfung und Template 1-DEV vor jeder Implementierung.
trigger: vor jeder Feature-Implementierung — nie ohne diesen Skill direkt
  mit Template 1-DEV beginnen
---

# Skill: feature-plan

## Eingabe (vom User)

- NC-ID: [z.B. NC-042]
- Titel: [Feature-Titel]
- Betroffenes Repo: [negotiation-buddy | negotiationcoach-backend | beide]
- Layer: [0 | 1 | 2 | 3 | UI]
- Tier-Auswirkung: [free | privat | kmu | profi | alle]

## Schritt 1 — Kontext laden

Lies:
- product/feature-register.md (Eintrag NC-ID)
- product/briefs/[NC-ID].md (falls vorhanden)
- tasks/lessons.md — relevante frühere Erkenntnisse für diesen Layer

## Schritt 2 — Layer-Abhängigkeit prüfen

Layer-Regel: 0 → 1 → 2 → 3 — kein Überspringen.

Ist der vorgelagerte Layer stabil und released?
- Falls nein: HOLD — Blocker dokumentieren.

STOP — HOLD ausgeben und warte auf User-Entscheidung.

- Falls ja: weiter mit Schritt 3.

## Schritt 3 — ADR-Check

Lies alle ADRs in docs/decision-log/ die für diesen Layer
oder diese Tier-Auswirkung relevant sind.

Gibt es Konflikte zwischen dem Feature-Scope und einem bestehenden ADR?
- Falls ja: BACK TO DOCS — ADR-Entscheidung erforderlich.

STOP — BACK TO DOCS ausgeben und warte auf User-Entscheidung.

- Falls nein: weiter mit Schritt 4.

## Schritt 4 — Impact-Check

Beantworte für jede Dimension:

| Dimension | Betroffene Dateien/Endpunkte | Risiko |
|---|---|---|
| Frontend (negotiation-buddy) | ... | ... |
| Backend (negotiationcoach-backend) | ... | ... |
| API-Vertrag (frontend-backend.md) | ... | ... |
| Supabase Schema/RLS | ... | ... |
| Tier-Gates | ... | ... |
| shared-context Docs | ... | ... |

## Schritt 5 — Template 1-DEV ausgeben

Lies: docs/delivery/claude-code-prompt-templates-dev.md

Fülle Template 1-DEV mit den Informationen aus Schritten 1–4.
Gib das vollständige ausgefüllte Template aus —
bereit zum Einfügen in Claude Code.

STOP — warte auf GO / HOLD / SPLIT / BACK TO DOCS vom User.
