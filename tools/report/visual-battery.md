# Visual Question Battery — archwright report (ticket 044)

Derived from the active D-anchors in `design/discovery/ui/` (2026-07-22). Method
authority: `skills/archwright-review/references/visual-conformance.md`. Method:
blind question-asking — answering sessions see screenshots + questions ONLY; these
decision texts never enter an answering prompt. Conservation: every question cites
one anchor; every active anchor appears below exactly once (question or
not-visually-checkable entry). Questions are one-decision-one-question, no embedded
expected answers, no presuppositions beyond what any screenshot of a web page grants.

## Questions

Postures: AC = all-clear capture set, NA = needs-attention capture set.

| Q | Region(s) | Posture | Question | Anchor |
|---|-----------|---------|----------|--------|
| Q1 | fullpage | AC+NA | What is the first thing this page communicates, and what kind of reader could understand it without domain training? List any specialist or technical vocabulary visible. | design-system#D002 |
| Q2 | fullpage | AC | What appears immediately after the page's title area, and what does it depict? | design-system#D006 |
| Q3 | section-how-archwright-works | AC | Describe what this graphic shows. What do the shapes represent and how are they related? | wf-all-clear#D004 |
| Q4 | verdict | AC | What overall state or outcome does this part of the page convey, and through which visual elements? | wf-overview#D001 |
| Q5 | section-what-isn-t-verified | AC | What is this section telling the reader? Is its content fully visible or does any of it require interaction to reveal? | wf-all-clear#D002 |
| Q6 | fullpage | NA | How many visually distinct groupings of items requiring reader action appear, and what distinguishes them from each other? | design-system#D003 |
| Q7 | section-decisions-2 | NA | For each item in this section, what elements accompany it (controls, text, options)? Is any option visually marked as preselected or favored? | wf-overview#D004 |
| Q8 | section-decisions-2 | NA | What actions can a reader take from this section, and how does the page describe each one? | wf-overview#D005 |
| Q9 | fullpage | NA | Does this page contain a diagram or graphic map of any kind? If so, describe any markings on its elements. | wf-all-clear#D005 |
| Q10 | fullpage | AC+NA | If a reader responds to something on this page, what does the page indicate happens to their responses? | wf-overview#D006, design-system#D005 |
| Q11 | fullpage | NA | What order do the major content areas appear in, top to bottom, and what is each about? | wf-overview#D003 |
| Q12 | section-what-isn-t-verified | NA | What is this section telling the reader? Is its content fully visible or does any of it require interaction to reveal? | wf-all-clear#D002 |

## Not visually checkable (recorded, never dropped)

| Anchor | Why not |
|--------|---------|
| design-system#D001 | Three-surface architecture (web/md/json) — a property of the bundle, not a screenshot; verified by the suite's bundle checks |
| design-system#D004 | Auto-approve config semantics — behavioral/config, invisible in a static capture (its `auto-approve: off` label is touched by Q4's verdict description) |
| design-system#D005 (static-first) | "Static self-contained HTML" is an artifact property; the response-recording *affordance* is covered by Q10 |
| wf-all-clear#D001 | SUPERSEDED by wf-all-clear#D004 — not active |
| wf-behavior-detail#D001/D002, wf-issue-detail#D001–D003, wf-overview#D002 | Drill/detail-view decisions — the current report renders no drill pages; recorded as coverage gap until those surfaces exist |
| wf-projections#D001 | Markdown/JSON projection shapes — checked by the suite, not visual |

## Known capture caveats (for the judging step)

- Sub-floor crops are PADDED with surrounding page context — a region crop may show
  neighboring content; region isolation is soft (verified at birth validation:
  verdict.png includes header + diagram context).
- The AC set is archwright's own dogfood bundle; the NA set is generated from
  `examples/partial` (project name "snackbox-partial"), whose design/ has models —
  diagram-presence questions are judgeable there.
