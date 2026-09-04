---
name: fix-diagnosed-bug
description: Implement the smallest authorized Negotiation AI defect fix only after accepted root-cause evidence, regression-test strategy, and an accepted fix plan exist. Use only through explicit invocation with a change ID and plan steps.
argument-hint: "[change-id] [fix plan-step-ids]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
---

# Fix a Diagnosed Bug

Editing and shell execution are intentionally not pre-authorized by this Skill. Normal Claude Code permissions and repository constraints remain in force.

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/DEBUG_PROTOCOL.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/GATE_MODEL.md`
4. `${CLAUDE_PLUGIN_ROOT}/references/EVIDENCE_STANDARD.md`
5. Accepted intent, specification, fix plan, `debug-evidence.md`, repository instructions, and scoped rules

## Entry gate

Confirm all of the following:

- the bug is associated with one canonical change;
- reproduction and raw evidence are recorded;
- root-cause conclusion is accepted or a bounded uncertainty decision is explicit;
- regression-test strategy exists;
- `fix_authorized: true` has a named owner, date, and rationale;
- an accepted plan defines the smallest fix boundary, tests, risks, and rollback;
- requested plan steps belong to the current repository and no blocker remains.

Stop with `BLOCKED` if any condition fails.

## Workflow

1. Restate the causal mechanism, fix boundary, regression test, and non-goals.
2. Add or preserve the regression test. Where safe and practical, demonstrate that it fails on the diagnosed revision before the fix.
3. Apply the smallest effective code or configuration change within the accepted boundary.
4. Run the regression test, adjacent non-regression checks, and repository-native checks listed in the plan.
5. Compare the causal mechanism before and after, not only the visible symptom.
6. Record any residual uncertainty, prevention or detection follow-up, and plan deviation.
7. Update canonical traceability with verified implementation and evidence references.
8. Produce a handoff for independent verification.

## Stop conditions

Stop and reopen diagnosis or planning when evidence contradicts the accepted cause, the fix requires broader scope, a new dependency or migration appears, the regression test does not discriminate the failure, or the change creates a new policy or interface impact.

## Prohibitions

Do not deploy, run production migrations, access or print secrets, modify remote services, upgrade dependencies, broaden refactoring, or weaken tests to make the fix pass.

## Required result

Report the regression demonstration, paths changed, causal effect, checks and exact results, deviations, residual uncertainty, traceability, and readiness for independent verification.
