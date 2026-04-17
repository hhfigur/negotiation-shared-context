# ADR-007 — Dual Layer-1-Architektur: Edge Function Engine

**Status:** DRAFT — Entscheidung ausstehend
**Erstellt:** 2026-04-17
**Entscheider:** Maik
**Klassifizierung:** Architecture Decision — Wave-2-Start-Gate
**Spawned by:** RFB-006 Deferral 2026-04-16, VG-06

---

## Kontext

### Problem

Zwei unabhängige Layer-1-Implementierungen existieren nebeneinander:

| Implementierung | Pfad | Schema | Status |
|---|---|---|---|
| **Railway (Node.js)** | `negotiationcoach-backend/src/layer1/` | `own_target / own_minimum` | ✅ Kanonisch (ADR-001) |
| **Edge Function (Deno)** | `negotiationcoach-backend/supabase/functions/_shared/engine/` | `user_goal / user_walkaway` | ⚠️ Inkompatibles Schema, batnaDetector undeployable |

Diese Situation wurde in Wave 1 als `CRIT-01` klassifiziert und aufgrund fehlender Architekturentscheidung zurückgestellt (RFB-006, RFB-026 → DEFERRED 2026-04-16).

### Auswirkungen des aktuellen Zustands

- **CRITICAL DRIFT**: Inkompatible Schemas zwischen EF und Railway — gleiche Business-Logik, verschiedene Feldnamen
- **batnaDetector undeployable**: `supabase/functions/_shared/engine/batnaDetector.ts` hat gebrochenen Import-Pfad, `NegotiationTier` ohne `'free'`, Schema-Divergenz
- **Dual-Maintenance-Risiko**: Jede Layer-1-Änderung muss potenziell in zwei Implementierungen erfolgen
- **Test-Ziel unklar**: Tests in `tests/layer1/` können nicht klar einem kanonischen Schema zugeordnet werden

### Welche Edge Functions nutzen `_shared/engine/`?

- **`/functions/v1/chat`** — nutzt EF für Streaming-Chat; ob Layer-1-Engine aktiv gerufen wird ist zu verifizieren
- **`/functions/v1/batnaDetector`** — nutzt `_shared/engine/batnaDetector.ts` direkt; aktuell undeployable
- **`/functions/v1/generate-plan`** — wurde in VG-06 als ACTIVE identifiziert, aber VG-06-A (RFB-033) hat JWT-Auth hinzugefügt; Layer-1-Abhängigkeit prüfen

> **Observed:** `generate-plan` hat laut VG-06-Analyse keine direkte Layer-1-Abhängigkeit. RFB-006-Scope ist primär `/chat` EF `_shared/engine/`.

---

## Optionen

### Option A — Retire: Edge Function engine löschen

**Beschreibung:** `supabase/functions/_shared/engine/` wird vollständig gelöscht. Edge Functions, die Layer-1-Logik benötigen, delegieren an Railway-Endpunkte via HTTP-Call.

**Vorteile:**
- Sauberste Lösung — eine kanonische Layer-1-Implementierung
- Schema-Drift-Problem vollständig eliminiert
- Wartungsaufwand halbiert
- CRIT-01 vollständig geschlossen

**Nachteile:**
- EF-zu-Railway-HTTP-Call fügt Latenz hinzu (Supabase EF → Railway)
- Erfordert Umbau der betroffenen Edge Functions
- Streaming-Chat-Pfad muss verifiziert werden (kein Layer-1-Call aus EF?)

**Aufwand:** Mittel — EF-Umbau + Verifikation

---

### Option B — Migrate: EF engine auf Railway-Schema ausrichten

**Beschreibung:** `_shared/engine/` bleibt, wird aber auf das Railway-Schema (`own_target / own_minimum`) migriert. Beide Implementierungen bleiben parallel, teilen aber dasselbe Schema.

**Vorteile:**
- EF-Autonomie bleibt erhalten (kein HTTP-Call zu Railway)
- Schema-Drift-Problem gelöst

**Nachteile:**
- Dual-Maintenance bleibt bestehen
- Jede Layer-1-Algorithmus-Änderung muss in zwei Codebasen erfolgen
- Langfristig fragil

**Aufwand:** Mittel — Schema-Migration + Tests

---

### Option C — Adapter: Schema-Adapter an EF-Boundary

**Beschreibung:** Ein dünner Adapter übersetzt zwischen EF-Schema (`user_goal`) und Railway-Schema (`own_target`) an der Grenze. Kein Umbau der EF-Implementierung.

**Vorteile:**
- Geringster kurzfristiger Aufwand
- Bestehende EF-Implementierung bleibt unverändert

