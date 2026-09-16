---
name: handoff
description: "Create or refresh docs/HANDOFF.yaml — the compact state snapshot that survives context resets — add the living-handoff rule to AGENTS.md, and optionally install the context-persistence hooks. Use when a repo has no handoff, when the user says /handoff, 'write handoff', 'save progress', 'snapshot state', or after a verified step in a long session. Snapshot not log; refs not content; under 40 lines."
argument-hint: "[what just happened]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/*), Bash(git status *), Bash(git log *), Bash(git diff *)
---

# Handoff

## Current state (generated now)

Handoff: !`cat docs/HANDOFF.yaml 2>/dev/null || echo "(none yet)"`
Git: !`git log --oneline -5 2>/dev/null; git status --short 2>/dev/null | head -20`

Owns `docs/HANDOFF.yaml`, the handoff rule and context persistence. Template:
[templates](../../shared/templates.md).

## Refresh the snapshot (the common case: `/handoff`)

Write or update the handoff now (create `docs/` if missing). Operator note,
if any: $ARGUMENTS

- Snapshot, not log: current state only; history lives in git.
- Fixed keys: `goal`, `done` (sha or path + one line with evidence), `wip`,
  `blocked`, `next` (one bounded, verifiable task), `decisions`, `refs`,
  `checks`, `platforms`.
- References not content: `path:line`, sha, test name. Never code, output or
  transcripts, credentials, or machine-specific absolute paths.
- Terse values, no prose. Hard cap 40 lines; evict the oldest `done` first.
- Do not touch dates or entries that did not change. Then print the file.

## Set up (first run in a repository)

- **Handoff:** Always leave one; a setup without a handoff is not finished.
  Reuse the location the repository already keeps session state in, whatever
  it is called, and write there rather than creating a second document; only
  when none exists, create `docs/HANDOFF.yaml` in the format above: a living
  snapshot updated after every verified step. One handoff per repository
  unless projects are released independently.
- **Context persistence:** Long sessions lose context on compaction; the
  handoff is what survives. Add the living-handoff rule to the working
  agreement (see [templates](../../shared/templates.md)). The `agentic-workflow` plugin ships hooks that
  re-inject `docs/HANDOFF.yaml` after compaction, remind the agent every N
  mutating tool calls, and refuse to end a turn while the tree is newer than
  the handoff; they are personal and no-op without the file. Write the same
  hooks into the repository's `.claude/settings.json` only when the user asks
  for a team-wide setup without the plugin. Codex gets the rule only.

Completion fields for a setup handoff: outcome; files/contracts changed; checks
and results; platforms actually tested; remaining limitations; next bounded task.
Before reporting setup done, confirm the handoff exists and says what was actually
verified, including checks not run and why. Never rewrite a completed handoff or
refresh its dates just because setup ran again.

## Validate

```sh
python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/validate_setup.py <repo-root> --agents claude --document docs/HANDOFF.yaml
```

Hooks self-check: `sh ${CLAUDE_PLUGIN_ROOT}/hooks/test.sh`.
