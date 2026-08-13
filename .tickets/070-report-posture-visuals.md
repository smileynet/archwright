---
id: "070"
title: "Report: posture-specific visual treatment"
status: done
blocked_by: ["061", "064"]
priority: medium
---

# Report: posture-specific visual treatment

## Problem

All four postures (all-clear, needs-attention, tool-error, empty-project) currently render with the same visual structure. The wireframes design distinct visual signatures per posture.

## What to build

1. **All-clear:** calm green-tinted verdict, diagram dominant (full-width), no urgency cues
2. **Needs-attention:** verdict with count badges (urgency), diagram with ✗ marks, DECISIONS/APPROVALS sections prominent
3. **Tool-error:** distinct warning banner (orange/amber), distinguishable from violations, explains what broke
4. **Empty-project:** friendly onboarding message ("run the pipeline to see results"), no diagram section, guidance on next steps

## Acceptance criteria

- [x] Each posture has a visually distinct verdict area
- [x] All-clear: green/calm, diagram-first, no action needed
- [x] Needs-attention: urgency cues, asks sections prominent
- [x] Tool-error: warning banner, not confused with violations
- [x] Empty-project: onboarding guidance, no broken/empty sections
