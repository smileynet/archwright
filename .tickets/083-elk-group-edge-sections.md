---
id: "083"
title: "ELK diagram: group multi-section edges under one element"
status: open
priority: medium
blocked_by: []
---

## Problem

ELK splits edges into multiple sections (e.g. when routing through hierarchy levels). Each section currently renders as an independent SVG element, so hover/selection highlights only one segment and arrowheads appear at intermediate joins.

## What to fix

Wrap all sections of a logical edge in one `<g>` element. Apply interaction handlers and highlight styles to the group. Render the arrowhead only on the terminal section.
