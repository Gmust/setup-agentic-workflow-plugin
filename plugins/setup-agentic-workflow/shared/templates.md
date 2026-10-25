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
[Ordered list: which document wins when two disagree. Mark plans as plans
(a roadmap, proposed changes); they rank below specs and code.
For UI: the design source (Figma URL / DESIGN.md / tokens) and whether code
or design wins on conflict.]

## Code and document map
| Area | Path | Owns | Checks |
| --- | --- | --- | --- |
| [name] | [relative/path] | [responsibility] | [command] |
| Design | [Figma URL or design/DESIGN.md] | [UI source of truth; consult before UI changes] | [visual/a11y check if any] |

One Design row per UI project when their designs differ.

In a monorepo, link each in-scope package's instructions from this table so
the link breaks when a package moves:
`| API | [packages/api](packages/api/AGENTS.md) | ... | [command] |`

## Working rules
- Inspect before editing; preserve unrelated and untracked work.
- Confirm before any destructive action.
- State expected evidence before implementing.
- Keep changes focused on the requested scope.
- When review or an incident misses a bug, also add what the reviewer lacked:
  a rule here [or in REVIEW.md, if it exists], or a new check.

## Boundaries
Do not edit without asking: [this repository's actual secrets and env files,
generated output, lockfiles, vendored code, migrations, CI workflows,
infra/deploy and production config paths].
Human review required: [paths where a mistake costs most here, e.g. auth,
billing, CI and release workflows, installers or updaters]. An agent's or AI
reviewer's approval does not count for these.
Shared contracts (omit when none): [OpenAPI / proto / schema / shared types
path] — owned by [project], used by [projects]. Before changing one, ask and
name every consumer it affects.

## Checks
[The single command, how to install what it needs, and what it does not cover.
The local run/dev command, if one exists, labelled as not part of the gate.]

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

Per-project `CLAUDE.md` (monorepo, Claude target): `@AGENTS.md` only, importing
that project's own file. Root rules already load from the parent directory.

## Root `REVIEW.md` (only when the team uses AI review)

Read by Claude Code's Code Review (repository root only) and by `/dual-review`.
Only rules that change review behavior; project context stays in AGENTS.md.
Under ~40 lines: length dilutes the rules that matter. Every line must be true
of this repository: no rule the check command already enforces, no path that
does not exist, no generic stack checklist. A rule a linter can enforce belongs
in lint config instead. In a monorepo, add a `## <project path>` section only
for a project with its own rules.

```markdown
# Review instructions

## What Important means here
[The failures that cost most in this repository, e.g. wrong results from
<core module>, data crossing <trust boundary>, migrations that block rollback.]
Style, naming and refactoring are Nit at most.

## Do not report
- Anything `[check command]` already enforces: [lint, format, types].
- [Generated, vendored and lockfile paths that exist here.]

## Always check
- [Repository rule no linter can enforce, tied to a path that exists.]
- Changes under [Human review required paths from AGENTS.md]: say in the
  summary that a person must review them.

## Evidence and reporting
- Behavior claims cite `path:line` and a concrete scenario, never a guess
  from a name.
- Flag the class of a bug: list every instance, not only the first.
- Mark bugs this change did not introduce as Pre-existing.
- At most five Nits; count the rest in the summary.
- After the first review, report Important findings only.
- Open the summary with the count of findings by severity, or with
  "No blocking issues."
```

## `.github/pull_request_template.md` (GitHub, none present)

Look for an existing template first (`.github/`, `.github/PULL_REQUEST_TEMPLATE/`,
`docs/`, repository root); add missing sections to it only if the user agrees.

```markdown
## What and why
[One or two lines; link the issue.]

## Testing
[Commands run and their result; screenshots for UI. "Not run: <why>" is an answer.]

## Risk
[What could break, who would notice, and which Human review required paths it touches.]

## How to revert
[Revert the commit, turn off the flag, or roll back the migration; or why it cannot be undone.]
```

`CODEOWNERS` for the Human review required paths only with owner handles the
user gives; never invent them. Branch protection (required reviews, dismissing
approvals on new commits) is a repository setting: recommend it in the report,
do not apply it.

## `ROADMAP.md` (only when the user wants one)

Only the milestones the user names, in their order: nothing invented, split,
reordered or estimated. Under ~40 lines; detail lives in the specs and issues
it links. The owner changes scope and order; an agent changes only Status, and
only once a milestone's Done when is verified.

```markdown
# Roadmap

A plan, not a spec: [code / specs path] wins on conflict. Work toward the
milestone marked `now`; later ones only when asked.

| # | Milestone | Done when | Status | Spec |
| --- | --- | --- | --- | --- |
| 1 | [goal, one line] | [observable exit: a check, a demo, a metric] | [done / now / next / later] | [openspec/changes/<id> or issue; drop the column when none] |

## Not planned
[What the owner ruled out, so agents do not build it.]

## Open questions
[Undecided items blocking a milestone; omit when none.]
```

## `docs/HANDOFF.yaml`

Snapshot, not log. Terse values, references not content, hard cap ~40 lines.

```yaml
goal: [one line: what this stretch of work delivers; its ROADMAP.md milestone, if any]
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
