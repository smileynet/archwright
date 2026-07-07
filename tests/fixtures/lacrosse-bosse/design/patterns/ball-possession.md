---
kind: pattern
id: ball-possession
name: "Ball Possession"
scale: verbs-interactions
confidence: "★★"
above:
  - practice-execution
resolves_into:
  - "behavior:ball-state-lifecycle"
  - "constraint:single-ball-writer"
  - "dependency:ball-write-ownership"
---

# Ball Possession

## Forces

- **Desire:** Any fielder can receive a pass at any time — gameplay fluidity requires the ball to move freely between players during practice execution.
- **Constraint (hard):** Exactly one entity holds the ball at any moment — a physical object cannot be in two places. Violating this produces impossible game states.
- **Constraint (hard):** Only one component writes possession state — multiple writers produce split-brain (two systems disagree on who has the ball).

## Tension

Free passing demands any fielder receive at any time, but physics requires exactly one holder, and architectural sanity requires a single source of truth for who that holder is. Without a resolution, controllers will write `ball_holder` directly, creating race conditions and double-possession bugs.

## Resolution

**Request/validate model.** Controllers REQUEST transfers via BallStateService. The service VALIDATES the request (is the ball available? is the receiver valid?) and COMMITS the state change. During transfer the ball is "in flight" (no holder). Invalid requests return the ball to the previous holder.

This gives fluidity (any controller can request at any time) while maintaining single-holder (only BallStateService commits) and single-writer (the service is the sole authority).

## Consequences

- **Recovery path needed:** What happens when BallStateService rejects a transfer? Ball returns to sender — must be smooth, not jarring.
- **In-flight duration is a tuning parameter:** Too long = unresponsive feel. Too short = might miss valid receives.
- **All ball state queries go through the service:** No component caches its own view of possession.

## Evidence

- Prior art: every team sport game (FIFA, NBA2K, Madden) uses single-authority possession with request/validate pattern.
- Domain rule: USA Lacrosse rules define possession explicitly — one player at a time, contested ball is "loose" (no holder).
- Architecture interview decision #15 (2026-06-17): "BallStateService as run-scoped source of truth. Single canonical answer to 'who has the ball'; controllers request, service validates."
