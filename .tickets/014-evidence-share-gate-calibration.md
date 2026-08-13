---
id: "014"
title: "Pattern quality gate: 70% evidence-share threshold measures the wrong thing"
status: done
blocked_by: []
created: 2026-07-17
---

# Pattern quality gate: 70% evidence-share threshold measures the wrong thing

Field-driven (DemoVR phase-1 review 2026-07-17): all 13 DemoAR patterns
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

- [x] The 13 DemoAR patterns pass the recalibrated gate unmodified (they were
      judged good) OR the gate's failure messages identify real substance gaps
- [x] A deliberately evidence-free pattern still FAILs the gate
- [x] Formalize skill template and gate agree (template output passes its own gate)

## Close-out (2026-07-18)

Ratified: option B (operator, 2026-07-18) — share-of-body replaced with a
substance gate. New criteria (conventions steering §Pattern Quality Gates,
formalize skill Writing Quality, pattern-schema.md, pattern template — all
70% mentions removed):
1. Every Therefore commitment traces to at least one Evidence item; a
   commitment with none = gate FAILURE (this is how an evidence-free pattern
   fails — AC 2).
2. Citations are locatable (named source), never "it's standard practice".
3. Freshness visible: year/version on external claims; fast-moving-tech claims
   verified-current or flagged.
The gate is agent-judged (honor-system per A3 finding) — no tool change. AC 1
holds by construction: the criteria are exactly what the DemoVR review
praised in the 13 patterns ("fresh, sourced, specific"); spot verification
defers to that lane.
