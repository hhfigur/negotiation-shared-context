---
name: contract-check
description: Prüft API-Vertrag zwischen TARGET REPO und shared-context/docs/contracts/.
  Erzwingt Type-Drift-Check und Violation-Scan vor jedem Merge oder Ship.
trigger: vor Merge oder Ship wenn Änderungen Request/Response-Shapes, Auth-Muster,
  Typen, Endpunkte oder Tier-Gates betreffen
---

# Skill: contract-check

## Eingabe (vom User)

- TARGET REPO: [negotiation-buddy | negotiationcoach-backend]
- Geänderte Bereiche: [Endpunkte / Typen / Auth / Tier-Gates / Schema]
- Commit oder Diff-Referenz: [optional — z.B. HEAD, branch-name]

## Schritt 1 — Contracts laden

Lies vollständig:
- docs/contracts/frontend-backend.md

Notiere:
- Aktuelle Type-Drift-Register-Einträge (Section 4)
- Aktuelle Known Contract Violations (Section 6)
- Betroffene Endpunkte basierend auf geänderten Bereichen

## Schritt 2 — Drift-Prüfung: Typen

Für jeden in Section 4 gelisteten Typ der von der Änderung betroffen ist:

```bash
# Im TARGET REPO — TypeScript-Typen prüfen
grep -r "NegotiationInputs\|ExtractedInputs\|AnalysisResult\|PlanResponse\|ChatMessage" \
  src/lib/types.ts src/types/index.ts 2>/dev/null
```

Vergleiche gegen docs/contracts/frontend-backend.md:

| Typ | Frontend-Definition | Backend-Definition | Drift? |
|---|---|---|---|
| NegotiationInputs | ... | ... | OK / DRIFT |
| ExtractedInputs | ... | ... | OK / DRIFT |
| [weitere betroffene Typen] | ... | ... | ... |

## Schritt 3 — Drift-Prüfung: Endpunkte und Auth

Für jeden betroffenen Endpunkt:

| Endpunkt | Contract (frontend-backend.md) | Aktuell im Repo | Abweichung? |
|---|---|---|---|
| POST /api/analyze | Request: NegotiationInputs, Auth: Bearer JWT | ... | OK / DRIFT |
| POST /api/enrich | Tier-Gate: requireTier('kmu') | ... | OK / DRIFT |
| [weitere] | ... | ... | ... |

Auth-Muster prüfen:
- Backend API: `Authorization: Bearer <JWT>` — kein Anon-Key
- Edge Functions: gemäß ADR-004 (user JWT für generate-plan, anon+fallback für chat)

## Schritt 4 — Bekannte Violations prüfen

Scan auf die bekannten Contract Violations (CON-01 bis CON-06):

| Violation | Status in frontend-backend.md | Durch diese Änderung betroffen? |
|---|---|---|
| CON-01 | RESOLVED RFB-009 | Ja / Nein |
| CON-02 | PARTIAL RESOLVED RFB-007 | Ja / Nein |
| CON-03 | Offen | Ja / Nein |
| CON-04 | Offen | Ja / Nein |
| CON-05 | Offen | Ja / Nein |
| CON-06 | Offen | Ja / Nein |

Falls eine Änderung eine bestehende Violation verschlimmert oder neue einführt:
HOLD — docs/contracts/frontend-backend.md muss zuerst aktualisiert werden.

STOP — zeige mir Drift-Tabelle und Violations-Scan.
Warte auf GO / HOLD vom User.

## Schritt 5 — docs/contracts/frontend-backend.md aktualisieren

Nur nach GO vom User:

Falls Endpunkte, Typen oder Auth-Muster geändert wurden:
- Type-Drift-Register aktualisieren
- Betroffene Endpunkt-Sections aktualisieren
- Neue oder resolved Violations in Section 6 eintragen

```bash
git add docs/contracts/frontend-backend.md
git commit -m "docs(contracts): update frontend-backend contract — [kurze Beschreibung]"
```

STOP — Contract aktualisiert. Zeige Commit-Hash.

---
**OUTPUT-SIGNAL:**
> CONTRACT CHECK — [DATUM]
> TARGET REPO: [repo]
> Typ-Drift: [Anzahl Abweichungen oder: keine]
> Violations betroffen: [Anzahl oder: keine]
> Contract-Doc aktualisiert: Ja / Nein
> Empfehlung: GO / HOLD
> Warte auf Bestätigung vom User bevor Merge/Ship.
