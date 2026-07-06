# Prior Art

Five distinct lineages, each contributing something specific to archwright.

## 1. Pattern Languages

Alexander → GoF → game design patterns: the force/resolution/network/confidence method itself.

**References:**
- Alexander, C., Ishikawa, S., & Silverstein, M. (1977). *A Pattern Language: Towns, Buildings, Construction.* Oxford University Press.
- Alexander, C. (1979). *The Timeless Way of Building.* (Companion volume on the generative method / "quality without a name.")
- Alexander, C. (1996). OOPSLA keynote — patterns, generativity, and what software took vs. left behind.
- Gamma, Helm, Johnson, Vlissides (1994). *Design Patterns: Elements of Reusable Object-Oriented Software.*
- Björk, S., & Holopainen, J. (2005). *Patterns in Game Design.*

## 2. Statecharts

Harel (1987) and modern tooling (XState / Stately Studio): hierarchy + orthogonal regions to beat state explosion; live current-state highlighting and gray-out of disabled guards; real-time simulation; directed-graph export.

**References:**
- Harel, D. (1987). *Statecharts: A Visual Formalism for Complex Systems.* Science of Computer Programming.
- XState / Stately Studio — statechart authoring, live visualization, simulation. https://stately.ai/ · https://github.com/statelyai/xstate

## 3. Model Finding / Lightweight Formal Methods

Alloy / Alcoa (Daniel Jackson): the counterexample as the primary artifact, rendered as a customizable graph; contrast-pair fault localization (FLACK); counterexample classification into behavior classes.

**References:**
- Jackson, D. *Alloy* / *Software Abstractions.* Alcoa overview: https://groups.csail.mit.edu/sdg/pubs/TR/alcoa-overview.pdf · CACM article: https://cacm.acm.org/research/alloy/
- Alloy 6 (with temporal operators): https://github.com/AlloyTools/org.alloytools.alloy
- Alloy* (HOLA) — higher-order solver, CEGIS for synthesis: https://github.com/aleksandarmilicevic/hola
- FLACK: Counterexample-Guided Fault Localization for Alloy Models (Zheng et al., 2021). Contrast-pair via PMAX-SAT, multi-granularity suspicion scoring. https://arxiv.org/pdf/2102.10152
- Counterexample Classification (Vick, Kang, Tripakis, 2021). Trace constraint partitioning, summary predicates, canonical counterexamples. https://arxiv.org/pdf/2108.00885

## 4. State-Machine Visualization & Invariant-First Design

FSM-visualization pedagogy (Morazán et al.) and SMGA: rendering an invariant predicate per state, live pass/fail after each transition; Gestalt principles for state pictures (keep visual identity stable; reserve color for status). Key insight: formulate the invariant *before* the transition function — the invariant IS the state's meaning.

**References:**
- Morazán et al. (2020) — Visual Designing and Debugging of DFAs; invariant predicates per state, live pass/fail, 9-step design recipe. https://arxiv.org/pdf/2008.09254
- "Better state pictures…" (SMGA; Gestalt principles for state pictures). https://link.springer.com/article/10.1007/s11042-021-10992-z
- Using State Machines for the Visualisation of Specifications via Refinement.

## 5. CEGAR & Refinement

Clarke et al. (CAV 2000 / JACM 2003) and compositional/learning variants: the spurious-vs-real refinement loop; assume-guarantee reasoning as modular refinement — our model for pass-up.

**References:**
- Clarke, Grumberg, Jha, Lu, Veith (2000/2003). *Counterexample-Guided Abstraction Refinement* (CAV 2000; JACM 2003).
- "25 Years of CEGAR" — compositional/modular (assume-guarantee), probabilistic, and learning/data-driven variants. https://link.springer.com/collections/jcchhbfcgh
- Explicit-Value Analysis Based on CEGAR and Interpolation (precision / feasibility check / refinement). https://arxiv.org/pdf/1212.6542

---

*(URLs captured from research on 2026-07-05; verify before citing formally.)*
