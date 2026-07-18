#!/usr/bin/env bash
# Deploy archwright skills and steering to an AI coding tool's discovery locations.
#
# Usage:
#   deploy-skills                            # kiro, global (~/.kiro/)
#   deploy-skills --tool claude              # claude code, global (~/.claude/)
#   deploy-skills --tool codex               # codex CLI, global (~/.agents/skills/)
#   deploy-skills --project <path>           # kiro, project (<path>/.kiro/)
#   deploy-skills --tool agy --project .     # agy, project (./.agents/skills/)
#
# Per-tool conventions (verified against official docs 2026-07-17, see
# .memory/audit/deploy-targets.md):
#
#   tool    skills (global)     skills (project)      steering
#   ------  ------------------  --------------------  --------------------------------
#   kiro    ~/.kiro/skills      <p>/.kiro/skills      ~/.kiro/steering/*.md
#   claude  ~/.claude/skills    <p>/.claude/skills    ~/.claude/rules/*.md (project: <p>/.claude/rules)
#   codex   ~/.agents/skills    <p>/.agents/skills    none native — SKIP + guidance (~/.codex/AGENTS.md)
#   agy     none (plugins only) <p>/.agents/skills    none native — SKIP + guidance
#
# All four tools consume the open agent-skills SKILL.md format, so skill
# content deploys unmodified. Steering is kiro/claude-native only; for codex
# and agy the script SKIPs with a reason and prints how to wire it manually
# (it never edits the user's AGENTS.md).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
STEERING_SRC="$REPO_DIR/steering"

# Parse args
TARGET=""
TOOL="kiro"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      TARGET="$(cd "$2" && pwd)"
      shift 2
      ;;
    --tool)
      TOOL="$2"
      shift 2
      ;;
    *)
      echo "Usage: deploy-skills [--tool <kiro|claude|codex|agy>] [--project <path>]" >&2
      exit 2
      ;;
  esac
done

# Resolve destinations per tool convention.
# STEERING_DST empty = no native steering home for this tool (SKIP with reason).
STEERING_DST=""
STEERING_SKIP_REASON=""
case "$TOOL" in
  kiro)
    if [ -z "$TARGET" ]; then
      SKILLS_DST="$HOME/.kiro/skills"; STEERING_DST="$HOME/.kiro/steering"
    else
      SKILLS_DST="$TARGET/.kiro/skills"; STEERING_DST="$TARGET/.kiro/steering"
    fi
    ;;
  claude)
    if [ -z "$TARGET" ]; then
      SKILLS_DST="$HOME/.claude/skills"; STEERING_DST="$HOME/.claude/rules"
    else
      SKILLS_DST="$TARGET/.claude/skills"; STEERING_DST="$TARGET/.claude/rules"
    fi
    ;;
  codex)
    # Codex discovers skills at ~/.agents/skills (USER) and <repo>/.agents/skills
    # — NOT ~/.codex/skills. No always-on steering dir; AGENTS.md is its mechanism.
    if [ -z "$TARGET" ]; then
      SKILLS_DST="$HOME/.agents/skills"
    else
      SKILLS_DST="$TARGET/.agents/skills"
    fi
    STEERING_SKIP_REASON="codex has no steering directory — reference the content from ~/.codex/AGENTS.md (steering source: $STEERING_SRC)"
    ;;
  agy)
    # agy loads global capability via plugins ('agy plugin install'), not a
    # copyable skills dir. Project scope uses the agent-skills standard.
    if [ -z "$TARGET" ]; then
      echo "SKIP: agy has no global skills directory (plugins only — 'agy plugin install')." >&2
      echo "      Deploy per-project instead: deploy-skills --tool agy --project <path>" >&2
      exit 2
    fi
    SKILLS_DST="$TARGET/.agents/skills"
    STEERING_SKIP_REASON="agy has no steering directory — bundle as plugin rules or reference manually (steering source: $STEERING_SRC)"
    ;;
  *)
    echo "Unknown tool: $TOOL (expected kiro|claude|codex|agy)" >&2
    exit 2
    ;;
esac

if [ -z "$TARGET" ]; then
  echo "Deploying for $TOOL (global → $SKILLS_DST):"
else
  echo "Deploying for $TOOL (project → $SKILLS_DST):"
fi

mkdir -p "$SKILLS_DST"
[ -n "$STEERING_DST" ] && mkdir -p "$STEERING_DST"

# Deploy skills.
# Global kiro deploys SYMLINK instead of copy: other deployers prune unmanaged
# COPIES from ~/.kiro/skills (crew-research init.sh deleted all 13 archwright
# skills on 2026-07-18; its prune — and doctor — treat symlinks as explicitly
# owned and keep them). Symlinks also keep deployed skills live with the repo.
# Generated references (domains/stacks/glossary below) then materialize into
# the repo source tree through the link — those paths are gitignored.
# Project deploys and other tools keep copies (a machine-local absolute
# symlink inside a shared project repo would break collaborators).
if [ -d "$SKILLS_SRC" ]; then
  for skill_dir in "$SKILLS_SRC"/archwright-*/; do
    [ -d "$skill_dir" ] || continue
    name=$(basename "$skill_dir")
    rm -rf "$SKILLS_DST/$name"
    if [ "$TOOL" = "kiro" ] && [ -z "$TARGET" ]; then
      ln -s "$SKILLS_SRC/$name" "$SKILLS_DST/$name"
      echo "  ✓ skill (symlink): $name"
    else
      cp -r "$skill_dir" "$SKILLS_DST/$name"
      echo "  ✓ skill: $name"
    fi
  done
fi

# Deploy domain overlays (source of truth: tools/domains/) into the survey
# skill's references dir — skills load them via references/domains/ (survey)
# or ../archwright-survey/references/domains/ (other skills), so overlays
# work on machines where this repo isn't cloned. Cross-skill relative paths
# hold in any tool's skills dir since all skills deploy side-by-side.
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

# Deploy steering (tools with a native steering/rules dir only)
if [ -n "$STEERING_DST" ] && [ -d "$STEERING_SRC" ]; then
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
elif [ -n "$STEERING_SKIP_REASON" ]; then
  echo "  ~ steering: SKIP — $STEERING_SKIP_REASON"
fi

echo "Done."
