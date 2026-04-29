# Brief: NC-SEC-01 — VG-01/VG-02: RLS-Audit in Produktion

**Status:** Qualified
**Release:** TBD (Wave 2 — Tier 1)
**Typ:** Enabler
**Priorität:** P0 — Critical/High Risk aus Wave-1-Audit
**Erstellt:** 2026-04-29

---

## Lagebeurteilung

VG-01 und VG-02 wurden in Wave 1 als Critical bzw. High eingestuft aber
nie in Produktion verifiziert. Die RLS-Policies existieren als Migrations-
dateien — ob sie in der laufenden Supabase-Instanz korrekt greifen,
ist Inferred, nicht Observed.

**VG-01 (Critical):** Verhindern Supabase RLS-Policies auf `teams` und
`team_members`, dass Nicht-Admins Admin-Aktionen ausführen?

**VG-02 (High):** Verhindert Supabase RLS auf `negotiation_sessions`,
dass User fremde Sessions lesen — auch mit anon_key?

---

## Ziel / Outcome

Observed (nicht Inferred) wissen, ob RLS in Produktion korrekt durchgesetzt wird.
Jeden kritischen Befund direkt im selben Commit als Migration schließen.

---

## Problem

- RLS-Policies existieren als Code — ob sie aktiv und korrekt sind ist unbekannt
- Bei Fehler: Nutzer können fremde Verhandlungsdaten lesen oder als Admin agieren
- Kein Telemetrie-Signal das unbefugten Zugriff aufdecken würde

---

## Affected Repos

- `shared-context` (Audit-Dokument: `docs/audits/rls-audit-2026.md`)
- `negotiationcoach-backend` (falls Migrations-Fix nötig: `supabase/migrations/`)

---

## Scope

### Phase 1 — Audit (READ ONLY)
Supabase SQL-Queries gegen die live Instanz `ujnyioggxipvuxxxcivr`:

```sql
-- VG-01: Prüfen ob admin_user_id RLS auf teams korrekt greift
SELECT * FROM teams WHERE admin_user_id != auth.uid();
-- VG-02: Prüfen ob user_id RLS auf negotiation_sessions korrekt greift
SELECT * FROM negotiation_sessions WHERE user_id != auth.uid();
-- Policy-Übersicht
SELECT schemaname, tablename, policyname, cmd, qual
FROM pg_policies
WHERE tablename IN ('teams', 'team_members', 'negotiation_sessions');
```

Klassifizierung: Observed / Inferred / Missing für jeden Befund.

### Phase 2 — Fix (nur wenn Lücke gefunden)
Falls RLS-Lücke bestätigt: neue Migration in `negotiationcoach-backend/supabase/migrations/`
mit korrigierter Policy. Manual apply via Lovable SQL-Editor.

---

## Non-Goals

- Neue Features in Teams oder Sessions
- Änderungen an Frontend-Komponenten
- RLS für andere Tabellen als teams, team_members, negotiation_sessions

---

## Acceptance Criteria

1. Audit-Dokument `docs/audits/rls-audit-2026.md` existiert mit Observed-Befunden
2. VG-01: RLS auf `teams.admin_user_id` ist Observed (greifen oder Lücke dokumentiert)
3. VG-02: RLS auf `negotiation_sessions.user_id` ist Observed
4. Falls Lücke: Migration existiert und ist als applied markiert
5. Beide VGs in wave1-completion-gate.md und source-of-truth-matrix.md als RESOLVED gestempelt

---

## Telemetry / Measurement

Nicht direkt messbar nach Fix. Sicherheits-Audit ist Pass/Fail.
NC-TELEMETRY wird danach Zugriffsmuster observierbar machen.

---

## Risks / Open Questions

| Risiko | Bewertung |
|---|---|
| MCP Supabase zeigt falsches Projekt — L-004 | **KRITISCH** — MCP NICHT nutzen. Nur direkter SQL-Editor in Lovable oder Dashboard |
| Audit findet kritische Lücke die sofortigen Hotfix braucht | Akzeptiert — Phase 2 ist vorbereitet |
| Lovable-verwaltetes Supabase: externe Migration-Anwendung beschränkt | Bekannt — Manual apply via Lovable SQL-Editor wie bei RFB-036 |

**Hinweis zur Tooling-Einschränkung (L-004):**
MCP Supabase ist mit dem falschen Projekt verbunden (`ivrfsjxdfzxrimexvoft`).
Alle Audit-Queries müssen über das Lovable-Dashboard oder einen direkten
Supabase-SQL-Editor-Zugang zu `ujnyioggxipvuxxxcivr` ausgeführt werden.
