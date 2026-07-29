---
id: "079"
title: "Report: smooth scroll for anchor navigation with reduced-motion respect"
status: open
blocked_by: []
priority: low
---

# Report: smooth scroll

## Finding

F09: `scroll-behavior` is not set — anchor navigation jumps instantly. The wireframe specifies smooth scroll for drill-down navigation with `prefers-reduced-motion` respect.

## What to fix

Add to CSS:
```css
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
```

## Acceptance criteria

- [ ] Clicking "← back to the diagram" smoothly scrolls
- [ ] Anchor links (#detail-*) smoothly scroll
- [ ] `prefers-reduced-motion`: instant scroll (no animation)
- [ ] Verified via Playwright: scroll position changes over multiple frames (not instant)
