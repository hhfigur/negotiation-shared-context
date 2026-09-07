# Changelog

## 0.1.1

Post-pilot hardening, based on the `20260904-health-endpoint-version` pilot retrospective.

- Add `references/ASSURANCE_BOUNDARY.md`: the read-only boundary during Verification, Review, and
  diagnosis now explicitly binds the orchestrating session, not only a delegated agent. A stale or
  inconsistent artifact discovered mid-assurance must be recorded as a finding, not silently
  corrected in the same turn.
- Add a deterministic-remediation fast path to `diagnose-bug`/`fix-diagnosed-bug` and
  `GATE_MODEL.md`, for defects whose root cause is already independently evidenced and whose fix
  is mechanical — with six explicit, evidenced entry criteria, still requiring owner authorization
  and independent re-verification. Full hypothesis-driven diagnosis remains the default whenever
  any criterion is uncertain.
- Add `diagnosis_mode` and a "Diagnosis mode" criteria table to the `debug-evidence.md` template.
- Rewrite `sdlc/scripts/validate_change.py` to remove its undeclared PyYAML runtime dependency —
  it now uses a documented, zero-dependency, stdlib-only parser for artifact frontmatter and a
  structural (non-semantic) presence check for `traceability.yaml`, with its parsing limits
  stated explicitly rather than silently assumed away.
- Rewrite the marketplace `README.md`'s installation section as a mandatory, ordered sequence
  (validate → register marketplace → install → `/reload-plugins` → verify lifecycle commands are
  live in the current session) — installing the plugin does not hot-load it into an
  already-running session.
- Add lifecycle-command-availability and deterministic-fast-path guidance to
  `controllers/DEVELOPMENT_CONTROLLER.md`'s session-start and debugging-gate sections.

## 0.1.0

- Add ten explicitly invoked lifecycle Skills.
- Add six advisory policy assessment Skills.
- Add eight read-only specialist agents.
- Add repository resolution, artifact, gate, policy, evidence, debugging, and traceability contracts.
- Keep hooks and external integrations out of the initial version.
