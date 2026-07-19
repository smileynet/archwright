---
kind: dependency
id: ball-write-ownership
from_patterns:
  - "pattern:ball-possession"
confidence: "★★"
protects_experience: "single-holder"  # product-force id
user_story: "When two fielders contend for the ball, exactly one ends up holding it — never both."
allowed:
  - source: "BallStateService"
    target: "ball_holder"
    type: writes
forbidden:
  - source: "FielderAIController"
    target: "ball_holder"
    type: writes
  - source: "PlayManager3D"
    target: "ball_holder"
    type: writes
check:
  method: grep
  target: "client/src"
  pattern: "ball_holder\\s*=(?!=)"
  expect: only-in
  only_in: "ball_state_service.gd"
links:
  - target: "constraint:single-ball-writer"
    type: enforces
---

# Ball Write Ownership

## Rule

Write access to `ball_holder` belongs to `BallStateService` alone. Controllers and executors are forbidden writers.

## Why

Single-writer ownership is what makes the at-most-one-holder invariant (★★) locally verifiable — one file to audit, one component to trust.

## Allowed

- BallStateService → ball_holder (writes) — it is the possession authority.

## Forbidden

- FielderAIController → ball_holder (writes) — must use `request_transfer()`.
- PlayManager3D → ball_holder (writes) — executors never mutate possession.
