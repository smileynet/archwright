# Findings

The load-bearing insights so far. These are the stable theoretical core — treat as shared vocabulary.

---

**0. Human desires are the primary forces — architecture serves people.**

Product-level desires (what coaches and players want to accomplish) initiate the design process. Architectural constraints exist to serve those desires. Desires span functional jobs (what it must do), emotional jobs (how it should feel), and social jobs (how it positions the user). Every architectural force should trace upward to a human desire via a `serves` link — orphaned constraints that serve no named desire are suspect. (Alexander: "most of the forces which occur in an environment are the ones which people experience inside themselves.")

---

**1. "Constraints" and "Desires" are Alexander's forces, split by polarity.**

Desires are attractive forces (what it wants to become); Constraints are bounding forces (what is given). Neither is a design. **Design exists only at the resolution** of a tension between them.

---

**2. The design lives in the transitions, not the states.**

A state is a mode; a transition is a *verb under conditions*. That's where forces land: a transition exists because of a Desire; its guard is a Constraint. Resolving a pattern mostly adds *guarded transitions*, not states.

---

**3. An invariant is the architectural form of a resolved force.**

When a pattern resolves "this Desire must survive that Constraint," the durable guarantee that it *stays* resolved across all states and inputs is an invariant on the graph. Alexander's two-star "true invariant of the problem" becomes, literally, an invariant assertion.

---

**4. An invariant is invisible when it holds — so you visualize its boundary.**

Every good visualization technique renders the *violation*: the counterexample, the near-miss, the trace that steps just outside the guarantee.

---

**5. The counterexample is a single artifact doing two jobs.**

It is simultaneously the best *visualization* of an invariant (its boundary made visible) and the *payload* of the pass-up flow (the correction, in flight). Build the counterexample renderer once; it serves both needs.

---

**6. Pass-up is the reciprocal of hands-down, on the same wiring.**

Hands-down carries commitments downward and concretizes; pass-up carries counterexamples upward and generalizes. They run along the *same provenance links* in opposite directions. This is CEGAR (counterexample-guided abstraction refinement) generalized to a design tower.

---

**7. Pass-up is level-terminating, not global.**

A signal rises only to the level that *owns the violated force*, being *re-expressed* in each level's vocabulary at every hop. The height a signal reaches measures how deep the mistake was.

---

**8. Confidence is the stopping rule — and it inverts intuition.**

High-confidence assertions refuse to bend, so they *force* signals upward; low-confidence resolutions absorb signals locally. Higher confidence ⇒ *more* escalation. This also gives the human/AI gate for free.

---

**9. Traceability is the routing table.**

Pass-up can only be targeted if every downstream artifact remembers what produced it. The recorded hands-down links *are* the up-routing table. Without provenance, "pass up" degenerates into "regenerate everything."

---

**10. Trace length matters more than scope for game models.**

The "small scope hypothesis" (most bugs found at scope 3) applies to structural/relational models. Game systems have temporal complexity — bugs require sequences of events to manifest. In testing: 6 steps catches 50% of bugs; 10 steps catches 100%. Scope (atom count) barely matters. Default to `steps = max(10, states × 3)`.

---

**11. The contrast pair is the natural pass-up payload.**

Not the raw counterexample (too noisy) and not just the classification (too abstract). The diff between the violation and the nearest valid alternative localizes the fault AND suggests the fix direction. FLACK's PMAX-SAT approach generates these mechanically.

---

**12. Bounded checking is necessary but not sufficient for ★★.**

Alloy finds counterexamples fast (94ms) but can only prove "no violation up to scope N." For genuine ★★ confidence (true invariant), unbounded proof is needed. Lean + AI provers (88.9% on benchmarks, 2025) provide the promotion path: compile spec to Lean theorem, attempt proof, kernel guarantees correctness if proof found.

---

**13. The methodology is self-extending — a coverage gap is a counterexample against archwright's own abstractions.**

When archwright encounters a stack, domain, or situation its material doesn't cover, that gap is not a descope candidate — it is CEGAR applied to the methodology itself. The failure artifact identifies the missing distinction (which adapter, which kind, what it unblocks); the extension is a new *instance* of an existing kind (a predicate, an overlay, a stack adapter), generated from the axis's existing template, conformance-tested at birth, and registered with guarantee-tiered status. Changing the *kinds themselves* is rarer and separately governed (ADR + human). This mirrors all three parent traditions: CEGAR refines abstractions minimally from the spurious counterexample; Alexander's pattern format is its own extension mechanism (new patterns are discovered in use, never invented top-down); reflective architectures bound the recursion — instances extend automatically, the meta-level answers to the human. (ADR 0008; protocol rules in `steering/archwright-conventions.md`.)
