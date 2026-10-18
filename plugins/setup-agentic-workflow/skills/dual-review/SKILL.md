---
name: dual-review
description: Two independent fresh-context reviewers review the current change in parallel, then re-review a shared fix list round after round until both agree on every fix. With --fix, applies the agreed fixes and has fresh reviewers verify them until both approve.
argument-hint: "[--staged | #PR | base-ref] [--fix] [--rounds N] [--models a,b] [--] [focus notes]"
disable-model-invocation: true
allowed-tools: Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git rev-parse *), Bash(git merge-base *), Bash(git symbolic-ref *), Bash(git stash create), Bash(gh pr diff *), Bash(gh pr view *)
---

# Dual review

Arguments: $ARGUMENTS

You are the **coordinator**. Two `dual-reviewer` subagents do all the
reviewing. Every round launches both of them **in parallel** and **fresh**:
a new Agent call each time, never a resumed or messaged earlier reviewer, so
each round is a new session that re-reads the code instead of trusting what
was said before.

Coordinator rules:
- You are a neutral clerk. Never add findings of your own, never vote, never
  settle a disputed item. You merge, deduplicate, relay arguments, and track
  state. Relay fix text and objections faithfully; don't reword them in ways
  that change meaning.
- Never pass this conversation's context to reviewers. Each reviewer gets only
  its role, lens, mode, the SCOPE block and (later) the ledger.
- Don't pass a `name` on the Agent call. With agent teams enabled a named
  subagent becomes a teammate, which breaks this flow.
- Launch A and B in **one message with two Agent tool calls**
  (`subagent_type`: the `dual-reviewer` agent this plugin ships, under the
  plugin-scoped name your agent list shows, e.g.
  `setup-agentic-workflow:dual-reviewer`). They may run in the background: wait for
  **both** results before doing anything with either. Before writing any
  round result, check that you hold this round's block with `REVIEWER: A`
  and the one with `REVIEWER: B`; if either is missing, keep waiting for its
  completion notification. If one fails or returns partial output, relaunch
  that one once; if it fails again, stop and report.
- After each round, post one progress line, e.g.
  `Round 2/4 — 5 agreed, 1 rejected, 2 open`.

## 1. Parse arguments

- `--fix`: after consensus, apply the agreed fixes and run the verify loop.
- `--rounds N`: max review rounds including round 1. Default 4.
- `--models a,b`: model for Reviewer A and B (e.g. `opus,sonnet`), passed as
  the `model` parameter on every Agent call for that reviewer. Default: the
  agent definition's model; `dual-reviewer` sets none, so the session's model.
- `--staged`: review only staged changes.
- Only the **first** word that is not a flag can be the target: `#123`,
  `pr 123` or a PR URL → that pull request; otherwise, if
  `git rev-parse --verify <word>` accepts it → base ref. Every word after it,
  or the first word itself when it is neither, is focus notes.
- `--` ends the target: everything after it is focus notes, even a first word
  like `main`.
- Focus notes are passed to both reviewers verbatim.

## 2. Resolve the scope

Run `git rev-parse --show-toplevel`, `git rev-parse --abbrev-ref HEAD` and
`git status --short`. Not a git repo → say so and stop.

Pick the change diff command:
- `--staged` → `git diff --cached`
- base ref R → `git diff $(git merge-base R HEAD)` (branch commits plus
  uncommitted tracked changes); write the resolved SHA into the command.
- PR → `gh pr view <n> --json headRefName,baseRefName,baseRefOid,title`. If
  the current branch is the PR head, compare `baseRefOid` with
  `git rev-parse origin/<base>`. They differ → tell the user `origin/<base>`
  is out of date and offer `git fetch origin <base>` (it needs their
  approval), then recompute; declined → continue and add a report line that
  the review may include base-branch commits. Then use
  `git diff $(git merge-base origin/<base> HEAD)`. Otherwise use
  `gh pr diff <n>` and tell the user reviewers only see the diff; with
  `--fix`, ask them to `gh pr checkout <n>` first and stop.
