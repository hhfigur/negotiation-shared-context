---
name: assess-supabase
description: Assess a Negotiation AI change for correct frontend or backend Supabase ownership, migrations, schemas, RLS, roles, auth, storage, edge functions, generated types, environment mapping, cross-project flows, and rollback. Use whenever Supabase or persistent data behavior changes.
user-invocable: false
context: fork
agent: negotiation-ai-sdlc:policy-auditor
background: false
allowed-tools: Read, Grep, Glob
---

# Assess Supabase and Data Boundaries

Read `${CLAUDE_PLUGIN_ROOT}/references/POLICY_APPLICATION.md`, the canonical Supabase policy, accepted change artifacts, project boundary map, migrations, schema, RLS, auth, storage, functions, generated clients or types, tests, and evidence.

Assess which Supabase project and repository own the change, migration authority, environment mapping, roles, service-key exposure, RLS positives and negatives, schema compatibility, generated outputs, cross-project calls or copying, idempotency, observability, backfill, rollback, and forward recovery.

Negotiation AI's frontend and backend intentionally share exactly one active Supabase project. Do not flag the sharing itself as a defect or propose separating it. Instead verify the governance controls the shared model requires: RLS enforcement on every table the change touches, the authentication/JWT boundary between the two repositories' consumption of that identity, service-role key custody (must stay backend-only), frontend versus backend access rights, explicit schema/migration/table/Edge-Function ownership, environment separation (or its documented absence), and auditability of privileged (service-role) access.

Apply the policy as mandatory only when `status: approved` and in scope. Otherwise return advisory gaps and required data-platform decisions.

Return policy status, applicability, boundary and control mapping, findings with severity and evidence, missing tests or decisions, and result `PASS`, `FAIL`, `ADVISORY_GAPS`, `NOT_APPLICABLE`, or `BLOCKED`. Do not edit artifacts, run migrations, or access secrets.
