# A Force-Resolution Design Language That Compiles to Architecture

*Working doc · v0.1 · living document — extend freely*

Companion figures (see `figures/`):
- **Fig. 1 — [`compilation.svg`](figures/compilation.svg)**: the vertical compile from forces to architecture.
- **Fig. 2 — [`invariant_boundary.svg`](figures/invariant_boundary.svg)**: invariant-as-no-go-region + the pass-up hop.
- **Fig. 3 — [`pass_up_tower.svg`](figures/pass_up_tower.svg)**: pass-up as a level-terminating climb.

---

## 1. Goal

Build an **AI-assisted design system** for games and applications in which human design intent is expressed in a small, principled *design language*, and that intent **compiles down into architecture** (a state graph and its supporting structure) with the compilation being **traceable and reversible** — so that what is learned downstream can be routed back up to revise the design.

Two halves, one pipeline:

1. **Design domain** — a vocabulary for thinking at the level of intent: what the thing wants to be, what bounds it, and how those are reconciled.
2. **Architecture domain** — the executable target: a state machine / graph as the central anchor, with data, interfaces, and invariants as supporting pillars.

The thesis: these are **not two systems but one compilation**, running in both directions. Downward (*hands-down*) turns intent into structure; upward (*pass-up*) turns downstream findings back into design revisions.

**Design principle we're committing to:** keep *forces* first-class. The reusable IP is not a catalogue of patterns; it is the method of naming and resolving tensions. The moment patterns become fixed templates, the system dies.

---

## 2. Origin & lineage

The ancestor is Christopher Alexander, Sara Ishikawa & Murray Silverstein, *A Pattern Language: Towns, Buildings, Construction* (1977) — 253 patterns ordered by scale, region → town → building → room → construction detail.

Four mechanics from that work are the parts we're stealing:

- **Patterns resolve forces.** A pattern is *context → problem → solution*, where the "problem" is a field of competing forces in tension and the "solution" is the configuration that balances them. No real tension ⇒ not a pattern, just a feature.
- **Generative, not templates.** A pattern lets you solve the same problem endlessly without ever solving it the same way twice. It is a rule for *making* form, not a blueprint.
- **A network, not a list.** Patterns link *up* (larger patterns they help complete) and *down* (smaller patterns that complete them). A design is a chosen path through the network; wholeness comes from the linking.
- **A confidence claim.** Alexander rated each pattern with two / one / zero asterisks — his stated confidence that it names a *true invariant* of the problem versus merely one workable arrangement.

