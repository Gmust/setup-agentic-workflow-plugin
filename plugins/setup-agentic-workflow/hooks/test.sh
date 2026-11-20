#!/bin/sh
# Self-check for the three hooks. Run: sh hooks/test.sh
set -e
H="$(cd "$(dirname "$0")" && pwd)"; T="${TMPDIR:-/tmp}/handoff-hooktest-$$"; S="t$$"
export TMPDIR="${TMPDIR:-/tmp}"
mkdir -p "$T/docs" && cd "$T" && git init -q && printf 'goal: t\nnext: x\n' > docs/HANDOFF.yaml && git add -A && git -c user.name=t -c user.email=t@t commit -qm i
j() { printf '{"cwd":"%s","session_id":"%s"%s}' "$T" "$S" "$1"; }
fail() { echo "FAIL: $1"; exit 1; }
# one hooks file read by Claude Code and Codex; a second copy in plugin.json would drift
jq -e '.hooks | has("SessionStart") and has("PostToolUse") and has("Stop")' "$H/hooks.json" >/dev/null || fail "hooks.json"
jq -e 'has("hooks") | not' "$H/../.claude-plugin/plugin.json" >/dev/null || fail "plugin.json missing or declares hooks"

out=$(j ',"source":"startup"' | sh "$H/handoff-inject.sh")
echo "$out" | grep -q 'goal: t' || fail inject
echo "$out" | grep -q -- '--- git' || fail "git truth"
echo "$out" | grep -q 'lint' && fail "false lint"
[ -f "$TMPDIR/handoff-session-$S" ] || fail marker
# a session started in a subdirectory still finds the handoff at the git root
mkdir sub; printf '{"cwd":"%s/sub","session_id":"%s"}' "$T" "$S" | sh "$H/handoff-inject.sh" | grep -q 'goal: t' || fail "subdir cwd"
# compaction continues the session: its start must not move
touch -t 200001010000 "$TMPDIR/handoff-session-$S"; touch -t 200101010000 .git/ref
j ',"source":"compact"' | sh "$H/handoff-inject.sh" >/dev/null
[ -n "$(find "$TMPDIR/handoff-session-$S" -newer .git/ref)" ] && fail "compact moved session start"
touch "$TMPDIR/handoff-session-$S"

# Codex wants JSON on every exit 0 of Stop
[ "$(j '' | sh "$H/handoff-stop.sh")" = '{}' ] || fail "stop on clean tree"
sleep 1; echo x > "a b.py"
j '' | sh "$H/handoff-stop.sh" | grep -q block || fail "stop should block (space path)"
[ "$(j ',"stop_hook_active":true' | sh "$H/handoff-stop.sh")" = '{}' ] || fail "stop loop guard"
sleep 1; touch docs/HANDOFF.yaml
j '' | sh "$H/handoff-stop.sh" | grep -q block && fail "stop after refresh"

cnt() { cat "$TMPDIR/handoff-counter-$S" 2>/dev/null || echo 0; }
b() { j ",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$1\"}" | sh "$H/handoff-counter.sh"; }
b 'cat a.py'; b 'ls src 2>/dev/null'
[ "$(cnt)" = 0 ] || fail "read counted"
for i in 1 2; do out=$(j ',"tool_name":"Edit","tool_input":{"file_path":"a.py"}' | HANDOFF_EVERY=2 sh "$H/handoff-counter.sh"); done
echo "$out" | grep -q additionalContext || fail "counter reminder"
b 'apply_patch <<EOF'
[ "$(cnt)" = 1 ] || fail "shell apply_patch counted"
# any change to the handoff resets, whatever wrote it
echo '# r' >> docs/HANDOFF.yaml; b 'perl -pi -e s/r/s/ docs/HANDOFF.yaml'
[ "$(cnt)" = 0 ] || fail "handoff write reset"
# Codex reports edits as apply_patch with the patch text in tool_input.command
p() { printf ',"tool_name":"apply_patch","tool_input":{"command":"*** Begin Patch\\n*** Update File: %s\\n%s*** End Patch"}' "$1" "$2"; }
j "$(p a.py)" | sh "$H/handoff-counter.sh"
[ "$(cnt)" = 1 ] || fail "apply_patch counted"
# a patch naming the handoff, or another package's handoff, did not change this one
j "$(p AGENTS.md '@@\n+see docs/HANDOFF.yaml\n')" | sh "$H/handoff-counter.sh"
j "$(p packages/a/docs/HANDOFF.yaml)" | sh "$H/handoff-counter.sh"
b 'sed -n 1,40p docs/HANDOFF.yaml 2>/dev/null'
[ "$(cnt)" = 3 ] || fail "handoff name or read reset"

# stale tree from before this session must not block
sleep 1; touch "$TMPDIR/handoff-session-$S"; sleep 1; touch docs/HANDOFF.yaml
echo y > old.py; touch -t 200001010000 old.py
j '' | sh "$H/handoff-stop.sh" | grep -q block && fail "pre-session change blocked"

# lint: empty next must block even with fresh handoff
printf 'goal: t\nnext: null\n' > docs/HANDOFF.yaml
j '' | sh "$H/handoff-stop.sh" | grep -q 'fails lint' || fail "lint block"
printf 'goal: t\nnext: x\n' > docs/HANDOFF.yaml
rm -rf "$T" "$TMPDIR/handoff-session-$S" "$TMPDIR/handoff-counter-$S" "$TMPDIR/handoff-counter-$S.sum"; echo OK
