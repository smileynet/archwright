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

# Deploy domain overlays (source of truth: tools/domains/) into the survey
# skill's references dir — skills load them via references/domains/ (survey)
# or ../archwright-survey/references/domains/ (other skills), so overlays
# work on machines where this repo isn't cloned.
DOMAINS_SRC="$REPO_DIR/tools/domains"
if [ -d "$DOMAINS_SRC" ] && [ -d "$SKILLS_DST/archwright-survey" ]; then
  rm -rf "$SKILLS_DST/archwright-survey/references/domains"
  mkdir -p "$SKILLS_DST/archwright-survey/references"
  cp -r "$DOMAINS_SRC" "$SKILLS_DST/archwright-survey/references/domains"
  echo "  ✓ domains: $(ls "$DOMAINS_SRC" | tr '\n' ' ')"
fi

# Deploy the stack adapter registry (source of truth: tools/stacks/REGISTRY.yaml)
# the same way — skills reference it as references/stacks/REGISTRY.yaml (survey)
# or ../archwright-survey/references/stacks/REGISTRY.yaml (other skills).
# Registry only — adapter implementations and conformance corpora stay in-repo.
STACKS_SRC="$REPO_DIR/tools/stacks/REGISTRY.yaml"
if [ -f "$STACKS_SRC" ] && [ -d "$SKILLS_DST/archwright-survey" ]; then
  mkdir -p "$SKILLS_DST/archwright-survey/references/stacks"
  cp "$STACKS_SRC" "$SKILLS_DST/archwright-survey/references/stacks/REGISTRY.yaml"
  echo "  ✓ stacks: references/stacks/REGISTRY.yaml"
fi

# Deploy the glossary (confidence vocabulary anchor) the same way — skills
# reference it as ../archwright-survey/references/glossary.md off-repo.
GLOSSARY_SRC="$REPO_DIR/docs/glossary.md"
if [ -f "$GLOSSARY_SRC" ] && [ -d "$SKILLS_DST/archwright-survey" ]; then
  mkdir -p "$SKILLS_DST/archwright-survey/references"
  cp "$GLOSSARY_SRC" "$SKILLS_DST/archwright-survey/references/glossary.md"
  echo "  ✓ glossary: references/glossary.md"
fi

# Deploy steering
if [ -d "$STEERING_SRC" ]; then
  for file in "$STEERING_SRC"/*.md; do
    [ -f "$file" ] || continue
    name=$(basename "$file")
    # Skip same-inode destinations (symlinked steering) — cp errors on same file
    if [ -e "$STEERING_DST/$name" ] && [ "$file" -ef "$STEERING_DST/$name" ]; then
      echo "  ✓ steering: $name (linked — already live)"
      continue
    fi
    cp "$file" "$STEERING_DST/$name"
    echo "  ✓ steering: $name"
  done
fi

echo "Done."
