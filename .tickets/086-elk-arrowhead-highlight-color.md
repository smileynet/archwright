---
id: "086"
title: "ELK diagram: arrowhead color follows edge highlight state"
status: done
priority: medium
blocked_by: []
---

## Problem

When an edge is highlighted (hover/selection), the path stroke changes color but the arrowhead marker retains its default color, creating a visual disconnect.

## What to fix

Either use `context-stroke` in the marker definition (if browser support is sufficient) or define per-state marker variants (default, hover, selected) and swap `marker-end` references when highlight state changes.
