---
kind: pattern
id: honest-all-clear
name: "Honest All-Clear"
scale: feel-finish
confidence: "★★"
status: active
serves: [trust-through-disclosure, cold-reader-comprehension]
context: [behavior-first-front-door]
completed_by: []
resolves_into:
  - "constraint:allclear-discloses-gaps"
---

# Honest All-Clear

## Problem

**A cold reader wants a trust verdict in one glance, but an all-clear that hides coverage gaps and accepted debt overstates trust.**

## Context

In the context of `behavior-first-front-door`, this pattern governs the all-clear posture's surface content — what a green verdict is obligated to disclose alongside itself.

## Forces

- **Desire:** Trust is earned by disclosed limits, not green screens (`trust-through-disclosure`).
- **Desire:** A cold reader gets a trust verdict in one glance (`cold-reader-comprehension`).
- **Constraint (soft):** Coverage gaps and accepted debt appear with the same prominence as verified content (`gaps-share-the-verdict`).

## Tension

The one-glance verdict wants maximal simplicity — "✓ all clear" and nothing else. But archwright's own history shows what unqualified green costs: checks that couldn't run read as checks that passed. Full disclosure inline threatens the glanceability the verdict exists for.

## Evidence

- Approved researched recommendation: "The all-clear view always discloses unchecked rules and accepted issues with the same prominence as the verified content — never hidden behind a fold" — user: "agree on both" [wf-all-clear#D002]
- Empirical grounding cited in the decision: this project's own vacuous-pass history — the Alloy compiler generated transition-less models for months and every check passed vacuously until a deliberately-violating spec exposed it; unchecked = coverage statement, not a pass [wf-all-clear#D002 rationale; Extension Protocol rule 4 precedent]
- Rejected alternative: folding gaps behind "details" — "an all-green verdict that hides blind spots overstates trust" [wf-all-clear#D002]
- Surface treatment, approved: skip/pending vocabulary renders as "couldn't be checked" / "check not built yet" — a coverage statement, never a pass [design-system tokens.vocabulary; status_roles skip note]
- Mechanism: the verdict line and the disclosure sections are separable — the glance reads the verdict; the disclosure sections sit unfolded below the diagram, so honesty costs scroll space, not glanceability [wf-all-clear wireframe]

```yaml
prior_art:
  - title: "Beer et al. — Efficient Detection of Vacuity in ACTL Formulas (CAV)"
    year: 1997
    relationship: confirms
    note: "'Vacuous satisfaction misleads users of model-checking into thinking a system is correct' — the founding statement; vacuity detection is default-on in industrial tools (Certora Prover sanity checks; SVA assert/cover pairing)."
  - title: "GitLab issue #29032 — skipped tests in pipeline status"
    year: 2019
    relationship: confirms
    note: "States the thesis verbatim: a skipped test shouldn't be a failure, but 'it also shouldn't be a success.'"
  - title: "Inozemtseva & Holmes — Coverage Is Not Strongly Correlated with Test Suite Effectiveness (ICSE 2014; MIP 2024)"
    year: 2014
    relationship: confirms
    note: "Even the coverage metric itself overstates assurance — green numbers need qualification."
  - title: "Hullman — Why Authors Don't Visualize Uncertainty (IEEE VIS)"
    year: 2019
    relationship: confirms
    note: "Omitting uncertainty implies unrealistic precision, and authors omit it for incentive reasons — motivating STRUCTURAL (mandatory) disclosure rather than optional."
  - title: "Hofman, Goldstein & Hullman — uncertainty display formats (CHI)"
    year: 2020
    relationship: extends
    note: "Caveat: disclosure FORMAT matters — naive uncertainty displays can themselves mislead. The report must state what a gap MEANS ('hardware simulator missing'), not just that it exists — matches skip-with-reason."
  - title: "'Watermelon effect' (green outside, red inside) — ITSM/PM reporting folklore"
    year: 2020
    relationship: confirms
    note: "Decades-old named failure mode of unqualified green status; every treatment prescribes structural disclosure."
```


## Therefore

**The verdict stays one-glance; the gaps stay on the surface.** In the all-clear posture, the report renders the plain verdict line, then — unfolded, below the behavior diagram — mandatory disclosure sections: WHAT ISN'T VERIFIED (unchecked/pending rules with reasons) and accepted known issues (with their acceptance date and cost). These sections appear with the same visual prominence as verified content and are never collapsed by default. Skip and pending states always phrase as coverage statements, never as passes.

## Consequences

- The report generator must treat skips, pendings, and baseline entries as first-class all-clear content — omitting them is a generation bug, not a styling choice.
- An all-clear with zero gaps renders the sections' absence honestly (nothing unchecked) rather than dropping the frame silently — the reader learns to expect the disclosure.
- Cost: the all-clear page is never as short as a bare green screen; teams with heavy accepted debt see it every run (which is the point).
- Does NOT cover: needs-attention posture content (`three-ask-types` + `behavior-first-front-door` own it); trend/run-over-run display (open — needs a data decision first, design-system Not Resolved).

## Verification

- Constraint check: all-clear rendering includes unverified/accepted-debt sections whenever skips, pendings, or baseline entries exist in the canonical document — `constraint:allclear-discloses-gaps`.

## Completion

This pattern is complete at its scale; it inherits its data from the canonical document (skips[], baseline, evidence ledger) and adds no new collection machinery.
