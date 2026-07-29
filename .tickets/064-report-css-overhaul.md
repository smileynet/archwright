---
id: "064"
title: "Report: CSS overhaul — layout, typography, visual hierarchy"
status: done
blocked_by: []
priority: high
---

# Report: CSS overhaul

## Problem

The current report has ~22 CSS rules producing a flat, unstyled appearance. The wireframes designed a polished dashboard with visual hierarchy, card elevation, proper spacing, and responsive layout. The output reads like a debug dump, not a product report.

## What to build

1. **Visual hierarchy:** verdict line large and colored; section headers with divider lines; cards with proper elevation (shadow, not just border)
2. **Card differentiation:** decision cards visually distinct from approval cards from drill-down cards (different left-border color, icon treatment)
3. **Button styling:** primary actions (Approve Fix) colored with contrast; secondary (Review/Amend) outlined
4. **Input styling:** radio buttons custom-styled, text inputs with clear focus states
5. **Section spacing:** 8px grid per design system; proper vertical rhythm between sections
6. **Responsive:** readable at mobile widths (the target game is mobile-landscape)
7. **Print stylesheet:** clean output without response bar, with diagram
8. **Focus/hover states:** all interactive elements have visible focus indicators (WCAG 2.4.7)

## Design tokens to implement

```
Typography: system-ui prose, ui-monospace code, tabular-nums counts
Scale: body 15px, heading 20/26px, caption 12.5px
Spacing: 8px unit; values 8, 16, 24, 32
Card: elevation via box-shadow, radius 8px
Status colors: success/danger/warning/neutral/info (existing vars)
```

## Acceptance criteria

- [ ] Verdict line visually dominant (size, color, weight)
- [ ] Cards have visible elevation (box-shadow, not flat border-only)
- [ ] Decision vs approval cards visually distinguishable without reading content
- [ ] Buttons styled as primary/secondary variants
- [ ] Readable at 360px viewport width (mobile portrait)
- [ ] Print: diagram prints, response bar hidden, cards clean
- [ ] All interactive elements have visible :focus-visible outline
- [ ] Dark mode: all elements maintain AA contrast
