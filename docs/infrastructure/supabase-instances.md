# Supabase Instance Map

**Last updated:** 2026-04-21
**Status:** Authoritative — always refer here, never guess

## Production instance — Lovable/Railway shared
- **Project ID:** ujnyioggxipvuxxxcivr
- **URL:** https://ujnyioggxipvuxxxcivr.supabase.co
- **Used by:** Lovable Frontend + Railway Backend (production)
- **JWT authority:** YES — all user JWTs issued here
- **External access:** Only via Lovable SQL Editor or
  Lovable UI — NOT via Supabase CLI or MCP
- **Modify schema via:** Lovable SQL Editor only
- **Tables:**
  - knowledge_base (curated, read-only)
  - knowledge_graph (Layer 2 cache — created 2026-04-21)
  - knowledge_queue
  - negotiation_sessions
  - session_messages
  - team_members, team_training_tasks, teams
  - user_profiles

## Local development instance — negotiationAI
- **Project ID:** ivrfsjxdfzxrimexvoft
- **URL:** https://ivrfsjxdfzxrimexvoft.supabase.co
- **Used by:** Local development only — NOT production
- **Local MCP points to:** THIS instance
- **Supabase CLI linked to:** THIS instance
- **Status:** Empty (0 rows in all tables as of 2026-04-21)
- **Decision pending:** Archive or delete — no active use

## Access matrix

| Tool | ujnyioggxipvuxxxcivr | ivrfsjxdfzxrimexvoft |
|---|---|---|
| Lovable UI | ✅ read/write | ❌ |
| Lovable SQL Editor | ✅ schema changes | ❌ |
| Supabase CLI (db push) | ❌ | ✅ |
| Local MCP | ❌ | ✅ |
| Railway (runtime) | ✅ service_role | ❌ |
| Claude Code MCP | ❌ | ✅ |

## Permanent rules

1. Schema changes to production → Lovable SQL Editor only
2. supabase db push → deploys to ivrfsjxdfzxrimexvoft only
   (local dev, not production)
3. Claude Code MCP → ivrfsjxdfzxrimexvoft only
   (cannot reach production instance)
4. knowledge_graph lives in ujnyioggxipvuxxxcivr
5. Railway SUPABASE_URL must always point to
   ujnyioggxipvuxxxcivr
6. Never assume MCP verification = production verification

## Auth architecture (ARCH-01)
JWT tokens issued by ujnyioggxipvuxxxcivr.
Railway validates tokens from this instance.
Permissive auth in dev: unauthenticated requests
receive tier: privat (middleware.ts).
Option C (single Supabase for everything) deferred
to pre-production release.

Reference: docs/adr/ADR-001-system-boundaries.md
