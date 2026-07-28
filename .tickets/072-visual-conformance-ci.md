---
id: "072"
title: "Tooling: visual conformance automation (capture + battery)"
status: open
blocked_by: ["061", "064"]
priority: low
---

# Tooling: visual conformance automation

## Problem

Ticket 044 proved the blind-question visual conformance method works but it's manual. After the visual overhaul, we need an automated path to detect visual regressions.

## What to build

1. `mise run visual-check` task: generates report → captures screenshots → runs battery → outputs findings
2. Update `tools/report/capture.mjs` for new Mermaid-rendered diagram sections
3. Auto-derive questions from active D-anchors in design-system.md
4. Produce a visual-diff artifact (before/after screenshots when changes detected)
5. Stays review-track (★-shaped, not a gate): findings route to human, never auto-fail

## Acceptance criteria

- [ ] `mise run visual-check` produces screenshots + battery answers
- [ ] Captures all four postures (all-clear, needs-attention, tool-error, empty-project)
- [ ] Light and dark mode screenshots
- [ ] Findings report with pass/mismatch/unclear per D-anchor
- [ ] Non-vacuity: CSS-broken variant still flips answers in broken dimensions
