---
id: "066"
title: "Report: code context rendering for violations"
status: done
blocked_by: ["064"]
priority: medium
---

# Report: code context rendering

## Problem

Evidence from violations renders as a plain `<pre>` dump of grep output. The wireframe (wf-issue-detail) shows formatted code context: file path header, ±2 lines of context, flagged line highlighted, additional locations expandable.

## What to build

1. Parse evidence lines into structured code blocks (file:line: content)
2. Render as a code block with line numbers and the flagged line visually marked (background highlight)
3. File path + line number as a header above the code block
4. When multiple locations: show first, then "(+ N more ▸)" expandable disclosure
5. Monospace font, proper overflow handling (horizontal scroll, not wrap)

## Acceptance criteria

- [x] Evidence renders as formatted code block with line numbers
- [x] Flagged line visually highlighted (background color)
- [x] File path displayed as header above code context
- [x] Multiple locations: first shown, rest behind disclosure
- [x] Horizontal scroll on long lines (no line wrapping in code blocks)
- [x] Dark mode: code highlighting visible with adequate contrast
