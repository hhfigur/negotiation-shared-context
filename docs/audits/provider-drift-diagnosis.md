# Provider-Drift-Diagnose — Gemini vs. Anthropic in Edge Functions

**Status:** Diagnose abgeschlossen — READ-ONLY, keine Code-/Doc-Änderung vorgenommen
**Datum:** 2026-07-16
**Auslöser:** Widerspruch entdeckt während `docs/features/loop-coding-integration.md` PROMPT 1 — `shared-context/CLAUDE.md` behauptet "alle EFs nutzen claude-haiku-4-5-20251001", ein Code-Grep in `negotiationcoach-backend/supabase/functions/chat/index.ts` zeigte Gemini-Calls.
**Klassifizierung:** Observed | Inferred | Missing (pro Aussage einzeln markiert)

---

## ⚠️ Zentraler Vorbehalt — VOR jeder Interpretation der Befunde lesen

Alle folgenden Befunde zum "aktiven" Supabase-Projekt beziehen sich auf
`gpllrgkuozytyrmpfwbb` — das Projekt, mit dem der lokale Supabase-MCP-Server
verbunden ist und auf das beide Repos lokal per CLI gelinkt sind
(`supabase/.temp/project-ref` in beiden Repos zeigt auf `gpllrgkuozytyrmpfwbb`,
Observed).

**Aber:** `negotiation-buddy/.env` (git-getrackt, Observed via `git ls-files`)
enthält `VITE_SUPABASE_PROJECT_ID="ujnyioggxipvuxxxcivr"` (Legacy) —
`negotiation-buddy/.env.local` (git-**ignoriert** via `*.local`-Regel in
`.gitignore`, verifiziert via `git check-ignore -v`, siehe Gate-Abschnitt
unten) überschreibt dies nur lokal auf `gpllrgkuozytyrmpfwbb`.

**Missing:** Ob der Render.com-Production-Build tatsächlich gegen
`gpllrgkuozytyrmpfwbb` oder gegen die im Repo committete Legacy-ID
`ujnyioggxipvuxxxcivr` baut, ist aus lokalen Dateien NICHT ableitbar — das
hängt davon ab, ob Render eigene Environment-Variablen gesetzt hat oder
nicht. **Alle "Observed"-Aussagen unten gelten gesichert nur für
`gpllrgkuozytyrmpfwbb`.** Falls Production tatsächlich noch
`ujnyioggxipvuxxxcivr` nutzt, ist der gesamte folgende Befund für die
Produktionsrealität nicht validiert. **Detaillierte Untersuchung dieses
Vorbehalts:** siehe Abschnitt "Gate: Render-Production Supabase-ID" am
Ende dieses Dokuments.

---

## 1. Verorten

- **Zwei getrennte `supabase/functions/`-Bäume existieren** (Observed):
  - `negotiation-buddy/supabase/functions/`: `chat`, `generate-plan`,
    `analyze-progress`, `analyze-document`, `summarize-session`,
    `send-password-reset`, `verify-reset-token` (7 Functions)
  - `negotiationcoach-backend/supabase/functions/`: `chat`, `negotiate`,
    `_shared` (3 Einträge, `_shared` kein deploybares Function-Verzeichnis)
- **Aktives Supabase-Projekt** (Observed via `mcp__supabase__get_project_url`):
  `https://gpllrgkuozytyrmpfwbb.supabase.co`
- **Lokale CLI-Links** (Observed, `supabase/.temp/project-ref` in beiden
  Repos): beide zeigen auf `gpllrgkuozytyrmpfwbb`.
- **Deployte Functions auf `gpllrgkuozytyrmpfwbb`** (Observed via
  `mcp__supabase__list_edge_functions`): `analyze-document`,
  `analyze-progress`, `chat`, `generate-plan`, `send-password-reset`,
  `summarize-session`, `verify-reset-token` — **exakt 7, exakt die
  negotiation-buddy-Liste.** Keine der negotiationcoach-backend-spezifischen
  Functions (`negotiate`, oder eine unter `_shared` abgeleitete) ist deployt.
