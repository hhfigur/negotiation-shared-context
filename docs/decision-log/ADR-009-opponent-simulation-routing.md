# ADR-009 — Opponent-Simulation Routing: Backend statt Edge Function

**Status:** DECIDED
**Datum:** 2026-06-30
**Entscheider:** Maik
**Klassifizierung:** Architecture Decision — Chat-Pfad-Abgrenzung
**Bezug:** Amendiert nicht ADR-004, sondern grenzt explizit gegen sie ab

## Kontext

NC-L3-OPPONENT (KI-Gegner-Rollenspiel, Brief: `product/briefs/NC-L3-OPPONENT.md`)
führt einen neuen, eigenständigen Übungsmodus ein: Nutzer verhandelt gegen eine
simulierte Gegenseite, deren Verhalten an eine serverseitig berechnete,
versteckte ZOPA-Range gekoppelt ist (Layer-1-Funktionen: `zopaCalculator.ts`,
`nashBargaining.ts`).

ADR-004 legt fest, dass die Supabase Edge Function `/functions/v1/chat` der
**kanonische Chat-Pfad für alle Tiers** ist — und dass das Express Backend
(Railway/Render) **nicht** für "direct frontend chat streaming" genutzt werden
darf, sondern für internen Gebrauch und strukturierte Extraktions-Flows reserviert
bleibt.

Ohne explizite Abgrenzung besteht das Risiko, dass eine spätere Prüfung
NC-L3-OPPONENT fälschlich als ADR-004-Verstoß einstuft — oder dass jemand
versucht, es nachträglich in die Edge Function zu verschieben und damit eine
dritte, inkompatible Kopie der Layer-1-Logik erzeugt (vgl. CRIT-01: Layer-1
bereits doppelt in Backend und Edge Function vorhanden, mit inkompatiblen
Schemas).

## Entscheidung

**NC-L3-OPPONENT läuft im Express Backend, nicht in der Edge Function.**

Begründung der Abgrenzung von ADR-004:
- ADR-004 regelt den **Coaching-Chat-Stream** (laufender Dialog zur
  Verhandlungsvorbereitung). NC-L3-OPPONENT ist kein Ersatz oder Zweig dieses
  Streams — es ist ein eigenständiges, separat aufgerufenes Tool (eigene Seite,
  eigene Endpoints, eigener State), analog zu `WhatIfSimulator.tsx`, das bereits
  heute `/api/analyze` und `/api/enrich` im Backend aufruft statt die Edge
  Function zu nutzen.
- Die versteckte Gegen-ZOPA-Berechnung **muss** dieselben Layer-1-Funktionen
  nutzen wie die reale Analyse, sonst widerspricht das Endergebnis der
  Auswertung der echten ZOPA/Nash-Berechnung. Diese Funktionen leben nur im
  Backend. Eine Duplikation in der Edge Function würde CRIT-01 vertiefen statt
  es zu vermeiden.
- ADR-004 erlaubt das Backend explizit für "future structured extraction flows"
  und internen Gebrauch — NC-L3-OPPONENT fällt darunter.

## Optionen bewertet

| Option | Entscheidung | Begründung |
|--------|-------------|------------|
| Express Backend (`/api/opponent-simulation/*`) | ✅ GEWÄHLT | Direkter Zugriff auf Layer-1-Funktionen, kein Duplikat, nutzt vorhandenes `modelRouter`-Scaffolding (`opponent_simulation`-Use-Case bereits auf Opus geroutet) |
| Supabase Edge Function | ❌ | Hätte eigene Kopie von ZOPA/Nash nötig (vgl. CRIT-01), widerspricht ADR-004s Zweck (EF = Chat-Stream, nicht Analyse-Tools) |

## Konsequenzen

**Positiv:**
- Keine neue Layer-1-Duplikation
- Bestehendes `modelRouter`-Scaffolding wird aktiviert statt totem Code zu bleiben
- Tier-Gate über vorhandenes `requireTier('profi')`-Middleware-Pattern, konsistent mit `/enrich`

**Negativ:**
- Zwei unterschiedliche Backend-Pfade für "Chat-artige" Interaktionen (Coaching-Chat in EF, Rollenspiel in Express) — muss in Doku klar unterschieden bleiben, sonst Verwechslungsgefahr bei künftigen Audits

## Abhängigkeiten

- `product/briefs/NC-L3-OPPONENT.md`
- `docs/decision-log/ADR-004-chat-path-routing.md` (Abgrenzung, keine Änderung)
- `docs/contracts/frontend-backend.md` — neue Endpoints ergänzen vor Implementierung
