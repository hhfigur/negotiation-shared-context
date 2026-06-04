---
name: release-check
description: Prüft Release-Bereitschaft. Zeigt offene Bugs, In-Delivery-Items,
  Gate-Status und ob ein Release freigegeben werden kann.
trigger: vor jedem Release oder wenn Release-Status unklar ist
---

# Skill: release-check

## Schritt 1 — Aktuellen Release laden

Lies: product/releases/current.md
Notiere: Release-ID, geplanter Scope, Exit Criteria, Status.

## Schritt 2 — Feature-Register prüfen

Lies: product/feature-register.md

Erstelle Tabelle aller Items im aktuellen Release-Scope:

| NC-ID | Titel | Status | Blocker |
|---|---|---|---|
| ... | ... | In Delivery / Blocked / Released | ... |

## Schritt 3 — Brief-Status prüfen

Für jedes Item aus Schritt 2 das Status Released hat:
Prüfe ob product/briefs/[NC-ID].md ebenfalls Released zeigt.

Falls Brief-Status und feature-register.md abweichen:
- Markiere als INCONSISTENT
- Kein Release-Gate-Pass bis Inkonsistenz behoben

## Schritt 4 — Offene Bugs prüfen

```bash
grep -rl "Status:.*OPEN" docs/delivery/bugs/ 2>/dev/null
```

Für jeden offenen Bug:
- Priorität (P0/P1/P2)
- Betroffener Layer und Tier
- Blockiert er den aktuellen Release?

P0/P1 offene Bugs = Release-Blocker ohne Ausnahme.
P2 offene Bugs = User-Entscheidung erforderlich.

## Schritt 5 — Gate-Prüfung

| Gate | Status | Notiz |
|---|---|---|
| Alle P0/P1 Bugs geschlossen | ✅/❌ | ... |
| Alle In-Delivery-Items verified | ✅/❌ | ... |
| Brief-Status konsistent mit feature-register.md | ✅/❌ | ... |
| shared-context Docs aktuell | ✅/❌ | ... |
| TypeCheck clean (beide Repos) | ✅/❌ | ... |

## Schritt 6 — Empfehlung ausgeben

RELEASE READY
— alle Gates grün
— Release kann durchgeführt werden

RELEASE BLOCKED
— offene Gates mit Begründung
— was muss zuerst behoben werden

RELEASE PARTIAL
— was kann released werden
— was muss zurückgehalten werden und warum

STOP — warte auf Entscheidung vom User.
