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
  # target_status: pending    # optional (CK-06): the target isn't built yet — check
                              # reports ○ PENDING (never pass/fail) and activates when
                              # the target exists. Remove once the code lands.
  pattern: "regex or semgrep pattern"
  include: ["*.cs"]  # optional globs scoping which files are searched — bare glob
                     # matches file name, glob with '/' matches project-relative path.
                     # Scope to source extensions so docs/assets/configs don't drown
                     # the check in noise. Not valid with command: checks.
  expect: absent  # absent | present | only-in (only-in also requires only_in: <substring>)
  # POLARITY (ticket 012): express positive conditions ("X must exist") as
  # expect:present ON THE ARTIFACT — never as expect:absent on its negation.
  # Use absent ONLY for forbidden-pattern greps ("X must never appear").
  # A wrong polarity guess silently passes forever; the tool guards the worst
  # case (absence claim over 0 scanned files = SKIP, not PASS) but cannot
  # detect an inverted intent.
  #   present example: pattern "class AccessibilityAssembly" on the owning file
  #   absent example:  pattern "ball_holder\\s*=" outside the authority service
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
