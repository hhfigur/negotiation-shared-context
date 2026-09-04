# Lifecycle Gate Model

## Intent gate

Pass only when the problem or opportunity, desired outcome, scope, constraints, affected users, measures, assumptions, and unresolved questions are explicit and a named owner accepts the artifact.

## Specification gate

Pass only when intent is accepted; requirements and acceptance criteria are testable; interfaces, data, authorization, errors, and relevant policy implications are explicit; and a named owner accepts the artifact.

## Plan gate

Pass only when the specification is accepted; current-state evidence supports the approach; repository workstreams, sequence, exact paths or bounded discovery, tests, risks, rollback, observability, and rejected options are explicit; and a named owner accepts the artifact.

## Diagnosis gate

For defects, pass only when reproduction was attempted, raw evidence exists, competing hypotheses were evaluated, the root-cause conclusion is supported or uncertainty is explicit, a discriminating regression-test strategy exists, and `fix_authorized` is true.

## Verification gate

Pass only when an independent verifier evaluates the accepted criteria and relevant quality checks against a defined implementation revision and records failures, unavailable checks, and limitations honestly.

## Review gate

Pass only when an independent reviewer has no unresolved blocker or high-severity issue unless a named owner explicitly accepts the risk according to approved governance.

## Release gate

Pass only when the exact revisions, verification and review results, deployment and rollback procedure, observability, control bands, residual risks, and decision owner are recorded.

## Outcome gate

Close only when measurement evidence exists or the record explicitly states why measurement is inconclusive, and the owner decides to close, monitor, iterate, roll back, or create an incident.

## Gate behavior

- `blocked` is a valid conclusion and must name the blocker and owner.
- Never infer acceptance from silence, a chat statement without persistence, or the existence of a file.
- A material change to an accepted artifact reopens the relevant gate.
