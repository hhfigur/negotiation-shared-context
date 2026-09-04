---
artifact: verification
schema_version: 1
change_id: "{{CHANGE_ID}}"
title: "{{TITLE}}"
status: draft
verifier: "<INDEPENDENT_VERIFIER>"
created: "{{DATE}}"
updated: "{{DATE}}"
implementation_reference: "<BRANCH_COMMIT_OR_PR>"
result: pending
---

# Verification: {{TITLE}}

## Scope and independence

- Implementation reference: `<REFERENCE>`
- Plan revision verified: `<REFERENCE>`
- Verifier did not author the implementation in this verification session: `<YES_NO_EXPLAIN>`
- Environments used: `<DETAILS>`

## Artifact and gate checks

| Check | Result | Evidence |
|---|---|---|
| Intent accepted | `<PASS_FAIL_BLOCKED>` | `<REFERENCE>` |
| Specification accepted | `<PASS_FAIL_BLOCKED>` | `<REFERENCE>` |
| Plan accepted and current | `<PASS_FAIL_BLOCKED>` | `<REFERENCE>` |
| Material deviations recorded | `<PASS_FAIL_NOT_APPLICABLE>` | `<REFERENCE>` |

## Acceptance-criteria verification

| AC ID | Method | Command or procedure | Result | Evidence ID | Notes |
|---|---|---|---|---|---|
| AC-001 | `<TEST_REVIEW_VISUAL_MANUAL_EVAL>` | `<EXACT_COMMAND_OR_STEPS>` | `<PASS_FAIL_BLOCKED_NOT_AVAILABLE>` | E-001 | `<NOTES>` |

## Quality checks

| Category | Command or method | Exit status or result | Evidence | Coverage limitation |
|---|---|---|---|---|
| Format | `<COMMAND_OR_NOT_AVAILABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |
| Lint | `<COMMAND_OR_NOT_AVAILABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |
| Type check | `<COMMAND_OR_NOT_AVAILABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |
| Unit tests | `<COMMAND_OR_NOT_AVAILABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |
| Integration tests | `<COMMAND_OR_NOT_AVAILABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |
| Build | `<COMMAND_OR_NOT_AVAILABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |
| Visual or browser | `<PROCEDURE_OR_NOT_APPLICABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |
| API or contract | `<PROCEDURE_OR_NOT_APPLICABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |
| Data or RLS | `<PROCEDURE_OR_NOT_APPLICABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |
| AI evaluation | `<PROCEDURE_OR_NOT_APPLICABLE>` | `<RESULT>` | `<REFERENCE>` | `<LIMIT>` |

## Defect regression evidence

Complete when `debug-evidence.md` exists.

- Regression test failed before fix: `<EVIDENCE_OR_NOT_DEMONSTRATED>`
- Regression test passes after fix: `<EVIDENCE>`
- Adjacent non-regression evidence: `<EVIDENCE>`

## Failures, blockers, and uncertainty

| ID | Type | Description | Impact | Owner | Required action |
|---|---|---|---|---|---|
| F-001 | `<FAILURE_BLOCKER_UNCERTAINTY>` | `<DETAILS>` | `<IMPACT>` | `<OWNER>` | `<ACTION>` |

## Verification conclusion

- Result: `<PASS_FAIL_BLOCKED_PASS_WITH_LIMITATIONS>`
- Release recommendation: `<PROCEED_DO_NOT_PROCEED_CONDITIONAL>`
- Residual limitations: `<DETAILS>`
