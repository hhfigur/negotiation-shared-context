---
name: assess-ai-quality
description: Assess a Negotiation AI change for intended model behavior, prompt and configuration versioning, evaluation coverage, tool permissions, data exposure, failure modes, human control, fallback, monitoring, and rollback. Use when prompts, models, retrieval, agents, tools, or AI-generated product behavior change.
user-invocable: false
context: fork
agent: negotiation-ai-sdlc:policy-auditor
background: false
allowed-tools: Read, Grep, Glob
---

# Assess AI Quality

Read `${CLAUDE_PLUGIN_ROOT}/references/POLICY_APPLICATION.md`, the canonical AI-quality policy, accepted change artifacts, model and prompt configuration, tool definitions, evaluation material, implementation, production signals, and evidence.

Assess intended task and prohibited behavior, versioning, representative positive and negative cases, adversarial and boundary cases, deterministic schema and permission checks, task-relevant metrics, hallucination or unsupported claims, tool actions, personal or confidential data exposure, human review, user correction, fallback, provider change, monitoring, and rollback.

Apply the policy as mandatory only when `status: approved` and in scope. Otherwise return advisory gaps and required AI product or risk decisions.

Return policy status, applicability, evaluation and control mapping, findings with severity and evidence, missing cases or decisions, and result `PASS`, `FAIL`, `ADVISORY_GAPS`, `NOT_APPLICABLE`, or `BLOCKED`. Do not edit artifacts or code and do not claim quality from anecdotal examples alone.
