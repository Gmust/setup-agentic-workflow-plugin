---
name: dual-review
description: Two independent fresh-context reviewers (plus a dedicated security reviewer on risky changes) review the current change in parallel, then re-review a shared fix list round after round until both agree on every fix. Review depth follows the change's risk. With --fix, applies the agreed fixes and has fresh reviewers verify them until both approve.
argument-hint: "[--staged | #PR | base-ref] [--fix] [--depth quick|standard|deep] [--security | --no-security] [--rounds N] [--models a,b] [--] [focus notes]"
disable-model-invocation: true
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git rev-parse *) Bash(git merge-base *) Bash(git symbolic-ref *) Bash(git stash create) Bash(gh pr diff *) Bash(gh pr view *) Bash(gh issue view *) PowerShell(git status *) PowerShell(git diff *) PowerShell(git log *) PowerShell(git rev-parse *) PowerShell(git merge-base *) PowerShell(git symbolic-ref *) PowerShell(git stash create) PowerShell(gh pr diff *) PowerShell(gh pr view *) PowerShell(gh issue view *)
---

# Dual review

Arguments: $ARGUMENTS

You are the **coordinator**. `dual-reviewer` subagents do all the reviewing:
A and B every round, plus S in round 1 when the security pass is on. Every
round launches them **in parallel** and **fresh**:
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
- Launch every reviewer of a round in **one message** (one Agent tool call
  each, `subagent_type: dual-reviewer`, or the plugin-scoped name your agent
  list shows, e.g. `dual-review:dual-reviewer`): A and B, plus S in round 1
  when the security pass is on. They may run in the background: wait for
  **all** results before doing anything with any. Before writing any round
  result, check that you hold this round's block from every reviewer you
  launched (`REVIEWER: A`, `REVIEWER: B`, and `REVIEWER: S` if launched); if
  one is missing, keep waiting for its completion notification. If one fails
  or returns partial output, relaunch
  that one once; if it fails again, stop and report.
- Noise costs a whole round, so every rule below that drops or parks an item
  is deliberate. Don't keep an item in the loop that the rules park.
- After each round, post one progress line, e.g.
  `Round 2/3 (standard) — 5 agreed, 1 rejected, 2 open`.

## 1. Parse arguments

- `--fix`: after consensus, apply the agreed fixes and run the verify loop.
- `--depth quick|standard|deep`: override the risk-based depth from step 2.
- `--security` / `--no-security`: force the dedicated security pass on or
  off. Default: on for `deep`, off otherwise.
- `--rounds N`: max review rounds including round 1; overrides the depth's
  default.
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

**Change diff.** Always write resolved SHAs into commands, never `$(...)`, so
the same command works in Bash and PowerShell.
- `--staged` → `git diff --cached`
- base ref R → `git diff <sha>` with `<sha>` from `git merge-base R HEAD`
  (branch commits plus uncommitted tracked changes).
- PR → `gh pr view <n> --json headRefName,baseRefName,baseRefOid,title,body`.
  If the current branch is the PR head, compare `baseRefOid` with
  `git rev-parse origin/<base>`. They differ → tell the user `origin/<base>`
  is out of date and offer `git fetch origin <base>` (it needs their
  approval), then recompute; declined → continue and add a report line that
  the review may include base-branch commits. Then use `git diff <sha>` with
  `<sha>` from `git merge-base origin/<base> HEAD`. Otherwise use
  `gh pr diff <n>` and tell the user reviewers only see the diff; with
  `--fix`, ask them to `gh pr checkout <n>` first and stop.
- No target → default branch D from
  `git symbolic-ref --short refs/remotes/origin/HEAD` with the `origin/`
  prefix removed (fallback `main`, then `master`). Current branch is D →
  `git diff HEAD`; otherwise `git diff <sha>` with `<sha>` from
  `git merge-base D HEAD`.

Untracked files, only for the base-ref, no-target and current-branch PR
scopes (none for `--staged` or `gh pr diff`): the `??` entries from
`git status --short`, minus build output, lockfiles and other generated files.

