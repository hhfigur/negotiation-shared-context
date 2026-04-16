# Wave 1 Completion Gate — Formal Closure Checklist

> **Status:** CLEARED | **Type:** Governance | **Created:** 2026-04-16
> **Path:** `shared-context/docs/audits/wave1-completion-gate.md`

**Purpose:** Formal gate for closing Wave 1 of the NegotiationCoach AI refactor backlog. Documents every item's status at closure, open carry-forward items, and post-gate actions.

---

## Wave 1 Scope

Wave 1 covers all refactor items RFB-001 through RFB-036 plus Active Blocker AB-001. It represents the initial architectural debt clearance: auth enforcement, boundary violations, contract gaps, dead code, and tier system alignment.

**Wave 1 is considered closed when:**
1. All P0 items are DONE or DEFERRED with documented rationale
2. All P1 items are DONE, DEFERRED, or blocked only by a documented Verification Gap with an owner
3. No unknown-status items remain in the Summary Index
4. All hash placeholders are either resolved or confirmed cosmetic (work done)
5. `wiki/index.md` open-items table reflects current reality
6. This gate document is committed to `shared-context`

---

## Gate Status by Priority

### P0 Items

| ID | Title | Status |
|----|-------|--------|
| RFB-001 | Railway authMiddleware 401 enforcement | ✅ DONE `fd68e1e` |
| RFB-003 | Move team CRUD to Railway API | ✅ DONE Phase A `0b10d9c` + Phase B Lovable 2026-04-08 |
| RFB-004 | Move session/message writes to Railway API (all phases) | ✅ DONE Phase A `2c51cb4`, Phase B `2415f72`, Phase C backend `6021665`, Phase C Lovable 2026-04-10, RFB-004-C `243c02d` |
| RFB-005 | Fix CORS wildcard override | ✅ DONE `e00e400` |
| RFB-029 | negotiation_sessions missing analysis columns | ✅ DONE `f759c18` |
| RFB-031 | Fix session_history table name in sessionRoutes.ts | ✅ DONE `2c51cb4` |
| RFB-032 | Stripe webhook handler — POST /api/webhooks/stripe | ⏸ DEFERRED — Stripe not live in production; unblocked by RFB-036 (done); carry into Wave 2 |
| AB-001 | Railway SUPABASE_URL placeholder fixed | ✅ DONE 2026-04-08 |

### P1 Items

| ID | Title | Status |
|----|-------|--------|
| RFB-002 | Verify/harden Supabase RLS for team admin | ✅ DONE — commit hash placeholder `<hash>` is cosmetic; work confirmed done |
| RFB-006 | Unify dual Layer 1 implementations | ⏸ OPEN — blocked on VG-06 (architecture decision unresolved); carry into Wave 2 |
| RFB-007 | Unify three incompatible tier systems | ✅ DONE Step A `1c68185`, Step B `6ba5710`, Step C re-scoped → RFB-036 |
| RFB-008 | Eliminate parallel type maintenance | ✅ DONE `9c51a43` |
| RFB-009 | Propagate actual user tier to Edge Function | ✅ DONE `d90d5c0` |
| RFB-010 | Verify Stripe webhook tier update path | ✅ INVESTIGATED 2026-04-09 — handler absent; spawned RFB-032 |
| RFB-011 | Integrate modelRouter into /api/chat and /api/plan | ✅ DONE `60848db` |
| RFB-012 | Resolve missing user_profiles row on signup | ✅ DONE 2026-04-03 (Lovable trigger on auth.users insert) |
| RFB-024 | Fix parsePlanResponse() silent fallback | ✅ DONE `fd031cc` |
| RFB-025 | Fix parseChatResponse() silent fallback | ✅ DONE `fe961ee` |
| RFB-030 | Add RLS policies for negotiation_sessions and session_history | ✅ DONE 2026-04-09 (pre-existing RLS confirmed; re-scoped) |
| RFB-033 | JWT auth + tier gate for generate-plan Edge Function | ✅ DONE `477df3d` |
| RFB-035 | Replace anon key with user JWT for all EF calls | ✅ DONE via RFB-035A + RFB-035B |
| RFB-035A | summarize-session auth guard + Index.tsx Change C | ✅ DONE `ffe0274` |
| RFB-036 | Migrate subscription_tier enum to Railway Tier values | ✅ DONE `a28d28c` (2026-04-16) |

### P2 Items

| ID | Title | Status |
|----|-------|--------|
| RFB-013 | Centralize token accessor in useAuth.tsx | ✅ DONE `c507353` |
| RFB-014 | Fix session message fire-and-forget persistence | ✅ DONE 2026-04-03 |
| RFB-015 | Add TTL/versioning to localStorage state | ✅ DONE 2026-04-03 |
| RFB-016 | Complete or remove knowledge candidate pipeline | ✅ DONE `a647d5a` |
| RFB-017 | Deduplicate password validation | ✅ DONE `48d0edc` |
| RFB-026 | Repair broken claudeClient import in batnaDetector.ts | ⏸ OPEN — blocked on RFB-006; carry into Wave 2 |
| RFB-028 | Enforce max_members in POST /api/teams/:id/members | ✅ DONE `402ee63` |
| RFB-035B | analyze-progress + analyze-document auth guards + Index.tsx Changes A+B | ✅ DONE `c60c419` |

### P3 Items

