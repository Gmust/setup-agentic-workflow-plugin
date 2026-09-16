# shared by hooks; sourced, not executed
input=$(cat)
cwd=$(printf '%s' "$input" | jq -r '.cwd // empty'); cwd="${cwd:-.}"
sid=$(printf '%s' "$input" | jq -r '.session_id // "default"')
hf="${HANDOFF_FILE:-docs/HANDOFF.yaml}"
marker="${TMPDIR:-/tmp}/handoff-session-$sid"
counter="${TMPDIR:-/tmp}/handoff-counter-$sid"
mtime() { stat -f '%m' "$1" 2>/dev/null || stat -c '%Y' "$1" 2>/dev/null; }
# git ground truth: recent commits + dirty tree, ~50 tokens; empty outside git
git_truth() {
  (cd "$cwd" 2>/dev/null && git rev-parse --is-inside-work-tree >/dev/null 2>&1) || return 0
  printf -- '--- git\n'; (cd "$cwd" && git log --oneline -5 2>/dev/null; git status --short 2>/dev/null | head -20)
}
# handoff content problems, one per line; empty = ok
handoff_lint() {
  grep -qE '^next:[[:space:]]*[^[:space:]~]' "$1" && ! grep -qE '^next:[[:space:]]*null[[:space:]]*$' "$1" || echo "next is empty/null"
  [ "$(wc -l < "$1")" -le 40 ] || echo "over 40 lines"
}
