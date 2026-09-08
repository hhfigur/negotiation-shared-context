---
artifact: specification
schema_version: 1
change_id: "{{CHANGE_ID}}"
title: "{{TITLE}}"
status: draft
owner: "<OWNER>"
created: "{{DATE}}"
updated: "{{DATE}}"
intent_status_verified: false
accepted_by: null
accepted_at: null
applicable_policies: []
---

# Specification: {{TITLE}}

## Source intent

- Canonical intent: `./intent.md`
- Accepted intent version or commit: `<REFERENCE>`

## Context and system boundary

Describe the relevant current behavior, actors, repositories, systems, and boundaries. Link to canonical architecture documents rather than copying them.

## Functional requirements

| ID | Requirement | Rationale | Priority | Source |
|---|---|---|---|---|
| FR-001 | `<TESTABLE_REQUIREMENT>` | `<WHY>` | `<MUST_SHOULD_COULD>` | `<INTENT_SECTION_OR_EVIDENCE>` |

## Non-functional requirements

| ID | Category | Requirement | Measure or threshold | Source |
|---|---|---|---|---|
| NFR-001 | `<SECURITY_PRIVACY_PERFORMANCE_RELIABILITY_ACCESSIBILITY_OPERABILITY>` | `<REQUIREMENT>` | `<MEASURE>` | `<POLICY_OR_INTENT>` |

## User journeys and behavior

### Journey 1: `<NAME>`

1. `<STEP>`
2. `<STEP>`

Expected errors, empty states, retries, permissions, and recovery:

- `<BEHAVIOR>`

## Interfaces and contracts

| Interface | Producer | Consumer | Contract or schema | Compatibility requirement |
|---|---|---|---|---|
| `<API_EVENT_UI_DATA_BOUNDARY>` | `<OWNER>` | `<CONSUMER>` | `<REFERENCE>` | `<RULE>` |

## Data and Supabase impact

- Owning Supabase instance: `<FRONTEND_BACKEND_NONE_DISCOVER>`
- Tables, views, functions, storage, auth, RLS, edge functions, or generated types affected: `<DETAILS>`
- Cross-project data flow: `<NONE_OR_EXPLICIT_FLOW>`
- Migration and rollback expectations: `<DETAILS>`
- Data classification and retention: `<DETAILS>`

## AI behavior and evaluation

Complete this section only when model, prompt, retrieval, agent, or AI-generated output behavior changes.

- Intended behavior: `<DETAILS>`
- Failure modes: `<DETAILS>`
- Evaluation set and metrics: `<DETAILS>`
- Human oversight and fallback: `<DETAILS>`
- Model or provider constraints: `<DETAILS>`

## Acceptance criteria

Use observable Given, When, Then statements or an equivalently testable form.

### AC-001: `<NAME>`

- Given `<PRECONDITION>`
- When `<ACTION>`
- Then `<OBSERVABLE_RESULT>`
- Evidence required: `<TEST_SCREENSHOT_LOG_METRIC_OR_REVIEW>`

## Policy assessment

| Policy | Status | Applicability | Requirement IDs | Gaps or exception |
|---|---|---|---|---|
| `<POLICY_PATH>` | `<APPROVED_DRAFT_MISSING>` | `<APPLICABLE_NOT_APPLICABLE>` | `<IDS>` | `<DETAILS>` |

## Alternatives and decisions

| Option | Benefits | Costs or risks | Decision |
|---|---|---|---|
| `<OPTION>` | `<BENEFITS>` | `<TRADE_OFFS>` | `<SELECTED_REJECTED_DEFERRED>` |

## Open questions

- [ ] `<QUESTION>` - owner: `<OWNER>`

## Specification acceptance checklist

- [ ] Intent is accepted and unchanged or differences are approved.
- [ ] Functional and non-functional requirements are testable.
- [ ] Interfaces, data ownership, permissions, errors, and recovery are covered.
- [ ] Relevant approved policies were applied; draft or missing policies are visible.
- [ ] Acceptance criteria cover the intended outcome and material failure modes.
- [ ] Alternatives and consequential trade-offs are recorded.
- [ ] Open questions are resolved or explicitly accepted as risk.

## Decision record

| Date | Decision | Decider | Rationale |
|---|---|---|---|
| `<DATE>` | `<ACCEPT_REJECT_REQUEST_CHANGES>` | `<NAME>` | `<RATIONALE>` |
