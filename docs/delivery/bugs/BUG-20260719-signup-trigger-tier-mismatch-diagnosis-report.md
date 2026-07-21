# Diagnose-Report — BUG-20260719-signup-trigger-tier-mismatch

**Datum:** 2026-07-20
**Basis:** BUG-FILE (bereits sehr detailliert vorbefüllt, inkl. eigenem
Laufzeit-Evidenz-Gate) + eigene Zusatzverifikation dieser Phase. Alle
Aussagen aus dem BUG-FILE wurden gegen den aktuellen Repo-/Migrations-Stand
erneut geprüft (Lessons-Regel vom 2026-07-20: Prämissen verifizieren statt
übernehmen), nicht blind kopiert.

## Symptom

`public.user_profiles.persona_type` wird bei **jedem** Signup unbedingt auf
`'pro'` gesetzt, unabhängig vom tatsächlich beabsichtigten Tier. **Observed**
— Migrationsdatei erneut gelesen und Zeile für Zeile mit dem im BUG-FILE
zitierten Code verglichen: identisch, keine Abweichung.

## Ursache

**Observed.** `negotiation-buddy/supabase/migrations/20260309180824_4da7e8b7-1562-43d7-a9c9-be554281a7be.sql`,
Funktion `public.handle_new_user()`, Trigger `on_auth_user_created`
(`AFTER INSERT ON auth.users`):

```sql
INSERT INTO public.user_profiles (user_id, persona_type, experience_level)
VALUES (NEW.id, 'pro', 1);
```

Die Funktion liest `NEW.raw_user_meta_data` an keiner Stelle und überschreibt
damit **unbedingt** den ursprünglichen, korrekten Spalten-Default.

**Präzisierung gegenüber dem BUG-FILE-Titel ("ignoriert raw_user_meta_data.tier"):**
Das Original-`CREATE TABLE` (Migration `20260309105420`) definiert bereits
ein korrektes, konsistentes Default-Paar:
`persona_type NOT NULL DEFAULT 'private'` und
`subscription_tier NOT NULL DEFAULT 'free'` — genau die Kombination, die
`Profile.tsx:20` (`tierToPersonaType`) auch für alle Nicht-`kmu`/Nicht-`profi`-Fälle
als korrekt behandelt. Der Trigger überschreibt **nur** `persona_type` mit dem
hartkodierten `'pro'` und lässt `subscription_tier` beim korrekten Default
`'free'` stehen — dadurch entsteht sofort nach jedem Signup ein inkonsistentes
Paar (`pro` + `free`) statt des korrekten (`private` + `free`). Das eigentliche
Problem ist also primär eine **Default-Überschreibung**, nicht primär ein
fehlendes Metadata-Read — das Metadata-Read ist ein sinnvoller Zusatz, aber
nicht die Kernursache des aktiven Schadens.

## Neue Erkenntnis (im BUG-FILE nicht geprüft): `raw_user_meta_data.tier` wird von echten Nutzern nie gesetzt

**Observed**, zwei unabhängige Belege:

1. `negotiation-buddy/src/hooks/useAuth.tsx:56-64` — der einzige produktive
   `supabase.auth.signUp()`-Aufruf im Frontend übergibt **kein** `options.data`
   / `user_metadata` überhaupt:
   ```ts
   const { error } = await supabase.auth.signUp({
     email, password,
     options: { emailRedirectTo: window.location.origin },
   });
   ```
2. Der einzige Ort im gesamten Codebase (beide Repos), der
   `user_metadata: { tier: ... }` bei `createUser` setzt, ist
   `negotiationcoach-backend/scripts/seed-verify-user.ts:114-119` — ein
   manuelles Seeding-Script für den dedizierten Verify-Harness-Testuser
   (`verify-harness@internal.test`, Wert `'kmu'`), nicht der reguläre
   Signup-Pfad.

