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
3. Delegate technical diagnosis to the read-only `negotiation-ai-sdlc:root-cause-analyst` agent. Require reproduction, competing hypotheses, discriminating tests, causal chain, confidence, residual uncertainty, and regression-test strategy.
4. Do not edit source, tests, dependencies, configuration, database state, or remote services during diagnosis.
5. Persist the agent's evidence-based result in `debug-evidence.md`. Preserve `INSUFFICIENT_EVIDENCE` when that is the honest conclusion.
6. Link evidence in `traceability.yaml` without claiming a fix.
7. Set `fix_authorized: true` only after a named owner accepts the root-cause conclusion or explicitly authorizes a bounded diagnostic fix attempt, with rationale and date.

## Gate rule

A suspected file or plausible explanation is not a root cause. The diagnosis gate requires evidence that discriminates the selected cause from credible alternatives and a regression-test strategy.

## Required result

Report reproduction status, hypotheses tested, root-cause conclusion and confidence, residual uncertainty, regression-test strategy, smallest fix boundary, authorization state, and exact next action.
