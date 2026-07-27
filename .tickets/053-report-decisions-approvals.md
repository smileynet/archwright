---
id: "053"
title: "Report: implement decisions + approvals sections with actionable cards"
status: open
blocked_by: ["052"]
priority: high
---

# Report: decisions + approvals sections

## Problem

The designed report (wf-overview) has two action sections that don't exist in the implementation:

**DECISIONS** — smart asks where the system can't resolve ambiguity alone:
- Rule vs code conflicts (repeated failures suggest rule may be wrong)
- Firm-rule violations needing explicit sign-off
- Trust changes (promote/demote guideline confidence)
- Accepting new known debt (baseline entries)
- Ambiguous routes (contrast pair doesn't determine code-vs-design)

**APPROVALS** — contrast-pair cards showing:
- "The design says: X" / "The code does: Y"
- Recommended action
- [Approve Fix] button

Currently: neither section exists. The report shows only the verdict + pending list.

## What to build

1. `derive.py` must classify check violations into decision-situations vs approvals (the 6 situations from wf-overview are the routing logic)
2. `render_html.py` must produce:
   - Decision cards with radio options + recommendation + "why" disclosure
   - Approval cards with contrast-pair body + action button
3. The `asks` block in report.json must carry the full ask-lifecycle data (ask-id, type: decision/approval/suggestion, options, recommendation)
4. Cards integrate with the page.js reducer for response accumulation

## Validation target

Run archwright-check against lacrosse-bosse with a deliberately-violating fixture (e.g., add a `progress.visible = false` line that triggers `step-progress-visible`) — the report should show an approval card with the contrast pair.

## Acceptance criteria

- [ ] Violations route to DECISIONS or APPROVALS based on situation type
- [ ] Decision cards show radio options with recommendation highlighted
- [ ] Approval cards show "design says / code does" contrast pair
- [ ] Cards have disclosure fold for history/rationale ("why this rule exists")
- [ ] Clicking a card's action accumulates a response in the page reducer
- [ ] Empty sections are hidden (not shown with "0 items")
- [ ] Lacrosse-bosse report with a planted violation shows a working approval card
