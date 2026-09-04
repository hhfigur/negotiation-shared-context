---
artifact: implementation_plan
schema_version: 1
change_id: "{{CHANGE_ID}}"
title: "{{TITLE}}"
status: draft
owner: "<OWNER>"
created: "{{DATE}}"
updated: "{{DATE}}"
spec_status_verified: false
accepted_by: null
accepted_at: null
repositories: []
---

# Implementation Plan: {{TITLE}}

## Source artifacts

- Intent: `./intent.md`
- Specification: `./spec.md`
- Accepted versions or commits: `<REFERENCES>`

## Current-state findings

Summarize only codebase facts that materially constrain the plan. Cite paths and symbols.

| ID | Finding | Evidence | Implication |
|---|---|---|---|
| E-001 | `<FINDING>` | `<REPO_PATH_SYMBOL_OR_COMMAND>` | `<IMPLICATION>` |

## Delivery strategy

Explain the smallest coherent approach and why it satisfies the specification.

## Repository workstreams

### Frontend: `negotiation-Buddy`

| Step | File, module, or path | Change | Requirement and AC IDs | Validation |
|---:|---|---|---|---|
| 1 | `<PATH_OR_DISCOVERY_BOUNDARY>` | `<EXACT_CHANGE>` | `<FR_NFR_AC_IDS>` | `<COMMAND_OR_EVIDENCE>` |

Generated-code handling: `<GENERATED_CODE_BOUNDARY_AND_UPDATE_METHOD_OR_NONE>` (do not assume Lovable is the active generation tool — verify current status)

### Backend: `NegotiationCoach-backend`

| Step | File, module, or path | Change | Requirement and AC IDs | Validation |
|---:|---|---|---|---|
| 1 | `<PATH_OR_DISCOVERY_BOUNDARY>` | `<EXACT_CHANGE>` | `<FR_NFR_AC_IDS>` | `<COMMAND_OR_EVIDENCE>` |

### Shared context and contracts

| Step | Path | Change | Reason | Validation |
|---:|---|---|---|---|
| 1 | `<PATH>` | `<CHANGE>` | `<REASON>` | `<VALIDATION>` |

## Sequence and dependencies

1. `<STEP_AND_PRECONDITION>`
2. `<STEP_AND_PRECONDITION>`

Parallelizable work: `<DETAILS>`

Cross-repository integration point: `<DETAILS>`

## Test and evidence plan

| AC or NFR ID | Test level | Repository | Test or evidence to add or run | Failure expected before change? |
|---|---|---|---|---|
| AC-001 | `<UNIT_INTEGRATION_CONTRACT_E2E_VISUAL_MANUAL_EVAL>` | `<REPO>` | `<DETAILS>` | `<YES_NO_NOT_APPLICABLE>` |

## Data, migration, and rollback plan

- Owning Supabase instance: `<DETAILS>`
- Migration sequence: `<DETAILS>`
- Backward compatibility: `<DETAILS>`
- Rollback trigger: `<DETAILS>`
- Rollback procedure: `<DETAILS>`
- Data recovery or irreversible effects: `<DETAILS>`

## Observability and outcome instrumentation

- Logs, metrics, traces, events, or analytics to add or verify: `<DETAILS>`
- How outcome measures in `intent.md` will be obtained: `<DETAILS>`

## Risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R-001 | `<RISK>` | `<LOW_MEDIUM_HIGH>` | `<LOW_MEDIUM_HIGH>` | `<MITIGATION>` | `<OWNER>` |

## Rejected or deferred options

| Option | Reason not selected | Revisit trigger |
|---|---|---|
| `<OPTION>` | `<RATIONALE>` | `<TRIGGER>` |

## Plan-deviation protocol

Stop before implementing a material deviation. Update this plan with the new path, rationale, affected requirements, risks, tests, and decision. Record the accepted revision in the decision log.

## Plan acceptance checklist

- [ ] Specification is accepted.
- [ ] Relevant repositories, files, modules, and generated-code boundaries are named or bounded by a discovery step.
- [ ] Sequence, dependencies, tests, evidence, risks, observability, and rollback are explicit.
- [ ] Cross-repository and Supabase boundaries are explicit.
- [ ] Rejected options and material trade-offs are recorded.
- [ ] No command, path, or capability is invented.

## Decision record

| Date | Decision | Decider | Rationale |
|---|---|---|---|
| `<DATE>` | `<ACCEPT_REJECT_REQUEST_CHANGES>` | `<NAME>` | `<RATIONALE>` |
