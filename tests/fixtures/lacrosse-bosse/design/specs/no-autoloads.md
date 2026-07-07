---
kind: constraint
id: no-autoloads
from_patterns:
  - "pattern:explicit-dependencies"
confidence: "★"
check:
  method: grep
  target: "project.godot"
  pattern: "^autoload/"
  expect: absent
links: []
---

# No Autoloads

## Rule

No autoloads registered in `project.godot` for v1. All dependencies are explicit via RuntimeExecutionContext injection.

## Rationale

Autoloads hide dependencies (can't see what a component needs from its interface), break testability (can't mock a global without framework hacks), and have the wrong lifecycle for run-scoped state (autoloads persist across the entire app; practice runs start and end).

From: `pattern:explicit-dependencies` → constraint "Zero autoloads for v1" (★)

Confidence is ★ (not ★★) because future promotion IS allowed — some services may genuinely earn autoload status if they meet promotion criteria (app-wide, persistent, needed by components that can't receive injection).

## Violations Look Like

```ini
# BAD — in project.godot:
[autoload]
autoload/InputManager="*res://src/services/input_manager.gd"
autoload/AudioManager="*res://src/services/audio_manager.gd"
```

## Correct State

```ini
# GOOD — project.godot has no [autoload] section, or it's empty:
[autoload]
# None for v1. Promotion criteria: app-wide + persistent + can't receive injection.
```
