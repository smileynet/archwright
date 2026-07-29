---
id: "076"
title: "Report: diagram shows most informative actor, not just first with transitions"
status: open
blocked_by: []
priority: medium
---

# Report: diagram actor selection

## Finding

F02: The diagram renders the clipboard actor (3 states) because it's the first actor with transitions. The practice-hud actor (5 states including the step-transition sub-lifecycle) would be a more informative front door for a cold reader trying to understand how the app works.

## What to fix

Change `_diagram_section` in `render_html.py` to select the actor with the most transitions (or states) rather than the first one found. For multi-actor models, consider showing the parent/top-level actor or the one linked to the most experiences.

Selection heuristic: max(transitions count) → ties broken by max(states count) → ties broken by actor order.

## Acceptance criteria

- [ ] Diagram shows the actor with the most transitions
- [ ] Lacrosse-bosse shows practice-hud (active → step_transitioning → play_complete → returning_to_clipboard)
- [ ] Verified via Playwright: diagram SVG contains the expected state names
