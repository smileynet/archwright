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

*(URLs captured from research on 2026-07-05; verified sources marked with dates.)*

## 6. Game Verification

Formal methods applied specifically to games — prior art for archwright's game domain overlay.

**References:**
- Mawhorter & Smith (FDG 2021). "Softlock Detection for Super Metroid with Computation Tree Logic." Formalizes softlock as `AG(EF(goal))`, builds tile-based Kripke structure, finds non-obvious softlocks via counterexample traces. https://dl.acm.org/doi/10.1145/3472538.3472542 *(verified 2026-07-07)*
- Rezin et al. (2017). "Model Checking in multiplayer games development." NuSMV on Penguin Clash (~10^72 states full, ~10^9 reduced, 2.5 hours). State explosion is real. https://ar5iv.labs.arxiv.org/html/1712.01207 *(verified 2026-07-07)*
- K-Machinations (Springer 2024). Testing and repairing Machinations game economy diagrams.
- Adams, E. (2010). "Preventing the Downward Spiral." Canonical definition of death spiral. Gamedeveloper.com.
- Salen & Zimmerman (2003). *Rules of Play.* Defines "degenerate strategy" formally.

## 7. Spec-Driven AI Development

Approaches to keeping AI-generated code aligned with architectural intent.

**References:**
- Grabowski, H. (2026). "The Spec Growth Engine: Spec-Anchored, Code-Coupled, Drift-Enforced Architecture for AI-Assisted Software Development." arXiv:2606.27045v1. Spec graph + context assembler + drift gate + growth rules. *(verified 2026-07-07)*
- Böckeler, B. (2025). "Exploring Gen AI: The Tools of Spec-Driven Development." martinfowler.com. Survey of Kiro, Spec Kit, Tessl — the maturity axis (spec-first → spec-anchored → spec-as-source).
- Murphy & Notkin (1995). "Software Reflexion Models." The ancestor of drift validation — comparing intended architecture to actual code structure.
- Parnas (1972). "On the Criteria to be Used in Decomposing Systems into Modules." Information hiding as the basis for both module design and agent context scoping.

## 8. Lean & AI-Assisted Verification

The emerging ecosystem that represents archwright's long-term verification backend.

**References:**
- Lean 4: https://lean-lang.org/ — programming language + proof assistant with minimal trusted kernel
- CSLib (2025-2026). The Lean Computer Science Library. Formalizes LTS, bisimulation, algorithms. https://arxiv.org/abs/2602.04846 *(verified 2026-07-07)*
- Veil (CAV 2025). Multi-modal protocol verification in Lean (model check + SMT + interactive proof). https://veil.dev *(verified 2026-07-07)*
- DeepSeek-Prover-V2 (2025). 88.9% on MiniF2F benchmark. AI-generated Lean proofs. https://arxiv.org/abs/2504.21801
- Kleppmann, M. (2025). "Prediction: AI will make formal verification go mainstream." https://martin.kleppmann.com/2025/12/08/ai-formal-verification.html *(verified 2026-07-05)*
- De Moura, L. (2026). "The Platform Is Ready." Lean FRO blog. https://leodemoura.github.io/blog/2026-4-20-signal-shot-the-platform-is-ready
