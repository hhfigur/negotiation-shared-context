---
name: close-change
description: Measure a released Negotiation AI change against its original intended outcome, record production evidence and unintended consequences, and decide whether to close, monitor, iterate, roll back, or create an incident. Use only through explicit invocation.
argument-hint: "[change-id] [measurement source or window]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Close the Production Feedback Loop

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/ARTIFACT_CONTRACT.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/EVIDENCE_STANDARD.md`
4. `${CLAUDE_PLUGIN_ROOT}/references/TRACEABILITY.md`
5. Accepted intent, release record, observability references, user feedback, support evidence, and existing outcome record

## Entry gate

Require a recorded release or explicitly document why outcome measurement is being performed for a partial, rolled-back, or failed release. Do not infer production success from merged code.

## Workflow

1. Create or update `outcome.md` for the defined measurement window.
2. Compare each original outcome measure with baseline, target, actual, source, confidence, and result.
3. Add user, operational, security, privacy, data, and AI-quality evidence as relevant.
4. Separate observed facts from causal inference and identify confounding changes.
5. Record unintended consequences and unresolved production signals.
6. Obtain a named decision: `CLOSE`, `MONITOR`, `ITERATE`, `ROLL_BACK`, or `CREATE_INCIDENT`.
7. For `ITERATE` or unmet outcomes, invoke the intent workflow for a linked follow-up change rather than silently extending the closed scope.
8. For operational harm or control-band breach, invoke the incident workflow.
9. Update traceability with outcome evidence and follow-up links.

## Prohibitions

Do not change production, manipulate metrics, omit negative evidence, or call an outcome successful without the measurement defined in intent.

## Required result

Report target versus actual outcomes, evidence confidence, unintended consequences, decision and owner, follow-up change or incident, traceability, and closure state.
