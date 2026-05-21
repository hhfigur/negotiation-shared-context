# Session Dump — 2026-05-21

Kontext-Reset vor neuem Session-Start. Dieser Dump ist der vollständige Übergabe-Stand.

---

## Was committed / erreicht

### Infrastructure (Breaking Migration)
- **Supabase komplett migriert** von Lovable-managed (`ujnyioggxipvuxxxcivr`) auf eigenes Projekt (`gpllrgkuozytyrmpfwbb`)
- **Render.com Static Site** für Frontend eingerichtet (`negotiation-buddy.onrender.com`)
- **SPA-Routing** via `public/_redirects` (`/* /index.html 200`)
- **CORS** im Backend auf neue Render-URLs erweitert (commit `19c370c`)

### Edge Functions (negotiation-buddy)
- Alle 5 AI-Edge-Functions von Lovable AI Gateway (`ai.gateway.lovable.dev`) auf **Anthropic claude-haiku-4-5** umgestellt
- Streaming: Anthropic SSE → OpenAI-Format transformiert (kein Frontend-Change nötig)
- `GOOGLE_AI_API_KEY` + `RESEND_API_KEY` als Supabase Secrets gesetzt
- Modellnamen bereinigt (gemini-2.5-* → gemini-2.0-flash → claude-haiku)

### Schema-Migrations (Supabase gpllrgkuozytyrmpfwbb)
| Migration | Inhalt |
|---|---|
| 20260515120000 | `negotiation_sessions` fehlende Columns (layer1_result, layer2_result, negotiation_id) + Defaults für title/persona_type |
| 20260519120000 | FK `negotiation_sessions.user_id` von `user_profiles(id)` auf `auth.users(id)` korrigiert |
| 20260519130000 | `session_history` Tabelle erstellt (Backend schreibt dort hin, Migrations hatten nur `session_messages`) |

### Frontend-Fixes (negotiation-buddy)
- **Plan-Trigger**: nutzt `effectiveProgress` statt raw `progressStatus` (Plan triggert jetzt auch bei Canvas-Flow)
- **BATNA aus Chat**: `extractInputs` EF-Call hatte falsches Format → gefixt; `alternatives` → `batna_description` Mapping
- **ZOPA-Rechner**: räumt `missing_fields` für Gegenseite-Felder auf, ruft jetzt `/api/enrich` für kmu/profi
- **handleNewSession**: räumt jetzt vollständig `extractedInputs` + Refs auf (kein Daten-Bleeding zwischen Sessions)
- **Sidebar-Layout**: Tools-Sektion fixiert am unteren Rand (`flex-none`), Sessions-Bereich scrollbar (`flex-1 overflow-y-auto min-h-0`), Timestamps entfernt, kompakteres Layout
- **Marktdaten-Tool**: in Sidebar-Tools hinzugefügt (→ `/strategy`)
- **analyze-progress**: Throttling auf jede 3. AI-Antwort (war jede — Memory-Druck reduziert)
- **planGeneratedRef**: Reset auf `false` bei Fehler (Plan kann jetzt retried werden)

### Backend-Fixes (negotiationcoach-backend)
- JWT `user_metadata.tier = kmu` für Test-User via SQL gesetzt
- MEMORY.md + Working Context in CLAUDE.md ergänzt

### Dokumentation
- `shared-context/MEMORY.md` erstellt
- `negotiationcoach-backend/MEMORY.md` erstellt
- `negotiation-buddy/MEMORY.md` erstellt
- Working Context in alle drei CLAUDE.md-Dateien ergänzt

---

## Offene Entscheidungen (nicht committed)

| Thema | Status | Entscheidung ausstehend |
|---|---|---|
| BATNA-Persistenz | Offen | localStorage für `extractedInputs`? Verloren bei Seitenreload |
| Session-Restore | Offen | Context aus DB laden wenn Session ausgewählt (BATNA, Analyse, etc.) |
| `session_history` vs `session_messages` | Schuld | Backend schreibt `session_history`, Frontend liest `session_messages` — zwei Tabellen, Konsolidierung nötig |
| Layer-2-Diagnose | P2 ausstehend | enrichWithMarketData Qualität noch nicht verifiziert |

---

## Nächster geplanter Schritt (exakt)

**1. Session-Save verifizieren** (höchste Priorität):
- `npm run dev` starten → neue Gehaltsverhandlung → paar Nachrichten schicken
- Kein "Sitzung konnte nicht gespeichert werden"-Toast erwartet
- Falls noch da: Render Backend-Logs prüfen (`negotiationcoach-backend` → Logs in Render Dashboard)

**2. Marktdaten testen**:
- ZOPA-Rechner → Werte eingeben → "ZOPA berechnen" → Strategie-Score öffnen
- Marktdaten-Sektion sollte für kmu-Tier erscheinen

**3. Falls beides grün**: R-2026-09 als Released markieren in `product/releases/current.md`

---

## Dateien aktuell geändert (seit letztem stabilen Stand)

### negotiation-buddy (main)
- `src/pages/Index.tsx` — Plan-Trigger, BATNA-Fix, extractedInputs-Reset, analyze-progress-Throttle
- `src/pages/ZopaCalculator.tsx` — missing_fields-Fix, enrich()-Call
- `src/components/SessionSidebar.tsx` — komplettes Layout-Rewrite (Tools fixiert, Sessions scrollbar)
- `supabase/config.toml` — project_id auf gpllrgkuozytyrmpfwbb
- `supabase/functions/chat/index.ts` — Anthropic + SSE-Transform
- `supabase/functions/analyze-progress/index.ts` — Anthropic, BATNA-Prompt verstärkt, slice(-20)
- `supabase/functions/generate-plan/index.ts` — Anthropic
- `supabase/functions/analyze-document/index.ts` — Anthropic + SSE-Transform
- `supabase/functions/summarize-session/index.ts` — Anthropic
- `supabase/migrations/` — 3 neue Migrations (20260515, 20260519x2)
- `public/_redirects` — SPA-Routing für Render
- `MEMORY.md` + `CLAUDE.md` — Working Context

### negotiationcoach-backend (main)
- `src/api/routes.ts` — CORS für Render-URLs
- `MEMORY.md` + `CLAUDE.md` — Working Context

---

## Ausstehende Acceptance Criteria (R-2026-09)

| Kriterium | Status |
|---|---|
| Verhandlungsplan erscheint nach vollständigem Chat-Flow | ✅ gefixt (effectiveProgress-Trigger) |
| Market-Data-Werte im UI sichtbar | ⚠️ partial — enrich() wird aufgerufen, aber Anzeige muss verifiziert werden |
| TypeCheck negotiation-buddy: 0 Fehler | ✅ verifiziert |
| Session-Save ohne Fehler | ⚠️ session_history-Migration deployed, Verifikation ausstehend |
| BATNA aus Chat erkannt | ⚠️ EF-Fix deployed, aber Persistenz über Reload fehlt |

---

## Kontext für nächste Session

```
TARGET REPO: negotiation-buddy (für Verifikation)
TARGET REPO: shared-context (für Doku-Updates)
```

Kritische Info: Das neue Supabase-Projekt `gpllrgkuozytyrmpfwbb` ist live. Der Test-User `hhfigur@gmx.net` hat `persona_type=kmu` in `user_profiles` UND `tier=kmu` in JWT `user_metadata`. Nach `/clear` kein neues Supabase-Setup nötig.
