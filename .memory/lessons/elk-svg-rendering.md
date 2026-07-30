# Lesson: ELK.js SVG Rendering

**Session:** 2026-07-30 (diagram spike comparison)
**Incident:** ELK spline edges rendered as jagged polylines. Codex identified: bend points for SPLINES mode are cubic bezier control points, not polyline vertices.

## Rule

When rendering ELK edge sections as SVG:
- **ORTHOGONAL/POLYLINE:** Use `M` + `L` (line-to) commands — points are actual bend vertices.
- **SPLINES:** Use `M` + `C` (cubic bezier) commands — points after the start come in groups of 3 (control1, control2, endpoint). Remaining points (< 3) fall back to `L`.

## Arrowhead alignment

- Use `markerUnits="userSpaceOnUse"` (not `strokeWidth`) — prevents scaling mismatch on highlight.
- Set `refX` to the marker width (tip exactly at path endpoint).
- Do NOT shorten the path — ELK's endpoints are pre-computed to the node boundary.
- For highlighted state: use separate `<marker>` definitions with different fill colors (CSS can't target markers inside `<defs>` via parent selectors).
