# dual-review

## Purpose and boundary
`/dual-review`: the coordinator in [skills/dual-review/SKILL.md](skills/dual-review/SKILL.md)
and the read-only reviewer in [agents/dual-reviewer.md](agents/dual-reviewer.md).
Independent of `setup-agentic-workflow`: it reads `REVIEW.md`, `AGENTS.md` and
`CLAUDE.md` when present and must work without any of them. Never reference
files of the setup plugin from here.

## Checks
No automated check covers behavior. Run the scenarios in
[evaluation.md](evaluation.md) on a disposable branch, and the installer once
with `HOME` pointed at an empty directory. `claude plugin validate plugins/dual-review`
checks the manifest.

## Constraints
- Claude Code only: it needs the `dual-reviewer` subagent. Bash and PowerShell
  both: commands carry resolved SHAs, never `$(...)`.
- One source for two installs: the plugin and a zip of this folder run by
  `install.sh` / `install.ps1`. The installers expect `agents/` and
  `skills/dual-review/` beside them; keep that layout.
- The agent name differs by install: `dual-reviewer` from a personal install,
  `dual-review:dual-reviewer` from the plugin. The skill must accept both.
