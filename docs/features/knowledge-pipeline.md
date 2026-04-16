# Feature: Knowledge Candidate Pipeline

**Status:** REMOVED — code removed in RFB-016 (2026-04-16). DB schema retained.
**Original intent:** Continuous learning flywheel — AI-extracted negotiation insights
promoted to a curated knowledge base that enriches future coaching sessions.

---

## What Was Built

### Active before removal

| Component | File | Behaviour |
|---|---|---|
| Tag emission | `negotiation-buddy/supabase/functions/chat/systemPrompt.ts:269,275,280,286` | AI instructed to wrap user insights in `[KNOWLEDGE_CANDIDATE]` tags via Methods 2–4 (opt-in only, max once per session) |
| Tag extraction | `negotiation-buddy/src/hooks/useChat.ts:29–48` | `stripInternalTags()` parses SSE stream for `[KNOWLEDGE_CANDIDATE]` regex matches after each response |
| Local storage | `negotiation-buddy/src/hooks/useChat.ts:169–177` | Appends extracted content to localStorage key `"knowledge_candidates"` as `{ content, timestamp }` objects |

**Note on tag emission:** Tags were emitted only for specific elicitation methods:
- Method 2 — user shares negotiation experience after being asked
- Method 3 — user contradicts a recommendation and explains their reasoning
- Method 4 — user reflects on what made a negotiation succeed
- Constraint: max one knowledge-gathering question per session; opt-in only; identity remains anonymous

### DB schema (retained — not dropped)

Migration: `negotiation-buddy/supabase/migrations/20260309105420_15cf29bb-f885-4dfb-87de-a2bd82f42b97.sql`

```sql
CREATE TABLE public.knowledge_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.user_profiles(id) ON DELETE SET NULL,
  session_id UUID,
  content TEXT NOT NULL,
  framework_tag TEXT,
  category TEXT,
  status public.knowledge_status NOT NULL DEFAULT 'pending',
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ
);

ALTER TABLE public.knowledge_queue ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public insert on knowledge_queue" ON public.knowledge_queue FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public read on knowledge_queue" ON public.knowledge_queue FOR SELECT USING (true);

CREATE TABLE public.knowledge_base (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL,
  framework_tag TEXT,
  category TEXT,
  usage_count INTEGER DEFAULT 0,
  approved_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read on knowledge_base" ON public.knowledge_base FOR SELECT USING (true);
```

**RLS — knowledge_queue:** Public insert + public read — no ownership filter. Any authenticated or anonymous caller can insert or read any row.
**Must be hardened before reactivation** — add `WITH CHECK (auth.uid() = user_id)` on INSERT; add ownership-scoped SELECT.

**RLS — knowledge_base:** Public read only. No write policy — inserts require SERVICE_ROLE_KEY. Correct for a curated table written only by admins.

### Type definitions (retained)
- `negotiation-buddy/src/integrations/supabase/types.ts:17` — auto-generated types for `knowledge_base`
- Same file includes `knowledge_queue` types (auto-generated from live DB schema)

---

## What Was Never Built

| Missing Component | Description |
|---|---|
| Review UI | No component to display accumulated `knowledge_candidates` from localStorage to user or admin |
| Submission flow | No path from localStorage → `knowledge_queue` INSERT; candidates accumulate in browser storage indefinitely |
| Railway endpoint | No `POST /api/knowledge` or equivalent; all DB access for this pipeline is absent from Railway |
| Admin review path | No UI or API for `pending → approved/rejected` status transitions on `knowledge_queue` |
| `knowledge_base` write path | No mechanism to promote approved candidates from `knowledge_queue` to `knowledge_base` |
| `knowledge_base` read path (frontend) | Frontend never reads `knowledge_base` directly; auto-generated types exist but no consuming component |
| `knowledge_status` enum migration | `knowledge_status` enum is referenced by `knowledge_queue.status` — enum origin and values unverified against live DB |

---

## Why Removed

- AI tokens wasted on `[KNOWLEDGE_CANDIDATE]` tag emission (and tag-stripping regex overhead) every chat session with no downstream consumer
- `localStorage.knowledge_candidates` accumulates indefinitely — no TTL, no bound, no reader, no submission path
- `knowledge_queue` table receives zero writes — schema exists but is inert
- Submission path was never built — partial pipeline produces cost with zero benefit
- RLS on `knowledge_queue` is dangerously permissive (public insert, public read) — no cleanup safe to ignore

---

## Rebuild Requirements

To reactivate this feature, build in this order:

### 1. Railway endpoint — `POST /api/knowledge/candidates`
- Auth: `authMiddleware` (user must own the session via `assertSessionOwner`)
- Request body: `{ session_id: string, candidates: Array<{ content: string, framework_tag?: string, category?: string }> }`
- Action: bulk INSERT into `knowledge_queue` with `status='pending'`, `user_id=req.user.id`
- Must replace any direct anon-key Supabase writes — no client-side DB access

### 2. RLS hardening — `knowledge_queue`
- Drop `"Allow public insert on knowledge_queue"` policy
- Add: `CREATE POLICY "Users can insert own candidates" ON knowledge_queue FOR INSERT WITH CHECK (auth.uid() = user_id)`
- Add: `CREATE POLICY "Users can read own candidates" ON knowledge_queue FOR SELECT USING (auth.uid() = user_id)`
- Keep `knowledge_base` public read — correct as-is

### 3. Submission trigger — `useChat.ts` or new hook
- After SSE stream ends and candidates are extracted via `stripInternalTags()`:
  - POST to `POST /api/knowledge/candidates` with the current `session_id`
  - On success: clear `localStorage.knowledge_candidates`
  - On failure: retain in localStorage for retry (with backoff limit)
- Remove the `localStorage.setItem("knowledge_candidates", ...)` accumulation pattern

### 4. Review UI — new page or modal (Lovable)
- Display pending `knowledge_candidates` for the current user before submission
- Allow user to approve/reject their own candidates before they enter the queue
- Alternative: auto-submit all and let admin review only (simpler, less user friction)

### 5. Admin review path — new Railway endpoints + UI
- `GET /api/admin/knowledge/queue` — list pending candidates (admin-only tier gate)
- `PATCH /api/admin/knowledge/candidates/:id` — approve/reject with `reviewed_at` timestamp
- On approve: INSERT into `knowledge_base` (require SERVICE_ROLE_KEY, Railway only)

### 6. `knowledge_base` integration — Layer 2 read path
- Confirm whether Railway Layer 2 already reads `knowledge_base` (not confirmed in current codebase)
- If absent: add query in `src/layer2/knowledgeGraph.ts` or `marketDataResolver.ts`
- Ensure approved knowledge is surfaced in market enrichment context for relevant session types

---

## DB Tables (retained in schema — do not drop)

| Table | Purpose | Current State |
|-------|---------|---------------|
| `knowledge_queue` | Staging area for pending/approved/rejected candidates | Schema exists, zero writes, permissive RLS |
| `knowledge_base` | Curated knowledge available to Layer 2 enrichment | Schema exists, no confirmed readers, public SELECT RLS |

A future rebuild starts from these tables. Do not drop them.

---

## Linked Items

- **RFB-016** — removal item (negotiation-buddy dead-code audit)
- **DC-004** — dead-code entry in `negotiation-buddy/docs/dead-code-candidates.md`
- **shared-context/docs/db-map.md** — `knowledge_queue` marked deprecated
- **negotiation-buddy/supabase/functions/chat/systemPrompt.ts** — tag emission removed in RFB-016
- **negotiation-buddy/src/hooks/useChat.ts** — `stripInternalTags()` + localStorage pattern removed in RFB-016
