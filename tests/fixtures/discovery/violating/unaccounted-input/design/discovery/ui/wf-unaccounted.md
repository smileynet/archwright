---
kind: discovery
id: wf-unaccounted
status: approved
area: ui
serves: []
---

# Wireframe: Unaccounted Input

## Decisions

### D001 — Grid layout
- **Category:** structure
- **Origin:** user
- **Decision:** Cards render in a responsive grid.
- **Rationale:** "Grid, definitely."
- **Alternatives:** List; rejected.

### D002 — Autosave every change
- **Category:** technical
- **Origin:** user
- **Decision:** Every edit persists immediately.
- **Rationale:** "I never want a save button."
- **Alternatives:** Explicit save; rejected.

## Hands To

- **Flow edges:** home → editor on EDIT [cites D001]
