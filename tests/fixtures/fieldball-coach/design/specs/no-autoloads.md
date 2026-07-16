---
kind: constraint
id: no-autoloads
from_patterns:
  - "pattern:explicit-dependencies"
confidence: "★"
check:
  method: grep
  target: "project.godot"
  pattern: "^\\[autoload\\]"
  expect: absent
links: []
---

# No Autoloads

## Rule

`project.godot` contains no `[autoload]` section. All services are injected explicitly.

## Rationale

Autoloads are hidden global dependencies — accessible from anywhere, mockable from nowhere. Explicit injection keeps every component testable headless.

## Violations Look Like

```ini
# BAD — global singleton registration:
[autoload]
BallStateService="*res://client/src/services/ball_state_service.gd"
```

## Correct Usage

```gdscript
# GOOD — explicit injection at scene setup:
fielder_controller.initialize(ball_state_service)
```
