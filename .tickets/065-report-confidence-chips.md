---
id: "065"
title: "Report: confidence badges as styled pill chips"
status: open
blocked_by: ["064"]
priority: medium
---

# Report: confidence badges as styled chips

## Problem

Confidence levels render as plain text in brackets (`[★★]`). The wireframe shows them as colored pill badges: `[firm rule]` / `[strong guide]` / `[advisory]` — visually distinct, using the vocabulary map's surface phrases.

## What to build

1. Render confidence as a `<span class="chip chip-{level}">` with background color and rounded corners
2. Use vocabulary surface phrases: "firm rule" (★★), "strong guideline" (★), "advisory" (—)
3. Color coding: firm rule = danger/warning background; strong guide = info; advisory = neutral
4. Satisfy P4: chip contains color + text label (never color alone)
5. Used on: approval cards, rule rows in behavior-detail, issue-detail header

## Acceptance criteria

- [ ] Confidence rendered as colored pill badges with plain-language labels
- [ ] Visually distinct from status glyphs (badges are background-colored; glyphs are text-colored)
- [ ] Readable in both light and dark modes (AA contrast on chip background)
- [ ] Applied consistently on approval cards and behavior-detail rule rows
