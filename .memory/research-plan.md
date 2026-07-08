# Research & Spike Plan

## Prior Art Review: project-overseer

project-overseer is a Rust planning tool that detects drift between specs and implementation (like `terraform plan` for project management). Relevant structural patterns for archwright:

**What translates directly:**
- **Schema-defined type system** — Overseer's Schema (kinds, fields, states, transitions, link rules) is essentially a state graph with constraints. Archwright's Pattern schema (§7) needs the same rigorous structure.
- **Drift detection as invariant checking** — Overseer's `compute_drift()` over a `ProjectGraph` is exactly "check invariants over a state snapshot." The drift rules (coverage gap, orphan detection, lifecycle coherence) are analogous to archwright's invariant tiers.
- **Provenance via typed links** — Overseer's `Link` (source → target, typed, directed) implements traceability. Archwright's provenance links need the same: direction + type + metadata.
- **Lifecycle-aware severity** — ADR 0003's insight (drift rules graduate based on spec maturity) maps to archwright's confidence-gated escalation (★★ = more escalation, not less).
- **In-place export / bidirectional flow** — ADR 0004's lesson (patch what you manage, preserve what you don't) is the hands-down/pass-up principle applied to files.
- **Layout → Mapper → Store pipeline** — Overseer separates discovery (Layout) from parsing (Mapper) from persistence (Store). Archwright's compilation pipeline needs the same separation.

**What differs:**
- Overseer's items are flat (kind + fields + links). Archwright patterns are hierarchical (scale levels, sub-patterns, nested forces).
- Overseer drift is computed from a static snapshot. Archwright's pass-up is dynamic — it can trigger re-compilation, not just reporting.
- Overseer links are explicit and human-authored. Archwright provenance links are generated automatically during hands-down compilation.

---

## Proposed Research Topics

### R1. The Lift Contract (§9 item 1)

**Question:** What is the explicit rule for translating a child-level failure into the parent's vocabulary?

**Why it matters:** Without this, pass-up degenerates into "dump trace on human." The AI needs a mechanical rule for re-expression.

**Approach:** Study CEGAR's abstraction function (how a concrete counterexample is mapped to the abstract state space). Study compiler error recovery (how GCC/Clang surface template instantiation failures in the user's vocabulary). Produce a formal definition of the lift operator per archwright scale boundary.

**Deliverable:** ADR + additions to §3 and §4.

---

### R2. Statechart Commitment (§9 item 3)

**Question:** Should the architecture domain use flat FSMs, Harel statecharts, or something else?

**Why it matters:** State explosion kills flat FSMs for real systems. This is the highest-leverage architectural decision for tooling.

**Approach:** Research XState's data model (parallel regions, hierarchy, guards, actions, context). Research Alloy's relation-based state encoding. Prototype a non-trivial game system (e.g., a character with movement + combat + inventory as concurrent regions) in both flat FSM and statechart forms. Measure: expressiveness, checkability, compilation target clarity.

**Deliverable:** ADR + §4 update (canonical form definition).

---

### R3. Invariant Authoring Model (§9 item 4)

**Question:** Inline assertions co-located with transitions, or separate temporal spec?

**Why it matters:** Determines the AI's mode of operation — generate-then-check vs. check-while-generating.

**Approach:** Study TLA+ (separate spec, model checked), Alloy (separate spec, instance found), XState (inline guards, runtime-checked), Rust type-state pattern (compile-time-checked). Evaluate on: developer ergonomics, verifiability, AI-generability, provenance clarity.

**Deliverable:** ADR.

---

### R4. Counterexample Classification (§9 item 5)

**Question:** How do you partition violations into named failure kinds?

**Why it matters:** Pass-up needs summaries ("your resolution leaks in 3 ways"), not trace dumps.

**Approach:** Study Alloy's FLACK (fault localization), the ASE 2021 counterexample classification paper. Study how static analysis tools (Coverity, Infer) group and deduplicate findings. Prototype: given N violation traces against an invariant, cluster them by "which guard/transition is responsible."

**Deliverable:** Research findings + prototype algorithm sketch.

---

### R5. Confidence Calibration (§9 item 6)

**Question:** How do ★-ratings get assigned and revised as evidence accumulates?

**Why it matters:** Confidence gates the entire pass-up/AI-autonomy system. Miscalibrated confidence breaks routing.

**Approach:** Study Bayesian belief updating. Study Alexander's own criteria for rating patterns. Study how prediction markets / forecasting tools calibrate confidence. Propose: initial assignment heuristics, revision triggers, demotion criteria.

**Deliverable:** Additions to §3 and §4, possibly ADR if the mechanism is non-obvious.

---

## Proposed Spikes

### S1. Pattern Schema as Data (build)

