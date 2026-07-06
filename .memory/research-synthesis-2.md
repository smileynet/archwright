# Research Synthesis (Round 2)

Synthesis of R6–R11, investigated 2026-07-05. Extends the first synthesis (R1–R5).

## Key Findings

### The system's strategic shape crystallizes

1. **Dual-target compilation** (R10) — one spec, two backends. Alloy for formal checking (counterexamples, FLACK, classification). XState for simulation and execution. The archwright spec layer is the single source.

2. **Contrast pairs replace raw counterexamples** (R8) — pass-up carries the *diff between violation and nearest valid state*, not just the violation. This makes attribution mechanical (the diff IS the cause) and gives a fix direction for free.

3. **Bounded checking is the default; unbounded is optional** (R7) — the small scope hypothesis holds for structural game design bugs. ★★ confidence can require deeper bounded checks or empirical evidence. Don't block on unbounded proof.

4. **Synthesis is the end-state; compilation is the on-ramp** (R6) — start with compilation (human writes resolution, system translates). The same CEGIS loop enables synthesis later (system proposes resolution from forces). Confidence gates which mode: ★★ = human must author, — = system can propose.

5. **Live validation changes the workflow fundamentally** (R11) — invariant-first design with immediate bounded checking on every change. The design process IS the verification. Provenance links built contemporaneously, not retroactively.

6. **A standard library of ~12 failure predicates** (R9) — softlock, death spiral, degenerate strategy, etc. These are the summary predicate vocabulary for counterexample classification in the game/app domain.

### Updated Pipeline

```
Human intent (forces, optional resolution)
  ↓ design (invariant-first, live validation)
Archwright spec (single source, YAML)
  ↓                           ↓
Alloy 6 model                XState machine
  ↓                           ↓
Bounded check               Simulate / playtest
  ↓                           ↓
Contrast pairs              Runtime monitoring
  ↓                           ↓
Classify (domain predicates)  Empirical evidence
  ↓                           ↓
  └────── Lift (diff summary) ──────┘
                ↓
  Revised pattern / force
                ↓
  Re-compile → quiescence
```

### New insights beyond the original 9 findings

- **Finding 10: The contrast pair is the natural pass-up payload.** Not the counterexample (too noisy) and not just the classification (too abstract). The diff between broken and working localizes the problem AND suggests the fix direction.

- **Finding 11: Invariant-first design builds evidence during design.** A statechart constructed with live invariant validation has stronger implicit confidence than one checked post-hoc. The design process itself is evidence.

- **Finding 12: Synthesis and compilation are the same loop with different initial conditions.** If the human provides a resolution → compilation (refine the translation). If the human provides only forces → synthesis (refine the candidate). CEGIS handles both; the starting point differs.

## Gaps Remaining

- **Alloy-to-archwright translation fidelity** — when Alloy finds a counterexample in relational terms, how cleanly does it map back to archwright's force/pattern vocabulary? Needs a spike.
- **Incremental Alloy performance** — can bounded checking be fast enough for live feedback (<200ms per change)? Unknown without profiling.
- **Summary predicate formalization** — the 12 candidate predicates are described in prose. Need formal expression over the statechart/Alloy vocabulary to be checkable.
- **Hierarchy encoding in Alloy** — statechart parallel regions and nested states don't have a standard Alloy encoding. Need a spike to validate expressiveness.

## Recommended Next Spikes

1. **S5 — Alloy compilation target** — take the Intimacy Gradient spec and hand-compile to Alloy 6. Run the analyzer. Does it find the EXTERNAL_UNLOCK counterexample from S2?
2. **S6 — Contrast pair generation** — given an Alloy counterexample, use PMAX-SAT (or Alloy's own machinery) to find the nearest satisfying instance. Verify the diff localizes the responsible element.
3. **S7 — Formal summary predicates** — express 3 of the 12 game failure predicates (softlock, death spiral, degenerate strategy) in Alloy's logic. Check them against a small game model.
4. **S8 — Incremental checking latency** — measure how fast Alloy can re-check a model after a single state/transition addition. Determines if live validation is feasible.
