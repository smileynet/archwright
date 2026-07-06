# Findings

The load-bearing insights so far. These are the stable theoretical core — treat as shared vocabulary.

---

**1. "Constraints" and "Desires" are Alexander's forces, split by polarity.**

Desires are attractive forces (what it wants to become); Constraints are bounding forces (what is given). Neither is a design. **Design exists only at the resolution** of a tension between them.

---

**2. The design lives in the transitions, not the states.**

A state is a mode; a transition is a *verb under conditions*. That's where forces land: a transition exists because of a Desire; its guard is a Constraint. Compiling a pattern mostly adds *guarded transitions*, not states.

---

**3. An invariant is the compiled form of a resolved force.**

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
