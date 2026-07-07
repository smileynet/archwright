---
kind: constraint
id: rule-slug
from_patterns:
  - "pattern:source-pattern-id"
confidence: "★★"
check:
  method: grep  # grep | semgrep | script | alloy
  target: "path/to/check"
  pattern: "regex or semgrep pattern"
  expect: absent  # absent | present
links:
  - target: "behavior:affected-component"
    type: constrains
---

# Constraint Name

## Rule

(What must be true — stated clearly enough that a human can verify it by reading the code.)

## Rationale

(Why this rule exists — which force demanded it and what goes wrong without it.)

## Violations Look Like

(Concrete example of code that would violate this constraint.)

```gdscript
# BAD — violates this constraint:
ball_holder = self  # direct write outside BallStateService
```

## Correct Usage

```gdscript
# GOOD — respects this constraint:
BallStateService.request_transfer(self)  # goes through the authority
```
