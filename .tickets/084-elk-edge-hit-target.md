---
id: "084"
title: "ELK diagram: wider invisible hit target for edges"
status: done
priority: medium
blocked_by: []
---

## Problem

Edges are thin (1–2px stroke) and difficult to click or hover precisely, especially on touch devices or at lower zoom levels.

## What to fix

Render a transparent `stroke-width: 12` path underneath each visible edge path. Attach pointer event handlers to the wider path so the interaction target is comfortable without changing the visual appearance.
