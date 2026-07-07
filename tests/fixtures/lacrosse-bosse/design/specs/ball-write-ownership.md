---
kind: dependency
id: ball-write-ownership
from_patterns:
  - "pattern:ball-possession"
confidence: "★★"
allowed:
  - source: "BallStateService"
    target: "ball_holder"
    type: writes
forbidden:
  - source: "FielderAIController"
    target: "ball_holder"
    type: writes
  - source: "FielderPlayerController"
    target: "ball_holder"
    type: writes
  - source: "PlayManager3D"
    target: "ball_holder"
    type: writes
check:
  method: grep
  command: "grep -rn 'ball_holder\\s*=' client/src/ | grep -v ball_state_service"
  expect: absent
links:
  - target: "behavior:ball-state-lifecycle"
    type: enforces
  - target: "constraint:single-ball-writer"
    type: enforces
---

# Ball Write Ownership

## Rule

Only BallStateService may write to ball possession state. Controllers, executors, and all other components must use the request API.

## Why

The single-source-of-truth invariant (★★) requires one writer. If any component outside BallStateService can mutate possession, the service's state becomes stale and the system has two conflicting views of reality.

## Allowed

- BallStateService → ball_holder (write) — the sole authority

## Forbidden

- FielderAIController → ball_holder (write) — must use request_transfer()
- FielderPlayerController → ball_holder (write) — must use request_transfer()
- PlayManager3D → ball_holder (write) — executor doesn't own ball state
- Any other component → ball_holder (write)
