---
name: create-plan
description: Produce a repository-grounded Negotiation AI implementation plan from an accepted specification, naming workstreams, exact files or bounded discovery, sequence, tests, risks, observability, migrations, rollback, and rejected options. Use only through explicit invocation before implementation.
argument-hint: "[change-id] [optional workstream focus]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Create Implementation Plan

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/ARTIFACT_CONTRACT.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/GATE_MODEL.md`
4. `${CLAUDE_PLUGIN_ROOT}/references/EVIDENCE_STANDARD.md`
5. `${CLAUDE_PLUGIN_ROOT}/references/TRACEABILITY.md`
6. Accepted intent and specification, canonical plan template, repository instructions, and relevant architecture

## Entry gate

Confirm accepted specification with named decision and current revision. Stop with `BLOCKED` if the gate is not satisfied.

## Workflow

1. Delegate read-only research to `negotiation-ai-sdlc:codebase-researcher` for every affected repository.
2. Ground current-state statements in paths, symbols, manifests, CI, tests, and existing documentation.
3. Define the smallest coherent delivery approach.
4. Split work into Shared-context, frontend, and backend workstreams with stable step IDs.
5. Name exact files or modules. When exact paths depend on exploration, define a bounded discovery step and decision point rather than guessing.
6. Identify generated-code handling (including any historical Lovable-origin boundaries — do not assume an active Lovable workflow), the shared Supabase project's ownership boundaries, interfaces, migrations, compatibility, and integration sequence.
7. Map every requirement and acceptance criterion to implementation steps and planned evidence.
8. Define repository-native checks, regression tests, visual or browser evidence, API or contract checks, data and RLS checks, and AI evaluations as applicable.
9. Define observability, rollout, rollback, recovery, irreversible effects, risks, owners, and rejected alternatives.
10. Identify which steps can run in separate repository windows and what handoff each requires.
11. Ask `negotiation-ai-sdlc:plan-critic` to review independently. Resolve or retain findings explicitly.
12. Update plan-step mappings in `traceability.yaml`.
13. Mark `accepted` only with a named decider, date, and rationale.

## Prohibitions

- Do not implement code while planning.
- Do not invent commands, file paths, integrations, or test capabilities.
- Do not bundle unrelated refactoring or dependency upgrades.

## Required result

Report artifact path, accepted source revisions, workstreams and sequence, tests and evidence plan, major risks, critic findings, plan gate state, and exact next action.
