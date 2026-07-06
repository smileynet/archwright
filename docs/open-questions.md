# Open Questions

Roughly prioritized. Each is a research topic or decision point that will produce findings, ADRs, or both.

## 1. The Lift Contract ← next up

The explicit rule by which a child level translates its failure into the parent's vocabulary — e.g., how an architecture counterexample becomes a verb-level design statement. This is what determines whether the AI can *route* a signal or merely dump it.

**Research topic:** [R1 in research plan](../.memory/research-plan.md)

## 2. Spurious-vs-Real Adjudication Handshake

A model checker can prove a trace infeasible, but "real design flaw vs. modeling artifact" often needs the *Desire* to adjudicate. Design the AI-proposes / human-confirms handshake, especially for ★★ invariants.

## 3. Canonical Form of the Graph

Flat FSMs won't survive real games (state explosion). Commit to **statecharts** (Harel: hierarchy + orthogonal regions), so an entity's animation / AI / health machines run as concurrent regions. Highest-leverage architectural decision.

**Research topic:** [R2 in research plan](../.memory/research-plan.md)

## 4. Invariant Authoring Model

Inline assertions co-located with transitions (ergonomic, always in sync) vs. a separate temporal spec the graph is checked against (verifiable, two artifacts to align). Determines whether "AI-assisted" means *generate-then-check* or *check-while-generating*.

**Research topic:** [R3 in research plan](../.memory/research-plan.md)

## 5. Counterexample Classification

Partition violations into a few named failure kinds and pass *those* up ("your resolution leaks in three ways"), rather than surfacing every trace. The AI's summarization contract.

**Research topic:** [R4 in research plan](../.memory/research-plan.md)

## 6. Confidence Calibration

How do ★-ratings get assigned and revised as evidence accumulates? What promotes a — to a ★★, and what should demote one?

**Research topic:** [R5 in research plan](../.memory/research-plan.md)

## 7. Promotion Policy

When is the right response to a spurious counterexample to promote extended→discrete state, vs. to accept a wider abstraction? When should play-evidence promote a Desire into an explicit invariant?

## 8. Quiescence / Shipping Criteria

Formalize "stable under its own pass-up": which residual tensions are acceptable to ship as logged zero-star known issues.

## 9. Tooling Surface

Does the whole thing live in / export to a statechart tool (XState-style), a model checker (Alloy/TLA-style), or a bespoke editor? What's the minimal viable pipeline?
