---
name: setup-agentic-workflow
description: "Set up a repository so coding agents work safely in it: AGENTS.md and CLAUDE.md entry points, a code map, one shared check command, a handoff document, and optional CI, in single-project repositories and monorepos. Use when preparing a repo for Claude Code or Codex, when adding or standardizing AGENTS.md or CLAUDE.md, or when starting an agentic development workflow. Do not use for implementing product features."
---

# Setup Agentic Workflow

Set up a repository so coding agents can find the owning code and requirements,
make focused changes, run trustworthy checks, and leave useful session state.
Apply this workflow only to the user's requested setup scope.

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

For a larger or unfamiliar repository, the optional read-only inventory helps:

```sh
python3 <skill-dir>/scripts/inspect_repo.py <repo-root>
```

Replace `<skill-dir>` with this skill's directory. The inventory lists relative
paths only, excludes common generated/private directories, and reports scan
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
- In a monorepo, which projects are in scope for this setup.
- Actual project constraints such as sensitive data or deployment boundaries.

For an empty repository without a selected stack, ask about the intended stack
before proposing build commands. Workflow setup does not authorize scaffolding a
product. Record that checks are not configured if there is no implementation yet.
For an existing repository, inspect manifests and scripts and propose the check
commands yourself. Ask the user only to resolve genuine alternatives.

## Reuse or add the minimum artifacts

Skeletons for the files below are in [templates](references/templates.md). Fill
them from the repository, drop sections that do not apply, and prefer an existing
file's headings over imposing new ones.

- **Agent entry points:** Codex uses root `AGENTS.md`; Claude uses root
  `CLAUDE.md` or existing `.claude/CLAUDE.md`. For both agents, prefer shared
  rules in `AGENTS.md` and a root `CLAUDE.md` importing `@AGENTS.md`. For an
  existing `.claude/CLAUDE.md`, the relative import is `@../AGENTS.md`. Preserve
  Claude-specific rules. Avoid import cycles. An existing file for one agent
  does not automatically satisfy the other. Preserve working arrangements rather
  than moving rules just to match this preferred shape. When an existing
  `CLAUDE.md` and `AGENTS.md` already repeat most of one another, say so with
  the share that overlaps and offer to replace the duplicated half with an
  import; make that change only if the user accepts it, never silently.
- **Per-project instructions:** In a monorepo, keep shared rules in the root
  `AGENTS.md` and give each in-scope project its own `AGENTS.md` holding only
  what differs: purpose, ownership boundary, check commands, and local
  constraints. Do not restate or copy root rules into it; two copies drift.
  Add a per-project `CLAUDE.md` importing the root `AGENTS.md` by relative path
  only when Claude must load that project's rules without the root file, and
  never alongside a duplicated copy of the same content. A single-project
  repository gets root files only. In the root code map, reference each in-scope
  package's `AGENTS.md` as a relative Markdown link rather than as plain text,
  so a renamed or moved package breaks the link instead of leaving the map
  quietly wrong, and so the validator resolves those files from the root.
- **Working agreement:** Keep instructions concise: source-of-truth order,
  inspect-before-editing, preserving unrelated work, destructive-action
  confirmation, expected evidence before implementation, focused changes,
  verification, and handoff. Link to detail rather than duplicating it.
- **Code and document map:** Identify actual entry points and ownership boundaries.
  Link product requirements, architecture, accepted decisions, and relevant
  checks by task when those documents exist. Label plans and unresolved decisions.
  Add a short missing section only when useful; do not fabricate a full spec,
  architecture, or precedence between conflicting documents.
- **Handoff:** Always leave one; a setup without a handoff is not finished.
  Reuse the location the repository already keeps session state in, whatever
  it is called, and write there rather than creating a second document; only
  when none exists, create `docs/HANDOFF.md`. Include
  current state, verified evidence, limitations, and one next verifiable task.
  Completion fields: outcome; files/contracts changed; checks and results;
  platforms actually tested; remaining limitations; next bounded task. One
  handoff per repository unless projects are released independently.
- **Quality gate:** Reuse an existing command. When a suitable command already
  exists, document it and leave the manifest alone: an incomplete existing gate
  is something to report and propose a change for, not something to fix as part
  of setup. Never narrow an existing script — hooks, CI steps and pull request
  templates call these by name, and removing a step from one silently weakens
  every caller. Widening what a script or a hook runs changes the contributor's
  workflow and needs explicit agreement first. Prefer the repository's own task
  runner — an `npm`/`pnpm` script, `cargo`, `go`, `make`, `just`, `task` — so a
  single documented command works on every developer platform. Compose a small
  shared command only when none exists, using the repository's runtime and
  platform conventions. When no runner exists and the only cross-platform
  option is a tool the repository does not already use, ask before adding it
  and record it in the handoff as a requirement this setup introduced, rather
  than presenting the result as dependency-free. Do not commit an OS-specific
  shell script unless the repository already standardizes on one, and never
  commit two scripts that must be kept in step. It must terminate, propagate
  any failed step as a nonzero exit, and use check-only formatting/linting
  rather than auto-fixing source.
  Avoid watch/dev servers, masked failures, deployments, or dependency
  installation as checks. Keep required tools and reproducible installation
  instructions discoverable. In a monorepo, keep each project's checks runnable
  on their own and give the root one command that runs the in-scope projects.
- **CI and contributing:** When requested, reuse the existing CI provider and
  make CI call the same quality gate. Preserve existing triggers and permissions.
  When the repository claims multiple platforms, run CI on those platforms rather
  than asserting support. Add contributor instructions only when they add missing
  information.

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
python3 <skill-dir>/scripts/validate_setup.py <repo-root> --agents codex claude --document docs/HANDOFF.md
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
For skill maintenance, use [behavioral scenarios](references/evaluation.md).
