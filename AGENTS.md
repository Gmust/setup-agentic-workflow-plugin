# Working agreement

## Mission and scope

This repository publishes one thing: the `setup-agentic-workflow` skill, plus
the plugin and marketplace manifests that let Claude Code install it. The skill
prepares other repositories for coding agents. It does not implement product
features, and neither does work in this repository.

Out of scope: adding unrelated plugins, changing anyone's installed copies, and
any change to `LICENSE` authorship.

## The four copies — read this first

The skill exists in four places, and only one of them is editable here:

| Copy | Location | Editable |
| --- | --- | --- |
| Source | `plugins/setup-agentic-workflow/skills/setup-agentic-workflow/` | yes — this is the only source of truth |
| Account | uploaded ZIP on claude.ai | no — rebuild and re-upload |
| Claude Code | `~/.claude/skills/setup-agentic-workflow/` | no — copy from source |
| Codex | `~/.agents/skills/` and `~/.codex/skills/` | no — copy from source |

Editing an installed copy changes nothing here and is silently lost on the next
install. Always edit the source, then rebuild the ZIP as `README.md` describes.
Never write to a path outside this repository as part of a change here.

## Source of truth, in order

1. [`SKILL.md`](plugins/setup-agentic-workflow/skills/setup-agentic-workflow/SKILL.md)
   — the skill's behavior. Its frontmatter `description` decides when the skill
   activates, and `plugins/setup-agentic-workflow/.claude-plugin/plugin.json`
   copies that same text for the marketplace listing: change both together.
2. [`references/evaluation.md`](plugins/setup-agentic-workflow/skills/setup-agentic-workflow/references/evaluation.md)
   — the behavioral scenarios a change must still satisfy.
3. [`tests/test_helpers.py`](plugins/setup-agentic-workflow/skills/setup-agentic-workflow/tests/test_helpers.py)
   — mechanical contract of the two helpers.
4. [`README.md`](README.md) — installation and distribution.

## Code and document map

| Area | Path | Owns | Checks |
| --- | --- | --- | --- |
| Skill text | `.../skills/setup-agentic-workflow/SKILL.md` | What the skill does and refuses to do | behavioral scenarios, run by hand |
| Templates | `.../references/templates.md` | Skeletons the skill fills in | none automated |
| Scenarios | `.../references/evaluation.md` | How a change is judged | run by hand in disposable repositories |
| Inventory helper | `.../scripts/inspect_repo.py` | Read-only repository inventory | `tests/test_helpers.py` |
| Validator helper | `.../scripts/validate_setup.py` | Read-only entry-point and link checks | `tests/test_helpers.py` |
| Manifests | `.claude-plugin/marketplace.json`, `plugins/*/.claude-plugin/plugin.json` | Marketplace and plugin identity | none automated |
| CI | `.github/workflows/tests.yml` | The gate on three platforms | itself |

One plugin is declared in `marketplace.json`. A second plugin is when each gets
its own `AGENTS.md`; today a per-plugin file would only restate this one.

## Working rules

- Inspect before editing; preserve unrelated and untracked work.
- Confirm before any destructive action.
- State the expected evidence before implementing.
- A helper must stay read-only: it may not execute a command it discovers, read
  file contents it was not asked for, or follow a reference outside the target
  repository. A change that weakens this is a defect regardless of test results.
- Both helpers use the standard library only. Do not add a dependency.
- Behavior claimed in `SKILL.md` needs a scenario in `references/evaluation.md`.
  A passing unit test is not evidence that the skill behaves correctly.

## Checks

```sh
python3 -B -m unittest discover -s plugins/setup-agentic-workflow/skills/setup-agentic-workflow/tests -v
```

Standard library only; no installation step. CI runs this on Ubuntu, macOS and
Windows against Python 3.10 and 3.13, plus a `compileall` pass.

Not covered by any automated check: whether the skill actually activates from a
natural request, whether Codex loads it, and every scenario in
`references/evaluation.md`. Those are exercised by hand in disposable
repositories, and the result belongs in the handoff.

## Handoff

Session state goes in [`docs/HANDOFF.md`](docs/HANDOFF.md). Record what was
actually verified, including what was not run and why.
