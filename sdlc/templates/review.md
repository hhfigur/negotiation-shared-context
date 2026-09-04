---
artifact: review
schema_version: 1
change_id: "{{CHANGE_ID}}"
title: "{{TITLE}}"
status: draft
reviewer: "<INDEPENDENT_REVIEWER>"
created: "{{DATE}}"
updated: "{{DATE}}"
implementation_reference: "<BRANCH_COMMIT_OR_PR>"
gate_recommendation: pending
---

# Independent Review: {{TITLE}}

## Review scope

- Repositories and revisions: `<REFERENCES>`
- Artifacts reviewed: `<REFERENCES>`
- Applicable approved policies: `<PATHS_OR_NONE>`
- Review limitations: `<DETAILS>`

## Summary

State whether the implementation satisfies intent and specification, the most material findings, and the gate recommendation.

## Findings

Use one section per finding. Do not silently fix findings during the independent review.

### F-001: `<TITLE>`

- Severity: `<BLOCKER_HIGH_MEDIUM_LOW_NOTE>`
- Category: `<CORRECTNESS_SECURITY_PRIVACY_ARCHITECTURE_UX_DATA_AI_QUALITY_MAINTAINABILITY_TRACEABILITY_TESTING>`
- Requirement or policy: `<REFERENCE>`
- Evidence: `<REPOSITORY_PATH_LINE_SYMBOL_TEST_OR_ARTIFACT>`
- Impact: `<CONSEQUENCE>`
- Recommendation: `<SPECIFIC_REMEDIATION_OR_DECISION>`
- Re-verification required: `<YES_NO>`
- Disposition: `<OPEN_FIXED_ACCEPTED_RISK_NOT_APPLICABLE>`
- Disposition owner and evidence: `<DETAILS>`

## Policy assessments

| Policy | Status | Result | Findings | Notes |
|---|---|---|---|---|
| `<PATH>` | `<APPROVED_DRAFT_MISSING>` | `<PASS_FAIL_NOT_APPLICABLE_ADVISORY>` | `<F_IDS>` | `<DETAILS>` |

## Traceability review

| Check | Result | Gaps |
|---|---|---|
| Intent to requirements | `<PASS_FAIL>` | `<DETAILS>` |
| Requirements to acceptance criteria | `<PASS_FAIL>` | `<DETAILS>` |
| Plan to implementation | `<PASS_FAIL>` | `<DETAILS>` |
| Acceptance criteria to evidence | `<PASS_FAIL>` | `<DETAILS>` |
| Release and outcome instrumentation | `<PASS_FAIL>` | `<DETAILS>` |

## Gate recommendation

- Recommendation: `<APPROVE_CONDITIONAL_APPROVAL_REJECT_BLOCKED>`
- Blocking findings: `<F_IDS_OR_NONE>`
- Required remediation: `<DETAILS>`
- Accepted residual risks: `<DETAILS>`
