---
id: "009"
title: "Explore: alloy-authoring guidance in derive skill (safety skeletons + non-vacuity probe)"
status: done
closed: 2026-07-17
blocked_by: []
created: 2026-07-17
---

# Explore: alloy-authoring guidance for behavior invariants

## Resolution (2026-07-17)

Both halves shipped — rule-of-two satisfied by the TileRush C10 run (second
field project needing both disciplines):
1. **Guidance:** `archwright-derive` step 4 gains an "Authoring alloy: expressions"
   subsection (safety skeletons for unprovable liveness; document-why on every
   unrendered invariant; probe after authoring).
2. **Tooling:** `archwright-check.py --probe <spec>` auto-injects the false
   invariant (exit 0 = counterexample/good, 1 = vacuous, 2 = not probeable).
   Conformance corpus in the suite: live model → exit 0; unsatisfiable-guard
   machine → vacuity exit 1 (also exercises ticket 008's guard compilation).

Feature suggestion from the DemoAR field run (2026-07-17, digest "Behavior model
checks ACTIVE") — process non-disruptively; no urgency, no current breakage.

## Observation

Authoring `alloy:` expressions for DemoAR's 3 behavior specs surfaced two reusable
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
  (behavior-spec steps) carry both disciplines? Worked example from DemoAR available.
- Is the non-vacuity probe better as skill guidance or as tooling (e.g.
  `archwright-check.py --probe <spec>` auto-injecting the false invariant)? Rule-of-two
  suggests guidance first, tool when a second project needs it.

## Evidence

- DemoAR `design/specs/{spatial-session,placement-lifecycle,mentor-session}.yaml`
  (rendered + documented-skip invariants), `.memory/archwright-digest.md` 2026-07-17
- Non-vacuity verified: injected false invariant → counterexample at trace length 2
