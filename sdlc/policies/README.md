# SDLC Policy Registry

## Status rule

A policy in this directory is enforceable only when its YAML frontmatter contains:

```yaml
status: approved
approved_by: "<NAME_OR_ROLE>"
approved_date: "<YYYY-MM-DD>"
```

The provided files start as `draft`. They are structured decision templates, not statements that the project already complies with any framework, regulation, or organizational standard.

## Application

1. Identify relevant policies while creating `spec.md`.
2. Apply mandatory controls only from approved policies.
3. Record draft, missing, contradictory, or stale policies as risks or open decisions.
4. Record every exception with scope, rationale, compensating control, owner, and expiry.
5. Reassess policies during independent review when scope or architecture changed.

## Included domains

- `security.md`
- `privacy.md`
- `architecture.md`
- `ux.md`
- `supabase.md`
- `ai-quality.md`