**Goal:** Implement the §7 pattern schema as a machine-readable format (YAML or JSON Schema) and validate it against 3-5 worked examples.

**Tests against:**
- §8's worked mappings (Intimacy Gradient, Light on Two Sides)
- A fresh game mechanic (invent one that exercises all fields)

**Success criteria:** Schema validates examples. No field is unused. Forces, tensions, and consequences are all representable without prose escape hatches.

**Informs:** Whether the schema is expressive enough before building compilation tooling.

---

### S2. Provenance Roundtrip (build)

**Goal:** Prototype the hands-down → provenance link → pass-up → re-locate cycle. Simplest possible version: a 2-level tower (one Pattern with one sub-pattern, compiling to one state machine with 3-4 states).

**What to prove:**
- Hands-down generates provenance links automatically
- Given a counterexample (a trace violating an invariant), the system can follow provenance links upward
- The lift operator can re-express "transition X fired when guard Y should have blocked it" as "pattern Z's resolution doesn't cover case W"

**Success criteria:** One end-to-end cycle works on paper (or in a script). The provenance format supports the walk.

---

### S3. Counterexample Rendering (visualize)

**Goal:** Produce a single visualization of an invariant boundary using the "no-go region" idiom from §4.

**Tools:** SVG generation (hand-authored or d3/mermaid), or an Alloy model that produces an instance.

**Success criteria:** The visualization makes the invariant's *boundary* visible — you see where violation begins, not where safety holds.

**Informs:** Whether the visualization primitives in §4 are actually buildable, or if they need revision.

---

### S4. XState as Compilation Target (prototype)

**Goal:** Take one worked pattern (e.g., Intimacy Gradient) and hand-compile it into an XState machine definition. Verify: guards encode constraints, transitions encode desires, the machine is simulable.

**Success criteria:** The XState machine runs in the Stately Studio visualizer. Guards fire correctly. The connection between pattern fields and machine elements is traceable by a human reading both.

**Informs:** R2 (statechart commitment) with empirical evidence. Also tests whether XState's format is sufficient as the architecture-domain representation.

---

## Ordering

```
        R1 (lift contract)
       ╱                   ╲
R2 (statecharts) ─────── S4 (XState spike)
       │
R3 (invariant authoring)
       │
R4 (counterexample classification)
       │                   
R5 (confidence) ─────── S2 (provenance roundtrip)

S1 (pattern schema) ← independent, do first
S3 (counterexample viz) ← independent, do anytime
```

**Recommended start:** S1 (pattern schema as data) — it's self-contained, validates the core vocabulary, and unblocks everything else. Then R1 (lift contract) because it's the agreed next thread from §9.

---

## Research Status

All 5 topics investigated (2026-07-05). See [research synthesis](research-synthesis.md) for combined findings.

**Key conclusions:**
- Statecharts confirmed as target (R2) — define a "spec layer" above XState
- Inline authoring + holistic checking (R3) — write invariants on elements, check over full graph
- Lift = project + summarize + attribute (R1) — interface alphabets make it mechanical
- Classification = invariant → responsible element → structural class (R4) — delta-debugging for attribution
- Confidence = evidence accumulator starting at — (R5) — track violation rates for calibration

**Updated spike priority:** S1 → S1b (spec layer schema, new) → S4 → S2 → S3

---

## Future Tooling Considerations (added 2026-07-07, from verified research)

### SARIF Output Format
`archwright-check` should consider emitting SARIF-compatible JSON alongside its current output. SARIF is adopted by GitHub Code Scanning, VS Code, Semgrep, and CodeQL. Benefits: violation fingerprinting (stable cross-run identity), baselineState (new/unchanged/updated/absent), fix suggestion encoding (replacement arrays), and free tooling integration. Not urgent but worth adopting when the output format stabilizes.

### Baseline Mechanism (from dependency-cruiser)
dependency-cruiser's `--output-type baseline` generates a JSON snapshot of known violations; `--ignore-known` suppresses them in subsequent runs. This enables gradual adoption: snapshot existing state, then only flag NEW violations. Archwright should offer similar: `archwright-check --baseline` to snapshot, then normal runs only report regressions.

### Apalache for Bounded Temporal Checking
Apalache is a symbolic TLA+ model checker (SMT-based) that handles some infinite-state models within bounded steps (6-12 practical). May be a better fit than TLC or Alloy's nuXmv backend for behavior specs with liveness properties. Worth spiking when liveness checking becomes a priority.

### PBT as Complementary Checking
Property-based testing (fast-check for TS, Hypothesis for Python) can complement Alloy: specs compile to BOTH Alloy models (exhaustive bounded proof) AND PBT properties (fast implementation-level violation detection). PBT shrinking is structurally analogous to contrast-pair generation — shrunk counterexamples are machine-generated minimal violations.
