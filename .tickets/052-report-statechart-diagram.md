---
id: "052"
title: "Report: render the statechart as an actual diagram with edges, not a state list"
status: open
blocked_by: []
priority: high
---

# Report: render the statechart as an actual diagram

## Problem

The report's "How it works" section was designed (wf-all-clear, wf-overview) to show an interactive statechart with:
- States as nodes with plain-language names (vocabulary-mapped)
- Edges labeled with events (also vocabulary-mapped)
- Per-step/arrow verification badges (✓/✗/○)
- Click any step or arrow to drill into behavior-detail

Currently it renders a flat `<ul>` bullet list of state names — no edges, no diagram, no interactivity.

## What to build

1. Use the model YAML (`design/models/*.yaml`) to extract states + transitions
2. Render as an SVG or Mermaid statechart (inline in the HTML — self-contained constraint holds)
3. Apply vocabulary map to state/event names (plain-language surface)
4. Add per-state verification badge from the check-json coverage data
5. Make states/edges clickable → scroll to or expand the behavior-detail section

## Validation target

Lacrosse Bosse `design/models/gameplay-ui-actors.yaml` — 7 actors, multiple states with transitions defined. The generated report should show the practice-hud and step-transition state machines as readable diagrams.

## Acceptance criteria

- [ ] States rendered as nodes with vocabulary-mapped names
- [ ] Transitions rendered as labeled edges between states
- [ ] Verification badges (✓/✗/○/…) appear per state
- [ ] Diagram renders inline in the self-contained HTML (no external dependencies)
- [ ] Click a state → shows its rules and what it protects (behavior-detail pattern)
- [ ] Lacrosse-bosse report shows the step-transition lifecycle as a readable diagram
