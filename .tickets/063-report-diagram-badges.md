---
id: "063"
title: "Report: verification badges on diagram state nodes"
status: done
blocked_by: ["061"]
priority: high
---

# Report: verification badges on diagram elements

## Problem

The wireframe (wf-all-clear) shows per-step verification badges (✓/✗/○) on the diagram itself — the diagram IS the verification surface. Currently badges only appear in the text drill-down sections.

## What to build

1. Append status glyphs to state labels in the Mermaid source: `state_name: "Label ✓"` or use Mermaid's note/annotation syntax
2. In needs-attention posture: failing states get ✗ badge and visual highlight (different fill/border)
3. Badge rendering must satisfy P4 (color + glyph + label together — WCAG 1.4.1)
4. Diagram footer text updates per posture: "every step verified ✓" vs "steps needing attention are marked ✗"

## Acceptance criteria

- [ ] All-clear: every state shows ✓ badge
- [ ] Needs-attention: failing states show ✗ with visual highlight
- [ ] Pending states show ○ (neutral)
- [ ] Badges are readable in both light and dark mode
- [ ] Planted violation on lacrosse-bosse shows ✗ on the affected state
