#!/usr/bin/env bash
# ship.sh — commit staged changes, verify upstream, push (guidance sync 2026-07-21).
#
# Usage: tools/ship.sh "commit message"   (or: mise run ship -- "commit message")
#
# Commits ONLY what is already staged (never `git add -A` — stage deliberately,
# per project git discipline), fetches, refuses to push over upstream divergence.
#
# Exit codes: 0 = committed and pushed, 1 = blocked (nothing staged, or
# upstream diverged — report printed), 2 = usage/tool error.
set -euo pipefail

MSG="${1:-}"
if [ -z "$MSG" ]; then
  echo "Usage: ship.sh \"commit message\"" >&2
  exit 2
fi

if git diff --cached --quiet; then
  echo "BLOCKED: nothing staged — stage files deliberately, then re-run" >&2
  exit 1
fi

git commit --quiet -m "$MSG"
git fetch --quiet

UPSTREAM_AHEAD=$(git log --oneline HEAD..@{upstream} 2>/dev/null | wc -l)
if [ "$UPSTREAM_AHEAD" -gt 0 ]; then
  echo "BLOCKED: upstream has $UPSTREAM_AHEAD new commit(s) — commit created locally, NOT pushed:"
  git log --oneline HEAD..@{upstream}
  echo "Review and merge/rebase per project conventions, then push manually."
  exit 1
fi

git push --quiet
echo "SHIPPED: $(git log --oneline -1)"
