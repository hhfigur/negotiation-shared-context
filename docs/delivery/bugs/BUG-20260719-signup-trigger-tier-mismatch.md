# BUG-20260719-signup-trigger-tier-mismatch

**Erstellt:** 2026-07-19
**Status:** OPEN
**Risiko:** P1 (Proposed — siehe Schweregrad-Begründung unten, keine Entscheidung getroffen)
**TARGET REPO:** cross-repo (Ursache: Supabase-DB-Trigger auf dem aktiven Projekt `gpllrgkuozytyrmpfwbb`, betrifft sowohl `negotiationcoach-backend` als auch `negotiation-buddy`)
**Layer:** API (Tier-/Autorisierungs-Infrastruktur, keine der Verhandlungs-Layer 0–3)
**Bug-Typ:** Auth-Bug (mit Data-Bug-Charakter — falscher Wert wird bei jedem Signup geschrieben)
**Betroffene Tiers:** alle — der Trigger ignoriert den übergebenen Tier vollständig, betrifft strukturell jeden Signup unabhängig vom beabsichtigten Tier
**ADR-Constraints:** ADR-006 (Tier-Mapping), ADR-004 (Chat-Path-Routing / EF-Tier-Enforcement) — beide setzen ein konsistentes Tier-Modell voraus, das dieser Bug unterläuft

**Titel:** Tier-Assignment-Trigger ignoriert `raw_user_meta_data.tier`

---

## Klassifizierungslegende
Jede Aussage unten ist mit **Observed** (direkt verifiziert), **Inferred** (logisch abgeleitet, nicht direkt bestätigt) oder **Missing** (nicht einsehbar, offene Lücke) markiert.

## Symptom

`public.user_profiles.subscription_tier` weicht vom Tier ab, der in
`auth.users.raw_user_meta_data.tier` hinterlegt ist. `persona_type` wird bei
**jedem** Signup unbedingt auf `'pro'` hartkodiert — unabhängig davon, welcher
Tier beim Signup tatsächlich beabsichtigt oder in den User-Metadaten gesetzt
wurde. **Observed.**

Konkretes Beispiel (aus der Diagnose in
`docs/features/loop-coding-integration.md` Abschnitt 9, Commit `5e5a52d`):
`verify-harness@internal.test` wurde mit `user_metadata.tier: 'kmu'` angelegt.
Ergebnis: `auth.users.raw_user_meta_data.tier = "kmu"`, aber
`user_profiles.subscription_tier = "free"`, `user_profiles.persona_type = "pro"`.
**Observed** (SQL-Query-Output, siehe Referenz-Abschnitt unten).

## Ort

Postgres-Funktion `public.handle_new_user()`, ausgelöst durch Trigger
`on_auth_user_created` (`AFTER INSERT ON auth.users`). **Observed**, exakte
Fundstelle: `negotiation-buddy/supabase/migrations/20260309180824_4da7e8b7-1562-43d7-a9c9-be554281a7be.sql`,
Zeilen 19–31 (Funktionsdefinition + Trigger-Erstellung). Live-Zustand auf dem
aktiven Supabase-Projekt via `pg_get_functiondef()` direkt gegengeprüft —
identisch mit der Migration, keine spätere Änderung.

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  INSERT INTO public.user_profiles (user_id, persona_type, experience_level)
  VALUES (NEW.id, 'pro', 1);
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

Die Funktion liest `NEW.raw_user_meta_data` an keiner Stelle. `persona_type`
ist hartkodiert `'pro'`, `subscription_tier` wird in diesem INSERT gar nicht
gesetzt (bleibt beim Spalten-Default `'free'`). **Observed.**

## Reproduktion

1. Neuen `auth.users`-Eintrag anlegen (z. B. via Supabase Admin API
   `createUser` oder regulären Signup-Flow) mit einem beliebigen
   `user_metadata.tier`-Wert (z. B. `"kmu"`).
