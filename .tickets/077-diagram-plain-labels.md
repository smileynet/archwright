---
id: "077"
title: "Report: diagram state labels use plain language, not raw IDs"
status: done
blocked_by: ["073"]
priority: medium
---

# Report: diagram state labels in plain language

## Finding

F03: State node labels in the diagram show raw identifiers with underscores (`library_open`, `practice_launching`). The wireframe design (D002, design-system) requires all surface text use plain language via the vocabulary map.

## What to fix

1. Map state IDs to human-readable labels before passing to Mermaid source
2. Use the model's state `description` field as the label (truncated if long), or a humanized version of the ID (underscores → spaces, title case)
3. Per-project vocabulary override (ticket 073) provides the ideal mapping; until then, humanize: `library_open` → `Library open`, `practice_launching` → `Practice launching`

## Acceptance criteria

- [x] Diagram state nodes show human-readable labels (no underscores)
- [x] Labels sourced from model state descriptions when available
- [x] Fallback: humanized ID (underscores → spaces)
- [x] Verified via Playwright: SVG text content has no underscores in state labels
