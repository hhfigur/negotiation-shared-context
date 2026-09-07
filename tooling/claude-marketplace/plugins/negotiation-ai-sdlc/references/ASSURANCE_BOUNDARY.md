# Assurance Read-Only Boundary

Applies to every Skill whose purpose is independent assurance: `verify-change`, `review-change`,
and the diagnosis portion of `diagnose-bug`.

## Scope of the rule

The read-only boundary applies to the entire assurance stage — the delegated read-only agent
*and* the orchestrating session that dispatched it. A sub-agent's restricted tool grant is not a
license for the orchestrator to do, with its own broader tool access, what the sub-agent was
built not to do. Observed failure mode this rule closes: during a pilot, a delegated verifier
stayed correctly read-only (its own tool grant excluded `Edit`/`Write`), but the orchestrating
session then edited a separate, already-accepted artifact's stale status line in a later step of
the same nominally read-only turn.

## Allowed during an assurance stage

- Creating or refreshing the one designated result artifact for that stage: `verification.md` for
  `verify-change`; `review.md` for `review-change`; `debug-evidence.md` for the diagnosis portion
  of `diagnose-bug`.
- Updating only the specific `traceability.yaml` references each Skill's own workflow explicitly
  authorizes — never more than that Skill's stated scope.

## Not allowed during an assurance stage, by the orchestrator or any delegated agent

- Modifying implementation code, tests, configuration, or dependencies.
- Modifying any accepted upstream artifact (`intent.md`, `spec.md`, `plan.md`, or any artifact
  from an earlier, already-accepted gate).
- Repairing an unrelated lifecycle artifact discovered to be stale or inconsistent while
  performing this stage.
- Silently correcting a finding instead of reporting it.

## When a stale or inconsistent artifact is discovered mid-assurance

Record it as an explicit finding — with severity, evidence, and a recommendation — in the current
stage's own result artifact. Do not edit the other artifact in the same turn. A correction to it
is a separate, subsequently and explicitly authorized remediation/bookkeeping step, following the
same authorization discipline as any other change to an accepted or completed record.

## Known enforcement limit

Tool-permission grants in this plugin's Skills are file-type-scoped (e.g. `Read, Grep, Glob,
Write, Edit`), not path-scoped — they cannot technically restrict *which* file a Write/Edit call
targets. This rule is therefore an instruction-level control, not a tool-level guarantee. Treat any
edit outside the two allowances above, made during one of these Skills, as a violation to report
and correct going forward, not as evidence the rule is unnecessary.
