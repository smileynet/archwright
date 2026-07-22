---
kind: constraint
id: fence-block-scalar-pass
from_patterns:
  - "pattern:conformance-fixture"
confidence: "★★"
protects_experience: "conformance-fixture"
user_story: "A spec whose check script greps for frontmatter fences parses and runs — the literal --- in the block scalar never truncates the frontmatter (ticket 039)."
check:
  method: script
  command: |
    n=$(grep -c "^---" tests/fixtures/frontmatter-fence/target/doc.md)
    if [ "$n" -ne 2 ]; then echo "doc.md: expected 2 fence lines, got $n"; exit 0; fi
    exit 1
  expect: absent
links: []
---

# Fence Lines Countable From a Block Scalar (passing variant)

## Rule

`target/doc.md` has exactly two frontmatter fence lines, counted by a script whose
command contains the LITERAL substring `---` inside a YAML block scalar.

## Rationale

Ticket 039: `extract_frontmatter` split on the substring `---` anywhere, so this
spec's frontmatter was truncated mid-script — surfacing as a bash "unexpected EOF"
two layers from the cause. Fence-aware extraction must parse this file completely.

## Violations Look Like

```
doc.md: expected 2 fence lines, got 1
```

## Correct Usage

Fence-matching patterns may be written literally (`grep -c "^---"`) — the `-\{3\}`
escaping workaround (reflection R11) is no longer required.
