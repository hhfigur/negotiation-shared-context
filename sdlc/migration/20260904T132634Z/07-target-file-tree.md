# Stage 2 — Target File Tree

`+` = new file/directory this migration would add. Unmarked = existing, unchanged. `~` = existing file, proposed to be merged/restructured (content preserved, not replaced). Nothing is marked for deletion (`ALLOW_DELETIONS_OR_RENAMES: false`).

**Delta review (2026-09-04, pass 1)**: this tree is consistent with the owner's corrections without structural changes — no separate `frontend_supabase`/`backend_supabase` instance directory or config was ever proposed here (that framing only appeared as `logical_instance` labels inside the `.sdlc/config.yaml` content shown in `09-proposed-file-diffs.md`, now annotated there). Two content-level (not structural) flags: `sdlc/policies/supabase.md` (below) and `controllers/AUDIT_REFACTORING_CONTROLLER.md` (below) must not be installed with their original kit wording verbatim — see the inline notes at each. (The kit itself was subsequently corrected in a separate authorized pass; both flags are resolved in the corrected kit — see `10-conflicts-and-decisions.md`.)

**Delta review (2026-09-04, pass 2 — C1/C3)**: also no structural change — C1 and C3 change file *content and role*, not the tree shape. `negotiationcoach-backend/docs/api-catalog.md` (existing, not shown as a separate tree line since `docs/` is already marked "existing, unchanged except proposed content fixes") is now explicitly the canonical API contract target. `negotiation-buddy/.claude/rules/api-contracts.md`'s annotation below changes from "SUPERSEDE_LATER" (fix in place) to "reduce to pointer." The four close-task Skills (already shown as existing, `KEEP pending item 7/8 decision`) gain a `LEGACY` marker per C3 — still no tree-shape change, see `09-proposed-file-diffs.md` Diff 8.

## shared-context/

```text
shared-context/
  CLAUDE.md                          (existing, KEEP)
  AGENTS.md                          (existing, KEEP)
  MEMORY.md                          (existing, KEEP)
  README-AUDIT.md                    (existing, SUPERSEDE_LATER proposal)
+ sdlc/
+   README.md                        (from shared-context-overlay/sdlc/README.md)
+   registry.yaml                    (from shared-context-overlay/sdlc/registry.yaml, <DISCOVER> fields resolved)
+   changes/                         (empty until pilot change is bootstrapped)
+   policies/
+     README.md
+     security.md                    (status: draft)
+     privacy.md                     (status: draft)
+     architecture.md                (status: draft)
+     ux.md                          (status: draft)
+     supabase.md                    (status: draft — content per 04-supabase-boundary-map.md's "Governance implications" section, not the kit's original POL-SUP-001 wording; C2 RESOLVED 2026-09-04, see 10-conflicts-and-decisions.md)
+     ai-quality.md                  (status: draft)
+   templates/
+     intent.md, spec.md, plan.md, debug-evidence.md, verification.md,
+     review.md, release.md, outcome.md, incident.md, traceability.yaml
+   scripts/
+     new_change.py, validate_change.py
    migration/
      20260904T132634Z/              (this analysis's own output - already exists)
+ controllers/
+   DEVELOPMENT_CONTROLLER.md         (from shared-context-overlay/controllers/)
+   AUDIT_REFACTORING_CONTROLLER.md   (must have "Lovable Plan Mode" removed from its invocation-path list before adoption — see 05-instruction-and-skill-map.md delta review; Lovable is retired)
+   SESSION_HANDOFF_TEMPLATE.md
+ tooling/
+   claude-marketplace/
+     README.md
+     .claude-plugin/marketplace.json
+     plugins/negotiation-ai-sdlc/
+       .claude-plugin/, CHANGELOG.md, README.md
+       agents/            (8 read-only assurance agents)
+       skills/             (10 manual lifecycle + 6 advisory policy Skills)
+       references/         (ARTIFACT_CONTRACT.md, DEBUG_PROTOCOL.md, EVIDENCE_STANDARD.md,
+                             GATE_MODEL.md, POLICY_APPLICATION.md, REPOSITORY_RESOLUTION.md,
+                             TRACEABILITY.md)
+   hook-design/
+     HOOK_CANDIDATES.md    (documentation only - no hook wired into any settings.json)
  .claude/                           (existing commands/skills/settings, all KEEP - see 06-gap-analysis.md item 7-8)
  docs/                              (existing, unchanged except proposed content fixes - see 10-conflicts-and-decisions.md)
  product/                           (existing, unchanged)
  tasks/                             (existing, unchanged)
```