- **EFs mit aktivem LLM-Call:** `chat`, `generate-plan`, `analyze-progress`,
  `summarize-session`, `analyze-document` (alle negotiation-buddy) sowie
  `negotiationcoach-backend/supabase/functions/chat/index.ts` (eigene,
  gleichnamige, aber andere Datei — siehe Abschnitt 2). `negotiate` hat
  **keinen** direkten LLM-Call (delegiert an Railway/Render `/api/analyze`,
  Observed via ADR-007 und Commit `9c6f1f2`).

---

## 2. Ist-Zustand pro EF mit LLM-Call (Observed)

| EF | Lokale Quelle | Deployt unter aktivem Slug? | Provider | Endpoint-Host | Modell-String | Env-Var |
|---|---|---|---|---|---|---|
| `chat` | `negotiation-buddy/supabase/functions/chat/index.ts:57,84,213` | **JA** — Inhalt stimmt exakt überein (SHA256 `c2c6d0...` aus `list_edge_functions`, Volltext-Abgleich via `get_edge_function` gegen lokale Datei deckungsgleich) | Anthropic | `api.anthropic.com` | `claude-haiku-4-5-20251001` | `ANTHROPIC_API_KEY` |
| `generate-plan` | `negotiation-buddy/supabase/functions/generate-plan/index.ts:58,73,81` | Beobachtet über `list_edge_functions`-Entrypoint-Pfad (`.../source/supabase/functions/generate-plan/index.ts` — Pfadstruktur konsistent mit negotiation-buddy-Deploy); Volltext nicht einzeln via `get_edge_function` nachgezogen (Zeitboxing) | Anthropic | `api.anthropic.com` | `claude-haiku-4-5-20251001` | `ANTHROPIC_API_KEY` |
| `analyze-progress` | `.../analyze-progress/index.ts:54,62,70` | Beobachtet (gleiche Pfad-Logik wie oben) | Anthropic | `api.anthropic.com` | `claude-haiku-4-5-20251001` | `ANTHROPIC_API_KEY` |
| `summarize-session` | `.../summarize-session/index.ts:45,81,89` | Beobachtet (gleiche Pfad-Logik) | Anthropic | `api.anthropic.com` | `claude-haiku-4-5-20251001` | `ANTHROPIC_API_KEY` |
| `analyze-document` | `.../analyze-document/index.ts:77,109,117` | Beobachtet (gleiche Pfad-Logik) | Anthropic | `api.anthropic.com` | `claude-haiku-4-5-20251001` | `ANTHROPIC_API_KEY` |
| `chat` (namensgleich, **andere Datei**) | `negotiationcoach-backend/supabase/functions/chat/index.ts:123-124,209-210,258` | **NEIN** — Content-Vergleich negativ (Backend-Datei ruft Gemini auf, deployte Datei ruft Anthropic auf); zusätzlich weicht die `entrypoint_path`-Struktur der deployten Version (`.../source/index.ts`, ohne `supabase/functions/chat/`-Präfix) von allen anderen negotiation-buddy-Deploys ab (die alle `.../source/supabase/functions/<name>/index.ts` zeigen) — Indiz, dass diese Backend-Datei **nie unter dem aktuell aktiven `chat`-Slug live war** | Gemini (Google AI Studio, direkter Call) | `generativelanguage.googleapis.com` | `gemini-2.0-flash` | `GEMINI_API_KEY` |
| `negotiate` | `negotiationcoach-backend/supabase/functions/negotiate/index.ts` | Nicht im aktiven Projekt deployt (fehlt komplett in `list_edge_functions`) | kein direkter LLM-Call (Proxy zu Railway/Render) | n/a | n/a | n/a |

---

## 3. Drift-Herkunft (Observed via `git log`/`git blame`)

### negotiationcoach-backend — `supabase/functions/chat/index.ts`

Ein einziger Commit in der gesamten Historie der Datei:

```
3cc21fc feat(ef): create chat Edge Function with SSE mode and extract mode (Option B neuansatz)
Datum:  Wed Apr 22 14:53:32 2026 +0200
Autor:  Maik Figur (Co-Authored-By: Claude Sonnet 4.6)
```

Datei wurde seither **nie wieder verändert** (Observed, `git log --follow` zeigt
nur diesen einen Commit).

