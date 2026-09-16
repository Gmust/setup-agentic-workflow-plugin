---
name: quality-gate
description: "Establish one shared check command for a repository and, on request, CI that calls it: reuse an existing script or task runner, never narrow it, compose a minimal command only when none exists, run baseline before and after. Use when a repo has no single check command, when checks and CI disagree, or when adding CI for agents. Does not create AGENTS.md or the handoff."
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/*), Bash(git status *), Bash(git log *), Bash(git diff *), Bash(jq *)
---

# Quality gate

## Current state (generated now)

Manifests: !`ls package.json pnpm-lock.yaml yarn.lock Cargo.toml go.mod pyproject.toml Makefile justfile Taskfile.yml build.gradle pom.xml 2>/dev/null || echo none`
npm scripts: !`jq -c .scripts package.json 2>/dev/null`
Make/just targets: !`grep -hE '^[a-zA-Z_-]+:' Makefile justfile 2>/dev/null | head -20`
CI: !`ls .github/workflows .gitlab-ci.yml .circleci 2>/dev/null || echo none`

Owns the single check command and CI. When run standalone: inspect manifests,
scripts and existing CI first, run the existing checks when feasible and record
pass / fail / not-run with a reason as the baseline, then propose before editing.

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

Document the command in the `Checks` section of `AGENTS.md` if that file exists
(see [templates](../../shared/templates.md)); otherwise report where it should go.

## Validate

Inspect selected commands before executing them. After changes, run the gate
and compare against the baseline; identify pre-existing failures separately and
never weaken checks or fix unrelated product code to make setup pass. Use bounded
execution for commands that could hang. Compilation alone does not establish
native platform support. Report the command, baseline delta, platforms actually
observed, and what the gate does not cover.
