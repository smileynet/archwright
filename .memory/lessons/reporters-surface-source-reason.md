# Reporters must surface the source's reason, not re-derive it

One-line: the suite hardcoded "(alloy jar unavailable)" as its skip label; when the real reason changed, the label lied.

**Date:** 2026-07-17 · **Source:** Alloy wiring session

`run-fixture-tests.sh` now prints check.py's own skip message. Any wrapper that
re-states a tool's status in its own words will drift from the truth.