## negotiation-buddy/ (frontend)

```text
negotiation-buddy/
~ CLAUDE.md                         (merge with repo-overlays/frontend/CLAUDE.md.template structure - see 09)
  AGENTS.md                         (existing, KEEP)
  MEMORY.md                         (existing, KEEP)
+ .sdlc/
+   config.yaml                     (from repo-overlays/frontend/.sdlc/config.yaml.template, filled in)
+   config.local.yaml               (gitignored - local absolute path to shared-context)
+   active-change.yaml              (only once a real pilot change is selected, per acceptance criteria "Pilot")
+ REVIEW.md                         (from repo-overlays/frontend/REVIEW.md.template)
  .claude/
    rules/
      architecture.md, data-access.md, db-boundaries.md, ui-boundaries.md,
      protected-files.md            (existing, all KEEP)
~     api-contracts.md              (existing, reduce to pointer to ../negotiationcoach-backend/docs/api-catalog.md - C1 RESOLVED 2026-09-04, see 10-conflicts-and-decisions.md and 09-proposed-file-diffs.md Diff 3)
+     00-sdlc-contract.md           (from repo-overlays/frontend/.claude/rules/00-sdlc-contract.md)
+     frontend-ui.md                (from repo-overlays/frontend/.claude/rules/frontend-ui.md, paths: verified against real src/ structure)
+     frontend-tests.md             (from repo-overlays/frontend/.claude/rules/frontend-tests.md, paths verified)
    hooks/                          (existing 4 hooks, all KEEP - already active/proven)
    skills/                         (existing 5 skills, all KEEP pending item 7/8 decision)
+ .gitignore                        (~ append line from repo-overlays/frontend/.gitignore.additions: ".sdlc/config.local.yaml")
  docs/                             (existing, unchanged except proposed content fixes)
  src/, supabase/, scripts/, tasks/, .lovable/, .superpowers/   (existing, unchanged)
```

## negotiationcoach-backend/

```text
negotiationcoach-backend/
~ CLAUDE.md                         (merge with repo-overlays/backend/CLAUDE.md.template structure - see 09)
  agents.md                         (existing, KEEP)
  MEMORY.md                         (existing, KEEP)
+ .sdlc/
+   config.yaml                     (from repo-overlays/backend/.sdlc/config.yaml.template, filled in)
+   config.local.yaml               (gitignored)
+   active-change.yaml              (pilot only)
+ REVIEW.md                         (from repo-overlays/backend/REVIEW.md.template)
  .claude/
    rules/
      architecture.md, data-access.md, ui-boundaries.md, protected-files.md   (existing, KEEP)
~     db-boundaries.md              (existing, MERGE - fix nonexistent src/engine/simulationEngine.ts reference)
+     00-sdlc-contract.md           (from repo-overlays/backend/.claude/rules/00-sdlc-contract.md)
+     backend-tests.md              (from repo-overlays/backend/.claude/rules/backend-tests.md, paths verified)
+     supabase-data.md              (from repo-overlays/backend/.claude/rules/supabase-data.md, paths verified)
    hooks/                          (existing 2 hooks, KEEP - already active/proven)
    skills/                         (existing 5 local + 5 symlinked, all KEEP pending item 7/8 decision)
+ .gitignore                        (~ append line from repo-overlays/backend/.gitignore.additions)
  docs/                             (existing, unchanged except proposed content fixes)
  src/, supabase/, scripts/, tasks/, .superpowers/   (existing, unchanged)
```

## Not shown / explicitly out of scope for this migration

- No `backend-api-domain.md` rule template was enumerated above with specific detail because its full content was not read this pass (only its existence in `repo-overlays/backend/.claude/rules/`); it would be added alongside `backend-tests.md`/`supabase-data.md` following the same pattern.
- No hook is added to any `.claude/settings.json` — `HOOK_CANDIDATES.md` is documentation only per constraint #10 and gap-analysis item 11.
- No file is deleted or renamed anywhere in this tree.
