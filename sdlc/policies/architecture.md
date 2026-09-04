---
artifact: policy
policy_id: POL-ARC-001
title: Architecture and Engineering Policy
status: draft
owner: "<ARCHITECTURE_OWNER>"
version: 0.1.0
approved_by: null
approved_date: null
review_date: null
source_authorities: []
scope: "Negotiation AI product and its repositories"
---

# Architecture and Engineering Policy

> This draft is not normative until approved. Existing canonical architecture decisions take precedence until reconciled.

## Objectives

Maintain clear boundaries, predictable change impact, testability, operability, and reversible evolution across the frontend, backend, and the Supabase project(s) they use — for Negotiation AI, this is a single project intentionally shared by both repositories; sharing is not itself a defect and boundaries must be maintained *within* it, not by assuming or proposing separate instances.

## Candidate mandatory controls

1. Preserve documented ownership boundaries between repositories and within the shared Supabase project (per-table/per-function ownership).
2. Put domain rules in the owning layer; do not duplicate authoritative business logic across frontend and backend.
3. Define interfaces and compatibility expectations before changing cross-repository contracts.
4. Prefer the smallest coherent change over broad refactoring unrelated to the accepted intent.
5. Identify generated code and update it through its generator or approved workflow whenever possible.
6. Keep configuration environment-specific and secrets external to source.
7. Design failure, retry, timeout, idempotency, concurrency, and rollback behavior for material integrations.
8. Add observability at boundaries where failures would otherwise be opaque.
9. Record consequential decisions and rejected alternatives in specification or plan artifacts.
10. Avoid new dependencies or architectural patterns without a concrete need, evaluation, and owner decision.

## Architecture assessment prompts

- Which component owns the behavior and data?
- What contract changes, and how is compatibility maintained?
- Does the design introduce new cross-boundary coupling, duplication, or ownership ambiguity within the shared Supabase project (see the Supabase and Data Boundary Policy's ownership-mapping controls) rather than assuming a clean split that does not exist?
- What fails partially, asynchronously, or under retry?
- What can be rolled back independently?
- Does the plan respect existing conventions and generated-code boundaries?

## Evidence expected

- Current-state path and symbol evidence.
- Interface or schema references.
- Test strategy across affected boundaries.
- Migration and rollback record.
- Observability and operational ownership.
