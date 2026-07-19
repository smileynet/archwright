---
id: 037
title: "deploy-skills.sh: stop overwriting crew-research's subagent-reliability steering"
status: done
blocked_by: []
---

# deploy-skills.sh: stop overwriting crew-research's subagent-reliability steering

## Context

Discovered 2026-07-19 during crew-research's known-tool integration (its ticket 37): `deploy-skills.sh` copies `steering/subagent-reliability.md` into `~/.kiro/steering/`, where crew-research deploys its own tier-owned `subagent-reliability.md` (different content — crew's has a references/ pointer and eval-validated wording). The two deploys ping-pong the file: whichever ran last wins, silently.

Crew-research recorded the collision in its `compositions/known-tools.yaml` with its copy as authoritative; the fix belongs here, on the writing side.

Note the same hazard class as the 2026-07-18 prune incident (crew's init.sh deleting archwright skill copies) — but inverted: this time archwright is the deployer clobbering the other project's managed file.

## What to build

`deploy-skills.sh` must not overwrite a steering file it doesn't own. Options (pick during implementation):

1. **Rename** archwright's file to a namespaced name (e.g., `archwright-subagent-reliability.md`) — but content overlaps crew's heavily; two always-on copies of near-identical guidance wastes eager context
2. **Drop** archwright's copy from the deploy set entirely — rely on crew-research's when present; keep the file in-repo for machines without crew-research and document manual wiring
3. **Detect-and-skip** — if the destination exists and isn't archwright's content (not same-inode/symlink), SKIP with a reason (matches the script's existing same-inode skip pattern)

Whatever the choice: collision behavior is explicit in the script output (never a silent overwrite), and `archwright-conventions.md` (symlinked, uncontested) is unaffected.

## Acceptance criteria

- [x] Running deploy-skills.sh on a machine with crew-research's subagent-reliability.md present does NOT replace crew's content, and says why
- [x] A machine without crew-research still gets subagent-reliability guidance by a documented path
- [x] README/AGENTS deploy notes updated if behavior changes
