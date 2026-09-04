# Hook Candidates - Inactive by Design

No hook in this migration kit is active. Hooks are deterministic enforcement and must be introduced only after exact repository commands, matchers, latency, failure mode, and rollback have been tested.

## Activation criteria for any hook

1. The underlying command is already proven locally and in repository documentation or CI.
2. The matcher targets only intended tools and paths.
3. Secret and personal-data handling is reviewed.
4. Timeout and non-zero-exit behavior are understood.
5. False positives and developer interruption cost are measured.
6. Bypass or recovery behavior is explicit and auditable.
7. The hook is tested on a dedicated branch and can be removed in one change.
8. The owner approves activation and scope.

## Candidate 1 - Lifecycle artifact validation after write

- Purpose: validate changed SDLC artifacts and prerequisite gates.
- Candidate trigger: post-write or post-edit for paths under `sdlc/changes/`.
- Dependency: stable `validate_change.py` behavior and acceptable latency.
- Failure behavior: report validation errors without corrupting the write.

## Candidate 2 - Repository formatter or linter after edit

- Purpose: provide rapid feedback on changed source files.
- Candidate trigger: post-edit with verified path matcher.
- Dependency: exact fast command that supports targeted files.
- Risk: latency, generated-code modification, and noisy failures.

## Candidate 3 - Secret and local-file protection

- Purpose: prevent committing known local path files or likely secrets.
- Candidate trigger: pre-commit or pre-shell command, depending on supported workflow.
- Dependency: repository-approved scanner and low false-positive rate.
- Note: do not implement a home-grown secret detector as a compliance claim.

## Candidate 4 - Implementation gate check

- Purpose: warn or block source edits when no accepted plan is active.
- Candidate trigger: pre-write or pre-edit in code paths.
- Dependency: reliable active-change resolution and exception path for emergency containment.
- Risk: blocking legitimate exploratory or incident work.

## Candidate 5 - Stop or completion evidence check

- Purpose: detect unsupported completion claims or missing handoff.
- Candidate trigger: stop event if supported by the installed Claude Code version.
- Dependency: stable artifact and evidence schema.
- Risk: repetitive loops or false completion prevention.

## Rollout

Activate at most one hook at a time. Observe real use, record failures and friction, and retain a simple rollback before considering the next candidate.
