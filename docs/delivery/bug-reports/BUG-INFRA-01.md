# BUG-INFRA-01 — Supabase MCP mit falschem Projekt verbunden

**Entdeckt:** 2026-04-27
**Geschlossen:** 2026-04-27
**Status:** WONT-FIX — strukturelle Einschränkung, nicht behebbar
**Klassifikation:** P0 — Infrastruktur

## Root Cause

Der Supabase MCP ist über den persönlichen Supabase-Account authentifiziert.
Dieser Account hat nur Zugriff auf `ivrfsjxdfzxrimexvoft` (negotiationAI — ungenutzt).

Das eigentliche App-Projekt `ujnyioggxipvuxxxcivr` wird von **Lovable** verwaltet.
Lovable-verwaltete Projekte sind für externe Supabase-Accounts nicht zugänglich.
Eine Reconnection oder Member-Einladung ist nicht möglich.

## Impact

| Operation | Status |
|---|---|
| `apply_migration` via MCP | Trifft falsches Projekt — NIEMALS verwenden |
| `execute_sql` via MCP | Trifft falsches Projekt — NIEMALS verwenden |
| `list_tables` via MCP | Trifft falsches Projekt — NIEMALS verwenden |
| `list_projects` via MCP | Gibt nur `ivrfsjxdfzxrimexvoft` zurück — wertlos |

## Betroffene vergangene Operationen

- `20260421000000_create_knowledge_graph.sql` → wurde gegen falsches Projekt applied.
  Manuell nachgeholt via Lovable (FU-L2-01 DONE).
- Alle `list_tables` / `execute_sql` Ergebnisse aus früheren Sessions sind ungültig.

## Permanente Workarounds (aktiv ab 2026-04-27)

| Bedarf | Workaround |
|---|---|
| Schema-Änderungen | Migration-Dateien im Repo — Lovable/Dashboard wendet sie an |
| Schema-Inspektion | Migration-Files + TypeScript-Interfaces lesen |
| Datenzustand prüfen | Render.com Logs oder API Smoke-Tests |
| MCP DB-Operationen | Verboten. Keine Ausnahmen. |

## Lesson

Dokumentiert in `negotiationcoach-backend/tasks/lessons.md` als **L-004** (aktualisiert 2026-04-27).
