---
name: create-spec
description: Translate an accepted Negotiation AI intent into a canonical, testable specification covering behavior, interfaces, data and Supabase ownership, non-functional requirements, policy implications, AI evaluation, and acceptance criteria. Use only through explicit invocation after intent acceptance.
argument-hint: "[change-id] [optional focus or source paths]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Create Specification

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/ARTIFACT_CONTRACT.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/GATE_MODEL.md`
4. `${CLAUDE_PLUGIN_ROOT}/references/POLICY_APPLICATION.md`
5. Accepted `intent.md`, canonical specification template, architecture references, and relevant repository instructions

## Entry gate

Confirm intent status, named acceptance decision, and revision. Stop with `BLOCKED` if intent is not accepted or has materially changed without re-acceptance.

## Workflow

1. Resolve the canonical change directory and inspect existing specification material before creating anything.
2. Delegate read-only codebase research to `negotiation-ai-sdlc:codebase-researcher` for relevant current-state facts. Do not use repository guesses as requirements.
3. Translate intent into uniquely identified functional and non-functional requirements.
4. Define complete user or system journeys, including errors, empty states, permissions, retries, recovery, and compatibility as relevant.
5. Identify interface producers and consumers, repository ownership, and frontend versus backend Supabase boundaries.
6. Apply only approved policies as mandatory. Record draft, missing, conflicting, or stale policy as a gap or decision.
7. Define AI behavior, evaluation, human oversight, and fallback only when the change affects model, prompt, retrieval, agent, tool, or AI output behavior.
8. Create testable acceptance criteria with required evidence.
9. Record alternatives, trade-offs, risks, assumptions, and open decisions.
10. Ask `negotiation-ai-sdlc:spec-critic` to review the draft independently. Integrate corrections visibly; do not erase unresolved findings.
11. Update requirement and acceptance-criterion entries in `traceability.yaml`.
12. Mark `accepted` only with a named decider, date, and rationale.

## Prohibitions

- Do not write implementation code or an implementation plan.
- Do not invent commands, schemas, APIs, or policy obligations.
- Do not collapse frontend and backend Supabase ownership into one assumed platform.

## Required result

Report artifact path, intent revision, requirement and acceptance-criterion counts, policy status, critic findings, open decisions, specification gate state, and exact next action.
