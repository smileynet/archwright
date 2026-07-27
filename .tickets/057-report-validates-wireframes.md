---
id: "057"
title: "Process: report implementation must validate against wireframes before closing"
status: open
blocked_by: []
priority: high
---

# Process: report validates against designed wireframes

## Problem

Ticket 041 (report implementation) was marked done with checked ACs, but the shipped output doesn't match the designed wireframes (wf-overview, wf-all-clear, wf-behavior-detail, wf-issue-detail, wf-projections). The gap:

- Statechart rendered as a bullet list, not a diagram
- No decisions/approvals sections
- No response bar or file export
- No drill-down from diagram to behavior detail
- No stability/history section

This happened because the ACs on 041 tested the **pipeline plumbing** (generate → derive → render, vocabulary completeness, reducer trace round-trip) without validating the **visual/interaction output** against the wireframes. The check tool measured structural correctness but not design conformance.

## What to change

1. **Add a visual-conformance gate to report tickets.** Each report ticket (052-056) must include an AC: "generated report for lacrosse-bosse matches the corresponding wireframe to structural accuracy" — open the HTML, compare to the ASCII wireframe, flag deviations.

2. **Lacrosse-bosse as the standing validation target.** It has a complete design/ directory (forces, model, specs) with a mix of passing and pending specs — realistic input for every report posture.

3. **Report fixture in archwright test suite.** Add lacrosse-bosse (or a synthetic equivalent) as a fixture that `run-fixture-tests.sh` generates a report from and validates structural expectations (sections present, diagram has edges, asks block non-empty when violations exist).

4. **Close the loop: ticket 041's unchecked AC.** The "all 6 constraint specs active and green" AC was left unchecked. Tickets 052-056 are the path to activating those specs — when they're done, go back and check that box.

## Acceptance criteria

- [ ] Tickets 052-056 each have a visual-conformance AC citing the specific wireframe
- [ ] Lacrosse-bosse design/ directory used as the test target for report generation
- [ ] A fixture test validates report structure (not just generation success)
- [ ] After 052-056 complete: lacrosse-bosse report visually matches wf-overview / wf-all-clear / wf-behavior-detail patterns
