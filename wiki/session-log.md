# NegotiationCoach AI — Control Tower Session Log

Append-only log of every Control Tower session. One entry per session. Format: `## [YYYY-MM-DD] <type> | <title>`. Types: `refactor | audit | wiki | maintenance`.

---

## [2026-04-15] maintenance | Backlog sync and hash resolution

- Synced refactor-backlog.md Summary Index to current state (commit `0b4c2d0`) — RFB-004, RFB-007, RFB-032, RFB-033–036 body entries and Dependency Graph added
- Resolved three `<hash>` placeholders: RFB-020 → `0cd7a01`, RFB-035A → `ffe0274` (commit `6d7d37a`)
- RFB-033 hash left as `<hash>` — generate-plan JWT auth changes were in the working tree, not yet committed at resolution time
- Next: wiki structure setup

## [2026-04-15] wiki | Initial wiki structure created

- Created `shared-context/wiki/` with `index.md`, `architecture.md`, `session-log.md`
- Wiki compiled from existing ADRs, bounded-contexts, source-of-truth-matrix, auth-permission-map, service-catalog
- Captures all six open backlog items in index.md; architecture.md summarizes all six ADRs
- Next: START NEXT REFACTOR when ready

## [2026-04-16] refactor | RFB-036 closed

- RFB-036 closed — Migrate subscription_tier DB enum to Railway Tier values, commit a28d28c

## [2026-04-16] refactor | RFB-004-C closed

- RFB-004-C closed — Add DB-level message count constraint to session_history, commit 243c02d

## [2026-04-16] refactor | RFB-016 closed

- RFB-016 closed — Remove knowledge candidate extraction pipeline (systemPrompt.ts + useChat.ts), commit a647d5a

## [2026-04-16] maintenance | Light audit pass — revalidate shared-context docs post Wave 1

- current-state-report.md: CRIT-02, CRIT-03, HIGH-01 (partial), HIGH-02, MED-04, LOW-01, LOW-02, LOW-05 stamped RESOLVED
- bounded-contexts.md: BC-03 Violations updated (RFB-004-C DONE); BC-05 Canonical Owner — VIOLATION label removed
- source-of-truth-matrix.md: Entity 4 Business Logic Owner updated (non-atomic → atomic trigger)
- auth-permission-map.md: Section 2.3 RFB-035 resolved; Section 4.2/4.3 modelRouter bypass note removed (RFB-011)
