---
name: verify-change
description: Commission and persist independent verification of a defined Negotiation AI implementation revision against accepted artifacts, acceptance criteria, tests, visual or API evidence, and relevant quality checks. Use only through explicit invocation after implementation.
argument-hint: "[change-id] [branch, commit, or PR reference]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Verify Change Independently

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/ARTIFACT_CONTRACT.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/GATE_MODEL.md`
4. `${CLAUDE_PLUGIN_ROOT}/references/EVIDENCE_STANDARD.md`
5. `${CLAUDE_PLUGIN_ROOT}/references/TRACEABILITY.md`
6. Accepted artifacts, implementation reference, repository instructions, and evidence produced by implementation

## Entry gate

The implementation target and accepted artifact revisions must be unambiguous. Stop with `BLOCKED` when the branch, commit, pull request, repository, or plan revision cannot be established.

## Workflow

1. Create or refresh a draft `verification.md` from the canonical template without declaring a result.
2. Delegate all implementation assessment and command execution to the read-only `negotiation-ai-sdlc:verifier` agent.
3. The verifier must inspect the target directly, run only proven non-destructive checks, and record exact commands, results, evidence, and limitations.
4. Require coverage of every acceptance criterion and relevant format, lint, type, unit, integration, build, visual, API, contract, authorization, Supabase, migration, AI-evaluation, and regression category.
5. Use `NOT_AVAILABLE`, `NOT_APPLICABLE`, or `BLOCKED` rather than converting missing checks into pass results.
6. Persist the verifier's returned result in `verification.md`. Do not change source, tests, or implementation while performing this Skill.
7. Update only verified evidence links and verification result in `traceability.yaml`.
8. If verification fails, return findings to the implementer through a handoff; do not silently fix them.

## Independence

Record whether the verifier authored the implementation in the same session. Where strict independence is unavailable in solo mode, use a fresh read-only agent context and disclose the limitation.

## Required result

Report target revisions, acceptance coverage, checks and results, failures and limitations, verification result, release recommendation, and exact next action.
