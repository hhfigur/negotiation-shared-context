# Skill: pm-sync-status

## Purpose
Update item status after delivery or QA completion.
Usage: `/pm-sync-status <ITEM-ID>`

## Steps
1. Read the brief in `product/briefs/<ITEM-ID>.md`
2. Verify acceptance criteria — ask for evidence (test output, log, manual check)
3. Update status in `product/feature-register.md`

---
### Pflichtschritt — Brief-Status aktualisieren

Nach Status-Update in product/feature-register.md:

1. Prüfe ob product/briefs/[NC-ID].md existiert:
```bash
ls product/briefs/[NC-ID].md 2>/dev/null
```

2. Falls Datei existiert:
   - Öffne product/briefs/[NC-ID].md
   - Setze Status-Feld auf: Released
   - Speichere die Datei

3. Falls Datei nicht existiert:
   - Notiere als Warning: "Brief für [NC-ID] nicht gefunden"
   - Kein Fehler — weiter mit nächstem Schritt

Dieser Schritt ist NICHT optional.
Brief-Status muss mit feature-register.md übereinstimmen.

---

4. Update `product/releases/current.md` if all in-scope items are done
5. If released: update `product/audit/refactor-backlog.md` if applicable
6. Output: status change summary

## Rules
- "Code complete" is not "Released"
- "Released" is not "Verified"
- require explicit evidence before status change to Verified

---
**OUTPUT-SIGNAL:**
> STATUS SYNC COMPLETE — [NC-ID] — [DATUM]
> feature-register.md: aktualisiert
> product/briefs/[NC-ID].md: Status auf Released gesetzt ← PFLICHT
> Warte auf Bestätigung vom User bevor Commit.
