---
kind: constraint
id: no-shell-exec
from_patterns:
  - "pattern:execution-purity"
confidence: "★"
protects_experience: "predictable-practice-runs"
user_story: "When a play executes, nothing leaves the engine sandbox — no spawned processes, no environment surprises."
check:
  method: grep
  target: "client"
  pattern: "OS\\.execute\\("
  include: ["*.gd"]
  expect: absent
links: []
---

# No Shell Execution in Game Scripts

## Rule

No `.gd` script calls `OS.execute(` — play execution stays inside the engine sandbox.

## Conformance Role (fixture suite)

This spec is the golden corpus for `check.include:` glob filtering (Extension
Protocol rule 4). `client/docs/porting-notes.md` deliberately contains the string
`OS.execute(` in prose. Unfiltered grep over `client/` matches it and FAILS;
with `include: ["*.gd"]` the check scopes to scripts, where the call is absent,
and PASSES. A regression in include filtering flips this check red.

## Violations Look Like

```gdscript
# BAD — shelling out mid-play:
OS.execute("ffmpeg", ["-i", replay_path])
```

## Correct Usage

```gdscript
# GOOD — in-engine replay rendering:
replay_renderer.render(replay_data)
```
