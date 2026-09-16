#!/bin/sh
# Stop: refuse to end the turn while files changed *this session* are newer than the handoff.
# stop_hook_active guard → blocks at most once per turn.
. "$(dirname "$0")/_common.sh"
[ "$(printf '%s' "$input" | jq -r '.stop_hook_active // false')" = "true" ] && exit 0
cd "$cwd" 2>/dev/null || exit 0
[ -f "$hf" ] || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

since=$(mtime "$marker"); since="${since:-0}"
hand=$(mtime "$hf")
# newest changed file (tracked or untracked), excluding the handoff; NUL-safe for odd paths
newest=$(git ls-files -m -o --exclude-standard -z | grep -zvx "$hf" | xargs -0 -I{} sh -c '[ -f "$1" ] && (stat -f %m "$1" 2>/dev/null || stat -c %Y "$1")' _ {} | sort -n | tail -1)
lint=$(handoff_lint "$hf")
if [ -n "$lint" ]; then
  jq -n --arg hf "$hf" --arg l "$(printf '%s' "$lint" | tr '\n' ';')" '{decision:"block",reason:("\($hf) fails lint: \($l). Fix it before stopping.")}'; exit 0
fi
[ -n "$newest" ] || exit 0
[ "$newest" -gt "$hand" ] && [ "$newest" -ge "$since" ] || exit 0

jq -n --arg hf "$hf" '{decision:"block",reason:("Working tree changed after \($hf) was last written. Update the snapshot (done/wip/next with evidence) before stopping. If nothing meaningful changed, touch the file.")}'
