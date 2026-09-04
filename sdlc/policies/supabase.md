---
artifact: policy
policy_id: POL-SUP-001
title: Supabase and Data Boundary Policy
status: draft
owner: "<DATA_PLATFORM_OWNER>"
version: 0.2.0
approved_by: null
approved_date: null
review_date: null
source_authorities: []
scope: "The single Supabase project shared by the frontend and backend, its clients, migrations, and integrations"
---

# Supabase and Data Boundary Policy

> This draft is not normative until approved. Negotiation AI uses exactly one active Supabase
> project, intentionally shared by the frontend and backend (confirmed project-owner fact,
> 2026-09-04). This is not a defect and this policy does not propose separating it. Its purpose
> is to make the ownership, access-control, migration-coordination, and audit boundaries the
> shared model needs explicit and testable — the controls below assess governance *within* the
> shared project, not whether it should be split.

## Objectives

Make project ownership, schema and table ownership, authorization, migration coordination,
generated types, environment mapping, and cross-repository access to the shared project explicit
and testable.

## Candidate mandatory controls

1. Record the owning repository or shared ownership for each schema, table, function, storage
   bucket, auth flow, Edge Function, and generated client in the one active Supabase project —
   do not leave ownership implicit because the project is shared.
2. Treat the shared project as a single governance surface with explicit sub-boundaries, not as
   two projects: for every change, state (a) RLS enforcement on every table touched, (b) the
   authentication/JWT boundary between the frontend's and backend's independent consumption of
   that identity, (c) service-role key custody — must stay backend-only, never present in
   frontend code, and (d) which repository has write/migration authority for the affected
   schema or table.
3. Coordinate migrations across both repositories against the one live project: each repository
   currently maintains its own `supabase/migrations/` directory targeting the same project, so a
   migration applied from one repository's CLI session must not silently drift from the other
   repository's migration history for the same schema. Define either a single designated
   migration-apply path or an explicit reconciliation check before any `db push`, and apply
   changes through a verified non-production-first process where one exists.
4. Treat Row Level Security and server-side authorization as explicit requirements for every
   table the shared project exposes; do not rely on client-side filtering, and do not assume RLS
   coverage is complete just because the project is shared and "someone" must have set it up.
5. Keep service-role key custody backend-only and out of frontend clients, source, logs,
   prompts, and evidence in either repository.
6. Keep generated types synchronized through the approved generation command in each consuming
   repository; do not hand-edit generated outputs unless that repository explicitly requires it.
7. Test positive and negative authorization cases for changed data paths, covering both the
   frontend's (typically anon-key, RLS-mediated) and the backend's (typically service-role,
   application-code-mediated) access patterns against the same tables.
8. Define backward compatibility, data backfill, failure recovery, and rollback for schema or
   function changes, naming which repository is accountable for executing the rollback.
9. Validate Edge Functions, webhooks, and any cross-repository-triggered calls for
   authentication, idempotency, replay, timeout, and observability — record which repository
   owns each Edge Function.
10. Record the project reference and environment mapping without copying secrets. If no
    lower (staging/dev) environment exists for the shared project — verify this rather than
    assume it — record that explicitly as a residual risk rather than leaving it undocumented.
11. Maintain an auditable record of privileged (service-role) access: what it is used for, from
    which repository, and how a reviewer can confirm it was not exposed or misused.

## Supabase assessment prompts

- Which repository (or both) owns the affected schema, table, or function in the shared project?
- Where is the authoritative migration for this change, and how does it avoid drifting from the
  other repository's migration history against the same live project?
- Which role (anon-key/RLS-mediated frontend access, or service-role backend access) executes
  each operation, and which RLS policy — if any — permits or would permit it?
- Is generated client or type output affected in one or both repositories?
- Does the change introduce new coupling, duplication, or ownership ambiguity within the shared
  project — for example, both repositories writing the same table without a documented owner —
  rather than assuming the existing split (if any) is already clean?
- Is the JWT/authentication boundary between the two repositories' independent consumption of
  the same identity provider still consistent after this change?
- How is rollback handled if the schema change is not reversible, and which repository executes it?

## Evidence expected

- Per-table/per-function ownership map for the shared project (which repository owns schema
  changes; whether both read/write it).
- Migration, RLS, auth, and generated-type paths in both repositories.
- Local or non-production validation command and output, where a lower environment exists.
- Positive and negative authorization tests covering both frontend and backend access patterns.
- Rollback or forward-recovery decision, with the accountable repository named.
