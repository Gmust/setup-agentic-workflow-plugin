# Working agreement

## Mission and scope

This repository publishes one plugin, `setup-agentic-workflow`: four skills
(`setup-agentic-workflow` orchestrator, `agent-entrypoints`, `quality-gate`,
`handoff`), shared templates and helpers, and hooks that keep a living
`docs/HANDOFF.yaml` in context across compaction. The plugin prepares other
repositories for coding agents. It does not implement product
features, and neither does work in this repository.

Out of scope: adding unrelated plugins, changing anyone's installed copies, and
any change to `LICENSE` authorship.

## The four copies — read this first

The plugin exists in four places, and only one of them is editable here:

| Copy | Location | Editable |
| --- | --- | --- |
| Source | `plugins/setup-agentic-workflow/` | yes — this is the only source of truth |
| Account | uploaded ZIP on claude.ai | no — rebuild and re-upload |
| Claude Code | `~/.claude/skills/setup-agentic-workflow/` | no — copy from source |
| Codex | `~/.agents/skills/` and `~/.codex/skills/` | no — copy from source |

Editing an installed copy changes nothing here and is silently lost on the next
install. Always edit the source, then rebuild the ZIP as `README.md` describes.
Never write to a path outside this repository as part of a change here.

## Source of truth, in order

1. The four `SKILL.md` files under [`skills/`](plugins/setup-agentic-workflow/skills/setup-agentic-workflow/SKILL.md)
   — behavior. Each frontmatter `description` decides when that skill
   activates. The orchestrator links the parts by relative path; keep those
   links valid.
2. [`shared/evaluation.md`](plugins/setup-agentic-workflow/shared/evaluation.md)
   — the behavioral scenarios a change must still satisfy.
3. [`hooks/test.sh`](plugins/setup-agentic-workflow/hooks/test.sh) and
   [`shared/tests/test_helpers.py`](plugins/setup-agentic-workflow/shared/tests/test_helpers.py)
   — mechanical contract of the hooks and the two helpers.
4. [`README.md`](README.md) — installation and distribution.

## Code and document map

| Area | Path | Owns | Checks |
| --- | --- | --- | --- |
| Orchestrator | `.../skills/setup-agentic-workflow/SKILL.md` | Inspect once, ask once, run the parts, validate | behavioral scenarios, run by hand |
| Part skills | `.../skills/{agent-entrypoints,quality-gate,handoff}/SKILL.md` | One artifact each; standalone and idempotent | behavioral scenarios, run by hand |
| Hooks | `.../hooks/*.sh` | Re-inject handoff on SessionStart; remind every N mutating calls; block Stop while tree newer than handoff or handoff fails lint | `hooks/test.sh` |
| Templates | `.../shared/templates.md` | Skeletons the skills fill in, incl. `HANDOFF.yaml` and the living-handoff rule | none automated |
| Scenarios | `.../shared/evaluation.md` | How a change is judged | run by hand in disposable repositories |
| Inventory helper | `.../shared/scripts/inspect_repo.py` | Read-only repository inventory | `shared/tests/test_helpers.py` |
| Validator helper | `.../shared/scripts/validate_setup.py` | Read-only entry-point and link checks | `shared/tests/test_helpers.py` |
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
- Hooks are POSIX `sh` + `jq` + `git`, no-op without the handoff file, and
  never author handoff content — the agent writes it, hooks only inject,
  remind and gate.
- Behavior claimed in any `SKILL.md` needs a scenario in `shared/evaluation.md`.
  A passing unit test is not evidence that the skill behaves correctly.

## Checks

```sh
python3 -B -m unittest discover -s plugins/setup-agentic-workflow/shared/tests -v && sh plugins/setup-agentic-workflow/hooks/test.sh
```

Standard library only; no installation step. CI runs this on Ubuntu, macOS and
Windows against Python 3.10 and 3.13, plus a `compileall` pass.

Not covered by any automated check: whether the skill actually activates from a
natural request, whether Codex loads it, and every scenario in
`shared/evaluation.md`. Those are exercised by hand in disposable
repositories, and the result belongs in the handoff.

## Handoff

`docs/HANDOFF.yaml` is the state that survives a context reset. Update it
after every verified step and before any long or risky one: snapshot, not log;
refs not content; under 40 lines; `next` always set. History is in git.