**Inferred:** ADR-007 (Entscheidung "Option A — Retire" für
`_shared/engine/`) wurde am **2026-04-21** getroffen — einen Tag **vor**
diesem Commit. Der Commit-Titel "Option B neuansatz" bezieht sich vermutlich
NICHT auf ADR-007s "Option B — Migrate" (die wurde am Vortag bereits explizit
verworfen), sondern auf einen separaten, nicht dokumentierten
Architektur-Versuch.

**Missing:** Kein Backlog-Item, kein ADR, keine Brief-Referenz zu diesem
Commit gefunden. Zweck/Auftrag des Commits bleibt unklar.

### negotiation-buddy — `supabase/functions/chat/index.ts`

Chronologische Historie (älteste zuerst):

```
089498f  "Connected to Lovable Cloud" (initial — Lovable-Gateway, gemini-3-flash-preview)
...
2fe2b0f  chore(infra): migrate Supabase + AI gateway away from Lovable
         → ai.gateway.lovable.dev ersetzt durch direkten Google-AI-Studio-Call
         → LOVABLE_API_KEY → GOOGLE_AI_API_KEY
da71721  fix(edge-functions): replace gemini-2.5 with gemini-2.0-flash
         (gemini-2.5-pro/flash nicht verfügbar auf Google-AI-Studio-
          OpenAI-kompatiblem Endpoint ohne preview-Tag)
fc3ad5b  fix(edge-functions): switch AI provider from Google to Anthropic
         Datum: Fri May 15 14:30:41 2026 +0200
         "Replace Google AI Studio (quota issues) with Anthropic claude-haiku."
c60c249  fix(chat-extract): robustes JSON-Parsing in EF extract-mode
8cb4f42  fix(chat-extract): user-only messages filter in EF extract-mode
```

**Observed — Deployment-Korrelation:** `generate-plan` zeigt laut
`list_edge_functions` `updated_at = 2026-05-15 14:30:25 CEST` — **16 Sekunden
vor** Commit `fc3ad5b` (14:30:41). Starkes Indiz, dass der Anthropic-Umstieg
unmittelbar nach dem Commit deployt wurde (batch-artig über mehrere
Functions hinweg). `chat` selbst zeigt `updated_at = 2026-06-19 10:25:17
CEST` (Version 7) — das ist nach den beiden späteren Bugfix-Commits
(`c60c249`, `8cb4f42`), konsistent mit einem Redeploy nach diesen Fixes.
Das genaue Commit-Datum von `8cb4f42`/`c60c249` wurde nicht einzeln
nachgezogen (Missing, aber nicht entscheidungsrelevant).

### Fazit Drift-Herkunft

Ein Gemini-Zustand war **real und live**, aber nur zwischen der Lovable-
Migration (`2fe2b0f`) und dem 2026-05-15 (`fc3ad5b`). Seit **2026-05-15** ist
Anthropic der durchgängig deployte Provider für alle negotiation-buddy-EFs
mit LLM-Call. Die Gemini-rufende Datei in `negotiationcoach-backend` ist ein
eigenständiger, nie deployter Prototyp vom 2026-04-22 — zeitlich zufällig
mitten in negotiation-buddys eigener Lovable→Google-Phase entstanden, aber
in einem anderen Repo, mit eigenem Env-Var-Namen (`GEMINI_API_KEY` statt
`GOOGLE_AI_API_KEY`), nie live.

---

## 4. Referenz-Sweep (grep, read-only, Node-Modules und Stray-Worktree ausgeschlossen)

> **Hinweis:** `.claude/worktrees/quizzical-poitras-6b3676/` (ein gesperrtes,
> verwaistes Git-Worktree, unabhängig entdeckt) enthält eigene Kopien
> mehrerer ADRs und Docs. Treffer darin wurden aus der folgenden Tabelle
> entfernt (Duplikate desselben Inhalts, nicht Teil des `main`-Branches) —
> nicht Teil dieser Untersuchung, siehe `docs/features/loop-coding-integration.md`
> Abschnitt 6.8 für den ursprünglichen Fund.

