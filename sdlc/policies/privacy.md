---
artifact: policy
policy_id: POL-PRV-001
title: Privacy and Data Handling Policy
status: draft
owner: "<PRIVACY_OWNER>"
version: 0.1.0
approved_by: null
approved_date: null
review_date: null
source_authorities: []
scope: "Negotiation AI product and its repositories"
---

# Privacy and Data Handling Policy

> This draft is not normative until approved. Legal applicability and organizational requirements must be confirmed by the responsible owner.

## Objectives

Process only necessary data for explicit purposes, make ownership and flows visible, and support retention, access, deletion, correction, and incident obligations where applicable.

## Candidate mandatory controls

1. Identify purpose, data categories, data subjects, source, owner, and legal or organizational basis before adding personal data processing.
2. Minimize collection, storage, replication, logging, prompt inclusion, and model exposure.
3. Classify data and document flows across client, backend, the shared Supabase project, model providers, analytics, and support tooling.
4. Define retention and deletion behavior, including backups, logs, embeddings, test data, and generated artifacts.
5. Restrict access by role and environment; do not use production personal data in development without explicit approval and safeguards.
6. Redact or pseudonymize sensitive values in logs, screenshots, prompts, tests, and evidence.
7. Document data-subject or customer-request handling where relevant.
8. Review new processors, regions, cross-border transfers, and AI providers before use.
9. Define detection and response for unauthorized disclosure or access.
10. Preserve an auditable decision record for material privacy trade-offs and exceptions.

## Data assessment prompts

- What data is collected, inferred, generated, stored, transferred, logged, or displayed?
- Which Supabase project owns each data set and why?
- Does the frontend store anything the backend assumes it owns, or vice versa?
- Is any personal or confidential data sent to a model, retrieval system, analytics provider, or external API?
- How is consent, notice, retention, deletion, and access controlled?

## Evidence expected

- Data inventory and flow diagram or equivalent structured record.
- Classification, retention, access-control, and deletion decisions.
- Redaction and negative-test evidence.
- Processor or provider decision where applicable.
- Explicit residual-risk decision.

## Exception record

Record control, data scope, affected users, rationale, compensating safeguards, owner, approval, expiry, and re-review trigger.
