---
artifact: policy
policy_id: POL-UX-001
title: User Experience and Accessibility Policy
status: draft
owner: "<UX_OWNER>"
version: 0.1.0
approved_by: null
approved_date: null
review_date: null
source_authorities: []
scope: "Negotiation AI frontend and user-facing behavior"
---

# User Experience and Accessibility Policy

> This draft is not normative until approved. Existing design-system and accessibility requirements must be linked and reconciled.

## Objectives

Deliver understandable, consistent, accessible, recoverable, and evidence-tested user behavior without bypassing the established frontend design system and workflow. (`negotiation-Buddy` originated from Lovable scaffolding; active frontend development now happens directly via Claude Code, not through a Lovable workflow — do not assume an active Lovable step exists.)

## Candidate mandatory controls

1. Follow the canonical design system, components, tokens, copy conventions, and generated-code workflow.
2. Specify loading, empty, error, success, permission-denied, timeout, and retry states for changed journeys.
3. Preserve keyboard navigation, focus order, semantic structure, labels, contrast, zoom, and assistive-technology behavior.
4. Make destructive, irreversible, or high-impact actions explicit and recoverable where possible.
5. Do not expose internal errors, secrets, sensitive data, or model instructions to users.
6. Use plain, actionable language and distinguish system facts from AI-generated suggestions.
7. Define responsive behavior for supported viewports.
8. Capture visual or browser evidence for material UI changes.
9. Test the user journey, not only individual components.
10. Record deviations from the design system or accessibility baseline.

## UX assessment prompts

- Can users understand what happened, what is happening, and what to do next?
- Are errors recoverable and permissions clear?
- Are AI outputs labeled and appropriately controllable?
- Does the change work with keyboard and common assistive patterns?
- Does it preserve existing design-system conventions and responsive behavior?

## Evidence expected

- Acceptance criteria for states and journeys.
- Screenshots or browser evidence at relevant viewports.
- Accessibility checks available in the repository.
- Recorded design-system deviations and owner decision.
