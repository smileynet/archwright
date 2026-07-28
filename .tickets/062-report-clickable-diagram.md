---
id: "062"
title: "Report: clickable diagram states link to behavior-detail anchors"
status: open
blocked_by: ["061"]
priority: high
---

# Report: clickable diagram states → behavior-detail

## Problem

The diagram says "click any step for details" but no click handlers exist. States and edges in the rendered diagram are not wired to the behavior-detail sections below.

## What to build

1. After Mermaid renders, attach click handlers to state nodes in the SVG
2. Clicking a state scrolls to `#detail-{actor}-{state}` (the existing behavior-detail anchors)
3. Clicking an edge scrolls to the source state's detail section
4. Visual affordance: cursor:pointer on states, subtle hover effect
5. Mermaid `click` directives or post-render JS event binding

## Acceptance criteria

- [ ] Clicking a state node in the diagram scrolls to its behavior-detail section
- [ ] States show pointer cursor on hover
- [ ] Smooth scroll animation to target section
- [ ] "← back to the diagram" links scroll back to #diagram-top
- [ ] Works with keyboard (Tab into diagram, Enter to follow link)
