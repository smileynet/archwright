---
id: "088"
title: "ELK diagram: export + figure semantics + aria-live"
status: open
priority: medium
blocked_by: []
---

## Problem

The diagram lacks semantic meaning for assistive technology, has no export capability for documentation, and the info panel updates silently without notifying screen readers.

## What to fix

- Add SVG `<title>` and `<desc>` elements for figure-level semantics
- Provide a PNG export button (canvas-based rasterization of the SVG)
- Add `aria-live="polite"` to the info/detail panel so screen readers announce selection changes
