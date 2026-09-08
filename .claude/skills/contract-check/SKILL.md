---
name: contract-check
description: Prüft API-Vertrag zwischen TARGET REPO und der kanonischen API-Contract-Quelle
  (NegotiationCoach-backend/docs/api-catalog.md, seit Owner-Entscheidung C1, 2026-09-04).
  Erzwingt Type-Drift-Check und Violation-Scan vor jedem Merge oder Ship.
trigger: vor Merge oder Ship wenn Änderungen Request/Response-Shapes, Auth-Muster,
  Typen, Endpunkte oder Tier-Gates betreffen
---

# Skill: contract-check

> **Korrektur (2026-09-04, C1):** die kanonische API-Contract-Quelle ist seit Owner-Entscheidung
> `NegotiationCoach-backend/docs/api-catalog.md` — `docs/contracts/frontend-backend.md` in diesem
> Repo ist nur noch ein Verweis (Transport-Übersicht, Type-Drift-Register, Known-Violations bleiben
> dort; die vollständigen Endpunkt-Contracts wurden dorthin verschoben). Schritt 1 und Schritt 5
> unten sind entsprechend angepasst.

## Eingabe (vom User)

- TARGET REPO: [negotiation-buddy | negotiationcoach-backend]
- Geänderte Bereiche: [Endpunkte / Typen / Auth / Tier-Gates / Schema]
- Commit oder Diff-Referenz: [optional — z.B. HEAD, branch-name]

## Schritt 1 — Contracts laden

Lies vollständig:
- `../NegotiationCoach-backend/docs/api-catalog.md` (kanonische Endpunkt-Contracts, inkl. Backend
  API Routes und Supabase Edge Function API Routes — seit C1, 2026-09-04)
- `docs/contracts/frontend-backend.md` (nur noch Transport-Übersicht, Type-Drift-Register Section 4,
  Known Contract Violations Section 6 — keine eigenen Endpunkt-Contracts mehr)

Notiere:
- Aktuelle Type-Drift-Register-Einträge (frontend-backend.md Section 4)
- Aktuelle Known Contract Violations (frontend-backend.md Section 6)
- Betroffene Endpunkte basierend auf geänderten Bereichen (aus api-catalog.md)

## Schritt 2 — Drift-Prüfung: Typen

Für jeden in Section 4 gelisteten Typ der von der Änderung betroffen ist:

```bash
# Im TARGET REPO — TypeScript-Typen prüfen
grep -r "NegotiationInputs\|ExtractedInputs\|AnalysisResult\|PlanResponse\|ChatMessage" \
  src/lib/types.ts src/types/index.ts 2>/dev/null
```

Vergleiche gegen `../NegotiationCoach-backend/docs/api-catalog.md`:

| Typ | Frontend-Definition | Backend-Definition | Drift? |
|---|---|---|---|
| NegotiationInputs | ... | ... | OK / DRIFT |
| ExtractedInputs | ... | ... | OK / DRIFT |
| [weitere betroffene Typen] | ... | ... | ... |

## Schritt 3 — Drift-Prüfung: Endpunkte und Auth

Für jeden betroffenen Endpunkt:

| Endpunkt | Contract (api-catalog.md) | Aktuell im Repo | Abweichung? |
|---|---|---|---|
| POST /api/analyze | Request: NegotiationInputs, Auth: Bearer JWT | ... | OK / DRIFT |
| POST /api/enrich | Tier-Gate: requireTier('kmu') | ... | OK / DRIFT |
| [weitere] | ... | ... | ... |

Auth-Muster prüfen:
- Backend API: `Authorization: Bearer <JWT>` — kein Anon-Key
- Edge Functions: gemäß ADR-004 (user JWT für generate-plan, anon+fallback für chat)

## Schritt 4 — Bekannte Violations prüfen

Scan auf die bekannten Contract Violations (CON-01 bis CON-06):

| Violation | Status (frontend-backend.md Section 6) | Durch diese Änderung betroffen? |
|---|---|---|
| CON-01 | RESOLVED RFB-009 | Ja / Nein |
| CON-02 | PARTIAL RESOLVED RFB-007 | Ja / Nein |
| CON-03 | Offen | Ja / Nein |
| CON-04 | Offen | Ja / Nein |
| CON-05 | Offen | Ja / Nein |
| CON-06 | Offen | Ja / Nein |

Falls eine Änderung eine bestehende Violation verschlimmert oder neue einführt:
HOLD — die kanonische Quelle (`NegotiationCoach-backend/docs/api-catalog.md`) muss zuerst
aktualisiert werden (Type-Drift/Violations-Kontext bleibt in `docs/contracts/frontend-backend.md`).

STOP — zeige mir Drift-Tabelle und Violations-Scan.
Warte auf GO / HOLD vom User.

## Schritt 5 — Kanonische Quelle aktualisieren

Nur nach GO vom User:

Falls Endpunkte oder Auth-Muster geändert wurden — **im Backend-Repo**, nicht hier:
- `../NegotiationCoach-backend/docs/api-catalog.md` — betroffene Endpunkt-Sections aktualisieren
  (Commit erfolgt im Backend-Repo)

Falls Typen, Type-Drift oder Violations betroffen sind — **in diesem Repo**:
- Type-Drift-Register (Section 4) und Known Contract Violations (Section 6) in
  `docs/contracts/frontend-backend.md` aktualisieren — dies ist weiterhin der richtige Ort für
  diesen Cross-Repo-Audit-Trail, nicht für die Endpunkt-Contracts selbst.

```bash
# Nur falls Section 4/6 in diesem Repo geändert wurden:
git add docs/contracts/frontend-backend.md
git commit -m "docs(contracts): update type-drift/violations register — [kurze Beschreibung]"
```

STOP — Contract-Quelle(n) aktualisiert. Zeige Commit-Hash(es) je Repo.

---
**OUTPUT-SIGNAL:**
> CONTRACT CHECK — [DATUM]
> TARGET REPO: [repo]
> Typ-Drift: [Anzahl Abweichungen oder: keine]
> Violations betroffen: [Anzahl oder: keine]
> Contract-Doc aktualisiert: Ja / Nein
> Empfehlung: GO / HOLD
> Warte auf Bestätigung vom User bevor Merge/Ship.
