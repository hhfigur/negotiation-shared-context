# Brief: NC-SEC-02 — VG-05-A: JWT-Auth-Hardening in Edge Functions

**Status:** Qualified
**Release:** TBD (Wave 2 — Tier 1)
**Typ:** Enabler
**Priorität:** P1 — High; Tier-Value-Promise aktuell ungesichert
**Erstellt:** 2026-04-29

---

## Lagebeurteilung

VG-05-A (dokumentiert 2026-04-09): Tier-Enforcement in Edge Functions ist
dekorativ. Es gibt keinen JWT-Check, kein Model-Switching basierend auf Tier,
kein echtes Gate für kmu/profi-Features.

Der Chat-EF (`supabase/functions/chat/`) verwendet `user_metadata.tier` aus
dem JWT als Prompt-Metadata — aber dieser Wert wird nicht verifiziert und
steuert weder Modell-Auswahl noch Feature-Gating.

ADR-004 (2026-04-09) entschied: EF ist kanonischer Chat-Pfad für alle Tiers;
Tier-Enforcement via JWT innerhalb der EF. Diese Entscheidung ist noch nicht
implementiert.

---

## Ziel / Outcome

Echter Tier-Gate in `supabase/functions/chat/`: JWT wird verifiziert,
Tier wird ausgelesen, Modell-Auswahl und ggf. Feature-Limits werden
tier-basiert gesteuert. kmu/profi-Nutzer bekommen das bessere Modell,
free/privat nicht.

---

## Problem

- Jeder Nutzer unabhängig von Tier bekommt dasselbe Modell
- Kein wirtschaftlicher Schutz für bezahlte Tier-Features
- ADR-004 ist entschieden aber nicht umgesetzt

---

## Affected Repos

- `negotiation-buddy` (Supabase Edge Function: `supabase/functions/chat/index.ts`)
- `shared-context` (ADR-004 ggf. ergänzen mit Implementierungs-Nachweis)

---

## Scope

1. `supabase/functions/chat/index.ts`: JWT aus Authorization-Header extrahieren
   und `app_metadata.tier` / `user_metadata.tier` auslesen
2. Tier-basierte Modell-Auswahl implementieren:
   - free/privat: `google/gemini-2.0-flash-lite` (oder aktuell günstigstes)
   - kmu: `google/gemini-2.5-flash`
   - profi: `google/gemini-2.5-pro`
3. Unauthenticated Requests: Default-Tier = free (kein 401 — Guest-Mode bleibt)

**ADR-Prüfung:** ADR-003 schreibt vor: EF → Gemini via Lovable AI Gateway.
Kein Anthropic in EF. Modell-Auswahl bleibt im Gemini-Spektrum. ✅

---

## Non-Goals

- Tier-Enforcement im Railway-Backend (bereits via requireTier Middleware)
- Stripe-Integration oder Abo-Verwaltung
- Änderungen an anderen EFs (generate-plan, analyze-progress etc.)
- Hard-Block für unauthenticated Requests (Guest-Mode bleibt offen)

---

## Acceptance Criteria

1. Authenticated kmu-User erhält anderes Modell als free-User (Observed in EF-Logs)
2. JWT-Parsing schlägt nicht fehl wenn kein Token vorhanden (Guest-Mode stabil)
3. TypeCheck negotiation-buddy: 0 Fehler
4. VG-05-A in wave1-completion-gate.md als RESOLVED gestempelt
5. ADR-004 Implementierungs-Nachweis ergänzt

---

## Telemetry / Measurement

Kein direktes Metriken-Target. Qualitative Verifikation: EF-Log zeigt
unterschiedliche Modell-IDs für unterschiedliche Tiers.

**Gap:** Kein automatisiertes Monitoring bis NC-TELEMETRY umgesetzt.

---

## Risks / Open Questions

| Risiko | Bewertung |
|---|---|
| Lovable-verwaltete EF: Deployment-Prozess unklar | Medium — EF-Änderungen gehen über Lovable-Deployment-Pipeline |
| JWT-Struktur weicht von erwartetem Schema ab | Low — bereits in VG-05 verifiziert (`app_metadata.tier`) |
| ADR erforderlich? | Nein — ADR-004 deckt diese Entscheidung bereits ab |
