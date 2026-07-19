---
id: 032
title: "Audit trace hardening fixes against upstream check_trace()"
status: open
blocked_by: []
---

# Audit trace hardening fixes against upstream check_trace()

Our local branch applied 7 codex review findings to the trace validation code.
Upstream absorbed trace validation into `check_trace()` inside
`archwright-check.py`. Audit whether upstream already has these fixes; port
any that are missing.

## The 7 findings (from commits 8ea21b0, 8ea6ef6)

Review the diff of those commits against `main` branch to extract the specific
fixes, then compare each against upstream's `check_trace()` (line ~1300 in
`tools/archwright-check.py`).

Common categories from that review:
- Exit code consistency (0/1/2 contract)
- Error handling for malformed traces
- Edge cases in predicate translation (Untranslatable class handling)
- Clock validation
- Guard evaluation strictness (ticket 015: never silent-pass)
- Evidence recording for trace mode

## What to build

1. Read both versions side-by-side
2. For each finding that upstream doesn't already cover, write a targeted patch
3. Ensure fixes match upstream's coding style (Python, not bash)

## Acceptance criteria

- [ ] Each of the 7 findings documented as: already-present / ported / not-applicable
- [ ] Any ported fixes follow upstream's patterns (error shape, exit codes, evidence recording)
- [ ] Suite green (incl. trace-strict fixture)