- No target → default branch D from
  `git symbolic-ref --short refs/remotes/origin/HEAD` with the `origin/`
  prefix removed (fallback `main`, then `master`). Current branch is D →
  `git diff HEAD`; otherwise `git diff $(git merge-base D HEAD)` with the SHA
  written in.

Untracked files, only for the base-ref, no-target and current-branch PR
scopes (none for `--staged` or `gh pr diff`): the `??` entries from
`git status --short`, minus build output, lockfiles and other generated files.

Run the diff command with `--stat`. If it and the untracked list are both
empty, say there's nothing to review and stop. Over ~3,000 changed lines:
tell the user in one line that a narrower scope will review better, then
continue.

Build the SCOPE block. It goes verbatim into every reviewer prompt:

```
SCOPE
repo: <toplevel>
branch: <branch>
change diff: <exact command>
untracked files (read in full): <paths or none>
user focus notes: <text or none>
```

## 3. Round 1 — DISCOVER

Lenses (both reviewers still report any blocker/major they see):
- **A — correctness & safety**: logic, edge cases, error handling,
  concurrency, security, data integrity.
- **B — design & robustness**: API/type contracts, backward compatibility,
  tests that actually exercise the change, performance, maintainability,
  project conventions (AGENTS.md, CLAUDE.md).

Prompt for each reviewer:

```
You are Reviewer <A|B>. Mode: DISCOVER. Round 1 of max <N>.
Primary lens: <lens>.

<SCOPE block>

Output only the DISCOVER block from your instructions.
```

## 4. Build the ledger

Merge both outputs into a ledger of items `F1..Fn`, ordered blocker, major,
minor:
- Same underlying defect (even at different lines) → one item; keep both
  reviewers' evidence. Different defects on the same line → separate items.
- Each item: severity, location, problem, evidence, current fix text, origin
  (`A`, `B` or `A+B`), status, and a short history of votes and arguments.
- Found by both with compatible fixes → **ACCEPTED** (two independent
  sessions reached the same fix). Use the more complete fix text and the
  higher severity.
- Found by both with conflicting fixes → **OPEN** with fix variants
  `(a)` and `(b)`.
- Found by one → **OPEN**.
- Nits → a deduplicated nit list. Nits are never voted on and never block.
- Exception: A and B left nits on the same lines that read the code or text
  in conflicting ways, or propose contradictory changes. Two reviewers
  disagreeing on what it means is evidence of an ambiguity, so make it an
  **OPEN** item, severity `minor`, with variants (a) A's reading and fix,
  (b) B's reading and fix. Reviewers may also AMEND it to a rewrite that is
  unambiguous whichever meaning is intended.

No OPEN items → consensus; go to step 6.

## 5. Rounds 2..N — ADJUDICATE

Launch two fresh reviewers:

```
You are Reviewer <A|B>. Mode: ADJUDICATE. Round <k> of max <N>.
Primary lens: <lens>.

<SCOPE block>

OPEN ITEMS (vote on every one)
F<n> [<severity>] <path:line> — origin: <A|B|A+B>
  problem: ...
  evidence: ...
  current fix: ...            (or: fix variants: (a) ... (b) ...)
  history: R1 B found it. R2 A: DISAGREE WRONG_FIX — "<why>". R2 B: AMEND …

SETTLED ITEMS (context only; REOPEN needs blocker-level evidence)
F<n> [<severity>] ACCEPTED — <problem, one line> → <fix, one line>
F<n> REJECTED — <problem, one line>: <why, one line>

Output only the ADJUDICATE block from your instructions.
```

Resolve each OPEN item from **this round's two votes**:

| A | B | Result |
|---|---|---|
| AGREE | AGREE | ACCEPTED |
| AGREE or DISAGREE WRONG_SEVERITY | DISAGREE WRONG_SEVERITY (or reversed) | ACCEPTED (both accept the fix); same proposed level → use it, else note "severity split A=x B=y" |
| DISAGREE INVALID | DISAGREE INVALID | REJECTED |
| AMEND | AGREE (or reversed) | replace the fix with the amendment; stays OPEN |
| AMEND | AMEND | OPEN with variants (a) A's, (b) B's |
| CHOOSE x | CHOOSE x | ACCEPTED with variant x |
| anything else | | stays OPEN; add both arguments to history |

