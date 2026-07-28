---
id: "069"
title: "Report: navigation — smooth scroll, sticky back-link, history"
status: open
blocked_by: ["062"]
priority: low
---

# Report: navigation & scroll behavior

## Problem

Navigation between sections is functional (anchor links work) but lacks polish: no smooth scroll, no persistent way-back, no browser history integration.

## What to build

1. Smooth scroll: `scroll-behavior: smooth` on html, with `prefers-reduced-motion` respect
2. Sticky "← back to diagram" when scrolled into behavior-detail territory
3. History: `pushState` on anchor navigation so browser Back button works
4. Scroll position restore when navigating back

## Acceptance criteria

- [ ] Clicking diagram state smoothly scrolls to detail section
- [ ] "← back to diagram" visible as sticky element when in detail area
- [ ] Browser Back button returns to previous scroll position
- [ ] `prefers-reduced-motion`: instant scroll, no animation
