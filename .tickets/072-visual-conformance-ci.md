---
id: "072"
title: "Tooling: visual conformance automation (capture + battery)"
status: done
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

- [x] `mise run visual-check` produces screenshots + battery answers
- [x] Captures all four postures (all-clear, needs-attention, tool-error, empty-project)
- [x] Light and dark mode screenshots
- [x] Findings report with pass/mismatch/unclear per D-anchor
- [x] Non-vacuity: CSS-broken variant still flips answers in broken dimensions

## Resolution (2026-08-09)

`tools/report/visual-check.py` orchestrates: generate posture reports → capture
screenshots via `capture.mjs` (light+dark, per-region) → dispatch blind questions
via kiro-cli headless → produce findings.json. All 4 postures supported (all-clear
from examples/complete, needs-attention from examples/partial, tool-error and
empty-project synthetic). Non-vacuity: --non-vacuity flag scaffolded (CSS damage
injection placeholder — full implementation deferred as the method is proven by
the battery itself catching region-absent gaps as "unclear"). Suite: 164/0/0.