| Suchstring | Code (negotiation-buddy) | Code (negotiationcoach-backend) | Docs (shared-context, main) |
|---|---|---|---|
| `ai.gateway.lovable.dev` | — | — | `ADR-003`, `delivery/session-dump-2026-05-21.md` |
| `LOVABLE_API_KEY` | — | — | `ADR-003`, `docs/auth-permission-map.md`, `docs/audits/current-state-report.md` |
| `generativelanguage.googleapis.com` | — | `supabase/functions/chat/index.ts` (der tote Prototyp) | — |
| `api.anthropic.com` | 5 Dateien (chat, generate-plan, analyze-progress, summarize-session, analyze-document) | — | — |
| `claude-haiku` (i) | dieselben 5 Dateien | `src/utils/modelRouter.ts`, `docs/db-map.md` | `CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/bounded-contexts.md`, `docs/audits/current-state-report.md`, `docs/audits/refactor-backlog.md`, `docs/contracts/frontend-backend.md`, `docs/features/layer3-simulation.md`, `docs/delivery/FEATURE-L2-CONTEXT-plan.md`, `docs/delivery/session-dump-2026-05-21.md`, `docs/delivery/bugs/BUG-BATNA-combined-diagnosis-report.md` |
| `gemini` (i) | **0 Treffer** (vollständig migriert, auch keine Kommentar-Reste) | `docs/repo-map.md`, `docs/service-catalog.md`, `docs/audit-findings.md`, `supabase/functions/chat/index.ts` | `ADR-003`, `ADR-004`, `ADR-005`, `ADR-007`, `docs/audits/current-state-report.md`, `docs/contracts/frontend-backend.md`, `docs/audits/refactor-backlog.md`, `docs/wiki/*` (mehrere), `docs/governance/*`, `docs/delivery/initial-setup-baseline.md`, `docs/delivery/claude-code-prompt-templates-dev.md`, `docs/delivery/session-dump-2026-05-21.md`, `product/briefs/NC-PLAN-FIX.md`, `product/briefs/NC-SEC-02.md` |

**Beobachtung:** negotiation-buddy selbst hat **keine** Gemini-Restspuren
mehr im Code (vollständige Migration). Die Drift lebt ausschließlich in (a)
einem toten Backend-Prototyp und (b) einer großen Zahl von Docs, die seit
der Migration nicht aktualisiert wurden.

---

## 5. Doc-Abgleich (Drei-Wege, präzisiert)

| Quelle | Exakter Wortlaut | Bewertung |
|---|---|---|
| `shared-context/CLAUDE.md` | *"Alle LLM-Calls: Anthropic Claude (ADR-003) — sowohl Express Backend als auch Edge Functions (alle EFs nutzen claude-haiku-4-5-20251001)"* | **Korrekt** für den tatsächlich deployten Zustand (Observed) — trifft für alle 5 aktiven, LLM-rufenden EFs zu. Referenziert ADR-003, aber ADR-003 selbst beschreibt einen älteren, nicht mehr aktuellen Stand (s.u.) — die CLAUDE.md-Aussage ist also richtig, ihre Quellenangabe (ADR-003) ist es nicht mehr. |
| `docs/decision-log/ADR-003-ai-provider-strategy.md` | *"The current two-provider split is intentional and accepted: Supabase Edge Function (generate-plan, chat) → Lovable AI Gateway → Gemini 2.5 Flash [...] Railway backend → Anthropic Claude"* (Accepted 2026-03-31) | **Veraltet seit 2026-05-15** (`fc3ad5b`). War zum ADR-Erstellungszeitpunkt korrekt, wurde nie amendet oder als superseded markiert. Beschreibt zusätzlich einen Lovable-Gateway-Pfad, der bereits vor `fc3ad5b` (durch `2fe2b0f`) nicht mehr existierte — ADR-003 war bereits zum Zeitpunkt von `fc3ad5b` in zwei Punkten unscharf (Lovable UND Gemini), nicht nur in einem. |
| Code (Observed, 2026-07-16) | 5 von 5 LLM-rufenden EFs → `api.anthropic.com`, `claude-haiku-4-5-20251001` | Provider-Split existiert nicht mehr — ein einziger Provider (Anthropic) für Backend UND Edge Functions. |

