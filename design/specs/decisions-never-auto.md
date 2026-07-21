---
kind: constraint
id: decisions-never-auto
from_patterns:
  - "pattern:three-ask-types"
confidence: "★★"
protects_experience: "exp-decisions-wait"
user_story: "Nothing ambiguous is ever answered by a setting — judgment calls always wait for a human."
check:
  method: grep
  target: "tools/report/"
  pattern: "ask_type\\s*===?\\s*(ASK_APPROVAL|[\"']approval[\"']).*auto|auto.*ask_type\\s*===?\\s*(ASK_APPROVAL|[\"']approval[\"'])"
  include: ["*.py", "*.ts", "*.js"]
  expect: present
links:
  - target: "behavior:ask-lifecycle"
    type: enforces
  - target: "contract:asks-block"
    type: constrains
---

# Decisions Are Never Auto-Approved

## Rule

The only code path that sets `auto_approved` is guarded by an explicit
`ask_type == "approval"` test on the same line or expression. No unconditional
or type-blind auto-approval exists anywhere in the generator.

## Rationale

`three-ask-types` + the `hitl-hard-floor` force (design-system#D003/#D004):
decisions carry genuine ambiguity and ★★ implications — no configuration may
resolve them. The ask-lifecycle behavior spec proves the property over the state
machine (Alloy, ★★); this constraint pins the implementation to the same guard
so the code cannot drift from the proven model. Positive polarity per ticket 012:
we check the guard EXISTS at the assignment site, not that a negation is absent.

## Violations Look Like

```python
# BAD — type-blind auto-approval:
if config.auto_approve != "off":
    ask.auto_approved = True
```

## Correct Usage

```python
# GOOD — the type guard is part of the auto-approve expression:
ask.auto_approved = ask_type == "approval" and covered_by(config.auto_approve, ask)
```
