---
name: diagnose-bug
description: Run an evidence-first diagnosis for a Negotiation AI bug or incident and create the canonical debug evidence record without modifying implementation code. Use only through explicit invocation before any fix.
argument-hint: "[change-id] [symptom or evidence path]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Diagnose Bug Without Fixing

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/DEBUG_PROTOCOL.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/EVIDENCE_STANDARD.md`
4. `${CLAUDE_PLUGIN_ROOT}/references/GATE_MODEL.md`
5. Canonical debug-evidence template and relevant accepted artifacts

## Workflow

1. Resolve or create the defect change record without duplicating an existing incident or change.
2. Record reported and expected behavior, impact, environment, revision, and available raw evidence.
3. Decide the diagnosis mode before proceeding — see "Deterministic-remediation fast path" below. Default to the full workflow (steps 4-7) unless every fast-path criterion is met and the owner has explicitly authorized it.
4. Delegate technical diagnosis to the read-only `negotiation-ai-sdlc:root-cause-analyst` agent. Require reproduction, competing hypotheses, discriminating tests, causal chain, confidence, residual uncertainty, and regression-test strategy.
5. Do not edit source, tests, dependencies, configuration, database state, or remote services during diagnosis. This applies to the orchestrating session as well as the delegated agent (`ASSURANCE_BOUNDARY.md`).
6. Persist the agent's evidence-based result in `debug-evidence.md`. Preserve `INSUFFICIENT_EVIDENCE` when that is the honest conclusion.
7. Link evidence in `traceability.yaml` without claiming a fix.
8. Set `fix_authorized: true` only after a named owner accepts the root-cause conclusion or explicitly authorizes a bounded diagnostic fix attempt, with rationale and date.

## Deterministic-remediation fast path

Skip delegating to `root-cause-analyst` (step 4) and the competing-hypotheses table only when
**all** of the following are true — record which ones and why directly in `debug-evidence.md`,
not merely assert the exception:

- the exact defect is already independently evidenced (e.g. by a prior independent review or
  verification finding), not merely suspected;
- the root cause is deterministic — the same input reliably produces the same outcome, no
  environment- or timing-dependence;
- no competing plausible root-cause hypothesis remains once the existing evidence is read;
- the affected artifact or location is identified precisely (exact file, exact line or field);
- the remediation is mechanical and minimal — no architectural or design decision is required;
- the owner explicitly authorizes skipping full diagnosis, with rationale, in the same message
  that authorizes the fix.

If any one of these is false, use the full workflow (steps 4-7) — do not partially apply the fast
path. The fast path still requires: owner authorization with rationale and date, a bounded
remediation, evidence, traceability, and independent re-verification before disposition becomes
`FIXED`. It never weakens the diagnose-before-fix rule for a defect with genuine uncertainty.

## Gate rule

A suspected file or plausible explanation is not a root cause. The diagnosis gate requires evidence that discriminates the selected cause from credible alternatives and a regression-test strategy — or, for the fast path, an explicit, evidenced statement of why no competing hypothesis is credible.

## Required result

Report diagnosis mode used (full or fast path, with fast-path criteria satisfied if applicable), reproduction status, hypotheses tested (or why none were needed), root-cause conclusion and confidence, residual uncertainty, regression-test strategy, smallest fix boundary, authorization state, and exact next action.
