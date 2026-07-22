---
kind: constraint
id: fence-block-scalar-fail
from_patterns:
  - "pattern:conformance-fixture"
confidence: "★"
protects_experience: "conformance-fixture"
user_story: "Deliberately-violating variant: asserts 3 fence lines where 2 exist — must FAIL, proving the block-scalar script survived parsing and actually executed (vacuity rule)."
check:
  method: script
  command: |
    n=$(grep -c "^---" tests/fixtures/frontmatter-fence/target/doc.md)
    if [ "$n" -ne 3 ]; then echo "doc.md: expected 3 fence lines, got $n"; exit 0; fi
    exit 1
  expect: absent
links: []
---

# Fence Lines Countable From a Block Scalar (violating variant)

## Rule

Deliberately wrong: asserts `target/doc.md` has three fence lines (it has two).

## Rationale

Extension Protocol rule 4: a checker proven only on passing cases may be vacuous.
If frontmatter parsing truncated the script, the check could never produce this
FAIL — so the FAIL is the proof the fix works end to end.

## Violations Look Like

```
doc.md: expected 3 fence lines, got 2
```

## Correct Usage

n/a — this variant exists to fail.
