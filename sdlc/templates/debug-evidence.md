---
artifact: debug_evidence
schema_version: 1
change_id: "{{CHANGE_ID}}"
title: "{{TITLE}}"
status: draft
owner: "<OWNER>"
created: "{{DATE}}"
updated: "{{DATE}}"
root_cause_status: unconfirmed
confidence: low
fix_authorized: false
---

# Debug Evidence: {{TITLE}}

## Reported symptom

- Observed behavior: `<DETAILS>`
- Expected behavior: `<DETAILS>`
- First known occurrence: `<DATE_OR_UNKNOWN>`
- Environment and version: `<DETAILS>`
- User or system impact: `<DETAILS>`

## Reproduction protocol

### Preconditions

- `<PRECONDITION>`

### Steps

1. `<STEP>`
2. `<STEP>`

### Reproduction result

- Reproduced: `<YES_NO_INTERMITTENT_BLOCKED>`
- Frequency: `<DETAILS>`
- Raw evidence: `<LOG_TEST_SCREENSHOT_TRACE_OR_PATH>`
- Uncontrolled variables: `<DETAILS>`

## Timeline and change correlation

| Time or version | Event or change | Evidence | Relevance |
|---|---|---|---|
| `<TIME>` | `<EVENT>` | `<REFERENCE>` | `<DETAILS>` |

## Competing hypotheses

| ID | Hypothesis | Supporting evidence | Contradicting evidence | Discriminating test | Result | Status |
|---|---|---|---|---|---|---|
| H-001 | `<HYPOTHESIS>` | `<EVIDENCE>` | `<EVIDENCE>` | `<TEST>` | `<RESULT>` | `<OPEN_SUPPORTED_REJECTED>` |

## Causal chain

Describe the chain from triggering condition through faulty behavior to observed symptom. Distinguish root cause, contributing conditions, and detection gap.

- Trigger: `<DETAILS>`
- Fault mechanism: `<DETAILS>`
- Propagation: `<DETAILS>`
- Observed symptom: `<DETAILS>`
- Detection or prevention gap: `<DETAILS>`

## Root-cause conclusion

- Conclusion: `<CONFIRMED_CAUSE_OR_INSUFFICIENT_EVIDENCE>`
- Evidence that discriminates this cause: `<DETAILS>`
- Confidence: `<LOW_MEDIUM_HIGH>`
- Residual uncertainty: `<DETAILS>`
- Why alternatives were rejected: `<DETAILS>`

## Regression-test strategy

| Test | Level | Failure before fix | Expected after fix | Related AC or requirement |
|---|---|---|---|---|
| `<TEST>` | `<UNIT_INTEGRATION_CONTRACT_E2E>` | `<EXPECTED_FAILURE>` | `<EXPECTED_PASS>` | `<ID_OR_NEW_AC>` |

## Fix boundary and authorization

- Smallest effective fix boundary: `<FILES_MODULES_OR_CONTRACT>`
- Non-goals: `<DETAILS>`
- Additional specification or plan change required: `<YES_NO_AND_REFERENCE>`
- Fix authorized by: `<NAME_OR_PENDING>`
- Authorization date: `<DATE_OR_PENDING>`

## Diagnosis gate

- [ ] Symptom and expected behavior are precise.
- [ ] Reproduction was attempted and evidence is attached.
- [ ] At least one competing hypothesis was evaluated.
- [ ] Root-cause conclusion is supported or explicitly remains unconfirmed.
- [ ] Regression-test strategy can distinguish broken from fixed behavior.
- [ ] Fix boundary and residual uncertainty are visible.
- [ ] `fix_authorized` is true before code is edited for the fix.