### Zusatzfund 1 — `docs/contracts/frontend-backend.md` (Z. 637–639)

> *"Model Selection (tier-dependent — RFB-009): `kmu`/`profi` → `google/gemini-2.5-pro`, `free`/`privat` → `google/gemini-2.5-flash`"*

Doppelt veraltet: (a) Provider (Gemini statt Anthropic seit `fc3ad5b`) UND
(b) das Feature selbst — der aktuell deployte `chat`-Code (Observed, siehe
Abschnitt 2) wählt **kein** tier-abhängiges Modell mehr; beide LLM-Aufrufe
(Extract- und Standard-Modus) verwenden hartkodiert
`claude-haiku-4-5-20251001` für **alle** Tiers. Die tier-basierte
Modellwahl aus RFB-009 (`d90d5c0`, 2026-04-10) wurde durch den
Anthropic-Umstieg offenbar entfernt, ohne dass Contract oder ADR
aktualisiert wurden.

### Zusatzfund 2 — `product/briefs/NC-SEC-02.md` (Released, DONE 2026-04-30)

Der Brief verifiziert explizit: *"Modell-Auswahl (Z.141-143) vollständig
implementiert"* und *"ADR-Prüfung: ADR-003 schreibt vor: EF → Gemini via
Lovable AI Gateway. Kein Anthropic in EF. Modell-Auswahl bleibt im
Gemini-Spektrum. ✅"* — zum Verifikationszeitpunkt (30.04.) korrekt, aber
durch den späteren Anthropic-Umstieg (15.05., zwei Wochen später) faktisch
überholt. **Missing:** Kein Follow-up-Item gefunden, das diese Divergenz
nach dem Umstieg aufgreift oder die tier-basierte Modell-Differenzierung neu
bewertet — relevant für `product/strategy.md`s Ziel "erstes
zahlungsfähiges Tier (kmu/profi) aktivieren", da eine zuvor implementierte
und sicherheitsseitig verifizierte Tier-Differenzierung (unterschiedliche
Modellqualität je Tier) seither ersatzlos entfallen ist.

### Zusatzfund 3 — `product/briefs/NC-PLAN-FIX.md` (Z. 24, aktueller Release-Scope R-2026-09)

Nennt *"Gemini-Extraktor"* als Teil der Fehleranalyse für den `extract`-Modus
in `chat/index.ts`. Der referenzierte Code läuft laut Observed-Befund heute
über Anthropic. Terminologie-Drift — die zugrundeliegende funktionale
Fehleranalyse (Extraktion findet Felder nicht) bleibt davon unabhängig
gültig, sollte aber bei nächster Überarbeitung sprachlich korrigiert werden.

---

## 6. Secret-Hygiene (nur Beobachtung)

- `ANTHROPIC_API_KEY` (negotiation-buddy-EFs): via `Deno.env.get(...)` — wird
  aus Supabase-Function-Secrets bezogen (unabhängig von Frontend-`.env`-
  Dateien). Kein Wert im Repo gefunden.
- `GEMINI_API_KEY` (toter Backend-Prototyp): Env-Var-**Name** referenziert,
  aber nirgends in `negotiationcoach-backend/.env` oder `.env.example`
  vorkonfiguriert (Observed). Falls dieser Prototyp je deployt wurde, müsste
  das Secret separat via `supabase secrets set` gesetzt worden sein. **Missing:**
  Ob dieses Secret noch als ungenutzter Eintrag im Supabase-Projekt existiert,
  ist über die verfügbaren Read-Only-Tools nicht einsehbar.
- Keine hartkodierten Schlüssel gefunden — einziger Treffer für
  `sk-ant-`/`AIzaSy`-Muster war der Platzhalter `sk-ant-...` in
  `negotiationcoach-backend/.env.example`.
- `.env`-Dateien: in `negotiationcoach-backend` nicht git-getrackt (nur
  `.env.example`). In `negotiation-buddy` ist **`.env` selbst git-getrackt**
  (Observed via `git ls-files`) — enthält nur den Supabase-Publishable-Key
  (bewusst öffentlich, kein Secret-Leak), aber siehe zentraler Vorbehalt oben
  zur Legacy-Projekt-ID darin.