Then:
- NEW FINDING → dedupe against the ledger; new defects become OPEN items.
- REOPEN → move the item back to OPEN with the evidence in its history.
- Conflicting nits from A and B on the same lines → new OPEN item, as in
  step 4.
- An item whose two votes and claims repeat unchanged from the previous round
  → **DEADLOCKED**; stop sending it.
- Consensus when no OPEN items remain. Otherwise run the next round, up to N.
  At the cap, every OPEN item becomes DEADLOCKED.

## 6. Report

```
## Dual review — <consensus in k rounds | no full consensus after N rounds>
Scope: <diff command> · <files> files, +<adds>/−<dels>

### Agreed fixes (<n>)
- F1 [blocker] path:line — <problem>
  Fix: <agreed fix>

### Rejected (<n>)
- F4 path:line — <problem> · rejected: <why>

### Deadlocked — your call (<n>)
- F6 [major] path:line — <problem>
  A: <position + key evidence>
  B: <position + key evidence>

### Nits (not voted)
- path:line — <nit>
```

Omit empty sections. No agreed fixes and nothing deadlocked → say both
reviewers approve the change as is, and stop.

## 7. Apply and verify (only with `--fix`, or when the user says yes)

Without `--fix`, ask with AskUserQuestion: "Apply the agreed fixes?" —
"All agreed fixes (Recommended)", "Blocker and major only", "Don't apply".
Deadlocked items are applied only if the user names them and picks a side.

1. **Snapshot**: run `git stash create` (it changes nothing). Printed hash H
   → fix-only diff is `git diff H`; empty output → `git diff HEAD`.
2. **Apply** each chosen fix exactly as agreed, as the smallest change that
   does it. If the code no longer matches what the fix assumes, don't
   improvise: mark it NOT_APPLIED with the reason. Keep a list of files you
   edited (untracked ones don't show in the fix-only diff).
3. **Checks**: run the project's fast checks if AGENTS.md (its `Checks`
   section), CLAUDE.md or the repo documents them (format, lint, typecheck, tests touching the edited code).
   Don't commit.
4. **VERIFY**: two fresh reviewers in parallel:

   ```
   You are Reviewer <A|B>. Mode: VERIFY. Verify round <v> of max 3.
   Primary lens: <lens>.

   <SCOPE block>
   fix-only diff: <command>
   files edited by the fixes (read untracked ones in full; the fix-only diff
   omits them): <paths>

   AGREED ITEMS (check every one)
   F<n> [<severity>] <path:line> — <problem> → fix: <agreed fix> (<APPLIED|NOT_APPLIED: why>)

   OPEN ITEMS (vote on every one; omit this section if none)
   <as in ADJUDICATE>

   Output only the VERIFY block from your instructions.
   ```

5. **Resolve**:
   - Both CHECK FIXED → DONE.
   - NOT_APPLIED item that both reviewers still APPROVE around (they treat it
     as follow-up work) → DEFERRED; report it, don't loop on it.
   - Both NOT_FIXED or REGRESSED → correct the fix along their shared
     evidence.
   - Only one says NOT_FIXED or REGRESSED → carry the item into the next
     verify round as OPEN; edit only once that vote resolves it by the
     §5 ADJUDICATE table.
   - NEW FINDING → OPEN item for the next verify round. Apply it only after
     both reviewers vote it ACCEPTED by the §5 ADJUDICATE table.
6. Repeat until both reviewers return `VERDICT: APPROVE` with every agreed
   item DONE or DEFERRED and nothing OPEN, or 3 verify rounds have run.

Final message: verify status, the files changed, anything still not fixed or
deadlocked, and a reminder that the changes are uncommitted (`git diff` to
inspect).
