---
kind: pattern
id: behavior-first-front-door
name: "Behavior-First Front Door"
scale: loops-systems
confidence: "★"
status: active
serves: [cold-reader-comprehension, actionable-without-literacy]
context: [canonical-doc-projections, plain-surface-progressive-disclosure]
completed_by: [honest-all-clear]
resolves_into:
  - "contract:model-view-block"
  - "constraint:violations-pin-to-diagram"
---

# Behavior-First Front Door

## Problem

**The report exists to convey verification results, but leading with check status makes the surface unreadable to anyone who doesn't already know what's being checked.**

## Context

In the context of `canonical-doc-projections`, this pattern owns the information architecture of the primary surface — what a reader meets first and how drilling proceeds.

## Forces

- **Desire:** A cold reader understands how the app behaves from the report alone (`cold-reader-comprehension`).
- **Desire:** A developer locates what to act on without archwright literacy (`actionable-without-literacy`).
- **Constraint (soft):** When something fails, the affected behavior must be locatable from the front door in one step (`fault-location-one-step`).

## Tension

Verification-first surfaces (status tables, rule lists) answer "what failed?" but never "what does this app do?" — the cold reader has no map to place failures on. Comprehension-first surfaces risk burying the actionable signal the developer opened the report for. One surface must serve both entries.

## Evidence

- User decision, verbatim: "I want to understand what does the app do. The state machine / business logic are core to how the app functions. even a non-technical user should be able to look at the diagram and understand how things will behave. consider how, from there, a user might want to drill in to understand the details behind each, first understanding the behavior and it's details, and from there _possibly_ wanting to know how we arrived at those conclusions" [design-system#D006]
- Superseded direction: promise-grouped all-clear surface (wf-all-clear#D001) — replaced by the diagram front door; promise-grouping moved into the drill [wf-all-clear#D004]
- Rejected alternatives: check-status-first surface (remains the posture only when items need attention); diagram behind a tab ("it IS the front door") [design-system#D006; wf-all-clear Layout Rationale]
- Violations pin to the map: "the same diagram renders with the affected step/arrow marked ✗ — the behavior map is constant across report states; only the badges change"; rejected alternative — diagram only in all-clear ("map disappears exactly when orientation matters most") [wf-all-clear#D005]
- Drill order, approved: what-happens → rules-that-apply → what-this-protects → folded how-we-got-here; "the 'possibly' in the user's drill description is honored by the fold" [wf-behavior-detail#D001]
- Rendering mechanism: pre-generated inline SVG at report-build time — no client-side diagram library, preserving the zero-build single-file principle [wf-all-clear Layout Rationale; design-system P5]

```yaml
prior_art:
  - title: "Simulink Coverage / Design Verifier — results painted onto Stateflow model canvas"
    year: 2024
    relationship: confirms
    note: "Canonical precedent for verification status on diagram elements; but lives in an IDE, not a report front door."
  - title: "ModelWisdom — TLA+ state-graph visualization with violation highlighting (FM 2026, arXiv:2602.12058)"
    url: https://arxiv.org/abs/2602.12058
    year: 2026
    relationship: confirms
    note: "Diagram-as-primary-surface for verification results, click-through from transitions to broken invariants (research tool)."
  - title: "C4 model / Structurizr — diagram as documentation entry point"
    year: 2024
    relationship: confirms
    note: "Front-door half only: structural diagrams with zoom navigation, no verification overlay."
  - title: "XState/Stately statecharts-as-docs tradition"
    year: 2024
    relationship: confirms
    note: "Statechart as the primary shared artifact readable by non-developers; no check status."
  - title: "BDD living documentation (Adzic 2011; Smart/Serenity 2014; Martraire 2019)"
    year: 2019
    relationship: extends
    note: "Docs-verified-by-execution is mainstream but list/narrative-first — identifies the exact IA gap this pattern fills."
# Both halves separately confirmed; the full combination (static report OPENING on a behavior
# diagram with per-element check badges) was not found in any existing generator — novel synthesis.
```


## Therefore

**The app's state machine, in plain language, is the constant front door; verification attaches to it.** The primary surface leads with the behavior diagram — states and transitions with vocabulary-map labels a non-technical reader follows as a story. Per-element verification rollups render as badges on the diagram; in needs-attention states the same diagram appears with affected elements marked, so violations pin to the map instead of living in a separate list. Drill order from any element is fixed: (1) what happens here, (2) the rules that apply with live status, (3) what this protects, (4) folded design story. The diagram is pre-rendered SVG at generation time.

## Consequences

- Demands the `model_view` derived block (model elements ↔ plain labels ↔ spec-status join) — the diagram's data contract.
- Requires a spec→model-element join in the canonical pipeline (which rules guard which state/transition).
- Two unresolved structural cases the model phase must answer: projects with no behavior model (constraint/dependency rules only — what's the front door?) and multi-actor projects (several machines — composition view?) [wf-all-clear Not Resolved].
- Cost: report quality is now coupled to model quality — an unmodeled app has a degraded front door by construction.
- Does NOT cover: the disclosure sections below the diagram (`honest-all-clear`); ask presentation (`three-ask-types`).

## Verification

- Constraint check: needs-attention rendering reuses the same diagram with badges, never a separate list-only view — `constraint:violations-pin-to-diagram`.
- Contract check: `model_view` block carries plain labels and per-element rollups for every model element.

## Completion

This pattern is incomplete unless it also contains:
- The all-clear disclosure rules (`honest-all-clear`)
- Resolutions for the no-model and multi-actor front-door cases (model phase)
