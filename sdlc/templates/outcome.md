---
artifact: outcome
schema_version: 1
change_id: "{{CHANGE_ID}}"
title: "{{TITLE}}"
status: draft
owner: "<OUTCOME_OWNER>"
created: "{{DATE}}"
updated: "{{DATE}}"
measurement_window: "<WINDOW>"
outcome_decision: pending
---

# Outcome Review: {{TITLE}}

## Original intent and release

- Intent: `./intent.md`
- Release: `./release.md`
- Measurement window: `<START_TO_END>`

## Outcome measures

| Measure | Baseline | Target | Actual | Source | Confidence | Result |
|---|---:|---:|---:|---|---|---|
| `<MEASURE>` | `<BASELINE>` | `<TARGET>` | `<ACTUAL>` | `<SOURCE>` | `<LOW_MEDIUM_HIGH>` | `<MET_PARTIALLY_MET_NOT_MET_INCONCLUSIVE>` |

## User and operational evidence

- User feedback: `<DETAILS_AND_SOURCE>`
- Reliability and support impact: `<DETAILS_AND_SOURCE>`
- Security, privacy, or data observations: `<DETAILS_AND_SOURCE>`
- AI-quality observations when applicable: `<DETAILS_AND_SOURCE>`

## Interpretation

Separate facts from inference. Explain causal uncertainty and confounding changes.

## Unintended consequences

| ID | Consequence | Evidence | Severity | Response |
|---|---|---|---|---|
| F-001 | `<DETAILS>` | `<SOURCE>` | `<HIGH_MEDIUM_LOW>` | `<ACTION>` |

## Outcome decision

- Decision: `<CLOSE_ITERATE_ROLL_BACK_MONITOR_CREATE_INCIDENT>`
- Rationale: `<DETAILS>`
- Follow-up change or incident ID: `<ID_OR_NONE>`
- Owner and date: `<DETAILS>`
