# Glossary

Concepts and terminology for the force-resolution design language and its compilation target.

## Design Domain

- **Force** — any pressure acting on a design decision. Split by polarity into Desires and Constraints.
- **Desire** — an *attractive* force: the intended feel, player fantasy, quality, aliveness. Directionless about limits. Desire alone is a mood board.
- **Constraint** — a *bounding* force: platform, budget, ruleset, rating/compliance, capacity, fictional physics. Tagged **hard** (inviolable) or **soft** (negotiable). Constraint alone is a spec sheet or a prison.
- **Tension** — the explicit statement of a conflict between forces (Desire vs Constraint, or Desire vs Desire under a Constraint). This is the actual *problem*.
- **Pattern** — a recurring, reusable *resolution* of a named tension that hands specific commitments down to architecture. Defined by the [pattern schema](pattern-schema.md).
- **Resolution** — the generative move that balances the forces. A rule for making form, never a fixed artifact.
- **Consequence** — a *new* force introduced by a resolution. Consequences propagate the design forward (downstream) and can also travel upward as emergent obligations.
- **Confidence** — Alexander's asterisks (★★ / ★ / —): stated belief that a resolution names a true invariant vs. one workable arrangement. Drives AI autonomy and the pass-up stopping rule.
- **Evidence** — the grounding for belief in a pattern: playtests, prior art, empirical data. The running artifact is the ultimate evidence source.

## Scales (large → small)

- **Premise** — genre, fantasy, whole experience. (Alexander's region/town.)
- **Loops & Systems** — core loop, meta loop, session shape, economies. (Buildings/neighborhoods.)
- **Verbs & Interactions** — moment-to-moment actions and feedback. (Rooms.)
- **Feel & Finish** — juice, affordances, microcopy, player expression. (Construction detail & ornament.)

## Architecture Domain

- **State graph** — the central anchor. States (modes) + transitions (guarded verbs). The one representation that is simultaneously human-designable, AI-generable, and formally checkable.
- **Discrete state** — the finite set of modes (small, enumerable → checkable).
- **Extended state (context)** — the typed data the guards read (where the real numbers live).
- **Guard** — the membrane between discrete and extended state; a transition fires only when mode + a predicate over context both permit it. Guards are Constraints compiled onto edges.
- **Event alphabet** — the finite set of events the graph accepts. The *real* API surface, more than the endpoint list.
- **Ingress / egress** — events that request transitions (ingress) vs. the derived read-model others observe (egress/projection). Egress is a view, never a second source of truth.
- **Invariant** — a property that must hold regardless of path. Three tiers:
  - **State invariant** — always true while in a state.
  - **Transition invariant** — pre/postconditions on an edge.
  - **Global / temporal invariant** — property over the whole graph across time (e.g., reachability/safety). What a model checker verifies.

## The Compilation & Its Two Directions

- **Hands-down** — the downward compile: forces → pattern → sub-patterns → state / data / interface / invariant. *Concretizes.*
- **Pass-up** — the upward flow: downstream findings → revised design. *Generalizes.* Level-terminating, confidence-gated, follows provenance links.
- **Provenance link** — the recorded "this came from that" trace laid down during hands-down; walked backward by pass-up. The routing table.
- **Counterexample** — a trace that violates an invariant; a case where a Constraint defeats a Desire (or two Desires collide) that a resolution missed. Falsification.
- **Spurious vs. real (the CEGAR fork)** — a *real* counterexample means the resolution is genuinely wrong → pass up. A *spurious* one is an artifact of over-abstraction → refine the model locally, no ascent. This fork is the routing/triage rule.
- **Lift (re-abstraction)** — translating a signal into the parent level's vocabulary at each up-hop (trace → "broken verb" → "hollow loop" → "false premise"). The hardest cognitive work in the system; the AI's job at each boundary.
- **Promotion** — turning implicit into explicit: an extended-state variable into a discrete mode (to resolve a spurious counterexample), or an unwritten Desire into an explicit invariant (in response to play evidence).
- **Assume-guarantee / compositional CEGAR** — a sub-pattern completes a parent under an assumed contract (the parent's guarantee); pass-up is *local* along that contract, not global. This is Alexander's up-link made dynamic.
- **Quiescence** — the practical "done" state: the tower is stable under its own pass-up; only low-confidence, low-severity signals still circulate, each resolved or consciously accepted as a zero-star known tension. Convergence, not perfection.

## Visualization Primitives

- **Live predicate-on-state** — per-state invariant badges (green/red), evaluated live as the graph is walked; disabled transitions grayed out (guards made visible). *Only shows the walked path.*
- **Counterexample-as-artifact** — the solver finds the smallest violating state/trace and renders it; the invariant becomes visible at its edge without hand-drawing.
- **No-go region** — a global/temporal invariant drawn as a shaded forbidden region over the graph, with the shortest counterexample trace stepping into it. Confidence-weighted boundary (solid wall = ★★, dashed = —).
- **Contrast pair / near-miss** — the counterexample shown beside the nearest satisfying instance; the diff localizes the responsible force/guard.
- **Counterexample classification** — partition many violations into a few named *kinds* of failure instead of dumping traces. The AI's summarization contract.
