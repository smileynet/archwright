---
kind: dependency
id: executor-boundaries
from_patterns:
  - "pattern:execution-purity"
confidence: "★"
allowed:
  - source: "PlayManager3D"
    target: "ResolvedPlayView"
    type: reads
forbidden:
  - source: "PlayManager3D"
    target: "PlayResolver"
    type: calls
  - source: "PlayManager3D"
    target: "UI layer"
    type: imports
  - source: "PlayManager3D"
    target: "PracticeBuilder"
    type: imports
check:
  method: grep
  command: "grep -n 'PlayResolver\\|PracticeBuilder\\|UILayer' client/src/execution/play_manager_3d.gd"
  expect: absent
links:
  - target: "constraint:executor-no-resolve"
    type: enforces
---

# Executor Boundaries

## Rule

`PlayManager3D` reads pre-resolved data (`ResolvedPlayView`) and nothing else from other layers: no resolver, no UI, no builder.

## Why

Execution purity — the executor is a pure interpreter of resolved plays. Any reach into resolution/UI/builder layers breaks headless testability and replay determinism.

## Allowed

- PlayManager3D → ResolvedPlayView (reads) — the executor's sole input.

## Forbidden

- PlayManager3D → PlayResolver (calls) — resolution happens before execution.
- PlayManager3D → UI layer (imports) — executor runs headless.
- PlayManager3D → PracticeBuilder (imports) — authoring is a separate phase.
