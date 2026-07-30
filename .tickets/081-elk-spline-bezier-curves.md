---
id: "081"
title: "ELK diagram: render splines as SVG cubic bezier curves"
status: open
priority: high
blocked_by: []
---

## Problem

ELK returns edge routes as spline control points, but the renderer currently connects them with straight line segments (SVG `L` commands), producing jagged polyline edges instead of smooth curves.

## What to fix

Translate ELK spline control points to SVG cubic bézier `C` commands. Group control points in sets of three (per the cubic bézier spec) and emit proper `M ... C ...` path data.