| ID | Title | Status |
|----|-------|--------|
| RFB-018 | Rename webSearch.ts to reflect actual behaviour | ✅ DONE `675cc21` |
| RFB-019 | Consolidate dual toast systems | ✅ DONE `056e672` |
| RFB-020 | Decompose Index.tsx god component — Phase 1 | ✅ DONE `0cd7a01` |
| RFB-020b | Extract useGuidedFlow hook from Index.tsx | ✅ DONE `64b7432` |
| RFB-020c | Extract useProgressEngine hook from Index.tsx | ✅ DONE — commit hash placeholder `[RFB-020c hash]` is cosmetic; work confirmed done |
| RFB-021 | Wire Zod for API input validation | ✅ DONE `5eed133` |
| RFB-022 | Fix broken test suite — align with Railway schema | ✅ DONE `ccc4460` |
| RFB-023 | Remove dead useChatApi export | ✅ DONE `aa703bd` |
| RFB-027 | Repair npm test runner — install Jest / wire ts-node | ✅ DONE `0665780` |
| RFB-034 | Annotate Railway /api/plan + generatePlan() as ADR-005 migration targets | ✅ DONE `f5e8190` / `deebb5a` |

---

## Verification Gaps at Gate

| VG-ID | Question | Status at Gate |
|-------|----------|----------------|
| VG-01 | Supabase RLS on `teams`/`team_members` — does `admin_user_id = auth.uid()` enforce? | ⚠️ UNKNOWN — RFB-002 confirmed at DB level but not independently verified in prod |
| VG-02 | Supabase RLS on `negotiation_sessions` — cross-user read prevention with anon_key? | ⚠️ UNKNOWN |
| VG-03 | Stripe webhook: where does it update `user_metadata.tier`? Active in production? | ⚠️ UNKNOWN — Stripe not live; deferred with RFB-032 |
| VG-04 | What creates the initial `user_profiles` row on signup? | ✅ RESOLVED — Lovable trigger on `auth.users` insert (RFB-012) |
| VG-05 | Tier enforcement in Edge Functions? | ✅ RESOLVED 2026-04-09 — tier is decorative prompt metadata only; VG-05-A logged (no JWT auth, severity High, open) |
| VG-06 | Dual Layer 1: retire Edge Function engine or unify with Railway? | ⏸ OPEN — architectural decision required; blocks RFB-006, RFB-026 |
| VG-07 | Which chat path for tier-paying users? | ✅ RESOLVED 2026-04-09 — ADR-004: Edge Function for all tiers; tier enforcement inside EF |

---

## Open Items Carrying into Wave 2

| ID | Priority | Reason |
|----|----------|--------|
| RFB-006 | P1 | Blocked on VG-06. Requires ADR before work can begin. |
| RFB-026 | P2 | Blocked on RFB-006. Sequenced behind it. |
| RFB-032 | P0 | Stripe not live. First Wave 2 item activated once Stripe goes live. |
| VG-06 | — | No architectural decision yet on dual Layer 1. Wave 2 kickoff action. |
| VG-01 | Critical | RLS enforcement unconfirmed in prod. Wave 2-A audit target. |
| VG-02 | High | Cross-user read prevention unconfirmed. Wave 2-A audit target. |
| VG-05-A | High | No JWT auth in Edge Functions — tier enforcement is decorative. Needs hardening. |

---

## Hash Placeholders — Cosmetic, Non-Blocking

The following items have placeholder hashes. Work is confirmed done; placeholders are a tracking artifact.

| ID | Placeholder | Resolution |
|----|-------------|------------|
| RFB-002 | `<hash>` | `git log --oneline` in relevant repo; grep for RLS migration commit |
| RFB-020c | `[RFB-020c hash]` | `git log --oneline` in negotiation-buddy; grep for useProgressEngine |

These do not block the gate or Wave 2.

---

## Gate Clearance Assessment

| Criterion | Result |
|-----------|--------|
| All P0 items DONE or DEFERRED with documented rationale | ✅ Clear |
| All P1 items DONE, DEFERRED, or blocked by documented VG | ✅ Clear — RFB-006 blocked by VG-06 (documented) |
| All P2 items DONE or blocked with documented dependency | ✅ Clear — RFB-026 sequenced behind RFB-006 |
| All P3 items DONE | ✅ Clear |
| No unknown-status items | ✅ Clear |
| Hash placeholders are cosmetic (work confirmed done) | ✅ Clear |
| `wiki/index.md` reflects current open items | ✅ Clear |
| Session log updated | ✅ Clear |

**Gate verdict: CLEARED — 2026-04-16**

Wave 1 is formally closed. Items RFB-006, RFB-026, RFB-032, and verification gaps VG-01, VG-02, VG-05-A, and VG-06 carry forward into Wave 2.

---

## Post-Gate Actions

1. **VG-06 ADR** — Schedule architecture decision session: retire or unify the Edge Function Layer 1 engine. Required before Wave 2 work on RFB-006 begins.
2. **VG-01 / VG-02 audit** — Verify Supabase RLS in production for teams and negotiation_sessions. High/Critical risk that has been open since Wave 1 audit.
3. **VG-05-A hardening** — Plan JWT auth enforcement in Edge Functions. Severity High; no current blocker.
4. **RFB-032 readiness** — Monitor Stripe go-live; activate RFB-032 immediately once confirmed.
5. **Hash placeholder cleanup** — Resolve RFB-002 and RFB-020c hashes at Wave 2 kickoff or first relevant session.
6. **Delivery Controller setup** — See `docs/governance/delivery-controller-setup.md`.
