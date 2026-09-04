# Artifact Contract

## Canonical chain

- `intent.md`: problem, desired outcome, affected users, scope, constraints, baseline, measures, assumptions, and decision.
- `spec.md`: testable functional and non-functional requirements, interfaces, data, AI behavior, acceptance criteria, policy implications, alternatives, and decision.
- `plan.md`: current-state evidence, exact workstreams, paths or bounded discovery, sequence, tests, risks, rollback, observability, rejected options, and decision.
- `debug-evidence.md`: reproduction, hypotheses, discriminating tests, causal chain, root-cause conclusion, confidence, regression strategy, and fix authorization.
- `verification.md`: independent execution or inspection of acceptance and quality evidence.
- `review.md`: independent findings, policy assessment, traceability assessment, and gate recommendation.
- `release.md`: revision, rollout, entry evidence, observability, rollback, residual risk, and release decision.
- `outcome.md`: measured result against original intent and follow-up decision.
- `incident.md`: impact, detection, timeline, containment, cause, follow-up, and closure.
- `traceability.yaml`: verified links among all artifacts, repositories, implementation, tests, evidence, findings, releases, and outcomes.

## General rules

1. Every artifact carries the same `change_id`.
2. Status and decision records must agree. A status field alone is not an approval.
3. Facts, assumptions, decisions, risks, and open questions must be distinguishable.
4. Links point to canonical sources. Do not paste large duplicate sections from architecture or policy documents.
5. Evidence references must exist and state producer, time, method, and result where possible.
6. Do not create empty later-stage artifacts merely to make the directory look complete.
7. Update `updated` metadata and decision history when meaning changes.
8. Preserve superseded artifacts or revisions through explicit references; do not erase history.
