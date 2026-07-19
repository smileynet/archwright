---
kind: discovery
id: ui-index
status: approved
area: ui
serves: []
---

# Discovery Index: UI (Archwright Report)

Session log + regenerable projection — entries in the artifacts are the truth.

## Sessions

| Date | Scope | Outcome |
|------|-------|---------|
| 2026-07-19 | Report-as-primary-surface design: design system + 5 wireframes + projections; graduation same day | All artifacts approved (design-system#D001 through design-system#D006 + per-screen ledgers below); model-seed compiled; repair of upstream check-tool clobber mid-session |

## Decisions (projection — regenerate from artifact ledgers)

| Entry | Artifact | Title | Category | Origin | Status |
|-------|----------|-------|----------|--------|--------|
| design-system#D001 | design-system.md | Three-surface output architecture (web primary, md, json) | structure | user | active |
| design-system#D002 | design-system.md | Plain-language, low-cognitive-load surface | experience | user | active |
| design-system#D003 | design-system.md | Approvals vs decisions ask-types | experience | user | active |
| design-system#D004 | design-system.md | Auto-approve via local mise, off by default | technical | user | active |
| design-system#D005 | design-system.md | Static HTML + agent-readable responses; live GUI backlogged | technical | user | active |
| design-system#D006 | design-system.md | Behavior-first information architecture | structure | user | active |
| wf-overview#D001 | wf-overview.md | Verdict-first, card-per-issue overview | structure | suggested | superseded by wf-overview#D003 |
| wf-overview#D002 | wf-overview.md | Contrast pair as the card body | structure | suggested | active |
| wf-overview#D003 | wf-overview.md | Two-zone overview: decisions above approvals | structure | user | active |
| wf-overview#D004 | wf-overview.md | Decision cards: options, no recommendation when ambiguous | experience | suggested | superseded by wf-overview#D005 |
| wf-overview#D005 | wf-overview.md | Options + freeform + marked recommendation + rationale fold-out | experience | user | active |
| wf-overview#D006 | wf-overview.md | Response accumulation bar | structure | suggested | active |
| wf-issue-detail#D001 | wf-issue-detail.md | Goal/design/check chain phrasing | structure | suggested | active |
| wf-issue-detail#D002 | wf-issue-detail.md | Escape hatch: reroute approval → decision | structure | suggested | superseded by wf-overview#D003 |
| wf-issue-detail#D003 | wf-issue-detail.md | Intent-labeled actions: Approve Fix / Review-Amend Rule | experience | user | active |
| wf-all-clear#D001 | wf-all-clear.md | Group all-clear by promise | structure | suggested | superseded by wf-all-clear#D004 |
| wf-all-clear#D002 | wf-all-clear.md | "What isn't verified" mandatory disclosure | experience | suggested | active |
| wf-all-clear#D003 | wf-all-clear.md | Third ask-type: optional suggestions | experience | suggested | active |
| wf-all-clear#D004 | wf-all-clear.md | Behavior diagram is the all-clear front door | structure | user | active |
| wf-all-clear#D005 | wf-all-clear.md | Violations pin to the diagram | structure | suggested | active |
| wf-behavior-detail#D001 | wf-behavior-detail.md | Drill order: happens → rules → protects → folded story | structure | suggested | active |
| wf-behavior-detail#D002 | wf-behavior-detail.md | Rules render as statements about the machine | experience | suggested | active |
| wf-projections#D001 | wf-projections.md | Markdown mirrors drill; JSON = canonical + derived blocks | structure | suggested | active |

Origin tally: 10 user, 13 suggested (3 superseded by user reversals) — creative-session tripwire never exceeded 2 consecutive unconfirmed.
