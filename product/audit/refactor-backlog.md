# Audit Refactor Backlog (PM-View)

## Source of Truth
The complete technical backlog with all 36 items, evidence, and 
analysis lives in:
→ `docs/audits/refactor-backlog.md`

This file is the operative PM-view only: release assignment, 
priority, and status for planning purposes.
Do NOT maintain a parallel item list here.
All item additions, removals, or technical changes go into 
`docs/audits/refactor-backlog.md`.

## Active Items (Wave 1 Carry-Forward → R-2026-05)

| ID | RFB-Ref | Title | Priority | Status | Blocks |
|---|---|---|---|---|---|
| AR-006 | RFB-006 | ADR-007 schreiben — VG-06 Dual Layer 1 — ✅ Released `9c6f1f2` | P0 | Released | — |
| NC-L2-FIX | — | Layer 2 Market Data Diagnose + Reparatur — ✅ DONE `339f136` | P0 | Released | — |
| AR-026 | RFB-026 | batnaDetector Edge Function reparieren — ✅ Dropped (superseded by ADR-007-A) | P0 | Dropped | — |
| AR-032 | RFB-032 | Stripe Webhook Handler | P2 | Paused | Stripe not live |
| AR-016a | RFB-016a | Knowledge Pipeline | P2 | Paused | ADR required |

## Priority legend
- P0: release-blocking or breaks active tier promise
- P1: release-relevant, should be in current release
- P2: backlog, next release candidate
- P3: cosmetic, no functional impact

## Rules
- Status changes go here AND in `product/feature-register.md`
- New items go into `docs/audits/refactor-backlog.md` first, 
  then get an AR-xxx ID here when they become release-relevant
- Last synced with `docs/audits/refactor-backlog.md`: 2026-04-20
