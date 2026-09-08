---
name: implement-change
description: Implement only accepted Negotiation AI plan steps in the owning repository, add required tests, maintain traceability, and stop for material deviations. Use only through explicit invocation with a change ID and plan step scope.
argument-hint: "[change-id] [plan-step-ids]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
---

# Implement Accepted Change

Editing and shell execution are intentionally not pre-authorized by this Skill. Normal Claude Code permissions and repository constraints remain in force.

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/ARTIFACT_CONTRACT.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/GATE_MODEL.md`
4. `${CLAUDE_PLUGIN_ROOT}/references/EVIDENCE_STANDARD.md`
5. `${CLAUDE_PLUGIN_ROOT}/references/TRACEABILITY.md`
6. Accepted intent, specification, plan, active repository instructions, scoped rules, and applicable approved policies

## Entry gate

Verify:

- accepted intent, specification, and plan with named decisions;
- exact implementation revision or branch and clean awareness of uncommitted work;
- requested plan step IDs belong to the current repository;
- no unresolved blocker applies;
- for defect work, the diagnosis gate and `fix_authorized` are satisfied.

Stop with `BLOCKED` if any condition fails.

## Workflow

1. Restate in-scope plan steps, acceptance criteria, non-goals, and evidence obligations.
2. Inspect affected code immediately before editing and preserve generated-code ownership.
3. Add or update discriminating tests at the appropriate feedback level.
4. Make the smallest coherent change that satisfies the accepted plan.
5. Run fast, focused checks first, then broader repository-native checks defined in the plan.
6. For frontend behavior, capture required visual or browser evidence. For backend or data behavior, capture API, contract, authorization, schema, RLS, or migration evidence as applicable.
7. Do not hide failing, flaky, skipped, or unavailable checks.
8. Update canonical traceability with verified paths, tests, evidence, branch, and commit or pull request only when they exist.
9. Write a session handoff before ending.

## Material deviation rule

Stop before implementing a new repository, interface, data store, dependency, migration, user journey, acceptance criterion, policy impact, or substantially different approach. Record the discovery and update the specification or plan for acceptance.

## Prohibitions

This Skill is not authorization to deploy, modify production, access or print secrets, change remote configuration, upgrade dependencies, run production migrations, or overwrite user work.

## Required result

Report completed and deferred plan steps, paths changed, tests and evidence with exact results, deviations, risks, traceability updates, and readiness for independent verification.
