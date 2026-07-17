---
id: 010
title: "Pattern quality gate: 70% evidence-share threshold measures the wrong thing"
status: open
blocked_by: []
created: 2026-07-17
---

# Pattern quality gate: 70% evidence-share threshold measures the wrong thing

Field-driven (AwsArchVR phase-1 review 2026-07-17): all 13 ExposeAR patterns
measure 25–39% evidence share against the "Evidence section: ≥70% of the pattern
body" gate — a 13/13 systematic miss — while the same review rated citation
quality "excellent throughout" (fresh, sourced, specific). When every instance
produced by the pipeline's own formalize skill fails a gate, the gate is
miscalibrated, not the corpus.

## What to build

- Recalibrate the gate: either lower the share threshold to something the
  formalize skill's own template can meet, or (better) replace share-of-body with
  a substance check (every Therefore clause traces to a cited source; no
  "it's standard practice" citations; evidence freshness bound).
- Update: pattern quality gates doc, archwright-formalize skill, deployed
  steering (archwright-conventions.md Pattern Quality Gates section).

## Acceptance criteria

- [ ] The 13 ExposeAR patterns pass the recalibrated gate unmodified (they were
      judged good) OR the gate's failure messages identify real substance gaps
- [ ] A deliberately evidence-free pattern still FAILs the gate
- [ ] Formalize skill template and gate agree (template output passes its own gate)
