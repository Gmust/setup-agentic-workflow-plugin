# Behavioral evaluation — dual-review

Run on a disposable branch. Reviewers are read-only; the coordinator edits only
with `--fix` or the user's yes. Record what actually ran: a scenario walked
through on paper is not an observed run.

| Scenario | Request and starting state | Expected observable outcome |
| --- | --- | --- |
| Plugin agent | Plugin installed; `/dual-review` on a branch with one change | Every reviewer of a round launches in one message, fresh, as the plugin-scoped `dual-reviewer` the session lists (e.g. `dual-review:dual-reviewer`); no "agent not found". |
| Consensus | Branch with one real off-by-one bug and one naming nit | The bug ends ACCEPTED with a `path:line` fix; the nit is listed, never voted on; no file changes; empty report sections omitted; the report opens with the tally line. |
| Bug class | The same defect at two places in the change | One item whose `instances` name both places; the agreed fix covers both. |
| Intent | Commit or PR body promises two behaviors; the change delivers one | `INTENT: PARTIAL` lands on the approach list; the missing behavior is a finding. A fix that only hides the symptom is at least `major`. |
| Docs lie | The change makes a line in AGENTS.md or CLAUDE.md false | A finding against that line; a change to those files is never `quick`. |
| Pre-existing | A real bug in code the change does not touch or make reachable | On the pre-existing list, never voted on, never applied by `--fix`, not repeated in later rounds. |
| Risk depth | One branch touching billing or invoice code; one touching only docs, under 200 lines | First: `deep`, reviewer S runs in round 1 only, the report has a `Security:` line. Second: `quick`, at most 2 rounds, blocker and major only. |
| Review rules | Repository with a root `REVIEW.md` | SCOPE lists it; its skip paths, severity and always-check rules show in the findings and the report. |
| Deadlock | A finding one reviewer rejects with evidence every round | The coordinator adds no findings and breaks no tie; votes repeated unchanged two rounds mark it DEADLOCKED and hand both arguments to the user. |
| Fix and verify | `--fix` with agreed fixes; AGENTS.md documents a `Checks` command | Each fix applied at every instance or marked NOT_APPLIED; the Checks command runs and its output reaches VERIFY; fresh VERIFY pairs loop until both APPROVE or 2 rounds; nothing committed. |
| Focus notes | `/dual-review main check HEAD handling`, then `/dual-review -- main is flaky` | First: base `main`, `check HEAD handling` stays focus notes. Second: no-target scope, the whole text is focus notes. |
| Stale PR base | Current branch is a PR head; local `origin/<base>` is behind `baseRefOid` | Offers `git fetch origin <base>` and waits for approval; declined → the review runs and the report says base-branch commits may be included. |
| Staged scope | `--staged` with an untracked scratch file present | SCOPE lists no untracked files. |
| Split verify | In VERIFY, one reviewer says NOT_FIXED, the other FIXED | No edit that round; the item goes to the next verify round as OPEN and is edited only after both votes resolve it. |
| Installer | `install.sh` with `HOME` pointed at an empty directory | Agent and skill land under `$HOME/.claude`; the installed `SKILL.md` matches the source byte for byte; a second run backs up instead of overwriting. |
