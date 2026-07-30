---
id: "082"
title: "ELK diagram: keyboard accessibility"
status: done
priority: high
blocked_by: []
---

## Problem

Diagram nodes and edges are not keyboard-navigable. Screen reader users and keyboard-only users cannot interact with the diagram — no focus indicators, no activation handlers, no ARIA roles.

## What to fix

- Add `tabindex="0"` and `role="button"` to interactive elements (nodes, edges)
- Add `aria-label` with meaningful descriptions (node name, edge source→target)
- Handle Enter/Space keydown for activation (same as click)
- Add `:focus-visible` styles for clear focus indication
