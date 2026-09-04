# Negotiation AI SDLC Artifact Home

## Purpose

This directory is the authoritative cross-repository record for product intent, specification, implementation planning, independent evidence, release decisions, incidents, and production outcomes.

Code and tests stay in their owning repositories. This directory links to them through `traceability.yaml`; it does not copy implementation artifacts.

## Change structure

```text
changes/<change-id>/
  intent.md
  spec.md
  plan.md
  debug-evidence.md       # defect or incident only
  verification.md
  review.md
  release.md
  outcome.md
  incident.md             # when applicable
  traceability.yaml
  evidence/
```

Only create artifacts when their stage begins. Empty templates must not be mistaken for completed work.

## Status vocabulary

Use these common values unless an existing approved project convention is retained:

- `draft`: under development; not approved.
- `in_review`: submitted for a named decision.
- `accepted`: approved as the basis for the next stage.
- `rejected`: not approved; rationale required.
- `superseded`: replaced by an explicitly linked artifact or version.
- `blocked`: cannot progress; blocker and owner required.
- `completed`: evidence is recorded and the artifact's work is complete.
- `released`: deployed through the recorded release decision.
- `measured`: outcome evidence has been collected.

## Gate rules

1. `intent.md` must be accepted before `spec.md` can be accepted.
2. `spec.md` must be accepted before `plan.md` can be accepted.
3. `plan.md` must be accepted before implementation begins.
4. For defects, `debug-evidence.md` must contain reproduction, root-cause conclusion, and regression-test strategy before a fix begins.
5. Verification and review must be produced independently from implementation and must cite evidence.
6. Release requires explicit residual-risk and rollback decisions.
7. Outcome measurement compares actual results with the original intent and may create a follow-up change.

## IDs and traceability

- Change ID: `YYYYMMDD-short-slug` by default.
- Requirement IDs: `FR-###` and `NFR-###`.
- Acceptance criteria: `AC-###`.
- Risks: `R-###`.
- Evidence: `E-###`.
- Hypotheses: `H-###`.
- Findings: `F-###`.

Every artifact references the same `change_id`. Every acceptance criterion maps to requirements, implementation, tests, and evidence in `traceability.yaml`.

## Policy use

Files under `policies/` are enforceable only when their frontmatter says `status: approved`. Draft files are scaffolding for owner decisions. Never claim compliance solely because a template exists.

## Working from separate repository windows

Each code repository uses `.sdlc/config.local.yaml` to locate this directory. The file is local and ignored by Git. Skills update the canonical change folder directly; they do not create local copies.

## Creating and validating a change

```bash
python3 sdlc/scripts/new_change.py --sdlc-root sdlc --id 20260902-example --title "Example change"
python3 sdlc/scripts/validate_change.py sdlc/changes/20260902-example
```

These scripts validate artifact structure only. Repository-native tests and human decisions remain required.
