# Evidence Standard

A completion or quality claim must be supported by reproducible evidence appropriate to the claim.

## Minimum fields

- Evidence ID.
- Claim or acceptance criterion addressed.
- Producer or session role.
- Date and implementation revision.
- Method, exact command, or procedure.
- Environment and relevant inputs.
- Exit status or observed result.
- Output path, screenshot, log, trace, test, commit, or review reference.
- Limitation or coverage gap.

## Result vocabulary

Use `PASS`, `FAIL`, `BLOCKED`, `NOT_AVAILABLE`, or `NOT_APPLICABLE`. Do not convert a skipped, unavailable, or unobserved check into `PASS`.

## UI evidence

A build is not visual evidence. Record relevant journey, viewport, state, screenshot or browser result, and accessibility evidence available in the repository.

## Backend and data evidence

Record API or contract behavior, authorization positives and negatives, migration or schema checks, non-production environment, RLS or role behavior, and rollback or recovery evidence where relevant.

## AI evidence

Record evaluation-set version or source, model and prompt or configuration revision, metrics or rubric, comparison baseline, failure cases, limitations, and human-review outcome.

## Security and privacy evidence

Never copy secrets, tokens, personal data, privileged payloads, or sensitive logs into lifecycle artifacts. Redact while preserving the evidentiary meaning.
