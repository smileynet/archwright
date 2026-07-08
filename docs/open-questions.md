# Open Questions

Prioritized. Resolved questions marked; new questions added from validation spikes and research.

## Resolved

- ~~#3 Canonical form of the graph~~ → Statecharts. ADR 0002.
- ~~#4 Invariant authoring model~~ → Inline authoring, holistic checking. R3 synthesis.
- ~~#9 Tooling surface~~ → Agent + scripts on PATH. ADR 0001, 0004.

## Active

### 1. The Lift Contract ← partially addressed

The explicit rule by which a child level translates its failure into the parent's vocabulary. R1 research established the three components (project, summarize, attribute) and S2 proved the provenance roundtrip works. Remaining: formalize the "summarize" step (currently requires AI judgment — can it be made more mechanical?).

### 2. State Explosion Mitigation ← NEW (from V2, Penguin Clash)

Real games hit state explosion (~10^72 states for a simple multiplayer game). Archwright's Alloy checking works only on ABSTRACTED models. How do we:
- Guide the designer/agent in choosing the right abstraction level?
- Assure that the abstraction faithfully represents the real system?
- Detect when an abstraction is too coarse (spurious counterexamples)?

Prior art: Mawhorter 2021 (hand-authored tile abstraction for Super Metroid), CEGAR (automatic refinement), Rezin 2017 (manual model reduction).

### 3. Lean Migration Timing ← NEW (from Lean research)

When does CSLib mature enough to serve as archwright's verification backend? Triggers:
- CSLib has robust LTS formalization with temporal properties
- AI provers reliably handle archwright-sized properties (not just math olympiad)
- Veil or similar provides model-checking mode within Lean

Current status (mid-2026): CSLib has basic LTS + bisimulation. Temporal logics on roadmap. AI provers at 88.9% on math benchmarks but untested on software specs.

### 4. Spurious-vs-Real Adjudication

A model checker can prove a trace infeasible, but "real design flaw vs. modeling artifact" often needs the Desire to adjudicate. Design the AI-proposes / human-confirms handshake, especially for ★★ invariants.

### 5. Confidence Calibration

How do ★-ratings get assigned and revised as evidence accumulates? What promotes a — to a ★★, and what should demote one? R5 established the framework; needs empirical validation on real projects.

### 6. Counterexample Classification Predicates ← updated

The 12 candidate game failure predicates need formal expression. Three are validated (softlock via Mawhorter's `AG(EF(goal))`, death spiral, degenerate strategy as established terms). Remaining: formalize the others and test on real game models.

### 7. The Abstraction Gap ← NEW

Checking an abstracted model proves properties of the ABSTRACTION, not necessarily the real system. How does archwright communicate this limitation? Options:
- Clearly label confidence as "proven in model" vs "proven in implementation"
- Runtime monitoring bridges the gap (check invariants during actual execution)
- Property-based testing against real implementation complements model checking

### 8. Quiescence / Shipping Criteria

Formalize "stable under its own pass-up": which residual tensions are acceptable to ship as logged zero-star known issues.