**Nachteile:**
- Versteckt das Problem, löst es nicht
- Zwei Schemas bleiben aktiv — erhöht Fehlerrisiko bei späteren Änderungen
- Adapter muss gewartet werden

**Aufwand:** Gering — aber technische Schulden

---

## Empfehlung (Proposed)

**Option A (Retire)** wird empfohlen, wenn verifiziert ist, dass `/chat` EF keinen aktiven Layer-1-Call in `_shared/engine/` ausführt (nur dann ist der Aufwand gering).

**Option B (Migrate)** wenn EF-Autonomie aus Performance-Gründen zwingend ist.

**Option C** wird nicht empfohlen — versteckt strukturelle Schulden.

> Diese Empfehlung ist vorläufig. Die Entscheidung muss nach Verifikation der aktiven EF-Nutzung getroffen werden.

---

## Entscheidung

**[ ] Noch nicht getroffen**

Optionen:
- [ ] **Option A — Retire**
- [ ] **Option B — Migrate**
- [ ] **Option C — Adapter**

Begründung:
> _(wird nach Entscheidung ausgefüllt)_

Datum:
> _(wird nach Entscheidung ausgefüllt)_

---

## Konsequenzen (nach Entscheidung auszufüllen)

### Bei Option A (Retire)

- `supabase/functions/_shared/engine/` wird gelöscht
- Betroffene EF delegieren an Railway via `fetch(process.env.RAILWAY_URL + '/api/...')`
- `tests/layer1/` testen ausschließlich gegen `src/layer1/` (Node.js)
- RFB-006 und RFB-026 werden als DONE geschlossen
- `bounded-contexts.md` BC-02 CRIT-01 → resolved
- `source-of-truth-matrix.md` Entity 5 → resolved
- `frontend-backend.md` Type Drift Register CRITICAL DRIFT → resolved

### Bei Option B (Migrate)

- `_shared/engine/` Schema wird auf `own_target / own_minimum` migriert
- `batnaDetector.ts` Import-Pfad repariert, `NegotiationTier` erweitert
- Dual-Maintenance-Risiko bleibt — ADR-Ergänzung: Synchronisationspflicht dokumentieren
- `bounded-contexts.md` BC-02 CRIT-01 → partial resolution

### Bei Option C (Adapter)

- Adapter-Datei `_shared/schema-adapter.ts` erstellt
- Bestehende EF-Implementierung unverändert
- Technische Schuld explizit dokumentiert
- `bounded-contexts.md` BC-02 CRIT-01 bleibt offen mit Adapter-Vermerk

---

## Voraussetzungen vor Entscheidung

- [ ] Verifizieren: Ruft `/functions/v1/chat` aktiv Layer-1-Logik aus `_shared/engine/` auf?
- [ ] Verifizieren: Hat `/functions/v1/generate-plan` nach RFB-033 noch Layer-1-Abhängigkeit?
- [ ] Verifizieren: Welche anderen EF nutzen `_shared/engine/`?

**Verifikations-Prompt für Claude Code in `negotiationcoach-backend`:**
```
PLAN ONLY. DO NOT CHANGE CODE YET.

Ziel: Verifizieren, welche Edge Functions aktiv _shared/engine/ aufrufen.

Analysiere:
1. supabase/functions/chat/index.ts — ruft es _shared/engine/ auf?
2. supabase/functions/generate-plan/index.ts — ruft es _shared/engine/ auf?
3. supabase/functions/ — alle anderen EF die _shared/engine/ importieren?

Klassifiziere jede Aussage als Observed / Inferred / Missing.
Kein Code-Fix. Nur Analyse.
```

---

## Abhängigkeiten

**Blockiert:**
- RFB-006 (Layer-1-Unification) — wartet auf diese Entscheidung
- RFB-026 (batnaDetector EF Reparatur) — wartet auf RFB-006

**Unblocks nach Entscheidung:**
- Wave-2-Step-4 und Step-5 können beginnen

---

## Referenzen

- ADR-001 — System Boundaries (Railway = kanonischer Execution-Path)
- ADR-003 — AI Provider Split (Anthropic/Railway + Gemini/Edge Function)
- RFB-006 — refactor-backlog.md (DEFERRED 2026-04-16)
- RFB-026 — refactor-backlog.md (DEFERRED 2026-04-16)
- VG-06 — source-of-truth-matrix.md (RESOLVED 2026-04-11)
- `bounded-contexts.md` BC-02 CRIT-01
- `frontend-backend.md` Type Drift Register — CRITICAL DRIFT
