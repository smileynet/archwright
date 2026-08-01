---
id: "090"
title: "report-publish: --verify flag runs Playwright smoke assertions after generation"
status: open
blocked_by: []
priority: low
---

# report-publish: --verify flag

## Problem

After `mise run report-publish`, verification is manual — grep for expected content, open in browser, eyeball. The session that shipped ELK integration ran ad-hoc Playwright checks 5+ times. A `--verify` flag would automate the smoke check.

## What to build

1. Add `--verify` flag to the report-publish mise task
2. When set, run a lightweight Playwright assertion script against the generated `report.html`
3. Assertions (minimum viable):
   - ELK diagram renders (SVG element present within 10s)
   - Actor count matches the model (states in JSON = nodes in SVG)
   - Verdict section present with expected glyph
   - Stability section present when evidence ledger exists
   - No JS console errors on page load
4. Exit 0 = all pass; exit 1 = assertion failure (report still generated, just flagged)
5. Graceful skip when playwright/chromium not installed (warn, don't block)

## Acceptance criteria

- [ ] `mise run report-publish -- --project <path> --verify` runs assertions after generation
- [ ] Assertions catch a broken ELK render (e.g., missing vendor JS)
- [ ] Missing playwright = warning + skip (not a hard failure)
- [ ] Assertion failures don't prevent the report from being written
