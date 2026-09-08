---
artifact: policy
policy_id: POL-SEC-001
title: Security Engineering Policy
status: draft
owner: "<SECURITY_OWNER>"
version: 0.1.0
approved_by: null
approved_date: null
review_date: null
source_authorities: []
scope: "Negotiation AI product and its repositories"
---

# Security Engineering Policy

> This draft is not normative until approved. Replace placeholders with verified project and organizational requirements.

## Objectives

Protect confidentiality, integrity, availability, authenticity, and accountability across frontend, backend, the shared Supabase project, integrations, and delivery tooling.

## Candidate mandatory controls

1. Authenticate users and services at every trust boundary; do not rely on UI state for authorization.
2. Enforce least privilege for application roles, service accounts, database access, storage, and deployment credentials.
3. Validate and normalize untrusted input at the boundary where it enters the system.
4. Encode output for its destination and prevent injection into HTML, SQL, shell, prompt, logs, or downstream tools.
5. Keep secrets out of source, prompts, logs, artifacts, screenshots, and test fixtures. Reference secret names only.
6. Use approved cryptography and transport security; do not design custom cryptographic schemes.
7. Fail closed for authorization and security-critical validation unless an approved exception states otherwise.
8. Log security-relevant decisions without logging sensitive content.
9. Define abuse cases, dependency risk, and rollback for material changes.
10. Add tests for authorization boundaries and known failure modes when those areas change.

## Threat assessment prompts

- What assets, actors, entry points, and trust boundaries change?
- What can an unauthenticated, ordinary, privileged, or compromised actor do?
- Within the shared Supabase project, can data or instructions cross an ownership or access-right boundary unexpectedly (e.g. frontend anon-key access reaching a table meant to be backend/service-role-only)?
- Can model or tool output cause an unsafe action?
- What prevents replay, tampering, enumeration, injection, privilege escalation, and data exfiltration?

## Evidence expected

- Security-relevant requirements and acceptance criteria.
- Authorization and negative tests.
- Dependency or configuration evidence when changed.
- Secret scan or equivalent repository evidence when available.
- Explicit residual-risk decision.

## Exception record

Every exception must include control, scope, rationale, compensating controls, owner, approval, expiry, and re-review trigger.
