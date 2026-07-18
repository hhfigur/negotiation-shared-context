# ADR-012 — AI Provider Strategy: Anthropic-only

**Status:** DECIDED — 2026-07-18
**Datum:** 2026-07-18
**Entscheider:** Maik Figur
**Klassifizierung:** Architecture Decision — AI Provider
**Supersedes:** ADR-003 (AI Provider Strategy — Two-Provider-Split)

---

## Kontext

ADR-003 (Accepted 2026-03-31) akzeptierte einen bewussten Zwei-Provider-Split:
Supabase Edge Functions (`generate-plan`, `chat`) über Lovable AI Gateway →
Gemini 2.5 Flash, Railway-Backend über Anthropic Claude. ADR-003 wurde nie
aktualisiert.

Am **2026-05-15** (Commit `fc3ad5b` in `negotiation-buddy`, Message:
*"Replace Google AI Studio (quota issues) with Anthropic claude-haiku."*)
wurde die Edge-Function-Seite von Google AI Studio (bereits vorher von
Lovable weg migriert, siehe `2fe2b0f`) vollständig auf Anthropic umgestellt —
Grund: Kontingent-/Quota-Probleme bei Google AI Studio, nicht ein
Lovable-Problem. Dieser Umstieg wurde nie in ADR-003 nachgezogen, wodurch
ADR-003 seit über zwei Monaten einen Zustand beschrieb, der nicht mehr
existierte.

Der Drift wurde am 2026-07-16 entdeckt (ausgelöst durch die Loop-Coding-
Integration, PROMPT 1 — `shared-context/CLAUDE.md` behauptet korrekt "alle
EFs nutzen claude-haiku-4-5-20251001", während ein Code-Grep in
`negotiationcoach-backend/supabase/functions/chat/index.ts` einen
Gemini-Call zeigte) und vollständig verifiziert in
`docs/audits/provider-drift-diagnosis.md` (Commit `1e9074e`, Nachtrag
`d3229d1`).

## Entscheidungsfrage

Welcher LLM-Provider gilt als kanonisch für alle LLM-Calls im System —
Railway/Render-Backend UND Supabase Edge Functions?

## Entscheidung

**Anthropic Claude (`claude-haiku-4-5-20251001`) für alle LLM-Calls —
sowohl Express-Backend (Render.com) als auch alle Supabase Edge Functions.
Kein Zwei-Provider-Split mehr.**

Dies formalisiert einen bereits seit 2026-05-15 gelebten, produktiven
Zustand — keine neue Migration, sondern eine überfällige Dokumentations-
Korrektur.

## Belege (Observed)

- `docs/audits/provider-drift-diagnosis.md` (Commit `1e9074e`, Nachtrag
  `d3229d1`): Volltext-Abgleich der aktiv deployten `chat`-Edge-Function auf
  dem aktiven Supabase-Projekt (`gpllrgkuozytyrmpfwbb`, Version 7) via
  Supabase-MCP (`get_edge_function`) bestätigt `api.anthropic.com`,
  `claude-haiku-4-5-20251001`, `ANTHROPIC_API_KEY` — deckungsgleich mit der
  lokalen Quelle in `negotiation-buddy/supabase/functions/chat/index.ts`.
  Alle fünf EFs mit aktivem LLM-Call (`chat`, `generate-plan`,
  `analyze-progress`, `summarize-session`, `analyze-document`) bestätigt
  Anthropic.
- **Dashboard-Verifikation (2026-07-18, User-bestätigt):** Sowohl der
  Backend-Render-Service als auch die Frontend-Static-Site bauen gegen die
  aktive Supabase-ID (`gpllrgkuozytyrmpfwbb`) — kein Split-Brain zwischen
  Production und dem in der Diagnose untersuchten Projekt. Damit ist der in
  `provider-drift-diagnosis.md` als "zentraler Vorbehalt" offen gelassene
  Punkt (Render-Build könnte theoretisch gegen die Legacy-Projekt-ID
  `ujnyioggxipvuxxxcivr` bauen) aufgelöst: **Observed statt Missing.**
- Commit `fc3ad5b` (`negotiation-buddy`, 2026-05-15 14:30:41 +0200):
  expliziter Migrationsgrund "Google AI Studio (quota issues)".

## Bekannter Nebenbefund (hier nur erwähnt, NICHT gelöst)

Die tier-basierte Modellwahl aus RFB-009 (`kmu`/`profi` → besseres Modell,
`free`/`privat` → günstigeres Modell) ist beim Umstieg auf Anthropic
ersatzlos entfallen — die aktuell deployte `chat`-EF verwendet
`claude-haiku-4-5-20251001` hartkodiert für alle Tiers, unabhängig von
`req.tier`. `product/briefs/NC-SEC-02.md` (Released, DONE 2026-04-30)
verifizierte die alte, Gemini-basierte Tier-Differenzierung vor dem
Umstieg — das ist seither nicht neu bewertet worden. Das ist eine
Produktentscheidung (Tier-Value-Versprechen für kmu/profi), keine
Architekturentscheidung — bewusst **nicht** Teil dieses ADRs. Siehe
`docs/contracts/frontend-backend.md` Abschnitt "Model Selection" für den
dokumentierten Ist-Zustand.

## Konsequenzen

- `docs/contracts/frontend-backend.md`, Abschnitt "Model Selection
  (tier-dependent — RFB-009)": Provider-Namen von Gemini auf Anthropic
  korrigiert, Verweis auf dieses ADR ergänzt (dieser Commit).
- `product/strategy.md`: Deep-dive-Referenz von ADR-003 auf ADR-012
  umgezogen (dieser Commit).
- `shared-context/CLAUDE.md` bleibt **unverändert** — die dortige Aussage
  ("Alle LLM-Calls: Anthropic Claude ... alle EFs nutzen
  claude-haiku-4-5-20251001") war bereits korrekt, nur ihre Quellenangabe
  (ADR-003) ist jetzt formal durch ADR-012 abgelöst.
- `negotiationcoach-backend/supabase/functions/chat/index.ts` (toter
  Gemini-Prototyp vom 2026-04-22, nie deployt — siehe
  `provider-drift-diagnosis.md` Abschnitt 3) bleibt unangetastet — Code-
  Änderungen sind explizit außerhalb des Scopes dieses docs-only Deliverys.
  Bleibt offener Cleanup-Kandidat.
- Weitere, nicht in diesem Delivery bearbeitete `ADR-003`-Referenzen (u. a.
  in `docs/wiki/*`, `docs/governance/*`, weiteren ADRs) bleiben gültig, da
  ADR-003 nicht gelöscht, nur als superseded markiert wurde — kein toter
  Link. Nicht Teil dieses Scopes, siehe `provider-drift-diagnosis.md`
  Abschnitt 4 (Referenz-Sweep) für die vollständige Liste.

## Betroffene Items

- NC-SEC-02 (tier-basierte Modellwahl — separates, offenes Produkt-Item)
- `docs/contracts/frontend-backend.md`
- `product/strategy.md`

## Referenzen

- ADR-003 — AI Provider Strategy (superseded durch dieses ADR)
- `docs/audits/provider-drift-diagnosis.md` (Commits `1e9074e`, `d3229d1`)
- Commit `fc3ad5b` (`negotiation-buddy`) — Anthropic-Migration
- `docs/features/loop-coding-integration.md` — Auslöser der Untersuchung
