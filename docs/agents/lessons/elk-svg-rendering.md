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


## Playwright Interaction with SVG Elements

**Session:** 2026-07-31 (ELK integration + visual validation)

SVG `<g>` elements (edge-groups) can't be clicked normally by Playwright because the parent `<svg>` element "intercepts pointer events" — the SVG covers the full container and Playwright's actionability check sees the SVG as the target.

- **State nodes** work because they have a visible `<rect>` filling their bounds (Playwright can hit-test it).
- **Edges** (thin `<path>` elements inside a `<g>`) fail because the visible stroke is too narrow and the SVG element gets reported as the interceptor.
- **Fix:** Use `{ force: true }` on edge clicks, or use `page.evaluate()` to dispatch the event programmatically.
- **Alternative:** The invisible hit-target path (`.edge-hit`, 14px stroke-width) exists for mouse interaction but Playwright still sees the SVG intercept.
