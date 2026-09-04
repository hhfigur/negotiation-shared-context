# Stage 1 — Command and Toolchain Evidence

Every command below was found verbatim in a manifest, script, or config file — none invented. `NOT_FOUND` means the category was checked for and genuinely absent, not skipped.

## Delta review — current vs. historical tooling (owner-confirmed, 2026-09-04)

The owner has confirmed as current fact: **Render.com** is the active hosting/deployment platform for both code repos, and **Lovable is no longer used for active frontend development** (Claude Code is the sole current dev path for `negotiation-buddy`). Applying that to every row below:

| Tooling reference | Status | Basis |
|---|---|---|
| Render.com (frontend static site, backend auto-deploy from `main`) | **Current** — owner-confirmed | Repository evidence is prose-only (`MEMORY.md` in both code repos); no `render.yaml`/Dockerfile/Procfile exists in either repo, so the deploy trigger/config itself remains unverifiable from repo content alone (`NOT_FOUND` rows below are unchanged and still accurate) |
| Railway (any URL, base-URL default, or deploy reference anywhere in `docs/`/`.claude/rules/`) | **Historical only** — owner-confirmed retired | No repository evidence needed beyond the owner statement; every live occurrence is a documentation-debt item, not a live-tooling question — see `06-gap-analysis.md` delta review |
| Lovable (as an active frontend development tool/editor) | **Historical only** — owner-confirmed retired | `lovable-tagger` remains a build-time Vite plugin dependency in `negotiation-buddy/package.json`/`vite.config.ts` — this is inert tooling residue, not evidence of active Lovable-based development, and is unaffected by this correction |
| Supabase Edge Function deploy / type-gen commands listed below | **Current, unaffected by these corrections** | These commands operate against whichever Supabase project is active (`gpllrgkuozytyrmpfwbb` — see `04-supabase-boundary-map.md`); the owner's corrections concern hosting/dev-tool identity, not this toolchain |

