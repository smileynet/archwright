---
id: "055"
title: "Report: behavior-detail drill-down from diagram clicks"
status: done
blocked_by: ["052"]
priority: medium
---

# Report: behavior-detail drill-down

## Problem

The designed report (wf-behavior-detail) has a three-level drill-down:
1. Overview (diagram + verdict)
2. Behavior detail (click a state → what happens here, rules that apply, what it protects)
3. Rationale fold (how we arrived at this design)

Currently: no drill-down exists. The report is flat — one level only.

## What to build

1. Clicking a state or edge on the statechart diagram scrolls to / expands a behavior-detail section
2. Each detail section shows:
   - **What happens here** — prose from model actor state description + arrives-from/leads-to
   - **Rules that apply** — which specs guard this state, with live status badges
   - **What this protects** — the `protects_experience` from the spec, in plain language
   - **How we arrived at this** (folded) — provenance chain back to forces/patterns/decisions
3. Data source: model YAML (state descriptions, transitions) + spec YAML (which specs reference which states) + forces (the `protects_experience` → product desire chain)

## Validation target

Lacrosse-bosse `step-transition` actor has 4 states (completing, repositioning, new_step_ready, active) with 2 invariants. Clicking "completing" should show: "Green flash on completed objective, progress bar pulse" + the 2 rules + "The player's joysticks stay responsive" experience.

## Acceptance criteria

- [x] Clicking a state on the diagram shows its behavior-detail section
- [x] "What happens here" populated from model state descriptions
- [x] "Rules that apply" shows relevant specs with status badges
- [x] "What this protects" shows the product experience in plain language
- [x] "How we arrived at this" folds out with provenance (force → decision → spec)
- [x] Navigation: "← back to the diagram" returns to overview
- [x] Works as in-page anchors (self-contained, no routing framework)
