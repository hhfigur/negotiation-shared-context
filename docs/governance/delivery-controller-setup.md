# Delivery Controller — Setup Package

> **Status:** Active | **Type:** Governance | **Created:** 2026-04-16
> **Path:** `shared-context/docs/governance/delivery-controller-setup.md`

**Purpose:** Complete setup package for a new Claude.ai Delivery Controller project. Used when handing off from Wave 1 closure to Wave 2 execution.

---

## Was ist der Delivery Controller?

Der Delivery Controller ist ein Claude.ai Project das die **operative Ausführungssteuerung** für laufende Refactor-Wellen übernimmt. Er ist nicht die Architektur-Steuerzentrale (das bleibt `App Governance & Audit`) — er ist der Executor, der:

- den aktuellen Backlog-Status kennt
- Claude Code Sessions initiiert und brieft
- Ergebnisse reviewed und Commits veranlasst
- den Wave-Fortschritt trackt und im session-log dokumentiert

---

## Wave 1 Gate Reference

Vor Wave 2 muss Wave 1 formal geschlossen sein:

→ [`docs/audits/wave1-completion-gate.md`](../audits/wave1-completion-gate.md)

**Gate verdict:** CLEARED — 2026-04-16
**Carry-forward items:** RFB-006, RFB-026, RFB-032, VG-01, VG-02, VG-05-A, VG-06

---

## Transition Knowledge Package

What the Delivery Controller must know before the first Wave 2 session.

### System State at Handoff (2026-04-16)

**Three repos:**

| Repo | Path | Role |
|------|------|------|
| `negotiation-buddy` | `/Users/maikfigur/app-workspace/negotiation-buddy/` | React SPA + Supabase Edge Functions (Lovable-managed) |
| `negotiationcoach-backend` | `/Users/maikfigur/app-workspace/negotiationcoach-backend/` | Railway Express API, Layer 1/2 algorithms |
| `shared-context` | `/Users/maikfigur/app-workspace/shared-context/` | Docs only — this repo |

**Auth model:**
- Supabase issues JWTs on login
- Railway `authMiddleware` validates JWTs and enforces 401 (RFB-001, done)
- Edge Functions receive JWT in `Authorization` header; enforcement is in-EF

**Tier system (post-ADR-006, 2026-04-16):**
- DB enum `subscription_tier`: `free` | `privat` | `kmu` | `profi`
- Tier is stored in `user_profiles.subscription_tier`
- Tier is read and passed as prompt metadata — no hard model gates (VG-05-A, severity High, open)

**Open items at Wave 2 start:**

| ID | Priority | Title | Blocker |
|----|----------|-------|---------|
| RFB-032 | P0 | Stripe webhook handler | Stripe not live in production |
| RFB-006 | P1 | Unify dual Layer 1 implementations | VG-06 — architecture decision required |
| RFB-026 | P2 | Repair batnaDetector.ts claudeClient import | RFB-006 |
| VG-06 | — | Dual Layer 1 architecture decision | Needs ADR before work begins |
| VG-01 | Critical | Supabase RLS on teams — admin enforcement unconfirmed | Audit task |
| VG-02 | High | Supabase RLS on negotiation_sessions — cross-user read | Audit task |
| VG-05-A | High | No JWT auth in Edge Functions — tier enforcement decorative | Hardening task |

**Decided ADRs:**

| ADR | Decision |
|-----|---------|
| ADR-001 | System boundaries: browser vs Railway vs Supabase |
| ADR-002 | Data ownership: write path rules |
| ADR-003 | AI provider split: Lovable/Gemini for EFs, Anthropic for Railway |
| ADR-004 | Edge Function is canonical chat path for all tiers |
| ADR-005 | Railway /api/plan is long-term path; generate-plan EF is temporary |
| ADR-006 | subscription_tier enum aligned to Railway Tier labels |

---

## Grundinstruktion

Paste the following as **Project Instructions** in the new Claude.ai Delivery Controller project:

---

Du bist der NegotiationCoach AI Delivery Controller für Wave 2.

Dein Auftrag ist operative Ausführungssteuerung — kein neues Design, kein Big-Bang-Refactor. Du arbeitest den Backlog ab.

**System-Kontext**

Drei Repos: negotiation-buddy (React SPA + Supabase EFs), negotiationcoach-backend (Railway Express), shared-context (Docs only).

Alle Architekturentscheidungen sind in shared-context dokumentiert (ADR-001 bis ADR-006).

**Offene Wave-2-Items bei Start:**
- RFB-032 (P0) — Stripe webhook; wartet auf Stripe go-live
- RFB-006 (P1) — Layer 1 Unification; wartet auf VG-06 ADR
- RFB-026 (P2) — batnaDetector.ts; wartet auf RFB-006
- VG-01/VG-02 — RLS-Audit; keine Blocker
- VG-05-A — Tier enforcement hardening; keine Blocker

**Wie du arbeitest**

