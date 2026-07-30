---
id: "085"
title: "ELK diagram: measure label width with SVG text metrics"
status: open
priority: high
blocked_by: []
---

## Problem

Node widths are currently estimated with a character-count heuristic, which is inaccurate for variable-width fonts. Labels overflow or nodes are oversized depending on content.

## What to fix

Use a hidden SVG `<text>` element to measure actual pixel width (via `getComputedTextLength()` or `getBBox()`) before passing dimensions to ELK. This gives the layout engine accurate size constraints.