2. Resultierende Zeile in `public.user_profiles` für denselben `user_id`
   abfragen.
3. Erwartung: `persona_type`/`subscription_tier` spiegeln den beim Signup
   übergebenen Tier. Tatsächlich: `persona_type = 'pro'` (immer, unabhängig
   vom übergebenen Wert), `subscription_tier = 'free'` (Spalten-Default,
   nie explizit gesetzt).

**Observed** — mit dem konkreten `verify-harness@internal.test`-Beispiel
(erstellt 2026-07-16) bereits durchexerziert und in
`docs/features/loop-coding-integration.md` Abschnitt 9 dokumentiert. Kein
zusätzlicher Reproduktionslauf für dieses BUG-FILE nötig — die Trigger-Logik
ist unbedingt (keine Bedingung, kein Pfad, der `raw_user_meta_data` je
berücksichtigt), daher gilt die Reproduktion für **jeden** Signup, nicht nur
für den einen beobachteten Fall.

## Logs / Fehlermeldungen

Kein Fehler, kein Crash — der Trigger läuft fehlerfrei durch. Das ist ein
**stiller** Bug: falsche Daten werden ohne jede Fehlermeldung geschrieben.
Die "Evidenz" ist der Funktionscode selbst (`pg_get_functiondef`-Output oben)
plus der SQL-Query-Vergleich zwischen `auth.users.raw_user_meta_data.tier`
und `user_profiles.subscription_tier`/`persona_type` für denselben User.
**Observed.**

## Verdacht (bestätigt, kein offener Verdacht mehr)

`handle_new_user()` wurde am **2026-03-09** (Migration
`20260309180824_...sql`) eingeführt und seither **nie verändert** — Grep
über alle Migrationen in `negotiation-buddy/supabase/migrations/` findet
genau diese eine Datei, die `handle_new_user` erwähnt. **Observed** (Betroffener
Scope damit beantwortbar, nicht Missing: **alle Signups seit 2026-03-09**).

## Auswirkung — welches Feld wird wo tatsächlich für Autorisierung gelesen (nicht spekulativ)

Es gibt **zwei unabhängige Tier-Lesepfade** im System, dieser Bug betrifft
sie **unterschiedlich stark**:

1. **`negotiationcoach-backend`, Express-API (`authMiddleware`,
   `src/api/middleware.ts:118-121`):** liest
   `data.user.user_metadata?.tier ?? data.user.app_metadata?.tier` —
   **direkt aus `auth.users`-Metadata, NICHT aus `user_profiles`.** Dieser
   Pfad ist von diesem Bug **nicht betroffen** — bestätigt durch den
   Curl-Test in `loop-coding-integration.md` Abschnitt 9 (`/api/enrich`,
   `requireTier('kmu')`, gegen den lokalen Dev-Server, Tier korrekt aus
   `auth.users`-Metadata gelesen und durchgesetzt). **Observed.**

2. **`negotiation-buddy`, Supabase Edge Function `chat`
   (aktiv deployt, `gpllrgkuozytyrmpfwbb`, Version 7, Volltext via
   `mcp__supabase__get_edge_function` gelesen):**
   ```
   const { data: profile } = await supabase
     .from("user_profiles").select("persona_type")
     .eq("user_id", user.id).maybeSingle();
   switch (profile?.persona_type) {
     case "pro":      resolvedTier = "profi";  break;
     case "kmu":      resolvedTier = "kmu";    break;
     case "private":  resolvedTier = "privat"; break;
     default:         resolvedTier = "free";
   }
   ```
   liest **`user_profiles.persona_type`** — genau das Feld, das dieser
   Trigger-Bug bei jedem Signup fest auf `'pro'` setzt. Ergebnis:
   `resolvedTier` wird für **jeden neuen Signup** zu `"profi"` — und
   `systemPrompt.ts` aktiviert den `M-10 | PREMIUM-TIEFE`-Block
   (proaktive Eskalationspfade, Machtanalyse, ZOPA-Schätzung,
   Black-Swan-Identifikation) unbedingt für `subscription_tier === "profi"
   || "kmu"`. **Beobachteter, aktuell aktiver Impact: jeder neue Chat-EF-
   Nutzer bekommt Profi-Tier-Systemprompt-Tiefe, unabhängig vom tatsächlich
   gebuchten/bezahlten Tier — nicht nur ein Datenkonsistenz-Problem, sondern
   ein aktives Tier-Value-Leck im laufenden Chat-Pfad.** **Observed** (Code
   direkt aus der deployten Function gelesen, nicht aus lokaler Quelle
   vermutet).

