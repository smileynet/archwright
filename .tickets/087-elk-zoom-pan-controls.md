---
id: "087"
title: "ELK diagram: zoom/pan controls"
status: done
priority: medium
blocked_by: []
---

## Problem

Large diagrams overflow their container with no way to navigate. Users cannot zoom in on detail or pan to off-screen regions.

## What to fix

- Manipulate SVG `viewBox` for zoom/pan state
- Wheel zoom (with Ctrl or pinch gesture on trackpad)
- Drag-to-pan (middle-click or modifier+drag)
- Fit-to-container button that resets viewBox to show the full graph
