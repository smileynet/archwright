---
id: "068"
title: "Report: response bar UX — progress, feedback, keyboard access"
status: open
blocked_by: ["064"]
priority: low
---

# Report: response bar UX polish

## Problem

The response bar works functionally but lacks polish: no progress indicator, no visual feedback when recording a response, no keyboard accessibility.

## What to build

1. Progress: "2 of 5 asks answered" (count of recorded / total non-auto-approved asks)
2. Visual feedback: when a response is recorded, the card's border briefly pulses or changes color
3. Keyboard: Tab navigates between asks; Enter/Space confirms radio selections; focus trapped in active card
4. Completed cards get a subtle "answered" visual state (dimmed or checkmark overlay)

## Acceptance criteria

- [ ] Response bar shows progress: "N of M answered"
- [ ] Recording a response triggers visible card feedback
- [ ] Tab key navigates between ask cards
- [ ] Answered cards visually distinct from unanswered