Run the diff command with `--stat`. If it and the untracked list are both
empty, say there's nothing to review and stop. Over ~3,000 changed lines:
tell the user in one line that a narrower scope will review better, then
continue.

**Intent.** Collect what the change is supposed to do. Skip any source that
fails (no `gh`, no remote, no PR); never stop over it.
- PR: title and body from `gh pr view` (the target PR, or the current
  branch's PR if one exists).
- Commits: `git log --format=%s <sha>..HEAD` (at most 20 subjects).
- Issue: a number from `Fixes/Closes #N` in the PR body, or from the branch
  name (`fix/2722-…` → 2722): `gh issue view N --json title,body`.
Quote, don't paraphrase: titles, plus up to 15 lines from the PR body and
the issue, acceptance criteria first. List the commands so reviewers can
read the full text.

**Review rules.** List `REVIEW.md` at the repo root if it exists, and every
`AGENTS.md` that governs a changed file: the root one and the nearest one in
a parent directory of each changed path. (CLAUDE.md loads into every reviewer
automatically; AGENTS.md does not unless CLAUDE.md imports it.)

**Depth.** Pick from what the change touches, not from who wrote it:
- `deep`: auth/authz, payments or billing, keys, signing or crypto,
  smart-contract or on-chain code, database migrations or schema, CI
  workflows, release or installer scripts, concurrency primitives, security
  config, or more than 1,000 changed lines.
- `quick`: only docs, comments, copy or tests, and under 200 changed lines.
  A docs change to CLAUDE.md, AGENTS.md or REVIEW.md is `standard`: agents act
  on it.
- `standard`: everything else.

Defaults: quick → 2 rounds, standard → 3, deep → 5. Verify rounds: 2 for all.
Security pass: on for deep, off otherwise, unless `--security` or
`--no-security` says so.

Build the SCOPE block. It goes verbatim into every reviewer prompt:

```
SCOPE
repo: <toplevel>
branch: <branch>
change diff: <exact command>
untracked files (read in full): <paths or none>
depth: <quick|standard|deep> (<reason in a few words>) · security pass: <on|off>
intent: <quoted titles/lines, or none found>
intent sources: <commands, or none>
review rules: <REVIEW.md and AGENTS.md paths, or none>
user focus notes: <text or none>
```

## 3. Round 1 — DISCOVER

Lenses (both reviewers still report any blocker/major they see):
- **A — correctness & safety**: logic, edge cases, error handling,
  concurrency, security, data integrity.
- **B — design & robustness**: intent and approach, API/type contracts,
  backward compatibility, tests that actually exercise the change,
  performance, maintainability, project conventions (AGENTS.md, CLAUDE.md,
  REVIEW.md).
- **S — security** (round 1 only, when the security pass is on): a dedicated
  attacker's-eye pass. S finds; it never votes. Its findings are verified by
  fresh A and B like any other.

Prompt for each reviewer:

```
You are Reviewer <A|B|S>. Mode: DISCOVER. Round 1 of max <N>.
Primary lens: <lens>.

<SCOPE block>

Output only the DISCOVER block from your instructions.
```

## 4. Build the ledger

Merge all round-1 outputs (A, B, and S if it ran) into a ledger of items `F1..Fn`, ordered blocker, major,
minor:
- Same underlying defect or bug class (even at different lines) → one item;
  union the `instances`; keep both reviewers' evidence. Different defects on
  the same line → separate items.
- Each item: severity, location, instances, problem, evidence, current fix
  text, origin (`A`, `B`, `S` or a combination like `A+S`), status, a
  `[security]` tag for anything S found or that is a security defect, `prevent` suggestions, and a short
  history of votes and arguments.
- `introduced: pre-existing` → not a ledger item. Put it on the
  **pre-existing list** (deduplicated, never voted on, never applied unless
  the user asks). If one reviewer says introduced and the other says
  pre-existing for the same defect, it's an OPEN item and the vote settles it.
- Found by two reviewers (any two of A, B, S) with compatible fixes →
  **ACCEPTED** (two independent sessions reached the same fix). Use the more complete fix text, the union
  of instances and the higher severity.
- Found by two with conflicting fixes → **OPEN** with fix variants
  `(a)` and `(b)`.
- Found by one → **OPEN**. Only A and B vote in later rounds, so an item from
  S alone always goes to a vote.
- Nits → a deduplicated nit list. Nits are never voted on and never block.
- Exception: A and B left nits on the same lines that read the code or text
  in conflicting ways, or propose contradictory changes. Two reviewers
  disagreeing on what it means is evidence of an ambiguity, so make it an
  **OPEN** item, severity `minor`, with variants (a) A's reading and fix,
  (b) B's reading and fix. Reviewers may also AMEND it to a rewrite that is
  unambiguous whichever meaning is intended.
- `APPROACH: CONCERN` from either reviewer → the **approach list** with the
  reviewer's words. From both → it leads the report. `INTENT: PARTIAL` goes
  on the same list.

No OPEN items → consensus; go to step 6.

## 5. Rounds 2..N — ADJUDICATE

Launch two fresh reviewers:

```
You are Reviewer <A|B>. Mode: ADJUDICATE. Round <k> of max <N>.
Primary lens: <lens>.

<SCOPE block>

OPEN ITEMS (vote on every one)
F<n> [<severity>] <path:line> — origin: <A, B, S or a combination like A+S>
  instances: ...
  problem: ...
  evidence: ...
  current fix: ...            (or: fix variants: (a) ... (b) ...)
  history: R1 B found it. R2 A: DISAGREE WRONG_FIX — "<why>". R2 B: AMEND …

SETTLED ITEMS (context only; REOPEN needs blocker-level evidence)
F<n> [<severity>] ACCEPTED — <problem, one line> → <fix, one line>
F<n> REJECTED — <problem, one line>: <why, one line>

ALREADY ON THE PRE-EXISTING LIST (don't report these again)
- <path:line> <one line>

Output only the ADJUDICATE block from your instructions.
```

Resolve each OPEN item from **this round's two votes**:

| A | B | Result |
|---|---|---|
| AGREE | AGREE | ACCEPTED |
| AGREE or DISAGREE WRONG_SEVERITY | DISAGREE WRONG_SEVERITY (or reversed) | ACCEPTED (both accept the fix); same proposed level → use it, else note "severity split A=x B=y" |
| DISAGREE INVALID | DISAGREE INVALID | REJECTED |
| DISAGREE PRE_EXISTING | DISAGREE PRE_EXISTING | move to the pre-existing list |
| AMEND | AGREE (or reversed) | replace the fix with the amendment; stays OPEN |
| AMEND | AMEND | OPEN with variants (a) A's, (b) B's |
| CHOOSE x | CHOOSE x | ACCEPTED with variant x |
| anything else | | stays OPEN; add both arguments to history |

Then, in this order:
- **Minor gets one vote.** A `minor` item that is not ACCEPTED or REJECTED
  after the round it was first voted on → **SUGGESTION** (reported with both
  positions, not deadlocked, not voted again).
- NEW FINDING → dedupe against the ledger and the pre-existing list; new
  defects become OPEN items. Each reviewer's PRE-EXISTING lines → the
  pre-existing list.
- REOPEN → move the item back to OPEN with the evidence in its history.
- Conflicting nits from A and B on the same lines → new OPEN item, as in
  step 4 (it gets the one minor vote next round).
- An item whose two votes and claims repeat unchanged from the previous round
  → **DEADLOCKED**; stop sending it.
- Consensus when no OPEN items remain. Otherwise run the next round, up to N.
  At the cap, every OPEN item becomes DEADLOCKED.

## 6. Report

Open with one tally line: `To fix: <n> (<x> blocker, <y> major, <z> minor)
· deadlocked <d> · pre-existing <p> · suggestions <s>`. When the security pass
ran, add a second line: `Security: <k> confirmed, <j> rejected, <d>
deadlocked` or `Security: no issues found`. Security items keep their
`[security]` tag and a deadlocked security blocker is listed first. If there is nothing
to fix and nothing deadlocked, the line is `Nothing to fix.` and you add the
pre-existing and suggestion counts only if non-zero.

```
## Dual review — <consensus in k rounds | no full consensus after N rounds> · <depth>
<tally line>
Scope: <diff command> · <files> files, +<adds>/−<dels>

### Approach (<n>)            ← first section when both reviewers raised it
- A: <concern> / B: <concern>

### Agreed fixes (<n>)
- F1 [blocker] path:line (+2 more: path:line, path:line) — <problem>
  Fix: <agreed fix>

### Deadlocked — your call (<n>)
- F6 [major] path:line — <problem>
  A: <position + key evidence>
  B: <position + key evidence>

### Suggestions (<n>)          ← minor items without consensus
- F7 path:line — <problem> · A: <position> · B: <position>

### Pre-existing — not caused by this change (<n>)
- path:line [<severity>] — <problem>

### Rejected (<n>)
- F4 path:line — <problem> · rejected: <why>

### Nits (not voted)
- path:line — <nit>

### Prevent recurrence
- <lint rule / test / AGENTS.md, CLAUDE.md or REVIEW.md line> — would have caught F1, F3
```

Omit empty sections. If a blocker is deadlocked, or both reviewers raised an
approach concern, end the report with one line suggesting the approach be
reconsidered before more fixing. If nothing is left to fix, end with one line:
this approval is evidence for the human reviewer, not a substitute for one.

## 7. Apply and verify (only with `--fix`, or when the user says yes)

Without `--fix`, ask with AskUserQuestion: "Apply the agreed fixes?" —
"All agreed fixes (Recommended)", "Blocker and major only", "Don't apply".
Deadlocked items, suggestions and pre-existing items are applied only if the
user names them (and picks a side for deadlocked ones).

1. **Snapshot**: run `git stash create` (it changes nothing). Printed hash H
   → fix-only diff is `git diff H`; empty output → `git diff HEAD`.
2. **Apply** each chosen fix exactly as agreed, at every listed instance, as
   the smallest change that does it. If the code no longer matches what the
   fix assumes, don't improvise: mark it NOT_APPLIED with the reason. Keep a
   list of files you edited (untracked ones don't show in the fix-only diff).
3. **Checks**: run the project's fast checks if AGENTS.md (its `Checks`
   section), CLAUDE.md or the repo documents them (format, lint, typecheck, tests touching the edited code).
   Keep each command and the last ~20 lines of its output. Don't commit.
4. **VERIFY**: two fresh reviewers in parallel:

   ```
   You are Reviewer <A|B>. Mode: VERIFY. Verify round <v> of max 2.
   Primary lens: <lens>.

   <SCOPE block>
   fix-only diff: <command>
   files edited by the fixes (read untracked ones in full; the fix-only diff
   omits them): <paths>
   checks run: <command → pass/fail + key output lines, or "none documented">

   AGREED ITEMS (check every one, every instance)
   F<n> [<severity>] <path:line> (+instances) — <problem> → fix: <agreed fix> (<APPLIED|NOT_APPLIED: why>)

   OPEN ITEMS (vote on every one; omit this section if none)
   <as in ADJUDICATE>

   ALREADY ON THE PRE-EXISTING LIST (don't report these again)
   - <path:line> <one line>

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
   - NEW FINDING on lines the fix-only diff changed → OPEN item for the next
     verify round; apply it only after both reviewers vote it ACCEPTED by the
     §5 ADJUDICATE table. A NEW FINDING anywhere else → pre-existing list.
6. Repeat until both reviewers return `VERDICT: APPROVE` with every agreed
   item DONE or DEFERRED and nothing OPEN, or 2 verify rounds have run. If
   the same item fails verification twice, stop fixing it: report it and
   suggest reconsidering that part of the approach.

Final message: the tally line, verify status, the files changed, anything
still not fixed, deadlocked or pre-existing, and a reminder that the changes
are uncommitted (`git diff` to inspect).
