---
kind: discovery
id: wf-orphan
status: approved
area: ui
serves: []
---

# Wireframe: Orphan Output

## Decisions

### D001 — Single column layout
- **Category:** structure
- **Origin:** user
- **Decision:** Content flows in one column.
- **Rationale:** "Keep it simple."
- **Alternatives:** Two columns; rejected.

## Hands To

- **Flow edges:** start → here on OPEN [cites D001]
- **Events emitted:** SUBMIT on button press with debounce and retry logic