## Laufzeit-Evidenz-Gate (Phase 1.5) — Prüfergebnis

Die vorliegende Evidenz ist ausreichend, um die zentrale Hypothese von
"Inferred" auf **"Observed"** zu heben:
- Root Cause: Observed (Funktionscode live + Migrationsdatei identisch).
- Seit wann: Observed (2026-03-09, einzige Migration, nie geändert).
- Auswirkung auf Express-API: Observed (Curl-Beweis, nicht betroffen).
- Auswirkung auf Chat-EF: Observed (deployter Code direkt gelesen, betroffen).

**Verbleibende, explizit offene Lücken (Missing — nicht unterstellt):**
- Ob die vier anderen Edge Functions mit LLM-Call (`generate-plan`,
  `analyze-progress`, `summarize-session`, `analyze-document`) denselben
  `persona_type`-Lookup nutzen und ähnlich betroffen sind — in dieser
  Diagnose **nicht geprüft**. Empfohlener Scope für eine Vertiefung, falls
  ein Fix geplant wird.
- Ob real zahlende Kunden (nicht nur `verify-harness@internal.test`) durch
  diesen Bug tatsächlich falsches Tier-Verhalten erlebt haben — erfordert
  Produktionsdaten-/Stripe-Abgleich, außerhalb der Reichweite dieser
  Repo-/SQL-Diagnose.
- Ob es überhaupt einen aktiven, produktiven Mechanismus gibt, der
  `user_profiles.persona_type`/`subscription_tier` nach dem Signup korrekt
  aktualisiert (z. B. nach Zahlungseingang) — AR-032 (Stripe-Webhook) ist
  laut `product/roadmap.md` extern blockiert/nicht live; ob ein anderer
  Mechanismus existiert, wurde hier nicht geprüft.

## Schweregrad-Begründung (Proposed, keine Entscheidung)

**P1** vorgeschlagen: der betroffene Pfad ist der produktionsweite
Signup-Trigger (jeder neue Nutzer, seit 2026-03-09, ohne Ausnahme) und der
Chat-EF-Impact ist bereits als aktiv bestätigt (nicht nur theoretisch). Kein
Datenverlust, kein Auth-Bypass im engeren Sinn (RLS bleibt korrekt,
Express-API-Zugriffskontrolle bleibt korrekt) — daher nicht P0. Endgültige
Priorisierung liegt beim Product Owner.

## Referenzen

- `docs/features/loop-coding-integration.md` Abschnitt 9 (Commit `5e5a52d`)
  — primäre Evidenzquelle (Tier-Divergenz-Query, RLS-Check, Curl-Beweis).
- `AGENTS.md`, Zeile 57: *"HIGH-03 | High | Three incompatible tier
  systems: backend tier, Supabase persona_type, Edge Function hardcoded
  'free'"* — dieser Bug ist die konkrete, mit Runtime-Evidenz belegte
  Ursache eines der drei genannten Systeme (Supabase `persona_type`).
- `negotiation-buddy/supabase/migrations/20260309180824_4da7e8b7-1562-43d7-a9c9-be554281a7be.sql`
  Zeilen 19–31.

## Plan
_Wird durch Template 1-DEV befüllt._

## Implement
_Wird durch Template 2-DEV befüllt._

## Abschluss
_Wird durch /close-task befüllt._
