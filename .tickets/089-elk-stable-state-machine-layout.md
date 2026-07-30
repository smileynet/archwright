---
id: "089"
title: "ELK diagram: stable layout for state machines"
status: open
priority: low
blocked_by: []
---

## Problem

Adding or removing a single state can cause the entire diagram to re-layout dramatically, making it hard to maintain a mental map of the structure across edits.

## What to fix

- Preserve model-order in the layout (states appear in declaration order where possible)
- Mark feedback edges (back-edges in the state graph) so ELK can route them without disrupting the primary flow
- Allocate dedicated spacing for self-loop edges to avoid overlap with outgoing transitions