**Konsequenz:** Für echte Endnutzer ist `raw_user_meta_data.tier` beim Signup
grundsätzlich `NULL` — die "ignoriert Metadata"-Formulierung im BUG-Titel
trifft technisch zu, ist aber für den *aktiven* Schaden bei echten Nutzern
irrelevant. Der aktive Schaden bei echten Nutzern ist ausschließlich die
Default-Überschreibung (siehe oben): **jeder neue reguläre Nutzer bekommt
`persona_type = 'pro'`**, was die Chat-EF (bereits im BUG-FILE belegt) auf
`resolvedTier = "profi"` abbildet — volle Profi-Tiefe für jeden Free-Signup.

## Neue Erkenntnis: kein anderer Schreibpfad existiert, der das nachträglich korrigiert

**Observed**, vollständige Grep-Prüfung über beide Repos nach jeder Stelle,
die `user_profiles.persona_type` schreibt:

- `negotiation-buddy/src/pages/Profile.tsx:108-122` (`handleDevTierChange`) —
  einziger DB-Schreibpfad für `persona_type`/`subscription_tier` nach dem
  Signup, aber **hart gated** hinter `VITE_DEV_TIER_MOCK === "true"`
  (Zeile 56), also kein Produktionspfad.
- `OnboardingDialog`-Komponente existiert im Code, ist aber laut Kommentar
  in `Index.tsx:14` (`// OnboardingDialog removed (A-3) — type kept for
  PersonaConfig`) **nicht mehr gerendert** — kein aktiver Onboarding-Schreibpfad.
- AR-032 (Stripe-Webhook) ist laut `product/roadmap.md` extern blockiert,
  nicht live.

**Konsequenz:** Es gibt aktuell **keinen** Mechanismus, der `persona_type`
nach dem fehlerhaften Trigger-Insert für einen echten Nutzer je korrigiert.
Der Trigger-Fix ist damit nicht nur notwendig, sondern auch **hinreichend**
— kein nachgelagerter Code überschreibt das Ergebnis erneut.

## Kopplungsrisiko ausgeschlossen: `subscription_tier` selbst braucht keine Änderung

`negotiation-buddy/src/pages/Index.tsx:246`:
`showSessionFeatures = !!persona && persona.subscription_tier !== "free"`
— gated korrekt auf `subscription_tier`, das bereits beim korrekten Default
`'free'` bleibt (der Trigger setzt es nie explizit). Kein zusätzlicher
Fix-Bedarf hier. **Observed**, keine Änderung am Fix-Scope nötig.

## Kopplungsrisiko ausgeschlossen: Verwechslung mit `negotiation_sessions.persona_type`

Grep über `persona_type` fand mehrere weitere Stellen mit hartkodiertem
`'pro'`-Default
(`negotiationcoach-backend/src/api/sessionRoutes.ts:124,193`,
`negotiation-buddy/src/hooks/useSessionManager.ts:130`). **Observed, aber
ein anderes Feld:** Das ist `negotiation_sessions.persona_type` — ein
Session-Erstellungsparameter (welche Persona/Framework für DIESE
Verhandlung), definiert in einer separaten Migration
(`20260309170414`, `persona_type public.persona_type NOT NULL` auf der
Session-Tabelle) — nicht `user_profiles.persona_type` (Account-Tier). Beide
Felder teilen zufällig denselben Enum-Typ und Spaltennamen, sind aber
konzeptionell unabhängig. **Kein Fix-Bedarf hier — expliziter Scope-Ausschluss,
um eine falsche Erweiterung des Fix-Radius zu vermeiden.**

## Kopplungsrisiko — Risiko eines naiven Fixes

Ein direkter Cast `(NEW.raw_user_meta_data->>'tier')::public.persona_type`
würde bei jedem Wert, der nicht exakt `'pro'|'kmu'|'private'` ist (z. B. eine
künftige produktseitige Bezeichnung wie `'profi'`/`'privat'`), eine
Postgres-Exception werfen — der Trigger läuft `AFTER INSERT` auf `auth.users`
**für jeden Signup**; eine ungefangene Exception dort würde die komplette
Signup-Transaction abbrechen. Ein aktuell stiller Daten-Bug würde so durch
einen naiven Fix zu einem harten Signup-Ausfall eskaliert. **Der Fix muss
das per CASE/Allowlist abfangen, nicht per direktem Cast.**

