---
kind: dependency
id: executor-boundaries
from_patterns:
  - "pattern:execution-purity"
confidence: "★★"
allowed:
  - source: "PlayManager3D"
    target: "ResolvedPlayView"
    type: reads
  - source: "PlayManager3D"
    target: "RuntimeObjective"
    type: reads
  - source: "PlayManager3D"
    target: "signals (step_completed, run_finished)"
    type: emits
forbidden:
  - source: "PlayManager3D"
    target: "PlayResolver"
    type: imports
  - source: "PlayManager3D"
    target: "RuntimeUI"
    type: imports
  - source: "PlayManager3D"
    target: "ObjectivePlanBuilder"
    type: imports
check:
  method: grep
  command: "grep -n 'PlayResolver\\|RuntimeUI\\|ObjectivePlanBuilder' client/src/execution/play_manager_3d.gd"
  expect: absent
links:
  - target: "constraint:executor-no-resolve"
    type: enforces
---

# Executor Boundaries

## Rule

PlayManager3D reads pre-computed data (ResolvedPlayView, RuntimeObjectives) and emits signals. It does NOT import or use PlayResolver, RuntimeUI, or ObjectivePlanBuilder.

## Why

Each forbidden dependency represents a different concern bleeding into the executor:
- PlayResolver → resolution logic (upstream data concern)
- RuntimeUI → presentation (parallel concern, different change cadence)
- ObjectivePlanBuilder → objective construction (mediation layer, testable separately)

The executor is a pure cursor: advance step, manage chains, signal completion. Nothing else.

## Allowed

- PlayManager3D → ResolvedPlayView (reads pre-computed play structure)
- PlayManager3D → RuntimeObjective (reads pre-built objectives)
- PlayManager3D → signals out (step_completed, run_finished)

## Forbidden

- PlayManager3D → PlayResolver (must not resolve — receives resolved data)
- PlayManager3D → RuntimeUI (must not present — UI observes via signals)
- PlayManager3D → ObjectivePlanBuilder (must not build objectives — receives built objectives)
