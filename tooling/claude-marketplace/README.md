# Negotiation AI Local Claude Code Marketplace

This marketplace distributes one versioned plugin across the frontend, backend, and Shared-context workspaces without copying lifecycle Skills into each repository.

## Expected installation

Use Claude Code 2.1.233 or later for current plugin-agent validation behavior.

From a Claude Code session with access to the local path:

```text
/plugin marketplace add <ABSOLUTE_PATH_TO_SHARED_CONTEXT>/tooling/claude-marketplace
/plugin install negotiation-ai-sdlc@negotiation-ai-local
/reload-plugins
```

Select the installation scope in Claude Code according to the desired visibility. Do not assume a user-wide installation is appropriate.

## Verification

```text
/plugin
/skills
/context
/hooks
/doctor
```

Before publishing an update:

1. Update the plugin version in both manifest locations.
2. Update the plugin changelog.
3. Run the migration kit static validator.
4. Run `claude plugin validate <PLUGIN_PATH> --strict` when the CLI is available.
5. Test at least one manual lifecycle Skill and one read-only agent in a non-production workspace.
