# Proposed: Next Research, Spikes, and Spec Updates

## New Research Topics

### R15. Abstraction Strategies for Game Models

**Question:** How do you abstract a game system to a tractably checkable model while preserving the properties you care about?

**Why it matters:** V2 and Penguin Clash showed state explosion is real. Archwright's checking only works on abstracted models. The agent needs a methodology for choosing abstractions.

**Approach:** Study Mawhorter's tile-based abstraction (hand-authored), CEGAR's automatic refinement, predicate abstraction, and counter-abstraction techniques. Produce: guidelines for when to abstract (always for behavior specs), what to keep (state identity, transitions, guards), what to drop (continuous values, exact timing, rendering state).

### R16. Runtime Monitoring as Conformance Bridge

**Question:** Can runtime invariant checking during actual gameplay bridge the gap between "proven in model" and "holds in implementation"?

**Why it matters:** The abstraction gap (open question #7). Model checking proves the model correct; runtime monitoring proves the implementation correct for observed executions.

**Approach:** Study runtime verification tools (MonitorLib, DejaVu, Montre). Evaluate: can archwright behavior spec invariants compile to runtime assertions that fire during gameplay? What's the overhead? Prior art: XState inspection protocol already provides state/transition events.

### R17. Lean Theorem Compilation Feasibility

**Question:** Can archwright behavior specs compile to Lean theorems that AI provers can handle?

**Why it matters:** This is the ★★ promotion path. If AI provers can't handle our specs, Lean remains theoretical.

**Approach:** Take the ball-state-lifecycle spec. Hand-translate to a Lean theorem using CSLib's LTS definition. Run DeepSeek-Prover-V2 (or similar) on it. Can it prove `at-most-one-holder`? How long does it take? What does it struggle with?

---

## New Spikes

### S9. Abstraction Quality Test

**Goal:** Take a REAL lacrosse-bosse subsystem (practice execution — 28 decisions, multiple components) and attempt to model it in Alloy at a useful abstraction level. Measure: how many states? How long to check? What properties survive the abstraction?

**Pass:** Model has <1000 states, checks in <10s, catches a known design constraint (e.g., "executor never resolves").
**Fail:** Model exceeds practical scope OR loses the property we care about during abstraction.

### S10. Runtime Monitoring Prototype

**Goal:** Take the ball-state-lifecycle spec's `at-most-one-holder` invariant and implement it as a runtime assertion in GDScript. Run during a simulated practice execution. Verify it fires when violated.

**Pass:** Assertion catches a deliberately introduced double-possession bug during runtime.
**Fail:** Can't express the invariant as a runtime check, or the overhead is unacceptable.

### S11. Lean Theorem from Behavior Spec

**Goal:** Hand-compile ball-state-lifecycle to a Lean 4 theorem using CSLib's LTS structure. Attempt proof (manually or via AI prover if accessible).

**Pass:** The theorem is expressible in Lean, type-checks, and either proves or produces a meaningful error about what's missing.
**Fail:** CSLib's LTS doesn't have enough infrastructure to express our spec, or the translation is so complex that it's impractical.

### S12. Mawhorter Replication

**Goal:** Replicate Mawhorter's softlock detection approach on a small game level. Use CTL `AG(EF(goal))` in Alloy 6 temporal mode. Compare: does our approach (Alloy) match their approach (pyModelChecking) in capability?

**Pass:** Alloy finds the same softlocks that Mawhorter's approach would find on an equivalent level.
**Fail:** Alloy's temporal bounded checking misses softlocks that require longer traces than our step budget allows (further validating V2's finding about trace length).

---

## Spec/Schema Updates

### 1. Add `abstraction_notes` field to behavior specs

Behavior specs should document what was EXCLUDED from the model:

```yaml
kind: behavior
id: ball-state-lifecycle
abstraction_notes:
  included: [possession states, transfer protocol, validation logic]
  excluded: [physics, proximity checks, animation timing, network latency]
  justification: "Properties we check (single holder, no double possession) are independent of physics/proximity. Those affect WHEN transfers happen, not WHETHER the invariant holds."
  scope_limit: "Checked at scope 4, 8 steps. Properties requiring longer sequences (economy accumulation) would need larger bounds."
```

### 2. Add confidence qualifiers to check results

Check results should report what level of assurance they provide:

```yaml
status: pass
assurance: bounded  # bounded | proven | conformance | empirical
scope: "4 atoms, 8 steps"
note: "No counterexample within bounds. Does not constitute proof for unbounded traces."
```

vs.

```yaml
status: pass
assurance: proven
backend: lean
note: "Theorem proved by kernel. Holds for all reachable states."
```

### 3. Add `prior_art` field to patterns

Patterns should acknowledge when the resolution has published precedent:

```yaml
---
kind: pattern
id: ball-possession
prior_art:
  - "Request/validate is standard in sports games (FIFA, NBA2K, Madden)"
  - "AG(EF(goal)) formulation for liveness: Mawhorter & Smith FDG 2021"
---
```

### 4. Update spec-schema to include `check.steps` default

The spec schema for behavior specs should recommend a step bound:

```yaml
# In behavior spec or as tool default:
check:
  backend: alloy
  scope: 4
  steps: 10  # default: max(10, states × 3)
  note: "Minimum steps for temporal properties with accumulation"
```

---

## Priority Order

| Item | Type | Effort | Impact | Priority |
|------|------|--------|--------|----------|
| Schema: `abstraction_notes` | Spec update | 15 min | High (honesty about limitations) | 1 |
| Schema: `assurance` in results | Spec update | 15 min | High (clarity on what "pass" means) | 2 |
| S9: Abstraction quality test | Spike | 2 hr | High (validates real-world scalability) | 3 |
| S12: Mawhorter replication | Spike | 1 hr | Medium (validates prior art integration) | 4 |
| R15: Abstraction strategies | Research | 2 hr | High (methodology for the agent) | 5 |
| S10: Runtime monitoring | Spike | 1 hr | Medium (bridges abstraction gap) | 6 |
| R16: Runtime monitoring research | Research | 1 hr | Medium (supports S10) | 7 |
| S11: Lean theorem | Spike | 2 hr | Medium (tests future path) | 8 |
| R17: Lean feasibility | Research | 1 hr | Low (future, not blocking) | 9 |
| Schema: `prior_art` field | Spec update | 15 min | Low (nice to have) | 10 |
