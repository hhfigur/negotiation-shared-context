# RLS Audit 2026 — NC-SEC-01

**Datum:** 2026-04-30
**Status:** COMPLETED
**Durchgeführt:** Manuell via Lovable SQL Editor gegen ujnyioggxipvuxxxcivr

## Ergebnis

Alle 9 Tabellen haben RLS aktiv. Alle kritischen Tabellen haben korrekte Policies.

| Tabelle | RLS | Policies | Status |
|---|---|---|---|
| negotiation_sessions | ✅ | 4 — user_id = auth.uid() | OK |
| teams | ✅ | 5 — admin + member | OK |
| team_members | ✅ | 3 — admin + member | OK |
| team_training_tasks | ✅ | 4 — admin + member | OK |
| session_messages | ✅ | SELECT via owns_session(), INSERT | OK |
| user_profiles | ✅ | SELECT/INSERT/UPDATE auf user_id | OK |
| knowledge_base | ✅ | Public read | OK — gewollt |
| knowledge_graph | ✅ | service_role INSERT, authenticated SELECT | OK |
| knowledge_queue | ✅ | Public read + insert | ⚠️ public INSERT ohne Auth — separates Review |

## Korrekturen

- session_history existiert nicht — Tabelle heißt session_messages
- owns_session() Funktion existiert und wird in session_messages genutzt
- Untracked Migration 20260403120000_add_team_rls_policies.sql committed (e74b49d)

## VG-01 / VG-02

- VG-01 (RLS auf allen Tabellen): RESOLVED
- VG-02 (owns_session Gap): RESOLVED — Funktion existiert und ist aktiv

## Offene Punkte

- knowledge_queue public INSERT ohne Auth — kein VG-01/VG-02 Scope, separates Review nötig
