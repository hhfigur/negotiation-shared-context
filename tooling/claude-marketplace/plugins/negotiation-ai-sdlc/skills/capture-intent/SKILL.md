---
name: capture-intent
description: Create or refine the canonical Negotiation AI intent artifact from a problem, opportunity, ticket, incident, interview, or owner statement while preserving originator language and separating desired outcomes from implementation. Use only through explicit invocation for a new or existing change.
argument-hint: "[change-id-or-NEW] [origin summary or source path]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Capture Intent

Use `$ARGUMENTS` to identify the change and source material.

## Read first

1. `${CLAUDE_PLUGIN_ROOT}/references/REPOSITORY_RESOLUTION.md`
2. `${CLAUDE_PLUGIN_ROOT}/references/ARTIFACT_CONTRACT.md`
3. `${CLAUDE_PLUGIN_ROOT}/references/GATE_MODEL.md`
4. Canonical `sdlc/templates/intent.md`
5. Relevant supplied source material and existing product context

## Workflow

1. Resolve Shared-context and the target change ID. For `NEW`, propose the default `YYYYMMDD-short-slug`; do not create it when ambiguous.
2. Check for an existing change or semantically overlapping intent. Link or update rather than creating a duplicate.
3. Preserve the originator's terminology for the problem and desired outcome. Separate observed facts, inference, assumptions, constraints, and proposed implementation.
4. Ask only questions that materially affect outcome, scope, constraints, users, measures, or risk. When operating non-interactively, record unresolved questions instead of guessing.
5. Draft or update only `intent.md` and verified intent-level entries in `traceability.yaml`.
6. Do not create `spec.md`, choose architecture, or authorize implementation.
7. Run the intent checklist. Mark `in_review` only when decision-ready.
8. Mark `accepted` only with a named decider, decision date, and rationale supplied or confirmed by the owner.

## Required result

Report:

- canonical artifact path;
- facts, assumptions, and open questions;
- material scope and outcome measures;
- duplicate or conflict checks;
- current intent gate state;
- exact next action.
