---
artifact: intent
schema_version: 1
change_id: "{{CHANGE_ID}}"
title: "{{TITLE}}"
status: draft
owner: "<OWNER>"
originator: "<ORIGINATOR>"
created: "{{DATE}}"
updated: "{{DATE}}"
accepted_by: null
accepted_at: null
supersedes: []
tags: []
---

# Intent: {{TITLE}}

## Problem or opportunity

Describe the observed problem or opportunity in the originator's language. Separate observations from interpretation.

## Desired outcome

Describe the user or business outcome. Avoid prescribing implementation unless it is an actual constraint.

## Affected users and stakeholders

- `<USER_OR_STAKEHOLDER>`: `<IMPACT>`

## Current evidence and baseline

| Evidence ID | Observation | Source | Confidence |
|---|---|---|---|
| E-001 | `<OBSERVATION>` | `<PATH_LINK_METRIC_OR_INTERVIEW>` | `<LOW_MEDIUM_HIGH>` |

## Scope

### In scope

- `<ITEM>`

### Out of scope

- `<ITEM>`

## Constraints

- `<BUSINESS_TECHNICAL_REGULATORY_TIME_OR_COST_CONSTRAINT>`

## Outcome measures

| Measure | Baseline | Target | Measurement window | Source |
|---|---:|---:|---|---|
| `<MEASURE>` | `<BASELINE>` | `<TARGET>` | `<WINDOW>` | `<SOURCE>` |

## Risks and assumptions

| ID | Type | Statement | Validation or mitigation |
|---|---|---|---|
| R-001 | assumption | `<STATEMENT>` | `<ACTION>` |

## Open questions

- [ ] `<QUESTION>` - owner: `<OWNER>`

## Intent acceptance checklist

- [ ] Problem or opportunity is supported by evidence.
- [ ] Desired outcome is observable or measurable.
- [ ] Scope and non-scope are explicit.
- [ ] Constraints and assumptions are separated.
- [ ] Affected users and systems are identified at an appropriate level.
- [ ] No unsupported implementation choice is embedded as intent.
- [ ] Open questions have owners or are accepted risks.

## Decision record

| Date | Decision | Decider | Rationale |
|---|---|---|---|
| `<DATE>` | `<ACCEPT_REJECT_REQUEST_CHANGES>` | `<NAME>` | `<RATIONALE>` |
