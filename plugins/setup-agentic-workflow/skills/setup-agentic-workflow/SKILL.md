---
name: setup-agentic-workflow
description: "Set up a repository so coding agents work safely in it: inspects the repo once, asks the unresolved questions in one batch, then runs agent-entrypoints, quality-gate and handoff in order and validates the result, in single-project repositories and monorepos. Use when preparing a repo for Claude Code or Codex or when starting an agentic development workflow. For one part only, invoke that skill directly. Do not use for implementing product features."
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/*), Bash(git status *), Bash(git log *), Bash(git diff *)
---

# Setup Agentic Workflow

Orchestrator. Inspect once, ask once, then run the part skills in order:
[agent-entrypoints](../agent-entrypoints/SKILL.md) → [quality-gate](../quality-gate/SKILL.md)
→ [handoff](../handoff/SKILL.md). Apply only to the user's requested setup scope.

## Repository inventory (generated now)

Existing agent files: !`ls AGENTS.md CLAUDE.md .claude/CLAUDE.md docs/HANDOFF.yaml 2>/dev/null || echo none`
Git: !`git log --oneline -5 2>/dev/null; git status --short 2>/dev/null | head -20`
Inventory:
!`python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/inspect_repo.py . 2>&1 | head -80`


## Inspect and propose

Read existing agent instructions and handoff, inspect the worktree including
untracked work, and identify manifests, source entry points, checks, and CI.
Use scoped source searches; distinguish implemented modules from planned ones.
Establish the repository shape before proposing files. A root that is not itself
a version-controlled repository, whose subdirectories each are, is neither one
project nor a monorepo: it is a folder of separate repositories, so set each one
up in its own root and create nothing in the parent. Otherwise read a workspace
or monorepo configuration — for example `pnpm-workspace.yaml`, `workspaces` in
`package.json`, `[workspace]` in `Cargo.toml`, `go.work`, `MODULE.bazel`,
`settings.gradle`, `nx.json`, `turbo.json`, or `<modules>` in `pom.xml` — and
judge it by the package or member list it declares, not by its presence: such a
file carrying only unrelated settings, or declaring no members, means a single
project. Otherwise derive boundaries from the manifests actually present. Those
names are examples, not a closed list; an unfamiliar ecosystem has its own, and
the repository is the authority. Ask only when boundaries stay ambiguous or the
user requested a narrower scope than the repository shape.

The read-only inventory above was produced by
`python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/inspect_repo.py .`; rerun it for a
different root. It lists relative paths only, excludes common generated/private directories, and reports scan
limits. It never reads file contents or executes repository commands. It matches
a fixed list of known manifest, check and CI names, so an empty `paths` result
means the ecosystem is unrecognized, never that the repository has no build or
checks; `unclassified_root_files` names the root files it could not classify.
Inspect the relevant files yourself; a discovered script name is not proof of
behavior, and an unfamiliar stack is found by reading the tree rather than by
trusting this list. If Python is unavailable, use native file search; do not
install dependencies.

Before editing, state the gaps, proposed files or targeted edits, and verification
evidence. Reuse existing paths and commands. Never delete files, discard user
changes, or replace existing instructions wholesale. Merge authorized additions;
ask only when a conflict requires choosing or removing a user rule.

## Resolve missing choices

Infer answers from the repository and conversation. Ask only unresolved questions
that affect the result, in a concise batch:

- Product mission, current scope, and important exclusions.
- Intended agents: Codex, Claude Code, or both. Do not infer the target solely
  from whichever agent is currently running the setup.
- Supported platforms and desired automation (local checks, CI, or both).
- For a product with a UI: the design source of truth — Figma file or node
  URL, `DESIGN.md`, a tokens directory, a Storybook, or none. Record it in
  the source-of-truth order and code map so UI work starts from it instead of
  from guesswork. Do not generate tokens, specs, or a design system; that is
  separate design tooling, linked from the map when it is already present.
- In a monorepo, which projects are in scope for this setup.
- Actual project constraints such as sensitive data or deployment boundaries.

For an empty repository without a selected stack, ask about the intended stack
before proposing build commands. Workflow setup does not authorize scaffolding a
product. Record that checks are not configured if there is no implementation yet.
For an existing repository, inspect manifests and scripts and propose the check
commands yourself. Ask the user only to resolve genuine alternatives.

## Run the parts

Pass the inspection result and answers to each part rather than letting it
re-inspect. Each part is idempotent and skips what is already correct.

1. **agent-entrypoints** — `AGENTS.md`, `CLAUDE.md`, per-project files, working
   agreement, code and document map (including the design source of truth).
2. **quality-gate** — the single check command, and CI on it when requested.
3. **handoff** — living `docs/HANDOFF.yaml`, the handoff rule, optional hooks.

Skeletons for every artifact are in [templates](../../shared/templates.md). Fill
them from the repository, drop sections that do not apply, and prefer an existing
file's headings over imposing new ones.


Keep credentials, customer data, private prompts, raw terminal transcripts, and
machine-specific absolute paths out of committed artifacts. Relative source paths,
documented commands, and sanitized check summaries belong in the workflow.
Keep personal skills, hooks, MCP servers, and subscriptions optional; do not
install them or change personal settings as a side effect of repository setup.

## Validate changes and repeat runs

Inspect selected commands before executing them. Before changing check/CI
configuration, run the existing checks when feasible and note pass, fail, or
not-run with a reason. After changes, run the relevant checks and compare against
that baseline. Identify existing failures separately; do not weaken checks or fix
unrelated product code to make setup pass. Use bounded execution for commands
that could hang. Compilation alone does not establish native platform support.

Validate the configured entry points and edited documents with the read-only
helper, choosing only the agents actually requested:

```sh
python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/validate_setup.py <repo-root> --agents codex claude --document docs/HANDOFF.yaml
```

Use `--claude-file .claude/CLAUDE.md` for that existing location. Repeat
`--document` for other edited Markdown files. In a monorepo, run the helper once
per project directory that received its own instructions. The helper checks
required files, simple inline local Markdown links, and standalone relative
`@file` imports in agent instructions. It follows those imports, checks cycles
and depth, and never executes checks or follows references outside the
repository. Warnings require manual review: it does not fully parse Markdown,
validate heading anchors, understand prose/code-span paths, or prove agent
activation or CI semantics. Fenced and indented code blocks are skipped, so a
broken path shown as an example is not reported. Python is optional: inspect
these same invariants manually when unavailable.

On a repeat invocation, fill only remaining gaps. Do not duplicate sections,
imports, or equivalent documents, rewrite a completed handoff, or change dates
just because setup ran. If requirements are already met, report no changes.
Re-read the final artifacts against the requested outcomes: would another setup
run need to change anything? Resolve concrete gaps before finishing.

Before reporting the work done, confirm the handoff exists and says what was
actually verified — including checks that were not run, and why. Then report
outcome, changed files/contracts, checks actually run and baseline deltas,
platforms observed, limitations, and the next independently verifiable task.
For skill maintenance, use [behavioral scenarios](../../shared/evaluation.md).
