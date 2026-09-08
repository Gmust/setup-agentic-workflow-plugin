# Setup Agentic Workflow

A skill that prepares a repository for coding agents: scoped instructions, one
trustworthy check command, a handoff document, and optional CI — for
single-project repositories and monorepos.

It sets up the workflow. It does not implement product features, scaffold a
stack you have not chosen, or weaken your existing checks to make setup pass.

## What it creates

| Artifact | Where | Purpose |
| --- | --- | --- |
| Agent entry points | `AGENTS.md`, `CLAUDE.md` (or `.claude/CLAUDE.md`) | Shared rules once, imported rather than duplicated |
| Per-project instructions | `<project>/AGENTS.md` | In a monorepo, only what differs from the root |
| Code and document map | inside `AGENTS.md` | Real entry points, ownership boundaries, which check covers what |
| Handoff | `docs/HANDOFF.md` | Current state, verified evidence, limitations, next bounded task |
| Quality gate | your repository's own runner | One command that terminates and fails loudly |
| CI | your existing provider | Calls the same command, on the platforms you claim to support |

Existing files are merged, never replaced wholesale. A second run on an
already-configured repository makes no changes.

## Install

### Claude Code — plugin

```sh
/plugin marketplace add Gmust/setup-agentic-workflow-plugin
/plugin install setup-agentic-workflow@gmust-plugins
```

### Claude Code — manual

```sh
cp -R plugins/setup-agentic-workflow/skills/setup-agentic-workflow ~/.claude/skills/
```

Use `.claude/skills/` inside a repository instead to share it with that project
only.

### Claude apps (claude.ai, desktop, Cowork)

Zip the skill folder so the folder itself is the archive root, then upload it
under **Customize → Skills → Add**:

Run this from the repository root:

```sh
rm -f setup-agentic-workflow.zip
( cd plugins/setup-agentic-workflow/skills && \
  zip -r "$OLDPWD/setup-agentic-workflow.zip" setup-agentic-workflow \
      -x '*.DS_Store' -x '*__pycache__*' )
```

The subshell keeps your working directory unchanged, and `$OLDPWD` resolves to
the repository root, so the archive never depends on how deep the skill sits.
Check the result with `unzip -l setup-agentic-workflow.zip` — the first entry
must be `setup-agentic-workflow/`, or the upload will be rejected.

### Codex

Copy the skill folder into your Codex skills directory. `agents/openai.yaml`
supplies the display name and default prompt.

## Use

Ask for it by name, or describe the task:

```
Use setup-agentic-workflow to set up a minimal agentic development workflow for this repository.
```

The skill inspects the repository first, states the gaps and the files it
proposes, and asks only the questions it cannot answer from what it found.

## Helper scripts

Both helpers are read-only, standard-library Python, and optional — the skill
falls back to manual inspection when Python is unavailable. Neither executes any
command it discovers, and neither follows references outside the target
repository.

```sh
python3 scripts/inspect_repo.py <repo-root>
python3 scripts/validate_setup.py <repo-root> --agents codex claude --document docs/HANDOFF.md
```

`inspect_repo.py` prints a bounded inventory of manifests, entry points, checks
and CI files. It matches a fixed list of known names plus a few suffixes, so an
empty `paths` result means the ecosystem is unrecognized, not that the
repository is empty; `unclassified_root_files` surfaces the root files it could
not classify, which is where an unfamiliar stack shows up. `validate_setup.py` exits nonzero when a required entry point is
missing, a local Markdown link points at nothing, an import escapes the
repository, or imports form a cycle. Its `verified` block reports how many
documents, local links and imports were actually checked, so a green result on a
file with no links is not mistaken for a thorough pass.

### What the validator does not do

It parses a simple Markdown subset. Fenced and indented code blocks are skipped,
so example paths are not reported. Reference-style links, complex links and
inline `@` mentions produce warnings for manual review rather than errors. It
does not validate heading anchors, prove that an agent loaded the generated
instructions, or reason about CI semantics.

## Development

```sh
python3 -B -m unittest discover -s plugins/setup-agentic-workflow/skills/setup-agentic-workflow/tests -v
```

The test suite covers helper mechanics only. Behavioral scenarios for the skill
itself are in `references/evaluation.md`; run them in disposable repositories,
twice with the same answers, and compare file bytes between runs.

## License

MIT. See [LICENSE](LICENSE).
