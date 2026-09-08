---
name: assess-privacy
description: Assess a Negotiation AI change for personal or confidential data purpose, minimization, flows, retention, deletion, access, logging, model exposure, providers, and privacy evidence. Use when data collection, storage, analytics, prompts, retrieval, exports, or external processors change.
user-invocable: false
context: fork
agent: negotiation-ai-sdlc:policy-auditor
background: false
allowed-tools: Read, Grep, Glob
---

# Assess Privacy

Read `${CLAUDE_PLUGIN_ROOT}/references/POLICY_APPLICATION.md`, the canonical privacy policy, accepted change artifacts, data-flow references, relevant implementation, tests, and evidence.

Assess purpose, data categories, subjects, source, ownership, minimization, classification, access, retention, deletion, redaction, test data, logs, screenshots, prompts, model or analytics providers, regions, transfers, incidents, and user rights as relevant.

Apply the policy as mandatory only when `status: approved` and in scope. Otherwise return advisory gaps and required legal, privacy, or owner decisions.

Return policy status, applicability, data-flow and control mapping, findings with severity and evidence, exceptions or missing decisions, and result `PASS`, `FAIL`, `ADVISORY_GAPS`, `NOT_APPLICABLE`, or `BLOCKED`. Do not edit artifacts or code and do not provide unsupported legal conclusions.
