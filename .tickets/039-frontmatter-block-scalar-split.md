---
id: "039"
title: "extract_frontmatter truncates YAML block scalars containing '---'"
status: in_progress
blocked_by: []
---

# extract_frontmatter truncates YAML block scalars containing '---'

Field report from the crew-research tkt pipeline run (2026-07-20).

## Why

`archwright-check.py` `extract_frontmatter()` (and the same idiom anywhere else) splits
file content with `content.split("---", 2)` — on the literal substring ANYWHERE, not on
fence lines. A constraint spec whose `check.command` block scalar legitimately contains
three consecutive hyphens (e.g. a grep for frontmatter fences: `grep -c "^---"`) gets its
frontmatter truncated mid-script, producing a baffling bash "unexpected EOF" error two
layers away from the real cause. Cost ~3 debug iterations in the field before diagnosis.

## What to build

Fence-aware extraction: split on `^---\s*$` LINES (regex, multiline) rather than the
substring — first fence must be line 1, closing fence is the next fence LINE. Add a
conformance case: a constraint spec with `---` inside a block-scalar `check.command`
must parse and run (and a violating variant must FAIL, per the vacuity rule).

Workaround meanwhile (documented in the field artifacts): write fence-matching patterns
as `-\{3\}` so the literal never appears in the frontmatter.

## Acceptance criteria

- [ ] Spec files with `---` inside block scalars parse correctly in check + validate tools
- [ ] Conformance fixture: passing AND violating variants
- [ ] Field workaround spec (crew-research design/specs/zero-migration.md) parses without the escaping trick
