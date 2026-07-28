---
id: "075"
title: "Reference: needs-attention posture validation with planted violation"
status: open
blocked_by: ["061", "064", "063"]
priority: medium
---

# Reference: needs-attention posture validation

## Problem

The all-clear posture is the standing lacrosse-bosse report. The needs-attention posture (decisions + approvals visible, diagram with ✗ marks) has only been validated via ad-hoc scripts, never as a committed artifact.

## What to build

1. Create a fixture check-doc with a planted violation against lacrosse-bosse specs
2. Generate report in needs-attention posture
3. Verify against wf-overview wireframe: verdict line counts, DECISIONS/APPROVALS sections, contrast pair cards, diagram with affected state marked
4. Commit as a second reference (or document the generation command for reproducibility)

## Acceptance criteria

- [ ] Needs-attention report generated from planted violation
- [ ] Verdict line shows ask-type counts
- [ ] Approval card visible with contrast pair and action buttons
- [ ] Diagram shows affected state with ✗ badge (after ticket 063)
- [ ] Visual output compared against wf-overview wireframe structure
