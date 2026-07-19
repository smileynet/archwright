---
kind: discovery
id: wf-behavior-detail
status: approved
area: ui
serves: []
---

# Wireframe: Behavior Detail

<!-- Drill level 2 of design-system#D006: opened by clicking a step or arrow on
     the how-it-works diagram. Answers "what happens here, exactly?" before any
     verification or rationale content. In-page anchor section (single file). -->

## Wireframe

```
+---------------------------------------------------------------------------+
|  ← back to the diagram                                                    |
|                                                                           |
|  ( Taking payment )                                          ✓ verified  |
|                                                                           |
|  WHAT HAPPENS HERE ------------------------------------------------------ |
|  The machine counts coins as they're inserted. From here the customer    |
|  either pays in full (→ Dispensing) or presses cancel (→ Cancelled,      |
|  money returned).                                                         |
|                                                                           |
|      arrives from:  Waiting (insert coins)                                |
|      leads to:      Dispensing (paid in full) · Cancelled (cancel)       |
|                                                                           |
|  THE RULES THAT APPLY HERE ---------------------------------------------- |
|  ✓  The balance never exceeds the item price plus change     [firm rule] |
|  ✓  Cancel always returns exactly what was inserted          [firm rule] |
|  ✓  Only the payment session may change the balance       [strong guide] |
|      ▸ how each rule is checked                                           |
|                                                                           |
|  WHAT THIS PROTECTS ----------------------------------------------------- |
|  "Customers pay before receiving snacks" · "Cancelling returns your      |
|  money"                                                                   |
|                                                                           |
|  ▸ HOW WE ARRIVED AT THIS ------------------------------------------------|
|    (folded) The design story: what pulled in different directions,       |
|    what was decided, what was rejected and why, when.                    |
+---------------------------------------------------------------------------+
```

## Design-System Elements Used

| Element | From design-system | Usage here |
|---------|-------------------|------------|
| Behavior-first drill order | design-system#D006 | what happens → rules → protects → (folded) how we got here |
| Plain-language surface | design-system#D002 | rules phrased as statements about the machine, not spec ids |
| Status chip | design-system (P4) | per-rule status, step-level rollup badge |
| Rationale fold-out | wf-overview#D005 precedent | "How we arrived at this" is the deepest, folded layer |

## Layout Rationale

Order mirrors design-system#D006's drill intent exactly: behavior first (prose + arrives-from/
leads-to in the diagram's vocabulary), then the rules guarding this step with
their live status, then the goals this step protects, and only then — folded by
default — the design story (tension, decision, rejected alternatives, date).
The "possibly" in the user's drill description is honored by the fold: rationale
is one click away but never in the reading path. Alternatives: rules-first
(rejected — verification before comprehension inverts design-system#D006); rationale inline
(rejected — "possibly wanting to know" means opt-in).

## Decisions

### D001 — Drill section order: happens → rules → protects → how-we-got-here (folded)
- **Category:** structure
- **Origin:** suggested
- **Decision:** Behavior detail renders in that fixed order; the design story is folded by default on every step.
- **Rationale:** "yes" (user approval of the presented drill ensemble, 2026-07-19; order derived from design-system#D006's drill description)
- **Alternatives:** Rules-first; rationale unfolded for steps with recent decisions.

### D002 — Rules render as statements about the machine
- **Category:** experience
- **Origin:** suggested
- **Decision:** Each rule appears as a plain declarative sentence about behavior ("Cancel always returns exactly what was inserted"), with its check mechanics behind a disclosure — spec ids and check methods never on the surface.
- **Rationale:** "yes" (user approval of the presented drill ensemble, 2026-07-19)
- **Alternatives:** Spec-id rows with tooltips; message-field verbatim (semi-technical).

## Not Resolved Here

- [ ] States: this view for an ARROW (transition) vs a STEP (state) — same template or a leaner one?; step with a failing rule (inherits issue-card content?)
- [ ] Edge cases: step with no rules yet, step serving no stated goal (orphan), long prose descriptions
- [ ] Interaction rules: "how each rule is checked" disclosure depth, keyboard flow between steps (next/prev along the machine?)
- [ ] Transitions: fold animation intent, deep-link anchors per step

## Hands To

- **Flow edges:** diagram element → this section; back → all-clear surface; rule row → issue detail when failing [cites D001]
- **State owned/shown:** model state prose + transitions in/out, specs joined to this model element with status, forces served (via provenance), pattern story behind the fold (tension, resolution, alternatives, date) [cites D001, D002]
- **Events emitted:** open rule check detail, unfold design story, navigate next/prev step [cites D001]
