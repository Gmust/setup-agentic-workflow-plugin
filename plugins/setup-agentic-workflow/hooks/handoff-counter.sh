#!/bin/sh
# PostToolUse: count mutating tool calls; every HANDOFF_EVERY (default 15) remind to refresh the handoff.
# Resets whenever the handoff's content changed since the previous call, whatever tool or command wrote it.
. "$(dirname "$0")/_common.sh"
[ -f "$cwd/$hf" ] || exit 0
every="${HANDOFF_EVERY:-15}"

sum=$(cksum < "$cwd/$hf")
if [ "$sum" != "$(cat "$counter.sum" 2>/dev/null)" ]; then
  printf '%s' "$sum" > "$counter.sum"
  [ -f "$counter" ] && { printf 0 > "$counter"; exit 0; }
fi
# ponytail: Bash counts only when the command looks like a write (Codex may run apply_patch through the shell); reads are free
if [ "$(printf '%s' "$input" | jq -r '.tool_name // empty')" = "Bash" ]; then
  printf '%s' "$input" | jq -r '.tool_input.command // empty' | sed -E 's/[0-9&]?>>? *\/dev\/null//g' \
    | grep -qE '(^|[^>])>[^&]|>>|sed -i|tee |git (commit|apply|mv|rm)|apply_patch|\bmv |\brm |\bcp |\btouch |\bmkdir ' || exit 0
fi

n=$(( $(cat "$counter" 2>/dev/null || echo 0) + 1 ))
printf '%s' "$n" > "$counter"
[ "$n" -ge "$every" ] || exit 0
printf 0 > "$counter"
jq -n --arg m "$n mutating tool calls since $hf was last written. Update it now from the facts below: goal/done/wip/blocked/next/decisions — snapshot, refs not content, under 40 lines.
$(git_truth)" \
  '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$m}}'
