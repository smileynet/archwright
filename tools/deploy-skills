#!/usr/bin/env bash
# Deploy archwright skills and steering.
#
# Usage:
#   deploy-skills                    # Deploy to global ~/.kiro/
#   deploy-skills --project <path>   # Deploy to <path>/.kiro/
#   deploy-skills --project .        # Deploy to current project
#
# Both modes copy skills/ and steering/ from this repo into the target's .kiro/ directory.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
STEERING_SRC="$REPO_DIR/steering"

# Parse args
TARGET=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      TARGET="$(cd "$2" && pwd)"
      shift 2
      ;;
    *)
      echo "Usage: deploy-skills [--project <path>]" >&2
      exit 2
      ;;
  esac
done

# Default to global
if [ -z "$TARGET" ]; then
  SKILLS_DST="$HOME/.kiro/skills"
  STEERING_DST="$HOME/.kiro/steering"
  echo "Deploying to global (~/.kiro/):"
else
  SKILLS_DST="$TARGET/.kiro/skills"
  STEERING_DST="$TARGET/.kiro/steering"
  echo "Deploying to project ($TARGET/.kiro/):"
fi

mkdir -p "$SKILLS_DST" "$STEERING_DST"

# Deploy skills
if [ -d "$SKILLS_SRC" ]; then
  for skill_dir in "$SKILLS_SRC"/archwright-*/; do
    [ -d "$skill_dir" ] || continue
    name=$(basename "$skill_dir")
    rm -rf "$SKILLS_DST/$name"
    cp -r "$skill_dir" "$SKILLS_DST/$name"
    echo "  ✓ skill: $name"
  done
fi

# Deploy steering
if [ -d "$STEERING_SRC" ]; then
  for file in "$STEERING_SRC"/*.md; do
    [ -f "$file" ] || continue
    name=$(basename "$file")
    cp "$file" "$STEERING_DST/$name"
    echo "  ✓ steering: $name"
  done
fi

echo "Done."
