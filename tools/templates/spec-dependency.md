---
kind: dependency
id: rule-slug
from_patterns:
  - "pattern:source-pattern-id"
confidence: "★"
protects_experience: "experience-id"  # modeled experience (preferred) or product-force id
user_story: "One sentence describing what the user experiences when this rule holds."
allowed:
  - source: "ComponentA"
    target: "ComponentB"
    type: imports  # imports | calls | writes | reads
forbidden:
  - source: "ComponentC"
    target: "ComponentB"
    type: imports
check:
  method: grep  # grep | semgrep | script
  command: "grep -rn 'ComponentB' src/component_c/"
  expect: absent
  # POLARITY (ticket 012): forbidden dependencies → expect:absent on the
  # forbidden import/call pattern. Required dependencies ("A must go through
  # B") → expect:present on the artifact, never absent-on-the-negation.
  # Declarative target+pattern checks SKIP (not PASS) when 0 files were
  # scanned; command: checks have no such guard — own your semantics.
links:
  - target: "boundary:system-boundary"
    type: enforces
---

# Dependency Rule Name

## Rule

(Which components can depend on which, and in what direction.)

## Why

(What architectural principle this protects — separation of concerns, testability, single responsibility.)

## Allowed

- ComponentA → ComponentB (because: A orchestrates B)

## Forbidden

- ComponentC → ComponentB (because: C is a peer, not a consumer — coupling here creates circular dependency)
