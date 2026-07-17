# Render leads-to invariants as safety skeletons; probe non-vacuity at authoring time

One-line: generated models stutter freely — raw liveness is unprovable, so check the successor/predecessor skeleton and prove the checker can fail before trusting PASS.

**Date:** 2026-07-17 · **Source:** ExposeAR behavior specs (first field alloy authoring)

The compiler's models permit stuttering and don't model bool vars, var updates, or
guard enforcement. Consequences for authoring `alloy:` expressions:

1. **`leads-to` liveness is unprovable** without fairness — render the checkable
   safety skeleton instead: `always (M.current = Evaluating implies M.current' in
   Evaluating + Idle + Solved)` ("no third exit exists"). Liveness half → trace check.
2. **Guard-dependent invariants would spuriously fail** (guards compile to comments —
   the model enters guarded states unconditionally). Leave prose-only with a YAML
   comment naming the blocker; ticket 008 tracks guard compilation.
3. **Every unrendered invariant documents WHY** (bool var / payload property /
   cross-machine / needs clock) so SKIPs are self-explaining.
4. **Non-vacuity probe:** after authoring, inject one deliberately false invariant
   (`always M.current = <Initial>`) and confirm a counterexample appears. Five PASSes
   mean nothing from a checker that cannot fail (see checkers-need-negative-tests).

Worked example: ExposeAR `design/specs/{spatial-session,placement-lifecycle,mentor-session}.yaml`.
Skill-text suggestion queued as ticket 009.
