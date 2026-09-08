# Negotiation AI SDLC Plugin

## Compatibility

Use Claude Code 2.1.233 or later for current plugin-agent validation behavior.

## Purpose

Provide one reusable control layer for the artifact chain:

`intent -> specification -> plan -> implementation -> verification -> review -> release -> outcome`

The plugin does not own project state. Canonical state remains in `Shared-context/sdlc/changes/<change-id>/`.

## Manual lifecycle Skills

These commands change lifecycle state or authorize consequential work, so they require explicit invocation:

- `capture-intent`
- `create-spec`
- `create-plan`
- `implement-change`
- `diagnose-bug`
- `fix-diagnosed-bug`
- `verify-change`
- `review-change`
- `incident-to-intent`
- `close-change`

## Advisory policy Skills

These Skills may be selected by the model when their domain is relevant. They run in a forked read-only policy-auditor context:

- `assess-security`
- `assess-privacy`
- `assess-architecture`
- `assess-ux`
- `assess-supabase`
- `assess-ai-quality`

Only approved policies are normative. Draft or missing policies produce advisory gaps, not false compliance claims.

## Agents

The plugin includes read-only agents for repository research, specification and plan critique, root-cause analysis, verification, change review, policy assessment, and traceability audit.

## Repository resolution

Read `references/REPOSITORY_RESOLUTION.md`. Skills must use an explicit Shared-context path or local `.sdlc/config.local.yaml`; they must not scan the full home directory or create duplicate change artifacts.

## Safety

- Implementation Skills do not pre-authorize editing or shell execution through `allowed-tools`; normal Claude Code permissions remain in force.
- Assurance agents have no Write or Edit tool.
- The plugin defines no hooks. Deterministic hooks are introduced separately only after commands and rollback behavior are proven.
- No Skill is authorization to deploy, change production, access secrets, upgrade dependencies, or modify remote services.
