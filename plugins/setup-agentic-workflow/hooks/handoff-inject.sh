#!/bin/sh
# SessionStart (any source): mark session start, put the handoff snapshot back into context.
# No-op when the repo has no handoff — safe in any project.
. "$(dirname "$0")/_common.sh"
touch "$marker"
f="$cwd/$hf"
[ -f "$f" ] || exit 0
printf 'HANDOFF (%s, state that survives context resets). Continue from `next`; update after each verified step.\n---\n' "$hf"
# ponytail: hot file only; 60-line cap so a bloated handoff cannot flood context
head -n 60 "$f"
lint=$(handoff_lint "$f"); [ -n "$lint" ] && printf '\n[handoff lint: %s]\n' "$(printf '%s' "$lint" | tr '\n' ';')"
git_truth
exit 0
