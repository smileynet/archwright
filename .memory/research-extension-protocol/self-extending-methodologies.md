# Self-Extending Methodologies — Prior Art

Research question: What prior art exists for methodologies/systems that extend their own method when encountering coverage gaps?

Date: 2026-07-17

## Summary

Three mature traditions handle the meta-level (a system improving its own abstractions) in structurally different ways. **CEGAR** treats a coverage gap (a spurious counterexample) as a machine-checkable signal that the abstraction vocabulary is too coarse, and refines the abstraction locally and automatically until it either proves the property or finds a real bug. **Alexander's pattern languages** hold that a language cannot be invented top-down — new patterns are *discovered in use* or adapted by trial and error, and the language's format is itself the mechanism for its own extension (piecemeal growth, validated against "degree of life"). **Self-adaptive systems research** makes the meta-level architectural: reflective layers (FORMS, three-layer models, MAPE-K) contain explicit models of the system itself, and the highest layer (goal management / meta-adaptation) changes the adaptation logic, not just the system. The common structure across all three: a *failure at the object level* (spurious counterexample, recurring unresolved problem, unmet goal) is routed upward as evidence that the *method's own abstractions* are inadequate, triggering a bounded, evidence-driven extension of the method — never an open-ended rewrite.

## Details

### 1. CEGAR — Counterexample-Guided Abstraction Refinement

**The loop** (Clarke, Grumberg, Jha, Lu, Veith, 2000): start with a deliberately coarse abstraction of the system; model-check it; if a counterexample is found, check whether it is *concrete* (replays on the real system) or *spurious* (an artifact of the abstraction). Spurious counterexamples drive refinement: the abstraction is strengthened just enough to exclude that spurious behavior (adding predicates, splitting abstract states, adding constraints or state variables). Iterate until either the abstraction proves correctness or a real counterexample emerges.

**How it handles the meta-level:**
- The coverage gap has a *formal signature*: a counterexample that cannot be concretized. The method does not rely on human judgment to detect that its abstraction is inadequate — spuriousness is decidable (in practice, via simulation of the abstract path on the concrete model).
- Refinement is **localized and minimal**: the abstraction evolves through "localized strengthening (e.g., adding predicates, split regions, constraints, or new state variables)" (Emergent Mind survey) — it excludes the spurious counterexample while still over-approximating the original system, keeping the loop sound.
- The refinement is **guided by the failure artifact itself**: the spurious counterexample tells you *which* distinction the abstraction is missing. This is the key move — the failure carries the information needed to extend the method.
- Termination is not guaranteed in general (infinite-state systems), which is why practical variants combine predicate abstraction with fixpoint approximation (CEGAAR) or interpolation.
- The pattern generalizes far beyond model checking: MDPs, POMDPs, neural network verification, multi-agent path finding — the meta-loop (abstract → check → diagnose gap → refine abstraction) is domain-independent.

**Relevance to Archwright:** CEGAR is the strongest formal precedent for "the check failed *because the spec vocabulary is too coarse*, so extend the vocabulary" — i.e., distinguishing a genuine violation (route to pass-up / re-resolution) from a *spec-coverage gap* (route to spec refinement). The spurious/concrete distinction maps to Archwright's need to decide whether a failed check means the code is wrong or the spec is missing a distinction.

### 2. Alexander — Generative Pattern Languages

**The claim:** A pattern language is not a fixed catalogue but a generative system. Alexander's 253 patterns (*A Pattern Language*, 1977) were explicitly presented as one language among many possible; *The Timeless Way of Building* (1979) describes the method for *making your own* language. Patterns were mined from evolved (not designed) building typologies — socio-geometric relations discovered by observing what worked.

