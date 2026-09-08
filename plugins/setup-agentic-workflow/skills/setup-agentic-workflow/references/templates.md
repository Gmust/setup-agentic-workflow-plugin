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
[Ordered list: which document wins when two disagree. Mark plans as plans.]

## Code and document map
| Area | Path | Owns | Checks |
| --- | --- | --- | --- |
| [name] | [relative/path] | [responsibility] | [command] |

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

## `docs/HANDOFF.md`

```markdown
# Handoff

## Current state
[What is implemented and working, in one short paragraph.]

## Verified evidence
| Check | Command | Result | Date |
| --- | --- | --- | --- |
| [name] | [command] | [pass / fail / not run + reason] | [YYYY-MM-DD] |

## Platforms tested
[Platforms actually exercised. Compilation alone is not a tested platform.]

## Limitations
[Known gaps, failing checks that predate this work, and unverified claims.]

## Next task
[One bounded, independently verifiable task.]
```

Do not rewrite a completed handoff or refresh its dates because setup ran again.
