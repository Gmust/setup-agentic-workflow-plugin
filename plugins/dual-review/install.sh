#!/usr/bin/env bash
# Installs the /dual-review skill and its dual-reviewer subagent for Claude Code.
#
#   ./install.sh                     # personal: ~/.claude (all projects)
#   ./install.sh --project           # this repo: ./.claude (commit it to share)
#   ./install.sh --as-code-review    # also take over /code-review
#   ./install.sh --uninstall [--project]
#
# Existing files are moved to *.bak.<timestamp>, never overwritten.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.claude"
SKILL_NAME="dual-review"
UNINSTALL=0

for arg in "$@"; do
  case "$arg" in
    --project)        DEST="$(pwd)/.claude" ;;
    --as-code-review) SKILL_NAME="code-review" ;;
    --uninstall)      UNINSTALL=1 ;;
    -h|--help)        sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

STAMP="$(date +%Y%m%d-%H%M%S)"
AGENT_FILE="$DEST/agents/dual-reviewer.md"

backup() {
  if [ -e "$1" ]; then
    local target="$1.bak.$STAMP" n=1
    while [ -e "$target" ]; do target="$1.bak.$STAMP.$n"; n=$((n + 1)); done
    mv "$1" "$target"
    echo "  backed up $1 -> $target"
  fi
}

if [ "$UNINSTALL" -eq 1 ]; then
  echo "Removing from $DEST"
  backup "$AGENT_FILE"
  for name in dual-review code-review; do
    dir="$DEST/skills/$name"
    if [ -f "$dir/SKILL.md" ] && grep -q "Mode: DISCOVER" "$dir/SKILL.md"; then
      backup "$dir"
    fi
  done
  echo "Done. Backups are kept next to the originals; delete them when you're sure."
  exit 0
fi

new_agents_dir=0
new_skills_dir=0
[ -d "$DEST/agents" ] || new_agents_dir=1
[ -d "$DEST/skills" ] || new_skills_dir=1

mkdir -p "$DEST/agents" "$DEST/skills"

echo "Installing into $DEST"
backup "$AGENT_FILE"
cp "$SRC/agents/dual-reviewer.md" "$AGENT_FILE"
echo "  agent  -> $AGENT_FILE"

SKILL_DIR="$DEST/skills/$SKILL_NAME"
backup "$SKILL_DIR"
mkdir -p "$SKILL_DIR"
sed "s/^name: dual-review\$/name: $SKILL_NAME/" \
  "$SRC/skills/dual-review/SKILL.md" > "$SKILL_DIR/SKILL.md"
echo "  skill  -> $SKILL_DIR/SKILL.md  (/$SKILL_NAME)"

echo
if [ "$new_agents_dir" -eq 1 ]; then
  echo "Restart Claude Code: $DEST/agents/ is new, and running sessions don't watch new directories."
elif [ "$new_skills_dir" -eq 1 ]; then
  echo "In running sessions run /reload-skills (new skills directory), or restart Claude Code."
fi
if [ "$SKILL_NAME" = "code-review" ]; then
  echo "/code-review now runs the dual review. The /review alias still runs the built-in review."
fi
echo "Try it: /$SKILL_NAME   or   /$SKILL_NAME main --fix"