**How it handles the meta-level:**
- **"A pattern language cannot be invented — it must either be discovered in actual use, or adapted to a new situation by methods of trial and error"** (Salingaros, *The Legacy of Christopher Alexander*). Extension of the language is empirical, not speculative: a new pattern earns its place by being observed to resolve a recurring tension in built reality.
- The **pattern format is itself a meta-pattern**: context → forces → resolution → consequences. Anyone encountering an unresolved recurring problem has, in the format, the instructions for writing the new pattern. The language ships with its own extension mechanism.
- **Validation is by degree of life / organized complexity**, not by authority: Salingaros formalizes this as raw complexity × number of connections, built up "piecemeal in an iterative cycle" — add only the complexity needed at each step, organize it into coherence with existing structure, remove the unnecessary, repeat. This is a human/aesthetic analogue of CEGAR's minimal refinement.
- **Coverage gaps are local first**: patterns are linked into a network; a gap shows up as a place where the existing patterns' resolutions do not compose (forces left unresolved at a scale). The new pattern is inserted at that scale and linked to its neighbors — the language grows at its frontier, not by global redesign.
- Alexander's later work (*The Nature of Order*) shifted from patterns to *generative sequences* and the 15 fundamental properties — an acknowledgment that the pattern catalogue alone under-specified the generative process. Even the meta-level got revised when it showed coverage gaps.

**Relevance to Archwright:** the forces-first principle and "resolves into, not compiles to" descend directly from this. The prior art here says: when the pipeline encounters a tension no existing pattern resolves, the correct move is to *write a new pattern from the observed tension* (trial and error, in-use discovery) — and the pattern schema must be rich enough to serve as its own extension instructions.

### 3. Reflective Architectures / Self-Adaptive Systems

**The taxonomy:** The SEAMS/SASO research community has ~20 years of structure for systems that modify themselves. Key reference models:

