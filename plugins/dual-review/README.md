# /dual-review for Claude Code

Two reviewers, each in a fresh session, review your change in parallel. Their
findings become one numbered fix list, and both reviewers keep re-reviewing
that list (again in fresh sessions) until they agree on every fix. With
`--fix`, the agreed fixes are applied and two fresh reviewers verify them
until both approve.

```
            ┌─ Reviewer A (correctness & safety) ─┐
round 1     │                                     ├─► merge into ledger F1..Fn
            └─ Reviewer B (design & robustness) ──┘
                                │ any OPEN items?
            ┌─ fresh A: vote AGREE / AMEND / DISAGREE / CHOOSE ─┐
round 2..N  │                                                   ├─► resolve votes
            └─ fresh B: vote AGREE / AMEND / DISAGREE / CHOOSE ─┘     │
                                ▲─────────── still OPEN ──────────────┘
                                │ all ACCEPTED / REJECTED / DEADLOCKED
                              report
                                │ --fix (or "yes")
            apply agreed fixes ─► fresh A + B VERIFY ─► re-fix ─► … until both APPROVE
```

## Files

```
agents/dual-reviewer.md        read-only reviewer subagent (DISCOVER / ADJUDICATE / VERIFY)
skills/dual-review/SKILL.md    the coordinator, invoked as /dual-review
.claude-plugin/plugin.json     plugin manifest (gmust-plugins marketplace)
evaluation.md                  behavioral scenarios a change must still satisfy
install.sh                     installer for macOS / Linux / Git Bash
install.ps1                    installer for Windows PowerShell
```

## Install

As a Claude Code plugin:

```
/plugin marketplace add Gmust/setup-agentic-workflow-plugin
/plugin install dual-review@gmust-plugins
```

Or from the zip, built from this folder (`cd plugins && zip -r dual-review.zip dual-review`):

```bash
unzip dual-review.zip && cd dual-review
./install.sh                      # personal, every project
./install.sh --project            # run from a repo root; commit .claude/ to share with the team
./install.sh --as-code-review     # install it as /code-review instead of /dual-review
./install.sh --uninstall          # moves the files aside as *.bak.<timestamp>
```

### Windows (PowerShell)

```powershell
cd $HOME\Downloads
Expand-Archive .\dual-review.zip -DestinationPath .
cd .\dual-review
powershell -ExecutionPolicy Bypass -File .\install.ps1      # personal, every project
# -Project       run from a repo root to install into .\.claude
# -AsCodeReview  install it as /code-review
# -Uninstall     move the files aside as *.bak.<timestamp>
```

It installs into `%USERPROFILE%\.claude`. `-ExecutionPolicy Bypass` applies to
this one run only; it doesn't change your system policy. With Git Bash you can
also run `bash install.sh`.

Restart Claude Code if `~/.claude/agents/` didn't exist before (running
sessions don't watch new directories). Otherwise both files are picked up live.

`--as-code-review` replaces the built-in `/code-review`. Per the Claude Code
docs, a skill can replace a bundled command but not its aliases, so `/review`
keeps running the built-in review.

## Use

```
/dual-review                         # branch vs default branch + uncommitted changes
/dual-review main                    # against a specific base
/dual-review --staged                # staged changes only
/dual-review #482                    # a PR (check it out first for full-file context)
/dual-review --fix                   # review, apply agreed fixes, verify until both approve
/dual-review --depth deep            # override the risk-based depth (quick | standard | deep)
/dual-review --security              # add the dedicated security reviewer (on by default for deep)
/dual-review --rounds 6              # override the depth's round cap
/dual-review --models opus,sonnet    # different models for A and B
/dual-review main focus on the auth middleware and token refresh
/dual-review -- main is flaky        # "--": everything after it is focus notes
```

A personal install (`~/.claude/skills/dual-review`) shadows the plugin: bare
`/dual-review` runs the personal copy, the plugin one is `/dual-review:dual-review`.

## What the reviewers get

- **Intent**: PR title and body, the linked issue (from `Fixes #N` or a branch
  name like `fix/2722-…`) and commit subjects. Reviewers check that the change
  does what it claims, and for a bug fix that it removes the root cause rather
  than hiding the symptom.
- **Rules**: `CLAUDE.md` always; `REVIEW.md` at the repo root if present
  (severity, paths to skip, checks to always run).
- **Depth**, picked from what the change touches:

  | Depth | When | Rounds |
  |---|---|---|
  | quick | only docs, comments, copy or tests, under 200 lines (not CLAUDE.md/AGENTS.md/REVIEW.md) | 2 |
  | standard | everything else | 3 |
  | deep | auth, payments, keys/crypto, smart contracts, migrations, CI/release, concurrency, security config, or 1,000+ lines | 5 |

  Quick reports blocker/major only. Deep asks reviewers to back each
  blocker/major with a command they ran.
- **Security pass**: on `deep` (or with `--security`), a third reviewer S
  runs in round 1 with an attacker's-eye checklist (authz, injection,
  secrets, crypto, SSRF, trust boundaries, dependencies and CI, on-chain
  access control and reentrancy). S only finds; A and B verify its findings
  by vote like any other. The report adds a `Security: …` line.

## How agreement works

- Round 1: both reviewers review independently. A finding both of them found
  with compatible fixes is accepted straight away. Each finding lists every
  place the same bug pattern appears, and the fix covers all of them.
- Bugs this change didn't introduce go to a separate **pre-existing** list.
  They're reported, never voted on and never applied unless you ask.
- Every later round launches two brand-new reviewers. They re-read the code,
  see the open items with each side's arguments, and vote on every item:
  `AGREE`, `AMEND` (propose a better fix), `DISAGREE` (`INVALID`, `WRONG_FIX`,
  `WRONG_SEVERITY` or `PRE_EXISTING`, with `path:line` evidence), or `CHOOSE`
  between two fix variants.
- An item is accepted when both agree on the same fix, rejected when both say
  it isn't real. After round 1, new findings must be introduced blockers or
  majors. A minor item gets one vote; without consensus it becomes a
  suggestion instead of another round. Nits are never voted on.
- An item whose votes repeat unchanged two rounds in a row, or that is still
  open at the round cap, is marked deadlocked and handed to you with both
  arguments.
- Verification only looks at the lines the fixes changed. An item that fails
  verification twice stops the loop with a suggestion to rethink that part.
- The report opens with a count (`To fix: 2 (1 blocker, 1 major) · …`) or
  `Nothing to fix.`, and ends with lint rules, tests or CLAUDE.md lines that
  would stop the same bugs coming back.
- The coordinator (your main session) never adds findings or breaks ties.

## Cost and tuning

Each round costs two full reviews. A standard run is at most 3 review rounds
plus 2 verify rounds, so up to 10 reviewer sessions; quick is up to 8, deep
up to 15 (5 rounds, S, 2 verify rounds). Most runs need fewer.
Ways to tune it:

- Round caps: pass `--rounds`, or edit the depth defaults in step 2 of
  `SKILL.md`.
- Depth rules: edit the deep/quick lists in step 2 of `SKILL.md`.
- Reviewer model or effort: set `model:` and `effort:` in
  `agents/dual-reviewer.md` (it ships with `effort: high` and your session's
  model).
- Lenses and checklist: edit the lens lines in step 3 of `SKILL.md` and the
  "What failure looks like here" section of the agent.
- Large diffs review better in slices: pass a narrower base or review a few
  commits at a time.
