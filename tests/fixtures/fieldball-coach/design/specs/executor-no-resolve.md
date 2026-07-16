---
kind: constraint
id: executor-no-resolve
from_patterns:
  - "pattern:execution-purity"
confidence: "★"
check:
  method: grep
  target: "client/src/execution"
  pattern: "PlayResolver"
  expect: absent
links:
  - target: "dependency:executor-boundaries"
    type: constrains
---

# Executor Never Resolves

## Rule

Nothing under `client/src/execution/` references `PlayResolver`. Execution consumes pre-resolved data only.

## Rationale

Resolution during execution makes runs non-reproducible (resolution consumes live state). Replayability requires resolve-then-execute.

## Violations Look Like

```gdscript
# BAD — executor re-entering resolution:
var decision = PlayResolver.resolve_step(current_state)
```

## Correct Usage

```gdscript
# GOOD — executor steps through pre-resolved data:
var decision = resolved_play_view.step(step_index)
```
