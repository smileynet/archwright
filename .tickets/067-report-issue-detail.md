---
id: "067"
title: "Report: issue-detail drill-down (wf-issue-detail)"
status: open
blocked_by: ["064", "066"]
priority: medium
---

# Report: issue-detail drill-down

## Problem

The three-level drill hierarchy is incomplete. Level 1 (behavior-detail from diagram) exists; Level 2 (issue-detail from clicking a failing rule) does not. The wireframe (wf-issue-detail) designs a detailed view showing contrast pair prominently, code context, provenance chain, recommendation, and history.

## What to build

1. New section type: `.card.issue-detail` with anchor `#issue-{spec-id}`
2. Linked from: behavior-detail rule rows (when status=fail), approval card titles
3. Content (per wf-issue-detail wireframe):
   - Contrast pair (prominent, top of card)
   - WHERE: code context (file + lines + flagged line, from ticket 066)
   - WHY THIS RULE EXISTS: Because/Decided/So provenance chain
   - WHAT WE RECOMMEND: recommendation + rationale fold + action buttons
   - HISTORY: first-seen/streak data (when evidence ledger available)
4. Navigation: "← back to overview" link

## Acceptance criteria

- [ ] Clicking a failing rule in behavior-detail opens issue-detail section
- [ ] Contrast pair rendered prominently at top
- [ ] Provenance chain shows Because/Decided/So format
- [ ] Action buttons (Approve Fix / Review / Amend Rule) present and functional
- [ ] "← back to overview" navigates to diagram area
- [ ] Works as in-page anchor (no routing framework)
