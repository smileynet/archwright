---
kind: discovery
id: wf-main
status: approved
area: ui
serves: []
---

# Wireframe: Main Screen

## Wireframe

```
+------------------------------+
|  Main Screen                 |
|  | grid area |               |
|        [ Place Tile ]        |
+------------------------------+
```

## Decisions

### D001 — Grid dominates the screen
- **Category:** structure
- **Origin:** user
- **Decision:** The play grid takes the top two thirds of the screen.
- **Rationale:** "The board IS the game — everything else is chrome."
- **Alternatives:** Side-by-side grid and controls; rejected as cramped.

### D002 — Tap to place tiles
- **Category:** mechanic
- **Origin:** user
- **Decision:** Tiles are placed by tapping a grid cell.
- **Rationale:** "Tapping feels immediate."
- **Alternatives:** Drag-and-drop; deferred.

### D003 — Drag to place tiles
- **Category:** mechanic
- **Origin:** user
- **Decision:** SUPERSEDES D002. Tiles are placed by dragging from the tray.
- **Rationale:** "After trying it, dragging reads better on tablet."
- **Alternatives:** Keeping D002 tap placement.

### D004 — Celebrate line clears
- **Category:** feedback
- **Origin:** suggested
- **Decision:** Completed lines flash before disappearing.
- **Rationale:** "Sure, some juice there is good."
- **Alternatives:** Instant removal; rejected as flat.

## Not Resolved Here

- [ ] States: loading / empty grid
- [ ] Edge cases: full tray

## Hands To

- **Flow edges:** title → main on START [cites D001]
- **State owned/shown:** grid contents, tile tray [cites D003]
- **Events emitted:** TILE_PLACED on drag release [cites D003]
