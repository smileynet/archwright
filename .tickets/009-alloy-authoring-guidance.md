---
id: 009
title: "Explore: alloy-authoring guidance in derive skill (safety skeletons + non-vacuity probe)"
status: open
blocked_by: []
created: 2026-07-17
---

# Explore: alloy-authoring guidance for behavior invariants

Feature suggestion from the ExposeAR field run (2026-07-17, digest "Behavior model
checks ACTIVE") — process non-disruptively; no urgency, no current breakage.

## Observation

Authoring `alloy:` expressions for ExposeAR's 3 behavior specs surfaced two reusable
disciplines that currently live only in that project's digest and spec comments:

1. **Safety-skeleton rendering.** Generated models permit stuttering and don't model
   bool vars, var updates, or guard enforcement — so `leads-to` liveness invariants
   are unprovable as written. The workable move: render the checkable safety skeleton
   (successor/predecessor restrictions, e.g. `always (M.current = Evaluating implies
   M.current' in Evaluating + Idle + Solved)`) and explicitly assign the liveness/
   payload halves to the trace check. Every unrendered invariant gets a YAML comment
   stating WHY (bool var / payload property / cross-machine / needs clock).
2. **Non-vacuity probe at authoring time.** After adding expressions, inject one
   deliberately false invariant (e.g. `always M.current = <InitialState>`) and confirm
   the checker produces a counterexample before trusting any PASS. This is Extension
   Protocol rule 4 logic applied to spec authoring — the exact defense against the
   transition-less-model episode.

## Suggested exploration

- Would a short "Authoring alloy: expressions" subsection in `archwright-derive`
  (behavior-spec steps) carry both disciplines? Worked example from ExposeAR available.
- Is the non-vacuity probe better as skill guidance or as tooling (e.g.
  `archwright-check.py --probe <spec>` auto-injecting the false invariant)? Rule-of-two
  suggests guidance first, tool when a second project needs it.

## Evidence

- ExposeAR `design/specs/{spatial-session,placement-lifecycle,mentor-session}.yaml`
  (rendered + documented-skip invariants), `.memory/archwright-digest.md` 2026-07-17
- Non-vacuity verified: injected false invariant → counterexample at trace length 2