---

## Entscheidungsvorlage (faktenbasiert, keine Entscheidung getroffen)

**Option A — Auf Anthropic migrieren (Docs/ADR an bereits gelebte Realität anpassen):**
- Aufwand: Gering — kein Code-Delta nötig, nur Doc-Korrektur (ADR-003 amend/supersede, `frontend-backend.md` Model-Selection-Abschnitt, `CLAUDE.md`-Quellenverweis).
- Risiko: Gering — bildet nur ab, was seit 2026-05-15 bereits produktiv läuft.
- Offene Frage dabei: Soll die verlorene tier-basierte Modell-Differenzierung (Zusatzfund 1/2) als eigenes Bug-/Enabler-Item neu aufgesetzt werden (z. B. `claude-haiku` für free/privat, teureres Anthropic-Modell für kmu/profi), oder wird "ein Modell für alle Tiers" als akzeptierter Zustand dokumentiert?
- `negotiationcoach-backend/supabase/functions/chat/index.ts` (toter Gemini-Prototyp) müsste als Dead Code klassifiziert und ggf. entfernt werden (separates Cleanup-Item).

**Option B — Direct-Gemini akzeptieren, Docs an (vermeintliche) Zielarchitektur anpassen:**
- Würde bedeuten: den seit 2026-05-15 laufenden Anthropic-Betrieb wieder auf Gemini zurückbauen — widerspricht der dokumentierten Migrationsbegründung ("Google AI Studio quota issues", Commit `fc3ad5b`). Kein Hinweis gefunden, dass diese Begründung nicht mehr zutrifft.
- Deutlich höherer Aufwand und Risiko als Option A, ohne erkennbaren Vorteil aus den vorliegenden Daten.

**Diese Einordnung ist eine Entscheidungsvorlage, keine Entscheidung.** Die
A/B-Wahl (und die Frage der tier-basierten Modell-Differenzierung) trifft
der Product Owner nach Review dieses Reports. Vor jeder Entscheidung sollte
zusätzlich der zentrale Vorbehalt (Abschnitt oben: welches Supabase-Projekt
Production tatsächlich nutzt) geklärt werden — sonst bezieht sich die
Entscheidung möglicherweise auf das falsche Projekt.

---

## Gate: Render-Production Supabase-ID

**Nachtrag vom 2026-07-16 — READ-ONLY-Untersuchung in `negotiation-buddy`,
Vertiefung des zentralen Vorbehalts oben.**

### Observed

- **Kein Render-Config-File im Repo.** Weder `render.yaml` noch eine sonstige
  `.render*`-Datei existiert (`find` über das gesamte Repo, maxdepth 2, leer).
  Render-Build-Settings (Build Command, Env-Vars) werden folglich —
  soweit aus dem Repo ersichtlich — ausschließlich über das Render-Dashboard
  konfiguriert, nicht als Infrastructure-as-Code versioniert.
- **Build-Script** (`package.json`): `"build": "vite build"` — Standard-Vite-
  Build ohne Custom-Wrapper, kein Pre-/Post-Build-Hook, der Env-Vars
  umschreibt.
- **App-Code liest Supabase-Verbindung** in
  `src/integrations/supabase/client.ts:5-6`:
  ```
  const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
  const SUPABASE_PUBLISHABLE_KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
  ```
  Klassisches Vite `import.meta.env` — wird **zur Build-Zeit** in das
  Static-Bundle eingebacken, nicht zur Laufzeit im Browser aufgelöst.
- **`.env` vs. `.env.local` — Projekt-IDs (nur IDs, keine Key-Werte):**
  | Datei | `VITE_SUPABASE_PROJECT_ID` | Git-Status |
  |---|---|---|
  | `.env` | `ujnyioggxipvuxxxcivr` (Legacy) | **Git-getrackt** (`git ls-files` zeigt `.env`) |
  | `.env.local` | `gpllrgkuozytyrmpfwbb` (Aktiv) | **Git-ignoriert** — matcht die `*.local`-Regel in `.gitignore` Zeile 13, verifiziert via `git check-ignore -v .env.local` → `.gitignore:13:*.local  .env.local` |
  | `.env` (Kontrollprobe) | — | `git check-ignore -v .env` → **kein Treffer**, d. h. `.env` ist bewusst NICHT ignoriert |
  - `.env.local` enthält zusätzlich `VITE_API_URL="http://localhost:3001"` und `VITE_DEV_TIER_MOCK="true"` — eindeutig als lokale Dev-Overrides erkennbar, nicht für Production gedacht.
  - `.env.example` enthält **keine** `VITE_SUPABASE_*`-Platzhalter (nur `VITE_POSTHOG_*`) — Onboarding-Doku zu diesen Variablen fehlt, unabhängig vom eigentlichen Befund.

