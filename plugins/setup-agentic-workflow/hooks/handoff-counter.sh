#!/bin/sh
# PostToolUse: count mutating tool calls; every HANDOFF_EVERY (default 15) remind to refresh the handoff.
# Resets whenever the handoff itself is written (by any tool).
. "$(dirname "$0")/_common.sh"
[ -f "$cwd/$hf" ] || exit 0
tool=$(printf '%s' "$input" | jq -r '.tool_name // empty')
target=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.command // empty')
every="${HANDOFF_EVERY:-15}"

case "$target" in *"$(basename "$hf")"*) printf 0 > "$counter"; exit 0 ;; esac
# ponytail: Bash counts only when the command looks like a write; reads (cat/grep/ls) are free
if [ "$tool" = "Bash" ]; then
  printf '%s' "$target" | grep -qE '(^|[^>])>[^&]|>>|sed -i|tee |git (commit|apply|mv|rm)|\bmv |\brm |\bcp |\btouch |\bmkdir ' || exit 0
fi

n=$(( $(cat "$counter" 2>/dev/null || echo 0) + 1 ))
printf '%s' "$n" > "$counter"
[ "$n" -ge "$every" ] || exit 0
printf 0 > "$counter"
jq -n --arg m "$n mutating tool calls since $hf was last written. Update it now from the facts below: goal/done/wip/blocked/next/decisions — snapshot, refs not content, under 40 lines.
$(git_truth)" \
  '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$m}}'
