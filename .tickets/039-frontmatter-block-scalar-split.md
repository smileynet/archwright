---
id: "039"
title: "extract_frontmatter truncates YAML block scalars containing '---'"
status: done
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

- [x] Spec files with `---` inside block scalars parse correctly in check + validate tools
- [x] Conformance fixture: passing AND violating variants
- [x] Field workaround spec (crew-research design/specs/zero-migration.md) parses without the escaping trick

## Resolution (2026-07-22)

- Fence-aware extraction in all three sites: `archwright-check.py extract_frontmatter`, `archwright-validate.py extract_frontmatter`, and `archwright-validate.py _discovery_body` — opening fence must be line 1 (`---[ \t]*\r?\n` at position 0), closing fence is the next `^---[ \t]*$` LINE (multiline regex). Block-scalar content is indented, so it can never match a fence line.
- Conformance fixture `tests/fixtures/frontmatter-fence/`: constraint spec with literal `grep -c "^---"` in a block-scalar script — passing variant PASSES (exit 0), deliberately-violating variant FAILs with its violation output (exit 1), proving the parsed script executed (vacuity rule). Validate parses it too. 3 suite checks; suite green 143/0/0 (all 140 prior checks pass under the rewrite — regression clean).
- crew-research `design/specs/zero-migration.md` verified parsing with the `-\{3\}` escaping removed (frontmatter complete, script intact, 1057 chars).
- R11 reflection marked OBSOLETE; derive skill Step 1b example updated; AGENTS.md count row → 143.
