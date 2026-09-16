# Artifact skeletons

Section skeletons only. Fill every bracketed field from the repository and the
user's answers, delete sections that do not apply, and never ship a placeholder.
Reuse an existing file's headings instead of imposing these on a repository that
already has a working arrangement.

## Root `AGENTS.md`

```markdown
# Working agreement

## Mission and scope
[What the product does. What is explicitly out of scope.]

## Source of truth
[Ordered list: which document wins when two disagree. Mark plans as plans.
For UI: the design source (Figma URL / DESIGN.md / tokens) and whether code
or design wins on conflict.]

## Code and document map
| Area | Path | Owns | Checks |
| --- | --- | --- | --- |
| [name] | [relative/path] | [responsibility] | [command] |
| Design | [Figma URL or design/DESIGN.md] | [UI source of truth; consult before UI changes] | [visual/a11y check if any] |

In a monorepo, link each in-scope package's instructions from this table so
the link breaks when a package moves:
`| API | [packages/api](packages/api/AGENTS.md) | ... | [command] |`

## Working rules
- Inspect before editing; preserve unrelated and untracked work.
- Confirm before any destructive action.
- State expected evidence before implementing.
- Keep changes focused on the requested scope.

## Checks
[The single command, how to install what it needs, and what it does not cover.]

## Handoff
[Where session state is recorded and what must be filled in.]
```

## Per-project `AGENTS.md` (monorepo)

Only what differs from the root file. Do not restate shared rules.

```markdown
# [project name]

## Purpose and boundary
[What this project owns, and what it must not change.]

## Checks
[Command runnable from this directory, plus anything the root command skips.]

## Constraints
[Platform, runtime, or data constraints specific to this project.]
```

## Root `CLAUDE.md`

```markdown
@AGENTS.md

[Claude-specific rules only, if any. Otherwise the import alone is enough.]
```

For an existing `.claude/CLAUDE.md`, the import is `@../AGENTS.md`.

## `docs/HANDOFF.yaml`

Snapshot, not log. Terse values, references not content, hard cap ~40 lines.

```yaml
goal: [one line: what this stretch of work delivers]
done:
  - [sha or path] [one line, with evidence: test name / check passed]
wip: [what is half-done, where — path:line, what is red]
blocked: [null, or what and why]
next: [one bounded, independently verifiable task]
decisions:
  - [choice made and why, or link to ADR]
refs: [relevant/paths, docs/ADR-n.md]
checks:
  gate: [the single command]
  last: [pass | fail: what | not run: why] [YYYY-MM-DD]
platforms: [actually exercised; compilation alone does not count]
```

Do not rewrite a completed handoff or refresh its dates because setup ran again.

## Living-handoff rule (for `AGENTS.md` → Handoff section)

```markdown
## Handoff
`docs/HANDOFF.yaml` is the state that survives a context reset. Update it after
every verified step and before any long or risky one: snapshot, not log; refs
not content; under 40 lines; `next` always set. History is in git.
```

## Lite persistence without hooks (team without the plugin)

Add the import to root `CLAUDE.md` so the snapshot loads with the instructions:

```markdown
@AGENTS.md
@docs/HANDOFF.yaml
```

Loaded at session start; whether Claude re-reads it after compaction is not
guaranteed, so it is weaker than the hooks below. Codex: put "read
`docs/HANDOFF.yaml` before starting" in the AGENTS.md Handoff section.

## `.claude/settings.json` hooks (team-wide, only on request)

Same behaviour as the `agentic-workflow` plugin, for contributors without it.
`hooks/*.sh` are the plugin's scripts copied into `.claude/hooks/`.

```json
{
  "hooks": {
    "SessionStart": [{ "matcher": "compact|resume",
      "hooks": [{ "type": "command", "command": "sh .claude/hooks/handoff-inject.sh" }] }],
    "PostToolUse": [{ "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash",
      "hooks": [{ "type": "command", "command": "sh .claude/hooks/handoff-counter.sh" }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "sh .claude/hooks/handoff-stop.sh" }] }]
  }
}
```
