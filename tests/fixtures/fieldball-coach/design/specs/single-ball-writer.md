---
kind: constraint
id: single-ball-writer
from_patterns:
  - "pattern:ball-possession"
confidence: "★★"
protects_experience: "single-holder"  # product-force id
user_story: "When possession changes, every fielder and the UI agree on who holds the ball — there is one writer of truth."
check:
  method: grep
  target: "client/src"
  pattern: "ball_holder\\s*="
  expect: only-in
  only_in: "services/ball_state_service.gd"
links:
  - target: "behavior:ball-state-lifecycle"
    type: constrains
---

# Single Ball Writer

## Rule

Only `BallStateService` (services/ball_state_service.gd) assigns `ball_holder`. All other components request transfers through it.

## Rationale

Physics: exactly one entity holds the ball (★★). Single-writer localizes the invariant to one file; N writers = race conditions and double-possession.

## Violations Look Like

```gdscript
# BAD — violates this constraint (any file except ball_state_service.gd):
ball_holder = self
```

## Correct Usage

```gdscript
# GOOD — respects this constraint:
BallStateService.request_transfer(self)
```
