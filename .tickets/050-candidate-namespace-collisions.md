---
id: "050"
title: "Links pass: contract-candidate event names are a global namespace — add collision lint or scoping"
status: in_progress
blocked_by: []
---

# Contract-candidate event-name collisions across area models

Field incident (discord-poc dp-poc run, 2026-07-22): two areas independently
modeled a `CELL_RESULT` event (p1 catalog-interop, f1 clean-rooms). Because
`--links` builds ONE `all_candidate_events` set across every model file,
same-named events in different areas alias each other: contract-spec coverage
matched cross-area, producing a spurious "covered by 2 contract specs" error
on unrelated seams. Field fix was a manual rename (`MEASUREMENT_CELL_RESULT`)
plus a vetting convention in the target project — that scales badly with area
count and relies on agents remembering.

## What to build

Pick one (research both, small ADR if the answer changes the artifact format —
this touches the links semantics, so it may be a KIND-level change per the
extension protocol's two-tier governance):

1. **Collision lint**: same event name declared as a candidate in 2+ model
   files → explicit error naming both models ("rename or declare shared"),
   with a `shared: true` opt-out for genuinely cross-area events (x1's
   consumer-contract events are legitimately multi-area)
2. **Per-model scoping**: candidate coverage resolved within the declaring
   model's file first; cross-model coverage only via an explicit
   `from_model: <other-model>` reference

## Acceptance criteria
- [ ] The dp-poc collision shape (two areas, same name, separate seams)
      produces a clear error or is safely scoped — fixture proves it
- [ ] x1-style deliberate cross-area contracts still validate
- [ ] Decision + rationale recorded (ADR if links semantics changed)
