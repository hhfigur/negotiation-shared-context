# Repository and Artifact Resolution

## Resolution order

Resolve `Shared-context` in this order and stop at the first verified match:

1. An explicit path supplied in the command arguments or current session.
2. `shared_context_path` in the current repository's `.sdlc/config.local.yaml`.
3. A Shared-context repository already open or accessible in the current workspace.
4. An immediate sibling whose Git root and repository metadata identify it as `Shared-context`.

Do not scan the full home directory. Do not search unrelated volumes or network locations.

## Verification

A candidate is valid only when:

- the path exists and is readable;
- the repository identity or content matches `Shared-context`;
- `sdlc/registry.yaml` or the accepted migration mapping confirms the artifact root;
- the requested change exists, or a new change is being explicitly created.

Record the resolved path locally in `.sdlc/config.local.yaml` when appropriate. Do not commit absolute machine paths.

## Active change resolution

Use this order:

1. Explicit `change-id` argument.
2. Current session's unambiguous active change.
3. `.sdlc/active-change.yaml`.

Never select a change merely because it was modified most recently. When multiple candidates exist, stop and request or record a decision.

## Access gaps

If Shared-context is inaccessible:

- allow read-only repository research that does not change lifecycle state;
- do not create local copies of canonical artifacts;
- do not implement or authorize a fix based on unavailable accepted artifacts;
- return the exact missing path or permission and a handoff.
