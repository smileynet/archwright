---
kind: constraint
id: executor-no-resolve
from_patterns:
  - "pattern:execution-purity"
confidence: "★★"
check:
  method: grep
  target: "client/src/execution/"
  pattern: "PlayResolver|play_resolver|resolve_play"
  expect: absent
links:
  - target: "dependency:executor-boundaries"
    type: enforces
---

# Executor Does Not Resolve

## Rule

`PlayManager3D` and all code in `client/src/execution/` must never import, reference, or call `PlayResolver` or any resolution logic. The executor receives pre-computed `ResolvedPlayView` — it does not compute it.

## Rationale

If the executor resolves play data, it becomes coupled to the data model and resolution logic. Changes to how plays are authored or resolved would require touching the executor. Separation means: change resolution logic → only PlayResolver changes. Change execution logic → only PlayManager3D changes.

From: `pattern:execution-purity` → constraint "PlayManager3D never resolves" (★★)

## Violations Look Like

```gdscript
# BAD — violates executor-no-resolve:
# file: client/src/execution/play_manager_3d.gd

var resolver = PlayResolver.new()
var resolved = resolver.resolve(play_data)  # executor is resolving!
```

## Correct Usage

```gdscript
# GOOD — executor receives pre-computed data:
# file: client/src/execution/play_manager_3d.gd

func start_execution(resolved_play: ResolvedPlayView) -> void:
    # already resolved — just execute
    _current_step = 0
    _advance_step()
```