No row in the tables below was found to describe a *currently invoked* Railway or Lovable-development command — the staleness is entirely in prose/documentation (`docs/lovable-workspace-knowledge.md`'s deploy notes, various `.claude/rules/*`), not in `package.json` scripts or `scripts/verify.sh`, which is why the tables that follow are unchanged from Stage 1: they were already tooling-accurate. The correction's effect is entirely on how *documentation* referencing this toolchain should be read and corrected (`08-migration-plan.md` Phase E, `09-proposed-file-diffs.md`).

## Shared-context

Not a buildable/testable code repository — no `package.json`/build system. Its only "commands" are Claude Code slash commands and Skills (see `05-instruction-and-skill-map.md`). No lint/test/build/deploy toolchain applies here.

## negotiation-buddy (frontend)

| Command | Source file | What it does |
|---|---|---|
| `vite` | `package.json` → `scripts.dev` | Start Vite dev server (port 8080 per `vite.config.ts`) |
| `vite build` | `package.json` → `scripts.build` | Production build |
| `vite build --mode development` | `package.json` → `scripts.build:dev` | Dev-mode build (source maps, keeps `lovable-tagger` active) |
| `eslint .` | `package.json` → `scripts.lint` | Lint via flat config `eslint.config.js`; note `@typescript-eslint/no-unused-vars` is explicitly turned `off` |
| `vite preview` | `package.json` → `scripts.preview` | Preview built output |
| `vitest run` | `package.json` → `scripts.test` | Run test suite once (jsdom env, `src/test/setup.ts`) |
| `vitest` | `package.json` → `scripts.test:watch` | Watch-mode tests |
| `npx tsc --noEmit -p tsconfig.app.json` | `scripts/verify.sh` step 1/6 | Typecheck against `tsconfig.app.json` |
| `npx vitest run` | `scripts/verify.sh` step 2/6 | Same as `npm test`, invoked directly |
| `npm run build` | `scripts/verify.sh` step 3/6 | Production build, hard-fail gate |
| contract-check | `scripts/verify.sh` step 4/6 | `[SKIPPED]` — not CLI-automatable, Skill-driven only |
| curl-assert / smoke | `scripts/verify.sh` step 5/6 | `[SKIPPED]` — no server-dependent step defined for this repo |
| `npm run lint` | `scripts/verify.sh` step 6/6 | Run as `[WARN]`-only — 54 pre-existing problems explicitly tolerated, not a hard gate |
| `supabase functions deploy <name>` | `docs/lovable-workspace-knowledge.md` (marked "Inferred" by that doc itself) | Edge function deploy — not found as an actual script/workflow in the repo |
| `supabase gen types typescript --project-id <id> > src/integrations/supabase/types.ts` | `docs/lovable-workspace-knowledge.md`, `.claude/rules/db-boundaries.md` (`--local` variant given there) | Type regeneration — two docs give inconsistent invocations, no wrapper script found |
| CI workflow | — | `NOT_FOUND` — no `.github/workflows/` directory exists |
| Deploy command/config in-repo | — | `NOT_FOUND` — no `render.yaml`/`vercel.json`/`netlify.toml`; deploy target described only in `MEMORY.md` prose ("Render.com Static Site, auto-deploy from `main`"), not codified as a repo artifact |
| e2e / browser / visual-regression test command | — | `NOT_FOUND` — no Playwright/Cypress/Percy/Chromatic config anywhere in the repo |
| Package manager | ambiguous | `package-lock.json`, `bun.lock`, and `bun.lockb` all coexist at root — see `10-conflicts-and-decisions.md` |

## negotiationcoach-backend

| Command | Source file | What it does |
|---|---|---|
| `nodemon --exec ts-node src/api/routes.ts` | `package.json` → `scripts.dev` | Dev server with hot reload |
| `tsc` | `package.json` → `scripts.build` | Compile TS to `dist/` per `tsconfig.json` |
| `node dist/api/routes.js` | `package.json` → `scripts.start` | Run compiled production server |
| `tsc --noEmit` | `package.json` → `scripts.typecheck` | Type-check without emitting |
| `ts-node --project tsconfig.test.json tests/layer1/layer1.test.ts && ...` (10 files chained with `&&`) | `package.json` → `scripts.test` | Runs each test file sequentially via `ts-node`; hand-rolled `console.assert`/throw assertions, no Jest/Mocha installed. Chain covers: layer1, layer2, telemetry, smlParser, promptBuilder, debriefEngine, simulationLoop, opponentEngine.regression, layer3/index, simulationRoutes |
| `./node_modules/.bin/tsc --noEmit` | `.claude/settings.local.json` allowlist | Same as typecheck, pre-approved for convenience |
| verify harness (composite) | `scripts/verify.sh` | Orders: (1) `tsc --noEmit`, (2) `npm test`, (3) live curl-based smoke checks (`curl-assert.sh`, `smoke-enrich.sh`) against a running dev server using a real seeded JWT (`lib-jwt.sh` + `seed-verify-user*.ts`) |
| Lint | — | `NOT_FOUND` — no lint script in `package.json`, no ESLint config file anywhere in the repo |
| Format | — | `NOT_FOUND` — no format script, no `.prettierrc`/`biome.json` |
| CI workflow | — | `NOT_FOUND` — no `.github/workflows/` directory |
| Deploy command/config in-repo | — | `NOT_FOUND` — no Dockerfile, Procfile, or render.yaml; per `MEMORY.md`, Render.com auto-deploy from `main`, configured entirely outside the repo (dashboard) |
| Migration apply | `.claude/rules/db-boundaries.md`, `CLAUDE.md` | Documented as "apply via `generate_typescript_types`/`apply_migration` MCP tool" — but `tasks/lessons.md` L-004 states the Supabase MCP available in this environment is permanently connected to a *different, unused* project (`ivrfsjxdfzxrimexvoft`); documented workaround is migration-files-only plus manual dashboard apply, never MCP. **Not independently re-verified this pass** — flagged in `04-supabase-boundary-map.md`. |

## Cross-repo toolchain observations

- **No repository has a CI workflow.** Verification in both code repos is a well-built local/manual `scripts/verify.sh` oracle that nothing invokes automatically on push/PR.
- **Neither repo has a deploy config committed** — both describe Render.com as the target only in prose (`MEMORY.md`), meaning the actual deploy trigger/config is entirely outside version control on both sides.
- **Lint coverage is asymmetric**: frontend has ESLint (with `no-unused-vars` disabled, and lint is a non-blocking `[WARN]` step in its own verify harness); backend has no lint tooling at all.
- **Test frameworks differ**: frontend uses Vitest (a real framework, jsdom); backend uses hand-rolled `ts-node`-executed assertion scripts chained with `&&` (fragile — a failure partway through the chain still runs the earlier files but any single `throw` aborts the rest via shell `&&` short-circuit, and there is no framework-level reporting/aggregation).
- **Neither repo has e2e or visual/browser test tooling** — a real gap against the master prompt's "frontend completion includes visual or browser evidence when UI behavior changes" acceptance criterion; that evidence, if produced, would currently have to come from ad hoc manual verification, not an automated harness.
