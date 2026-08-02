---
id: 091
title: "Property-based testing harness generation from behavior specs"
status: done
blocked_by: []
priority: high
---

# Property-based testing harness generation from behavior specs

## Context

Hillel Wayne (Pragmatic Engineer podcast, 2026-07-29) identifies property-based
testing as the practical middle ground between unit tests and full formal
verification. Archwright behavior specs already declare invariants (properties)
and state machines — the ingredients for PBT. Currently our verification layers
are:

- Static: grep/semgrep (structural conformance)
- Trace: replay of specific observed event sequences
- Alloy: bounded model checking (exhaustive within scope)

The gap: traces test specific paths; Alloy tests all paths within a bound but
operates on the model, not code. PBT would generate *random* event sequences
and check invariants hold against the *actual implementation* — bridging the
abstraction gap between model and code.

## What to build

A new check mode: `--pbt <behavior-spec.yaml> --target <module>` that:

1. Reads a behavior spec (states, transitions, invariants, guards)
2. Generates a PBT harness (Hypothesis for Python, fast-check for TypeScript)
   that:
   - Uses the spec's state machine as a strategy (generate valid event sequences)
   - After each event, evaluates invariants against the real system state
   - Shrinks failing sequences to minimal counterexamples
3. Outputs: passing property count, failing properties with shrunk counterexample,
   or a generated test file the user can run in their suite

## Stack adapter pattern

This follows the Extension Protocol (ADR 0008): each language gets a PBT adapter
in `tools/stacks/<lang>/pbt_harness/`. The adapter translates the spec's state
machine + invariants into the target language's PBT framework.

| Language | PBT Framework | Adapter |
|----------|---------------|---------|
| Python | Hypothesis (stateful testing) | `tools/stacks/python/pbt_harness/` |
| TypeScript | fast-check (model-based) | `tools/stacks/typescript/pbt_harness/` |
| GDScript | None native (generate Python Hypothesis against GDScript API?) | Deferred |

## Research needed (before implementation)

- [x] Spike: can Hypothesis stateful testing consume a YAML state machine definition?
      → YES. GitHub gist (technillogue) demonstrates exact pattern. ~80 lines adapter.
- [x] Spike: how does fast-check model-based testing map to our spec format?
      → YES. Command factory pattern maps cleanly. Good async support.
- [x] What's the right interface between PBT harness and the system under test?
      → DECIDED (grill 2026-08-01): Hybrid (Option D). User provides step(event, context),
        PBT drives, trace emitter observes state. See .memory/grill/pbt-contract-alloy-architecture.md
- [x] Should the generated harness be a one-shot file or a live `--pbt` mode?
      → DECIDED (grill 2026-08-01): Inline default + --emit for files (Option C).
        Fast feedback is primary; --emit produces CI artifact.

## Acceptance criteria

- [ ] `--pbt` mode generates a runnable Hypothesis test from a behavior spec
- [ ] Generated test uses spec's state machine as the generation strategy
- [ ] Invariants checked after each transition
- [ ] Failing runs produce shrunk counterexamples
- [ ] At least one stack adapter at ★ (conformance corpus passes)
- [ ] Suite green; AGENTS.md flags note updated
