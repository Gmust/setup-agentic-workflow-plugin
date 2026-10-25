# Behavioral evaluation

Use this when maintaining the skill. Helper tests validate mechanics only.
Evaluate actual skill use in disposable repositories without real user data.
Run each setup twice with the same answers; compare file bytes after each run.
Second runs should make no changes when the requested setup is already complete.
Do not regenerate timestamps or handoff text solely because setup was invoked.
Every scenario below also requires a handoff that exists and records what was
actually verified, including checks not run and the reason. A run that produces
instructions but no handoff fails its scenario, however good the instructions are.

| Scenario | Request and starting state | Expected observable outcome |
| --- | --- | --- |
| Empty | Empty directory; ask for setup for both agents, no stack provided | Ask for intended stack before suggesting build checks; no invented product scaffold or passing checks. After answers, create appropriate instructions and a truthful handoff. |
| Configured | Valid AGENTS, CLAUDE import, handoff, shared local/CI gate | No file changes, duplicate documents, or needless questions. |
| Custom Claude | Existing CLAUDE.md with custom rules; request both agents | Preserve original rules; add compatible shared instructions without cycles or duplicated imports. |
| Failing baseline | Existing check exits nonzero; request setup | Report the baseline failure separately; retain failing exit status and source behavior; do not weaken tests or fix unrelated code. |
| Monorepo | Workspace config with three packages; request setup for two of them | Shared rules stay in the root AGENTS.md; each in-scope package gets an AGENTS.md of deltas only; the untouched package gains no files; root command runs the in-scope checks; the root code map links each in-scope package's AGENTS.md and the validator resolves those links. |
| Platform claim | Repository claims Linux, macOS and Windows; only Linux checks exist | Propose the repository's own runner rather than an OS-specific script; record which platforms were actually exercised. |
| Unknown stack | Repository in an ecosystem the inventory does not recognize | Locate manifests and checks by reading the repository; never report that no build or checks exist because the helper returned an empty inventory. |
| Sibling repositories | Parent folder without version control; three subfolders that each have it | Set up each subfolder as its own repository; create no files in the parent and do not call it a monorepo. |
| Workspace file, no members | `pnpm-workspace.yaml` present but declaring only unrelated settings, one manifest | Treat it as a single project; no per-package instructions for packages that do not exist. |
| No runner available | Bare Cargo or single-binary repository with several separate check commands | Ask before introducing a new tool to chain them; record it in the handoff as a new requirement; do not commit an OS-specific script. |
| Existing gate | Repository already has a check command wired to a hook and CI, missing one step | Document the existing command and report the missing step; no edit to the manifest, no script narrowed, no hook made slower without agreement. |
| Long session | Existing repo with `docs/HANDOFF.yaml`; ask for setup for Claude Code | Working agreement gains the living-handoff rule; no second handoff document; hooks written into `.claude/settings.json` only if the user asked for team-wide setup. |
| Multi-service | One repository, no workspace config: web, backend with `openapi.yaml`, mobile, desktop and CRM, each with its own manifest and Figma file; request both agents | Each service gets an AGENTS.md of deltas and a CLAUDE.md that imports only its own AGENTS.md; root Boundaries names `openapi.yaml` with owner and consumers; the map has one Design row per app; no shared runner means asking before adding one. |
| Boundaries | Repository with a lockfile, a generated `dist/`, a `migrations/` directory, `.github/workflows/` and a dev-server script | AGENTS.md Boundaries names exactly those paths, nothing generic or absent; Human review required names only risky paths that exist; Checks lists the dev command as not part of the gate. |
| UI product | Web app with a Figma link in README and no design docs in repo | Ask for the design source of truth once; link it in source-of-truth order and code map; generate no tokens, DESIGN.md, or component specs. |
| Review instructions | Node repo, gate runs lint, a JSDoc check and tests; `src/gen/`, a lockfile, `migrations/`, `.github/workflows/`, GitHub remote; user uses Claude Code's Code Review | Root `REVIEW.md` under ~40 lines: Important from the mission and constraints, Do not report names the gate and exactly those generated and lockfile paths, Always check covers migrations and workflows and no rule the gate already enforces; no generic stack checklist. A PR template with Testing, Risk and How to revert. A second run changes no file except a handoff fact that is newly verified. |
| No AI review | Same repository; user answers none for AI review | No `REVIEW.md`, no PR template, no rule that points at REVIEW.md; the report does not recommend `dual-review`. |
| PR template | Same repository with an existing `.github/pull_request_template.md` lacking Risk and revert sections; user wants `/dual-review` | Template untouched unless the user agrees, with the missing sections proposed in the report; never a second template; no `CODEOWNERS` without handles from the user; the report recommends installing `dual-review` and does not install it. |
| Roadmap | Repository without a roadmap; user wants one and names three milestones with a done-when each | Asked once, in the batch; `ROADMAP.md` holds exactly those milestones in that order, one marked `now`, none invented, split or estimated; AGENTS.md links it as a plan below specs and code. A second run changes nothing. |
| No roadmap | Same repository; user declines, or wants one but names no milestones | No `ROADMAP.md`, no roadmap entry in AGENTS.md, no placeholder milestones; the report says none was created. |
| Existing roadmap | Repository with a `ROADMAP.md` | Linked as a plan in source-of-truth order; the roadmap question is not asked; the file is not rewritten. |
| OpenSpec | `openspec/config.yaml` whose context names the stack and conventions, plus `specs/` and `changes/`; no roadmap | AGENTS.md links `openspec/` in source-of-truth order, `specs/` as current and `changes/` as plans, and does not restate the stack or conventions; the roadmap question is still asked; given milestones, each links its matching change. |

Also exercise nested `.claude/CLAUDE.md`, missing local links, import cycles,
external symlinks, links inside fenced and indented code blocks, and
unavailable Python. A helper must not execute any command it discovers or
inspect referenced files outside the target repository.

Run mechanical tests using the standard library:

```sh
python3 -B -m unittest discover -s ${CLAUDE_PLUGIN_ROOT}/shared/tests -v
```

Record what actually ran and remaining limitations. Do not call a hypothetical
walkthrough an observed agent evaluation, or a passing helper test proof that
Claude/Codex loaded the generated instructions in a fresh session.

