---
name: assess-architecture
description: Assess a Negotiation AI change for repository and domain ownership, interface compatibility, coupling, generated-code handling, resilience, observability, migrations, dependencies, and rollback. Use when behavior crosses modules, repositories, services, Supabase projects, or architectural boundaries.
user-invocable: false
context: fork
agent: negotiation-ai-sdlc:policy-auditor
background: false
allowed-tools: Read, Grep, Glob
---

# Assess Architecture

Read `${CLAUDE_PLUGIN_ROOT}/references/POLICY_APPLICATION.md`, the canonical architecture policy, accepted change artifacts, repository architecture, implementation, tests, and evidence.

Assess ownership, separation of concerns, duplicated rules, contracts, compatibility, coupling, generated code, configuration, failure behavior, retry and idempotency, observability, dependencies, migration sequence, rollback, and fit with established conventions.

Apply the policy as mandatory only when `status: approved` and in scope. Otherwise return advisory gaps and required architecture decisions.

Return policy status, applicability, control-to-evidence mapping, findings with severity and evidence, trade-offs or exceptions, and result `PASS`, `FAIL`, `ADVISORY_GAPS`, `NOT_APPLICABLE`, or `BLOCKED`. Do not edit artifacts or code.
