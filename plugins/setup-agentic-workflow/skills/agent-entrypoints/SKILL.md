---
name: agent-entrypoints
description: "Add or standardize agent instruction files: root AGENTS.md and CLAUDE.md with @AGENTS.md import, per-project AGENTS.md in monorepos, the working agreement, and a code and document map that links requirements, architecture, ADRs and the design source of truth (Figma, DESIGN.md, tokens). Use when a repo needs AGENTS.md or CLAUDE.md created, merged, or de-duplicated, or when the code map is missing or stale. Does not touch checks, CI, or the handoff."
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/*), Bash(git status *), Bash(git log *), Bash(git diff *)
---

# Agent entry points

## Current state (generated now)

Files: !`ls AGENTS.md CLAUDE.md .claude/CLAUDE.md 2>/dev/null || echo none`
Root AGENTS.md head: !`head -40 AGENTS.md 2>/dev/null`
Root CLAUDE.md head: !`head -20 CLAUDE.md .claude/CLAUDE.md 2>/dev/null`
Monorepo markers: !`ls pnpm-workspace.yaml go.work turbo.json nx.json MODULE.bazel settings.gradle 2>/dev/null; jq -c .workspaces package.json 2>/dev/null; grep -l '^\[workspace\]' Cargo.toml 2>/dev/null`

Owns `AGENTS.md`, `CLAUDE.md`, per-project instructions, the working agreement
and the code/document map. Skeletons: [templates](../../shared/templates.md).
Fill them from the repository, drop sections that do not apply, and prefer an
existing file's headings over imposing new ones.

When run standalone: read existing instructions and the worktree first, establish
the repository shape (single project, monorepo, or a folder of separate repos —
see [setup-agentic-workflow](../setup-agentic-workflow/SKILL.md)), and state gaps
and proposed edits before writing. Never delete files, discard user changes, or
replace existing instructions wholesale; merge, and ask only when a conflict
requires removing a user rule. Ask for the intended agents (Codex, Claude, both)
and, for a UI product, the design source of truth if not inferable.

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
  For a UI product, link the design source of truth (Figma URL, `DESIGN.md`,
  tokens, Storybook) in the source-of-truth order and the map, stating whether
  code or design wins on conflict. Do not generate tokens or specs.

Keep credentials, private prompts and machine-specific absolute paths out.

## Validate

```sh
python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/validate_setup.py <repo-root> --agents codex claude
```

Use `--claude-file .claude/CLAUDE.md` for that location; in a monorepo run once
per project that received its own instructions. It checks required files, inline
local links and standalone `@file` imports (cycles, depth); it does not parse
Markdown fully or prove agent activation. On a repeat run fill only remaining
gaps: no duplicate sections or imports. Report no changes if already met.
