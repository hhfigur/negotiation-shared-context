# Traceability Contract

## Required direction

Trace both forward and backward:

`intent outcome -> requirement -> acceptance criterion -> plan step -> implementation path -> test or evidence -> finding -> release -> production outcome`

## Update rules

- Add only references that exist.
- Use stable requirement, acceptance, plan-step, evidence, risk, and finding IDs.
- Record repository logical name, path, branch, and commit or pull request when available.
- Do not use a branch name alone as immutable evidence.
- Update mappings when an accepted artifact changes.
- Keep unresolved mappings visible rather than guessing.

## Audit questions

- Does every in-scope intent outcome have requirements or an explicit non-software action?
- Does every requirement have acceptance criteria?
- Does every acceptance criterion have an implementation and evidence path?
- Does every material plan step map to a requirement or risk-control need?
- Are findings linked to the affected requirement, policy, code, or evidence?
- Can a release be reconstructed from exact revisions and evidence?
- Does the outcome record compare production evidence with original intent?
