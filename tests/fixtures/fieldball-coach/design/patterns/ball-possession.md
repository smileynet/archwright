---
kind: pattern
id: ball-possession
name: "Ball Possession Authority"
scale: verbs-interactions
confidence: "★★"
status: active
serves: [ball-always-somewhere]
context: []
completed_by: []
resolves_into:
  - "behavior:ball-state-lifecycle"
  - "contract:ball-possession-events"
  - "constraint:single-ball-writer"
  - "dependency:ball-write-ownership"
---

# Ball Possession Authority

## Problem

**Any fielder can receive a pass at any time, but the world's physics say exactly one entity holds the ball.**

## Context

Core play mechanic. Every action in a practice execution flows through who has the ball.

## Forces

- **Desire:** Any fielder can receive a pass at any time (open play, responsive AI).
- **Constraint (hard):** Exactly one entity holds the ball — physics of the sport (★★).
- **Constraint (hard):** Only one component may write possession state, or race conditions produce double-possession.

## Evidence

- Without a single authority, two AI controllers writing `ball_holder = self` in the same frame produced double-possession in early prototypes.
- Prior art: request/validate is the standard model in sports games (FIFA, NBA2K) — controllers request, an authority commits.
- Rejected alternative: locking per-controller writes — spreads the invariant across N controllers instead of centralizing it in 1 service.

## Therefore

**Request/validate model.** Controllers REQUEST transfers via `BallStateService.request_transfer()`. BallStateService VALIDATES and commits. The ball is "in flight" during transfer (no holder). Only BallStateService writes `ball_holder`.

## Consequences

- Controllers must handle rejection (transfer_rejected event).
- Introduces one frame of "in flight" state that UI must render.
- All possession bugs localize to one file.

## Verification

- `constraint:single-ball-writer` — grep: `ball_holder` assignments only in `ball_state_service.gd` (★★, mechanical)
- `behavior:ball-state-lifecycle` — statechart invariant `at-most-one-holder` (★★, model-checked / trace-validated)

## Completion

- Completed by a possession-UI pattern (not included in this fixture).
