---
artifact: release
schema_version: 1
change_id: "{{CHANGE_ID}}"
title: "{{TITLE}}"
status: draft
owner: "<RELEASE_OWNER>"
created: "{{DATE}}"
updated: "{{DATE}}"
release_decision: pending
released_at: null
---

# Release Record: {{TITLE}}

## Release scope

- Repositories and revisions: `<COMMITS_TAGS_OR_PR_REFERENCES>`
- Environments: `<DETAILS>`
- Feature flags or staged rollout: `<DETAILS>`
- Data or schema changes: `<DETAILS>`

## Entry evidence

| Gate | Result | Reference |
|---|---|---|
| Verification | `<PASS_PASS_WITH_LIMITATIONS_FAIL_BLOCKED>` | `./verification.md` |
| Independent review | `<APPROVE_CONDITIONAL_APPROVAL_REJECT_BLOCKED>` | `./review.md` |
| Blocking findings closed | `<YES_NO_NOT_APPLICABLE>` | `<REFERENCE>` |
| Rollback tested or reviewed | `<YES_NO_NOT_APPLICABLE>` | `<REFERENCE>` |

## Deployment procedure

1. `<VERIFIED_STEP_OR_REFERENCE_TO_EXISTING_RUNBOOK>`

Do not place secrets in this record.

## Observability and control bands

| Signal | Expected range | Alert or rollback threshold | Owner | Source |
|---|---|---|---|---|
| `<SIGNAL>` | `<RANGE>` | `<THRESHOLD>` | `<OWNER>` | `<DASHBOARD_OR_QUERY>` |

## Rollback

- Trigger: `<DETAILS>`
- Procedure: `<VERIFIED_RUNBOOK_OR_STEPS>`
- Data implications: `<DETAILS>`
- Decision owner: `<OWNER>`

## Residual risk and exceptions

| ID | Risk or exception | Decision | Owner | Expiry or review date |
|---|---|---|---|---|
| R-001 | `<DETAILS>` | `<ACCEPT_MITIGATE_DEFER>` | `<OWNER>` | `<DATE>` |

## Release decision

- Decision: `<APPROVE_REJECT_HOLD>`
- Decider: `<NAME>`
- Date: `<DATE>`
- Rationale: `<DETAILS>`
- Actual release result: `<SUCCESS_PARTIAL_FAILED_ROLLED_BACK_PENDING>`
- Release evidence: `<REFERENCE>`
