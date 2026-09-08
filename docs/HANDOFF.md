# Handoff

## Current state

The skill and the plugin/marketplace manifests were already in place and
published. This session added the repository's own agent instructions —
`AGENTS.md`, `CLAUDE.md` and this document — and changed
`scripts/inspect_repo.py` and `tests/test_helpers.py` so the inventory
recognizes repositories that contain skills. `SKILL.md`, `references/`, the
manifests and the CI workflow were not modified.

What changed in the inventory: `SKILL.md` joined the known names; `.agents/`
and `.codex/` joined the traversed agent directories alongside `.claude/`;
files in `scripts/` and `bin/` are now matched by script suffix instead of the
four name prefixes `check`/`test`/`lint`/`verify`; a directory containing a
`SKILL.md` keeps its own subdirectories when the depth cap would otherwise cut
them off; and `--max-depth` became a command-line flag. Before the change this
repository's own inventory reported neither its `SKILL.md` nor either helper
script; it now reports all three with `limits_reached: []`.

## Verified evidence

| Check | Command | Result | Date |
| --- | --- | --- | --- |
| Helper tests, before any change this session | `python3 -B -m unittest discover -s plugins/.../tests` | pass, 21 tests | 2026-09-08 |
| Helper tests, after the change | same | pass, 28 tests; 7 added, none removed, verified name-by-name against `git HEAD` | 2026-09-08 |
| Syntax | `python3 -m compileall -q plugins/.../scripts` | pass | 2026-09-08 |
| Entry points | `validate_setup.py . --agents codex claude --document docs/HANDOFF.md` | see below | 2026-09-08 |
| CI matrix | GitHub Actions run on commit `6551c92` | pass, 6 jobs — but that commit predates this change and ran the 21-test suite | 2026-09-08 |

## Platforms tested

CI passed on `ubuntu-latest`, `macos-latest` and `windows-latest` against Python
3.10 and 3.13 — for commit `6551c92`, which predates this change. The current
28-test suite has run on Linux only. Pushing this change is what proves the
rest. On Windows `test_external_symlink_is_rejected` may report as
skipped, because creating a symlink there needs privileges the runner may lack;
treat Windows coverage as 20 of 21 tests unless the job log says otherwise.

## Limitations

- Corrected from an earlier reading of this file: `inspect_repo.py` could not
  see this repository's own skill source, and the depth cap was **not** the
  cause. `SKILL.md` was simply missing from the helper's list of known names,
  and helper scripts were matched only when their names began with `check`,
  `test`, `lint` or `verify`. Raising the depth alone changed nothing. Both
  gaps are now closed. Separately, `--max-depth` became a command-line flag;
  that is a real improvement but it was not the fix.
- Codex has never been observed loading this skill. It is installed in both
  candidate directories, and `agents/openai.yaml` follows the published layout,
  but no Codex session has confirmed it. `README.md` should not be read as
  evidence that it works there.
- No scenario in `references/evaluation.md` is automated. All of them are run by
  hand, and the record of those runs lives only in conversation, not in this
  repository.
- The marketplace install path has not been exercised end to end: no one has
  run `/plugin marketplace add` against the published repository yet.

## Next task

Push this change so CI runs the 28-test suite on all three platforms, then run
one Codex session in a repository with no agent files and record whether the
skill activates without being named — that second result decides whether the
Codex section of `README.md` is a claim or a fact.
