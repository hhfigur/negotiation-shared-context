# Negotiation AI Local Claude Code Marketplace

This marketplace distributes one versioned plugin across the frontend, backend, and Shared-context workspaces without copying lifecycle Skills into each repository.

## Expected installation

Use Claude Code 2.1.233 or later for current plugin-agent validation behavior.

Installing this plugin does **not** hot-load it into an already-running Claude Code session.
Marketplace registration and plugin installation update on-disk configuration only; the running
session's skill and slash-command registry is not refreshed until an explicit reload. Follow this
exact sequence — do not stop after step 3 assuming the plugin is already usable:

1. **Validate** the marketplace and plugin manifests before registering them:
   ```text
   claude plugin validate <ABSOLUTE_PATH_TO_SHARED_CONTEXT>/tooling/claude-marketplace
   ```
2. **Register the marketplace**:
   ```text
   /plugin marketplace add <ABSOLUTE_PATH_TO_SHARED_CONTEXT>/tooling/claude-marketplace
   ```
   Select the installation scope according to the desired visibility. Do not assume a user-wide
   installation is appropriate.
3. **Install the plugin**:
   ```text
   /plugin install negotiation-ai-sdlc@negotiation-ai-local
   ```
4. **Reload the running session** — required, not optional, even though the CLI reports success
   for steps 2-3:
   ```text
   /reload-plugins
   ```
5. **Verify lifecycle commands are actually available before starting a change.** Confirm at
   least one gate-controlled Skill resolves as a live slash command in this session (e.g. by
   checking `/skills` output for `negotiation-ai-sdlc:capture-intent` and the other lifecycle
   Skills) before treating the plugin as ready. Do not assume steps 1-4 succeeding implies this —
   verify it directly, in this session, every time.

## Verification

```text
/plugin
/skills
/context
/hooks
/doctor
```

`/skills` is the step that actually confirms lifecycle commands are live in *this* session — the
other four confirm installation/configuration state, not session-level command availability.

Before publishing an update:

1. Update the plugin version in both manifest locations.
2. Update the plugin changelog.
3. Run the migration kit static validator.
4. Run `claude plugin validate <PLUGIN_PATH> --strict` when the CLI is available.
5. Test at least one manual lifecycle Skill and one read-only agent in a non-production workspace.
