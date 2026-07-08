# Research Synthesis

Synthesis of 5 research topics (R1–R5) investigated 2026-07-05.

## Key Findings

### The system has a clear architectural shape

The five topics aren't independent — they form a coherent pipeline:

1. **Statecharts are the target** (R2). No serious alternative. Flat FSMs fail at real scale; Alloy is a verification tool, not a design surface. XState's data model is the serialization format, but archwright needs a **spec layer above it** that adds invariants, provenance, and confidence metadata.

2. **Inline authoring, holistic checking** (R3). Write invariants co-located with the elements they constrain (guards on transitions, annotations on states, temporal properties at top level). Check them by analyzing the full state space. This is generate-then-check at the pattern level — each compilation ends with a check pass.

3. **Lift has three components** (R1): project (filter to interface alphabet), summarize (re-express in parent vocabulary), attribute (identify responsible force). The interface alphabet between scales is the set of forces/consequences that cross the boundary.

4. **Classification is the summarization contract** (R4). Three-level hierarchy: invariant → responsible element → structural class. Delta-debugging finds the responsible element. Count per class drives priority.

5. **Confidence calibrates the whole system** (R5). Start at —, promote with evidence, demote with counterexamples. ★★ requires proof or overwhelming empirical evidence. Track violation-rate-per-level to detect miscalibration.

### The compilation loop, concretely

```
Pattern (forces + resolution)
  ↓ hands-down
Statechart spec (states + transitions + guards + invariant annotations + provenance links)
  ↓ compile to
XState machine (executable/simulable)
  ↓ check
Model checker / test gen explores state space
  ↓ finds
Counterexample traces
  ↓ classify (delta-debug → responsible element)
K named failure classes
  ↓ lift (project → summarize → attribute)
Failure in parent vocabulary
  ↓ route (follow provenance to owning force)
Revised pattern or force
  ↓ re-compile
...quiescence
```

### What's new (not in the original working doc)

- **The "spec layer"** — archwright needs its own schema that's a superset of XState: statechart + invariant annotations + provenance metadata + confidence markers. This compiles down to bare XState for execution.
- **Interface alphabets** — each scale boundary has a defined set of forces/events that are visible across it. This is what makes lift mechanical rather than purely creative.
- **Delta-debugging for attribution** — systematically weakening elements to find the minimal responsible set. This makes "which guard is broken?" answerable mechanically.
- **Confidence as evidence accumulator** — not a fixed assignment but a tracked belief that updates with each check cycle. Start low, promote with evidence.

## Recommended Approach

**Build the spec layer first.** Everything else (checking, lift, classification) depends on having a machine-readable representation that's richer than raw XState.

The spec layer is: XState machine definition + per-element annotations:
- `_provenance: { from_pattern, from_force }` on every state/transition
- `_invariant: { type: state|transition|temporal, predicate, confidence }` on relevant elements
- `_forces: [{ id, polarity, scale }]` at the pattern level

This is Spike S1 (pattern schema as data) extended to the architecture side.

## Gaps Remaining

- **Lift automation** — we know the three components (project, summarize, attribute) but haven't defined how AI performs "summarize" mechanically. This is the creative/cognitive step. It may need to be AI-assisted with human confirmation for ★★ forces.
- **Temporal property notation** — full LTL/CTL is too academic for designers. Need a restricted subset. Proposal: safety properties only (□¬bad) for v1, add liveness (□◇good) later.
- **Model checker selection** — what tool checks the spec layer? Options: custom state-space explorer, adaptation of XState's `@xstate/test`, integration with an existing tool (SPIN, TLC, UPPAAL). This is a tooling decision deferred until the spec layer exists.
- **Hierarchy-invariant interaction** — does a parent's ★★ invariant implicitly constrain all children? (Probably yes, but the mechanism needs definition.)

## Recommended Spikes (updated priority)

1. **S1 — Pattern schema as data** — unchanged, still the right starting point
2. **S1b — Spec layer schema** (new) — define the XState-superset format with annotations. Validate by hand-compiling Intimacy Gradient into it.
3. **S4 — XState as compilation target** — now informed by the spec layer; compile the annotated schema down to bare XState and run it in Stately Studio
4. **S2 — Provenance roundtrip** — now concrete: use the spec layer's `_provenance` fields to walk back from a counterexample to the responsible pattern/force
5. **S3 — Counterexample rendering** — deferred until S4 produces a machine worth visualizing

---

## Verification Note (2026-07-07)

Findings R1–R5 were originally synthesized from training knowledge (2026-07-05) without fetching cited sources. On 2026-07-07, subagent research verified key claims against actual documentation:

- **R1 (Lift/CEGAR):** Verified via Clarke et al. paper. α is a surjective quotient map; spuriousness check requires *consistency* (re-abstraction landing within the original counterexample). The consistency requirement maps directly to archwright's level-terminating pass-up. See `.scratch/research/verified-cegar-lift.md`.
- **R3 (Invariant authoring):** Verified via TLA+ docs. Two distinct modes: state invariants (fast, per-state) vs temporal properties (require full state graph + fairness for liveness). Liveness is much slower. Apalache (symbolic/SMT) may be more practical than TLC for bounded temporal checking. See `.scratch/research/verified-tlaplus-invariants.md`.
- **R5 (Confidence):** Game failure terms (softlock, death spiral, degenerate strategy) verified as established terms with published definitions. No unified ontology exists — archwright fills this gap. See `.scratch/research/verified-game-failures.md`.

Original claims were directionally correct but lacked source verification. Verified files now provide the evidence.
