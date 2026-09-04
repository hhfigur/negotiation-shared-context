---
name: assess-ux
description: Assess a Negotiation AI user-facing change for journey completeness, design-system consistency, loading and error states, accessibility, responsiveness, AI-output clarity, recovery, and visual evidence. Use when frontend behavior or user interaction changes.
user-invocable: false
context: fork
agent: negotiation-ai-sdlc:policy-auditor
background: false
allowed-tools: Read, Grep, Glob
---

# Assess UX and Accessibility

Read `${CLAUDE_PLUGIN_ROOT}/references/POLICY_APPLICATION.md`, the canonical UX policy, accepted change artifacts, design-system references, implementation, tests, screenshots, and browser evidence.

Assess journey completeness, information clarity, loading, empty, error, success, permission, timeout, retry, recovery, destructive actions, keyboard, focus, labels, semantics, contrast, zoom, responsive behavior, AI-output labeling, design-system conventions, and visual evidence.

Apply the policy as mandatory only when `status: approved` and in scope. Otherwise return advisory gaps and required UX decisions.

Return policy status, applicability, control-to-evidence mapping, findings with severity and evidence, missing visual or accessibility evidence, and result `PASS`, `FAIL`, `ADVISORY_GAPS`, `NOT_APPLICABLE`, or `BLOCKED`. Do not edit artifacts or code.
