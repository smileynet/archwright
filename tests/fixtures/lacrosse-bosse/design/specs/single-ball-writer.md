---
kind: constraint
id: single-ball-writer
from_patterns:
  - "pattern:ball-possession"
confidence: "★★"
check:
  method: grep
  target: "client/src/"
  pattern: "ball_holder\\s*="
  expect: only-in
  only_in: "client/src/services/ball_state_service.gd"
links:
  - target: "behavior:ball-state-lifecycle"
    type: constrains
---

# Single Ball Writer

## Rule

Only `BallStateService` may assign to `ball_holder`. No other component writes possession state directly.

## Rationale

Multiple writers produce split-brain — two components disagree on who has the ball. The request/validate model requires a single authority. If controllers write directly, the service's validation is bypassed and the single-holder invariant can be violated.

From: `pattern:ball-possession` → constraint "Only BallStateService writes possession" (★★)

## Violations Look Like

```gdscript
# BAD — violates single-ball-writer:
class_name FielderAIController

func _on_catch_ball():
    ball_holder = self  # direct write! bypasses BallStateService
```

## Correct Usage

```gdscript
# GOOD — respects single-ball-writer:
class_name FielderAIController

func _on_catch_ball():
    ball_state_service.request_transfer(self)  # goes through authority
```
