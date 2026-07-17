---
kind: constraint
id: rule-slug
from_patterns:
  - "pattern:source-pattern-id"
confidence: "★★"
protects_experience: "experience-id"  # modeled experience (preferred) or product-force id
user_story: "One sentence describing what the user experiences when this rule holds."
check:
  method: grep  # grep | semgrep | script | alloy
  target: "path/to/check"     # or a YAML list of roots — matches are unioned
  pattern: "regex or semgrep pattern"
  expect: absent  # absent | present | only-in (only-in also requires only_in: <substring>)
  # include: "*.cs"           # optional glob (or list) scoping matched file NAMES
  # include_comments: true    # optional: match inside comments too (stripped by default)
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
