# BUG-INFRA-01 — Supabase MCP mit falschem Projekt verbunden

**Entdeckt:** 2026-04-27
**Status:** OPEN — MCP noch nicht reconnected
**Klassifikation:** P0 — Infrastruktur
**Impact:** Alle bisherigen MCP-Migrationen und Schema-Abfragen liefen
gegen ivrfsjxdfzxrimexvoft, nicht gegen ujnyioggxipvuxxxcivr (echte App-DB)

## Betroffene Operationen (potenziell falsch applied)
- 20260421000000_create_knowledge_graph.sql → manuell nachgeholt (FU-L2-01 DONE)
- Alle list_tables / execute_sql Ergebnisse aus früheren Sessions
  spiegeln nicht die echte App-DB wider

## Regel ab sofort
Vor jeder MCP-Schema-Operation verifizieren:
mcp list_projects → project_ref muss ujnyioggxipvuxxxcivr sein
Falls nicht: MCP in Claude Code Settings auf korrektes Projekt umstellen.

## Pending
- MCP auf ujnyioggxipvuxxxcivr reconnecten
- Nach Reconnect: CLAUDE.md-Regel updaten