1. Vor jedem Task: wiki/index.md und refactor-backlog.md auf aktuellen Stand lesen
2. Claude Code Sessions starten mit: `cd <repo> && claude --add-dir ../shared-context`
3. Nach jedem abgeschlossenen Task: `/close-task` aufrufen (Steps A–J)
4. Nie selbst committen — immer die git-Befehle ausgeben und auf User-Ausführung warten
5. Keine Architekturentscheidungen ohne ADR in shared-context/docs/decision-log/

**Was du nicht tust**

- Kein Code schreiben außerhalb von explizit briefed Tasks
- Keine neuen Features
- Keine Annahmen über offene Verification Gaps — offen lassen bis geklärt
- Keine Änderungen an shared-context Docs ohne expliziten Auftrag

---

## Launch Workflow

### Session starten

```bash
# Für Backend-Tasks (aus negotiationcoach-backend):
cd negotiationcoach-backend
claude --add-dir ../shared-context

# Für Frontend-Tasks (aus negotiation-buddy):
cd negotiation-buddy
claude --add-dir ../shared-context

# Für Docs-only-Tasks (aus shared-context):
cd shared-context
claude --add-dir ../negotiationcoach-backend
# oder:
claude --add-dir ../negotiation-buddy
```

### Vor jedem Task

1. `wiki/index.md` lesen — welche Items sind offen?
2. Entry Body des Ziel-RFB in `refactor-backlog.md` lesen
3. Blocker-Status prüfen
4. Standard Verification Steps ausführen (`npx tsc --noEmit`, `npm test`)

### Nach jedem Task

```
/close-task ITEM_ID=<ID> COMMIT=<hash> REPO=<repo> DATE=<YYYY-MM-DD>
```

Führt automatisch aus (Steps A–J):
- Entry body DONE stamp
- Summary Index ✅ stamp
- `wiki/index.md` open items row removal
- `wiki/session-log.md` append
- Two-commit git commands output

---

## Wave 2 Execution Order

Empfohlene Sequenz basierend auf Blockern:

```
Phase 2-A — Unblocked (start immediately):
  ├─ VG-01 + VG-02: Supabase RLS audit (teams, negotiation_sessions)
  └─ VG-05-A: Plan tier enforcement hardening in EFs

Phase 2-B — ADR required first:
  ├─ VG-06 ADR: Retire or unify EF engine (decision session)
  └─ RFB-006: Unify dual Layer 1 (after VG-06 resolved)
       └─ RFB-026: Repair batnaDetector.ts (after RFB-006)

Phase 2-C — External trigger:
  └─ RFB-032: Stripe webhook (activate once Stripe goes live)
```

---

## Templates

### Task Brief

```
TASK BRIEF — <RFB-ID>: <title>
────────────────────────────────
Repo:       <negotiationcoach-backend | negotiation-buddy | shared-context>
Priority:   <P0 | P1 | P2 | P3>
Blocker:    <none | <ID>>
Depends on: <none | <ID>>

Scope:
- <bullet 1>
- <bullet 2>

Out of scope:
- <what NOT to change>

Verification:
- npx tsc --noEmit
- npm test 2>&1 | tail -20
- <specific check>

Docs to update:
- <list or "none">

Close with:
/close-task ITEM_ID=<ID> COMMIT=<hash> REPO=<repo> DATE=<YYYY-MM-DD>
```

### ADR Request

```
ADR REQUEST — VG-<ID>: <architectural question>
────────────────────────────────────────────────
Question:
  <the decision to make>

Option A: <approach> — <trade-off>
Option B: <approach> — <trade-off>

Blocked items: <RFB-IDs that cannot start until decided>
Risk if deferred: <consequence>
Decide by: <date or external trigger>
Owner: <who makes the call>
```

### Session Log Entry

Session-log entries are written automatically by `/close-task` Step J.
For maintenance sessions (not tied to an RFB), append manually to `wiki/session-log.md`:

```markdown
## [YYYY-MM-DD] <type> | <title>

- <bullet: what changed>
- <bullet: what was decided>
- Next: <what comes next>
```

Types: `refactor` | `audit` | `wiki` | `maintenance`

---

## Key Document Map

| Document | When to read |
|----------|-------------|
| `wiki/index.md` | Start of every session — open items and session log pointer |
| `wiki/session-log.md` | For session history and recent decisions |
| `docs/audits/refactor-backlog.md` | Entry bodies for context before any task |
| `docs/audits/wave1-completion-gate.md` | Wave 1 closure record and carry-forward rationale |
| `docs/decision-log/ADR-*.md` | Architectural decisions — read before touching bounded context |
| `docs/system-overview.md` | Runtime map, auth flow, data paths |
| `docs/bounded-contexts.md` | Ownership and violation history by context |
| `docs/contracts/frontend-backend.md` | API contracts and known type drift |
| `.claude/skills/close-task/SKILL.md` | Close task procedure Steps A–J |