- **Computational reflection as foundation** (Andersson, de Lemos, Malek, Weyns, 2009, "Reflecting on self-adaptive software systems"): "computational reflection forms the foundation of a self-adaptive system" — the system maintains a causally-connected self-representation; changing the representation changes the system.
- **FORMS** (FOrmal Reference Model for Self-adaptation; Weyns, Malek, Andersson, 2012): a small set of formally specified primitives — reflection perspective (base-level subsystem vs. reflective subsystem containing *reflection models* of the base level), MAPE-K working perspective, and distribution perspective. The reflective subsystem monitors and adapts the base level; crucially, reflective subsystems can be *stacked* — a meta-reflective layer adapts the adaptation logic itself.
- **Three-layer architecture** (Kramer & Magee, adapted in Weyns' *Engineering Self-Adaptive Software Systems — An Organized Tour*, 2019): (1) component control — the running system; (2) change management — reactive plans that reconfigure the system; (3) **goal management** — generates *new* plans when change management has no plan covering the current situation. Layer 3 is exactly the "extend the method when coverage gaps appear" layer: a gap in the plan repertoire triggers plan synthesis from goals.
- **MAPE-K** (Monitor, Analyze, Plan, Execute over shared Knowledge): the canonical feedback loop; the Knowledge component holds the models that the meta-level revises.
- **Four Types of Self-adaptive Systems metamodel** (2017) classifies by *what* is adapted: parameters, components/structure, the environment model, or the adaptation logic itself — the last type being the fully meta-level case.
- **ActivFORMS** (Weyns & Iftikhar): extends the loop to *evolution* — formal models used at runtime are themselves updated when goals change, spanning design → deployment → runtime adaptation → evolution.

**How it handles the meta-level:**
- The meta-level is a **first-class architectural element**, not an emergency escape hatch: reflection models are explicit artifacts, and adapting them follows the same MAPE discipline as adapting the base system.
- **Layering bounds the recursion**: three layers (not arbitrary towers) is the community's practical answer to "who adapts the adapter" — goal management is the top; beyond it sits the human. This matches Archwright's pass-up-is-level-terminating principle.
- **Uncertainty is the trigger vocabulary**: the field frames coverage gaps as *uncertainties* (environment changes, resource dynamics, goal variation) that the system "collects additional data about... during operation" to resolve — extension is data-driven, deferred to runtime, and scoped to the uncertainty that triggered it.
- Guarantees degrade up the tower: layer 1 can be verified statically; layer 2 with runtime formal techniques (ActivFORMS uses verified runtime models); layer 3 (plan/goal synthesis) typically requires human ratification — a direct precedent for confidence-gated autonomy (★★/★/—).

**Relevance to Archwright:** FORMS' stacked reflection and the three-layer model give an architectural template for where "extend the method" lives: it is a distinct top layer, invoked only when the lower layers' repertoires fail, producing new artifacts of the same checked kinds (new plans/models — analogously, new predicates, new patterns, new spec kinds), with human ratification at the top.

### Cross-cutting synthesis

| | Gap signal | Extension unit | Minimality discipline | Who ratifies |
|---|---|---|---|---|
| CEGAR | Spurious counterexample (machine-decidable) | Predicate / state split | Exclude only the spurious trace; stay sound | Fully automatic |
| Alexander | Recurring unresolved tension in use | New pattern (in standard format) | Piecemeal growth; add only needed complexity | Community / in-use validation |
| Self-adaptive | Unhandled uncertainty; no plan covers situation | New plan / model / adaptation rule | Layered scope; adapt lowest layer that suffices | Escalates by layer; human at top |

Shared invariants worth adopting:
1. **The failure artifact carries the refinement information** (CEGAR's strongest lesson) — a good coverage-gap report should identify *which missing distinction* caused it.
2. **Extensions are instances of existing kinds** — new predicate, new pattern, new plan — never a change to the meta-format itself except under separate, rarer governance (Alexander revising the pattern format into generative sequences took decades and a new book).
3. **Recursion is bounded and level-terminating** — three layers, then human.
4. **Minimal refinement** — extend just enough to cover the observed gap; over-general extensions are the failure mode in all three traditions (predicate explosion in CEGAR, template-ossification in patterns, adaptation-logic sprawl in SAS).

## Sources

- [L4:established] Wikipedia — Counterexample-guided abstraction refinement — https://en.wikipedia.org/wiki/Counterexample-guided_abstraction_refinement (spurious-counterexample check; Clarke et al. 2000 lineage)
- [L4:reported] Emergent Mind — Counterexample-Guided Abstraction Refinement — https://www.emergentmind.com/topics/counterexample-guided-abstraction-refinement-cegar (survey framing: iterative framework vs. state-space explosion)
- [L4:reported] Emergent Mind — Iterative Abstraction Refinement Techniques — https://api.emergentmind.com/topics/iterative-abstraction-refinement-techniques (localized strengthening: predicates, split regions, constraints, new state variables)
- [L4:established] arXiv 0807.1173 — CEGAR Framework for Markov Decision Processes — https://arxiv.org/abs/0807.1173 (coarse-to-refined loop generalized to probabilistic systems)
- [L4:established] arXiv 1701.06209 — CEGAR for POMDPs — https://ar5iv.labs.arxiv.org/html/1701.06209
- [L4:established] arXiv 1712.01734 — Partial Predicate Abstraction and CEGAAR — https://ar5iv.labs.arxiv.org/html/1712.01734 (refinement + fixpoint approximation for infinite-state)
- [L4:established] arXiv 1212.6542 — Explicit-Value Analysis Based on CEGAR and Interpolation — https://ar5iv.labs.arxiv.org/html/1212.6542 (counterexample = error path definition)
- [L4:established] ACM TOSEM — Abstraction and Refinement: Scalable and Exact Verification of Neural Networks — https://dl.acm.org/doi/10.1145/3644387 (CEGAR transplanted to DNN verification; sound+complete refinement)
- [L4:established, read] Salingaros — The Legacy of Christopher Alexander: Form Language, Pattern Language, and Complexity — https://patterns.architexturez.net/doc/az-cf-193123 ("a pattern language cannot be invented — discovered in actual use or adapted by trial and error"; piecemeal organized-complexity growth)
- [L4:established] Wikipedia — Pattern language — https://en.wikipedia.org/wiki/Pattern_language (definition; generative claim)
- [L4:established] Wikipedia — A Pattern Language — https://en.wikipedia.org/wiki/A_Pattern_Language (253 patterns as one language; format)
- [L5:reported] Doug Lea — Christopher Alexander: An Introduction for Object-Oriented Designers — http://www.patternlanguage.com/bios/douglea.htm (patterns in broader review of Alexander's design writings)
- [L5:reported] Dawes & Ostwald — Christopher Alexander's A Pattern Language: analysing, mapping and classifying the critical response — https://link.springer.com/doi/10.1186/s40410-017-0073-1
- [L4:established] Weyns, Malek, Andersson — FORMS: Unifying reference model for formal specification of distributed self-adaptive systems — https://dl.acm.org/doi/10.1145/2168260.2168268 (reflection perspective; formally specified primitives; stackable reflective subsystems)
- [L4:established] Andersson, de Lemos, Malek, Weyns — Reflecting on self-adaptive software systems — https://www.researchgate.net/publication/220265998_Reflecting_on_self-adaptive_software_systems ("computational reflection forms the foundation of a self-adaptive system")
- [L4:established] Weyns — Engineering Self-Adaptive Software Systems: An Organized Tour — https://www.researchgate.net/publication/330119817_Engineering_Self-Adaptive_Software_Systems_-_An_Organized_Tour (three-layer architecture; FORMS reflection primitives; uncertainty framing)
- [L4:established] Weyns & Iftikhar — ActivFORMS: A Formally-Founded Model-Based Approach to Engineer Self-Adaptive Systems — https://arxiv.org/abs/1908.11179 (runtime formal models; evolution stage = updating the models themselves)
- [L5:reported] The Four Types of Self-adaptive Systems: A Metamodel — https://www.researchgate.net/publication/318132984_The_Four_Types_of_Self-adaptive_Systems_A_Metamodel (taxonomy by what is adapted, incl. the adaptation logic itself)
- [L4:established] Weyns et al. — On Patterns for Decentralized Control in Self-Adaptive Systems — https://link.springer.com/10.1007/978-3-642-35813-5_4 (MAPE loop as canonical control structure)
- [L4:reported] arXiv 2511.06352 — State of the Art on Self-adaptive Systems — https://arxiv.org/html/2511.06352v1

## Open Questions

1. **Gap-vs-violation discrimination:** CEGAR decides spuriousness mechanically by concretizing the counterexample. What is Archwright's analogue — how does a failed check get classified as "code wrong" vs. "spec missing a distinction" vs. "force unresolved"? Is there a concretization step (e.g., replay the trace against the human's stated forces)?
2. **Minimality of extension:** CEGAR refines to exclude exactly one spurious trace. What is the minimal unit of methodology extension in Archwright — one predicate in a domain overlay? one new spec? one new pattern? Is there a discipline preventing over-general extensions?
3. **Meta-format governance:** all three traditions treat changing the *format itself* (pattern schema, spec kinds, reference model) as a rarer, separately-governed event. Should Archwright formalize a two-tier extension policy (instances auto-extendable within a span; kinds require ADR + human)?
4. **Termination:** CEGAR can fail to terminate on infinite-state systems. Does the archwright re-resolution loop (violation → pass-up → re-resolve → re-check) have a quiescence guarantee, or does it need a divergence detector (same tension re-opened N times → escalate)?
5. **Where do discovered extensions live?** Alexander's answer is "in the shared language" (patterns are largely universal); SAS's answer is "in this system's knowledge base." When a project-level pipeline run discovers a new predicate or pattern, when does it get promoted from the target project's `design/` into `tools/domains/` or the global skill set?
6. **Empirical validation of new patterns:** Alexander requires in-use discovery / trial-and-error before a pattern is admitted. What is the software analogue — does a candidate pattern need N observed instances (across projects? across modules?) before formalization, or does one well-evidenced tension suffice?