## Betroffene Dateien

- `negotiation-buddy/supabase/migrations/20260309180824_4da7e8b7-1562-43d7-a9c9-be554281a7be.sql`
  — Ursprungsdefinition, **wird nicht editiert** (Repo-Konvention: Migrationen
  sind append-only, bestätigt durch `20260311161754`/`20260403120000`, die
  Änderungen als neue Migrationen nachreichen statt Historie zu editieren).
- **Neu:** `negotiation-buddy/supabase/migrations/<timestamp>_fix_handle_new_user_persona_type.sql`
  — `CREATE OR REPLACE FUNCTION public.handle_new_user()` mit korrigierter Logik.
- Live-Anwendung der Migration auf das aktive Supabase-Projekt
  (`gpllrgkuozytyrmpfwbb`) zusätzlich zum Migrationsfile nötig (Repo-Regel:
  DB-Änderungen müssen in Produktion verifiziert werden, nicht nur als Datei
  committet).
- `negotiationcoach-backend`: **kein Dateiwechsel nötig.** Backend hat ein
  eigenes, unabhängiges `supabase/migrations/`-Verzeichnis (7 Dateien) ohne
  jede Berührung von `handle_new_user`/`user_profiles`-Auth-Trigger — bestätigt
  per Grep, keine Überschneidung mit den 14 Migrationen in `negotiation-buddy`.

## Nicht einsehbar (Missing)

- Ob real zahlende Bestandskunden (vor 2026-07-20 registriert) durch den
  fehlerhaften `persona_type='pro'`-Default tatsächlich falsches
  Chat-Verhalten *erlebt* haben — erfordert Produktions-/Nutzungsdaten,
  außerhalb der Reichweite dieser Repo-Diagnose. Ein Fix behebt nur
  **künftige** Signups; Bestandsdaten-Korrektur (Backfill) ist eine separate
  Entscheidung, nicht Teil des minimalen Fix-Scopes.
- Ob die vier anderen Edge Functions mit LLM-Call (`generate-plan`,
  `analyze-progress`, `summarize-session`, `analyze-document`) denselben
  `persona_type`-Lookup nutzen — weiterhin ungeprüft, aus dem BUG-FILE
  übernommen, für den Trigger-Fix selbst nicht blockierend.

## Empfohlener Fix-Scope (minimal)

Neue Migration in `negotiation-buddy/supabase/migrations/`, die
`public.handle_new_user()` per `CREATE OR REPLACE FUNCTION` ersetzt:

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  requested_tier text := NEW.raw_user_meta_data->>'tier';
BEGIN
  INSERT INTO public.user_profiles (user_id, persona_type, experience_level)
  VALUES (
    NEW.id,
    CASE
      WHEN requested_tier IN ('pro', 'kmu', 'private') THEN requested_tier::public.persona_type
      ELSE 'private'
    END,
    1
  );
  RETURN NEW;
END;
$$;
```

- Ändert **ausschließlich** die `persona_type`-Zuweisung.
- `subscription_tier` bleibt unangetastet (Spalten-Default `'free'` ist
  bereits korrekt, siehe Kopplungsrisiko-Analyse oben).
- Allowlist statt direktem Cast (Sicherheit gegen Signup-Ausfall, siehe oben).
- Kein Backfill für Bestandsdaten — explizit außerhalb des Scopes (siehe
  Missing), eigene Entscheidung falls gewünscht.
- Migration muss zusätzlich live auf `gpllrgkuozytyrmpfwbb` angewendet werden
  (`supabase db push` oder `mcp__supabase__apply_migration`) — Datei allein
  genügt nicht.