**Lineage note / cautionary tale.** This book spawned software design patterns (Gang of Four, 1994; Ward Cunningham's original wiki was a pattern repository) and a games branch (Björk & Holopainen, *Patterns in Game Design*, 2005). Alexander's 1996 OOPSLA keynote essentially warned the software field that it had taken his catalogue and dropped the soul — the forces, and the question of whether the generated thing is actually good to inhabit. Our system is a deliberate attempt to keep the soul: forces stay first-class and confidence-weighted, all the way down to code.

---

## 3. Findings (the load-bearing insights so far)

1. **"Constraints" and "Desires" are Alexander's forces, split by polarity.** Desires are attractive forces (what it wants to become); Constraints are bounding forces (what is given). Neither is a design. **Design exists only at the resolution** of a tension between them.

2. **The design lives in the transitions, not the states.** A state is a mode; a transition is a *verb under conditions*. That's where forces land: a transition exists because of a Desire; its guard is a Constraint. Compiling a pattern mostly adds *guarded transitions*, not states.

3. **An invariant is the compiled form of a resolved force.** When a pattern resolves "this Desire must survive that Constraint," the durable guarantee that it *stays* resolved across all states and inputs is an invariant on the graph. Alexander's two-star "true invariant of the problem" becomes, literally, an invariant assertion.

4. **An invariant is invisible when it holds — so you visualize its boundary.** Every good visualization technique renders the *violation*: the counterexample, the near-miss, the trace that steps just outside the guarantee.

5. **The counterexample is a single artifact doing two jobs.** It is simultaneously the best *visualization* of an invariant (its boundary made visible) and the *payload* of the pass-up flow (the correction, in flight). Build the counterexample renderer once; it serves both needs.

6. **Pass-up is the reciprocal of hands-down, on the same wiring.** Hands-down carries commitments downward and concretizes; pass-up carries counterexamples upward and generalizes. They run along the *same provenance links* in opposite directions. This is CEGAR (counterexample-guided abstraction refinement) generalized to a design tower.

7. **Pass-up is level-terminating, not global.** A signal rises only to the level that *owns the violated force*, being *re-expressed* in each level's vocabulary at every hop. The height a signal reaches measures how deep the mistake was.

8. **Confidence is the stopping rule — and it inverts intuition.** High-confidence assertions refuse to bend, so they *force* signals upward; low-confidence resolutions absorb signals locally. Higher confidence ⇒ *more* escalation. This also gives the human/AI gate for free.

9. **Traceability is the routing table.** Pass-up can only be targeted if every downstream artifact remembers what produced it. The recorded hands-down links *are* the up-routing table. Without provenance, "pass up" degenerates into "regenerate everything."

---

## 4. Concepts & terminology (glossary)

### Design domain

- **Force** — any pressure acting on a design decision. Split by polarity into Desires and Constraints.
- **Desire** — an *attractive* force: the intended feel, player fantasy, quality, aliveness. Directionless about limits. Desire alone is a mood board.
- **Constraint** — a *bounding* force: platform, budget, ruleset, rating/compliance, capacity, fictional physics. Tagged **hard** (inviolable) or **soft** (negotiable). Constraint alone is a spec sheet or a prison.
- **Tension** — the explicit statement of a conflict between forces (Desire vs Constraint, or Desire vs Desire under a Constraint). This is the actual *problem*.
- **Pattern** — a recurring, reusable *resolution* of a named tension that hands specific commitments down to architecture. Defined by the schema in §7.
- **Resolution** — the generative move that balances the forces. A rule for making form, never a fixed artifact.
- **Consequence** — a *new* force introduced by a resolution. Consequences propagate the design forward (downstream) and can also travel upward as emergent obligations.
- **Confidence** — Alexander's asterisks (★★ / ★ / —): stated belief that a resolution names a true invariant vs. one workable arrangement. Drives AI autonomy and the pass-up stopping rule.
- **Evidence** — the grounding for belief in a pattern: playtests, prior art, empirical data. The running artifact is the ultimate evidence source.

### Scales (large → small)

- **Premise** — genre, fantasy, whole experience. (Alexander's region/town.)
- **Loops & Systems** — core loop, meta loop, session shape, economies. (Buildings/neighborhoods.)
- **Verbs & Interactions** — moment-to-moment actions and feedback. (Rooms.)
- **Feel & Finish** — juice, affordances, microcopy, player expression. (Construction detail & ornament.)

### Architecture domain

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

### The compilation & its two directions

- **Hands-down** — the downward compile: forces → pattern → sub-patterns → state / data / interface / invariant. *Concretizes.*
- **Pass-up** — the upward flow: downstream findings → revised design. *Generalizes.* Level-terminating, confidence-gated, follows provenance links.
- **Provenance link** — the recorded "this came from that" trace laid down during hands-down; walked backward by pass-up. The routing table.
- **Counterexample** — a trace that violates an invariant; a case where a Constraint defeats a Desire (or two Desires collide) that a resolution missed. Falsification.
- **Spurious vs. real (the CEGAR fork)** — a *real* counterexample means the resolution is genuinely wrong → pass up. A *spurious* one is an artifact of over-abstraction → refine the model locally, no ascent. This fork is the routing/triage rule.
- **Lift (re-abstraction)** — translating a signal into the parent level's vocabulary at each up-hop (trace → "broken verb" → "hollow loop" → "false premise"). The hardest cognitive work in the system; the AI's job at each boundary.
- **Promotion** — turning implicit into explicit: an extended-state variable into a discrete mode (to resolve a spurious counterexample), or an unwritten Desire into an explicit invariant (in response to play evidence).
- **Assume-guarantee / compositional CEGAR** — a sub-pattern completes a parent under an assumed contract (the parent's guarantee); pass-up is *local* along that contract, not global. This is Alexander's up-link made dynamic.
- **Quiescence** — the practical "done" state: the tower is stable under its own pass-up; only low-confidence, low-severity signals still circulate, each resolved or consciously accepted as a zero-star known tension. Convergence, not perfection.

### Visualization primitives (from prior art)

- **Live predicate-on-state** — per-state invariant badges (green/red), evaluated live as the graph is walked; disabled transitions grayed out (guards made visible). *Only shows the walked path.*
- **Counterexample-as-artifact** — the solver finds the smallest violating state/trace and renders it; the invariant becomes visible at its edge without hand-drawing.
- **No-go region** — a global/temporal invariant drawn as a shaded forbidden region over the graph, with the shortest counterexample trace stepping into it. Confidence-weighted boundary (solid wall = ★★, dashed = —).
- **Contrast pair / near-miss** — the counterexample shown beside the nearest satisfying instance; the diff localizes the responsible force/guard.
- **Counterexample classification** — partition many violations into a few named *kinds* of failure instead of dumping traces. The AI's summarization contract.

---

## 5. The model in one line

**Desires + Constraints → resolved Pattern → hands-down (with provenance) → State · Data · Interface · Invariant → check → counterexample → pass-up (lift, confidence-gated, level-terminating) → revised Pattern/Force → recompile → … → quiescence.**

---

## 6. Prior art (traditions we're drawing from)

Four distinct lineages, each contributing something specific:

1. **Pattern languages** (Alexander → GoF → game design patterns): the force/resolution/network/confidence method itself.
2. **Statecharts** (Harel, 1987) and their modern tooling (XState / Stately Studio): hierarchy + orthogonal regions to beat state explosion; live current-state highlighting and gray-out of disabled guards; real-time simulation; directed-graph export.
3. **Model finding / lightweight formal methods** (Alloy / Alcoa, Daniel Jackson): the counterexample as the primary artifact, rendered as a customizable graph; contrast-pair fault localization (FLACK); counterexample classification into behavior classes.
4. **State-machine graphical animation (SMGA)** and FSM-visualization pedagogy (Morazán et al.): rendering an invariant predicate per state, live pass/fail after each transition; Gestalt principles for state pictures (keep visual identity stable; reserve color for status).
5. **CEGAR** (Clarke et al., CAV 2000 / JACM 2003) and its compositional/learning variants: the spurious-vs-real refinement loop; assume-guarantee reasoning as modular refinement — our model for pass-up.

---

## 7. Appendix A — The Pattern schema (proposed)

The fields *are* the vocabulary for thinking at the design level, and they double as the compile record:

| Field | Purpose |
|---|---|
| `id` / `name` | the token to reason and talk in |
| `scale` | Premise / Loops&Systems / Verbs&Interactions / Feel&Finish |
| `context` / `above` | where it applies; larger patterns it completes (assume-guarantee up-link) |
| `desires` | attractive forces (typed, optionally weighted) |
| `constraints` | bounding forces, each tagged hard / soft |
| `tension` | the explicit conflict — the problem |
| `resolution` | the generative rule that balances them |
| `consequences` | new forces spawned (drive the next compile step; can pass up) |
| `hands_down` | sub-patterns **and** the architectural commitments implied — **the provenance link** |
| `confidence` | ★★ / ★ / — ; gates AI autonomy and pass-up escalation |
| `evidence` | why we believe it: playtests, prior art, empirical grounding |

---

## 8. Appendix B — Worked mappings (Alexander → games/apps)

- **#127 Intimacy Gradient** (public→private sequence) → onboarding / progressive disclosure. Desire: players feel oriented before exposed to depth. Constraint (hard): attention budget. Tension: depth wants to be shown, comprehension wants it hidden. Resolution: stage exposure shallow→deep. Hands-down: a progression state machine + gated data unlocks.
- **#159 Light on Two Sides** → critical state legible from two independent feedback channels.
- **#106 Positive Outdoor Space** → negative space / whitespace as intentional, not leftover.
- **#112 Entrance Transition** → the first-run threshold.
- **#253 Things From Your Life** → player customization / expression.

---

## 9. Areas to explore (open questions, roughly prioritized)

1. **The lift contract (next up).** The explicit rule by which a child level translates its failure into the parent's vocabulary — e.g., how an architecture counterexample becomes a verb-level design statement. This is what determines whether the AI can *route* a signal or merely dump it.
2. **Spurious-vs-real adjudication handshake.** A model checker can prove a trace infeasible, but "real design flaw vs. modeling artifact" often needs the *Desire* to adjudicate. Design the AI-proposes / human-confirms handshake, especially for ★★ invariants.
3. **Canonical form of the graph.** Flat FSMs won't survive real games (state explosion). Commit to **statecharts** (Harel: hierarchy + orthogonal regions), so an entity's animation / AI / health machines run as concurrent regions. Highest-leverage architectural decision.
4. **Invariant authoring model.** Inline assertions co-located with transitions (ergonomic, always in sync) vs. a separate temporal spec the graph is checked against (verifiable, two artifacts to align). Determines whether "AI-assisted" means *generate-then-check* or *check-while-generating*.
5. **Counterexample classification as the generator's summarization contract.** Partition violations into a few named failure kinds and pass *those* up ("your resolution leaks in three ways"), rather than surfacing every trace.
6. **Confidence calibration.** How do ★-ratings get assigned and revised as evidence accumulates? What promotes a — to a ★★, and what should demote one?
7. **Promotion policy.** When is the right response to a spurious counterexample to promote extended→discrete state, vs. to accept a wider abstraction? When should play-evidence promote a Desire into an explicit invariant?
8. **Quiescence / shipping criteria.** Formalize "stable under its own pass-up": which residual tensions are acceptable to ship as logged zero-star known issues.
9. **Tooling surface.** Does the whole thing live in / export to a statechart tool (XState-style), a model checker (Alloy/TLA-style), or a bespoke editor? What's the minimal viable pipeline?

---

## 10. References

**Pattern languages**
- Alexander, C., Ishikawa, S., & Silverstein, M. (1977). *A Pattern Language: Towns, Buildings, Construction.* Oxford University Press.
- Alexander, C. (1979). *The Timeless Way of Building.* (Companion volume on the generative method / "quality without a name.")
- Alexander, C. (1996). OOPSLA keynote — patterns, generativity, and what software took vs. left behind.
- Gamma, Helm, Johnson, Vlissides (1994). *Design Patterns: Elements of Reusable Object-Oriented Software.*
- Björk, S., & Holopainen, J. (2005). *Patterns in Game Design.*

**Statecharts & tooling**
- Harel, D. (1987). *Statecharts: A Visual Formalism for Complex Systems.* Science of Computer Programming.
- XState / Stately Studio — statechart authoring, live visualization, simulation. https://stately.ai/ · https://github.com/statelyai/xstate

**Model finding / lightweight formal methods**
- Jackson, D. *Alloy* / *Software Abstractions.* Alcoa overview: https://groups.csail.mit.edu/sdg/pubs/TR/alcoa-overview.pdf · CACM article: https://cacm.acm.org/research/alloy/
- FLACK: Counterexample-Guided Fault Localization for Alloy Models (ASE 2021). https://arxiv.org/pdf/2102.10152
- Counterexample Classification. https://arxiv.org/pdf/2108.00885

**State-machine visualization (invariants)**
- Morazán et al. — Visual Designing and Debugging of DFAs; invariant predicates per state, live pass/fail. https://arxiv.org/pdf/2008.09254
- "Better state pictures…" (SMGA; Gestalt principles for state pictures). https://link.springer.com/article/10.1007/s11042-021-10992-z
- Using State Machines for the Visualisation of Specifications via Refinement.

**CEGAR & refinement**
- Clarke, Grumberg, Jha, Lu, Veith (2000/2003). *Counterexample-Guided Abstraction Refinement* (CAV 2000; JACM 2003).
- "25 Years of CEGAR" — compositional/modular (assume-guarantee), probabilistic, and learning/data-driven variants. https://link.springer.com/collections/jcchhbfcgh
- Explicit-Value Analysis Based on CEGAR and Interpolation (precision / feasibility check / refinement). https://arxiv.org/pdf/1212.6542

*(URLs captured from research on 2026-07-05; verify before citing formally.)*

---

## 11. How to use this doc

- **Findings (§3)** and **Concepts (§4)** are the stable core — treat them as the shared vocabulary.
- **Areas to explore (§9)** is the backlog; item 1 (the lift contract) is the agreed next thread.
- Keep the **forces-first principle** (§1) as the tie-breaker whenever a decision threatens to turn a pattern into a template.
