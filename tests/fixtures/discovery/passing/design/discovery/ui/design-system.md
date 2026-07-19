---
kind: discovery
id: design-system
status: approved
area: ui
serves: []
---

# Design System: Discovery Fixture

## Tokens

```yaml
tokens:
  spacing: { unit: "8px grid", allowed: [8, 16, 24] }
```

## Decisions

### D001 — One primary action per screen
- **Category:** experience
- **Origin:** user
- **Decision:** Every screen has exactly one visually dominant action.
- **Rationale:** "I never want to guess what to press next."
- **Alternatives:** Two equal-weight actions; rejected as ambiguous.

### D002 — Fixed 8px spacing grid
- **Category:** structure
- **Origin:** suggested
- **Decision:** All spacing values come from an 8px grid.
- **Rationale:** "Fine, keep it consistent."
- **Alternatives:** Free-form spacing; rejected for drift.

## Graduates to Patterns

| Tension resolved | Ledger entry | Pattern (filled at graduation) |
|------------------|--------------|-------------------------------|
| clarity vs density | design-system#D001 | pattern:one-primary-action |

## Not Resolved Here

- [ ] Dark mode theming
