---
name: assess-security
description: Assess a Negotiation AI intent, specification, plan, or implementation for security risks, trust boundaries, authorization, input and output handling, secrets, abuse cases, and evidence. Use when a change affects authentication, authorization, data, integrations, AI tools, or other security-sensitive behavior.
user-invocable: false
context: fork
agent: negotiation-ai-sdlc:policy-auditor
background: false
allowed-tools: Read, Grep, Glob
---

# Assess Security

Read `${CLAUDE_PLUGIN_ROOT}/references/POLICY_APPLICATION.md`, the canonical security policy, accepted change artifacts, relevant implementation, tests, and evidence.

Assess trust boundaries, assets, actors, authentication, authorization, least privilege, validation, injection, output handling, secrets, logs, dependencies, abuse cases, availability, rollback, and AI or tool actions as relevant.

Apply the policy as mandatory only when `status: approved` and in scope. Otherwise return advisory gaps and required owner decisions.

Return policy status, applicability, control-to-evidence mapping, findings with severity and evidence, exceptions or missing decisions, and result `PASS`, `FAIL`, `ADVISORY_GAPS`, `NOT_APPLICABLE`, or `BLOCKED`. Do not edit artifacts or code and do not claim broader compliance.
