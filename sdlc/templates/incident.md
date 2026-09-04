---
artifact: incident
schema_version: 1
change_id: "{{CHANGE_ID}}"
title: "{{TITLE}}"
status: draft
incident_id: "<INCIDENT_ID>"
severity: "<SEVERITY>"
owner: "<INCIDENT_OWNER>"
started_at: "<TIMESTAMP>"
resolved_at: null
created: "{{DATE}}"
updated: "{{DATE}}"
---

# Incident: {{TITLE}}

## Impact

- Affected users or systems: `<DETAILS>`
- Business and operational impact: `<DETAILS>`
- Duration and scope: `<DETAILS>`

## Detection

- Detection source: `<ALERT_USER_SUPPORT_REVIEW_OTHER>`
- First signal: `<DETAILS>`
- Detection gap: `<DETAILS>`

## Timeline

| Time | Event | Evidence |
|---|---|---|
| `<TIME>` | `<EVENT>` | `<REFERENCE>` |

## Containment and recovery

| Action | Owner | Result | Evidence |
|---|---|---|---|
| `<ACTION>` | `<OWNER>` | `<RESULT>` | `<REFERENCE>` |

## Cause and contributing factors

Link to `debug-evidence.md` for technical diagnosis. Distinguish direct cause, contributing conditions, and process or detection gaps.

## Follow-up actions

| Action | Type | Owner | Due | Change ID | Status |
|---|---|---|---|---|---|
| `<ACTION>` | `<PREVENT_DETECT_RECOVER_LEARN>` | `<OWNER>` | `<DATE>` | `<ID_OR_PENDING>` | `<STATUS>` |

## Incident closure

- Customer or stakeholder communication: `<REFERENCE_OR_NOT_APPLICABLE>`
- Follow-up intent created: `<ID_OR_NONE>`
- Closure decision and owner: `<DETAILS>`
