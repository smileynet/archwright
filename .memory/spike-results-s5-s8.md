# Spike Results: S5–S8

## S5 — Alloy Compilation Target ✅

**Model:** Intimacy Gradient spec → Alloy 6 (75 lines)  
**Result:** Alloy finds the EXTERNAL_UNLOCK bypass counterexample in **94ms**.

Counterexample trace:
```
State 0: tier=Shallow, score=0, reached={Shallow}
State 1: tier=Deep,    score=0, reached={Shallow, Deep}  ← externalUnlock bypasses Intermediate
```

**Conclusion:** The archwright spec layer compiles cleanly to valid Alloy 6 using `var` fields + temporal operators. Statechart-to-Alloy encoding is straightforward for flat machines. Hierarchy encoding still needs validation.

## S6 — Contrast Pair Generation ✅

**Approach:** After finding the counterexample, asked Alloy to find a satisfying trace that ALSO reaches Deep (maximally similar to the violation).

**Contrast pair:**
```
Counterexample:  Shallow → Deep (1 step, externalUnlock)
Satisfying:      Shallow → Shallow → Shallow → Intermediate → Deep (5 steps, legitimate)
```

**The diff:** externalUnlock vs. demonstrate+advance path. The responsible element (`externalUnlock`) is immediately obvious from the structural difference (1 step vs. 5 steps; skips Intermediate).

**Solving time:** 198ms for the satisfying trace.

**Conclusion:** Contrast pairs work. The diff between violation and nearest valid state localizes the fault mechanically. No AI interpretation needed for attribution at this level.

## S7 — Formal Summary Predicates ✅

Expressed three game failure predicates in Alloy against a combat/resource game:

| Predicate | Result | Time | Finding |
|-----------|--------|------|---------|
| Softlock | **Found** | 408ms | Player reaches hp=0, gold=0 (alive but no recovery) |
| Death Spiral | **Found** | 76ms | Player at hp=2, gold<0 (fighting drains remaining health) |
| Degenerate Strategy | **Not found** | UNSAT | Shopping IS required to win (no dominant single strategy) |

**Conclusion:** Game failure predicates ARE expressible in Alloy's logic and produce meaningful counterexamples. The predicates need careful formulation (integer overflow is a real concern — use appropriate bitwidths). The failures found are genuine design issues that a human designer would want to know about.

## S8 — Incremental Checking Latency ✅

| Metric | Value |
|--------|-------|
| JVM startup | ~500ms |
| SAT solving (small model, 5 states) | 76–94ms |
| SAT solving (medium model, 5+ states, integers) | 198–408ms |
| Total per-check (warm JVM) | **<500ms** |

**Conclusion:** Live validation IS feasible with a warm JVM. The solving itself is fast enough for interactive feedback (<200ms for structural checks, <500ms for integer-heavy models). The JVM must stay running (language-server pattern, not CLI-per-check).

## Combined Findings

The dual-target architecture is validated:
1. **Archwright spec → Alloy 6** works (S5). Counterexamples found, contrast pairs generated (S6).
2. **Domain failure predicates** are expressible and produce actionable results (S7).
3. **Latency is acceptable** for live validation with a warm JVM (S8).

The critical open question answered: **Alloy is a viable checking backend for archwright.** The compilation from spec layer to Alloy is mechanical, the checking is fast, and the results map cleanly back to archwright's force/pattern vocabulary via provenance annotations.

### Limitations (verified 2026-07-07)

- **Bounded checking cannot prove inductive properties.** If a property requires induction (e.g., "for ALL traces of ANY length, X holds"), no finite scope suffices. Escalation to unbounded verification (Alloy's nuXmv backend, Apalache for TLA+, or Lean proofs) is needed for ★★ promotion of such properties.
- **Liveness properties are expensive.** Temporal liveness (◇good, "eventually reaches X") requires full state graph construction + fairness constraints. Much slower than safety (□¬bad). Apalache (symbolic/SMT-based) may be more practical than explicit-state checkers for bounded liveness.
- **Integer overflow at small bitwidth.** Default 4-bit integers (-8..7) cause spurious counterexamples. Must set appropriate bitwidth for numeric specs.
- **Scope 3 catches ~90% of bugs** (Jackson's empirical data). Scope 5-7 is practical confidence. Report the scope used alongside any "no violation found" result.