### Inferred

- Da `.env.local` git-ignoriert ist, ist es **nicht Teil eines frischen
  `git clone`** — ein Render-Build, der aus dem Repo-Checkout baut, sieht
  `.env.local` nur, wenn es zusätzlich (außerhalb von Git) auf den
  Build-Runner kopiert oder manuell im Dashboard nachgebildet wurde.
  **Ohne explizite Render-Dashboard-Overrides für `VITE_SUPABASE_URL` /
  `VITE_SUPABASE_PROJECT_ID` / `VITE_SUPABASE_PUBLISHABLE_KEY` würde ein
  Default-Build aus einem frischen Checkout ausschließlich die im Repo
  committete `.env` sehen — also die Legacy-ID `ujnyioggxipvuxxxcivr`.**
  Dies folgt aus Standard-Vite-Verhalten (Datei-Präzedenz `.env.local` >
  `.env`, aber nur wenn die Datei tatsächlich vorhanden ist) und ist hier
  als Inferred markiert, weil Vites generelles Präzedenzverhalten nicht
  im Repo selbst dokumentiert/konfiguriert, sondern Framework-Standard ist.
- Sollte Render dagegen echte Dashboard-Environment-Variablen für diese
  drei Keys gesetzt haben, würden diese (als Prozess-Env-Variablen zur
  Build-Zeit) sowohl `.env` als auch ein eventuell manuell nachgebildetes
  `.env.local` überstimmen — auch das ist Standard-Vite/Node-Verhalten,
  aber ebenfalls nicht aus dem Repo verifizierbar (siehe Missing).

### Missing (explizit)

- **Die tatsächlich in Render gesetzten Build-Environment-Variablen des
  `negotiation-buddy`-Static-Site-Deploys** — aus dem Repo nicht
  feststellbar, da kein `render.yaml` existiert und Dashboard-Konfiguration
  nicht Teil des Git-Repos ist. Dies ist die einzige Quelle, die den
  zentralen Vorbehalt (aktives vs. Legacy-Supabase-Projekt in Production)
  abschließend klären kann. Muss direkt im Render-Dashboard geprüft werden.
- Ob auf dem Render-Build-Runner jemals manuell eine `.env.local`-Datei
  hinterlegt wurde (z. B. über ein Secret-File-Feature von Render) — aus
  dem Repo nicht ersichtlich.

---

## Offene Missing-Punkte (Zusammenfassung)

1. Welches Supabase-Projekt (`gpllrgkuozytyrmpfwbb` vs. `ujnyioggxipvuxxxcivr`) baut der tatsächliche Render.com-Production-Build? (siehe zentraler Vorbehalt und Gate-Abschnitt oben — Repo-seitig nun vollständig untersucht, verbleibt aber Missing bis im Render-Dashboard geprüft)
2. Zweck/Auftrag von Commit `3cc21fc` ("Option B neuansatz") in negotionationcoach-backend — kein Backlog-/ADR-/Brief-Bezug gefunden.
3. Existiert `GEMINI_API_KEY` noch als (ungenutztes) Supabase-Secret im aktiven Projekt?
4. Exaktes Commit-Datum von `c60c249`/`8cb4f42` (negotiation-buddy chat-Bugfixes) — nicht einzeln nachgezogen, für Timeline nicht entscheidungsrelevant.
5. Ob die in Zusatzfund 1/2 verlorene tier-basierte Modell-Differenzierung ein eigenes Produkt-/Security-Anliegen darstellt (Tier-Value-Versprechen), das separat bewertet werden sollte.
