---
name: review-change
description: Commission and persist an independent Negotiation AI change review covering intent alignment, correctness, architecture, security, privacy, UX, Supabase, AI quality, evidence, and traceability before release. Use only through explicit invocation after verification.
argument-hint: "[change-id] [branch, commit, or PR reference]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Review Change Independently

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/ARTIFACT_CONTRACT.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/GATE_MODEL.md`
4. `${CLAUDE_PLUGIN_ROOT}/references/ASSURANCE_BOUNDARY.md`
5. `${CLAUDE_PLUGIN_ROOT}/references/POLICY_APPLICATION.md`
6. `${CLAUDE_PLUGIN_ROOT}/references/EVIDENCE_STANDARD.md`
7. `${CLAUDE_PLUGIN_ROOT}/references/TRACEABILITY.md`
8. Accepted artifacts, implementation revision, verification, repository review contract, and applicable approved policies

## Entry gate

Require an unambiguous implementation target and verification record. A failed or blocked verification may still be reviewed for diagnosis, but release approval cannot be recommended as though verification passed.

## Workflow

1. Create or refresh draft `review.md` without preselecting a recommendation.
2. Delegate implementation review to the read-only `negotiation-ai-sdlc:change-reviewer` agent.
3. Invoke relevant read-only policy assessment Skills for security, privacy, architecture, UX, Supabase, and AI quality based on actual scope. Apply only approved policies as mandatory.
4. Delegate an end-to-end mapping check to `negotiation-ai-sdlc:traceability-auditor`.
5. Consolidate findings without erasing disagreement or uncertainty. Use stable IDs, severity, evidence, impact, recommendation, disposition, and re-verification need.
6. Persist results in `review.md`. This applies to the orchestrating session, not only any delegated agent (see `ASSURANCE_BOUNDARY.md`): do not edit implementation, tests, or any accepted upstream artifact (`intent.md`, `spec.md`, `plan.md`, `verification.md`) during this Skill.
7. Update finding and review references in `traceability.yaml` — nothing beyond that.
8. Return unresolved findings to the Development Controller. A remediation must be independently re-verified before disposition becomes `FIXED`.
9. If a stale or inconsistent *other* lifecycle artifact is noticed during review (e.g. a disposition in `traceability.yaml` that has drifted from what a prior artifact records), record it as a finding here rather than editing that other artifact in this Skill invocation. Its correction is a separate, subsequently authorized step.

## Gate rule

Conclude only `APPROVE`, `CONDITIONAL_APPROVAL`, `REJECT`, or `BLOCKED`. List blocking findings and residual risks explicitly.

## Required result

Report review scope, policy status, findings by severity, traceability gaps, gate recommendation, required remediation or decisions, and exact next action.
