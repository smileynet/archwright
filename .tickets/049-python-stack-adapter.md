---
id: "049"
title: "Stacks registry: python adapter (trace emitter) — extension-protocol instance"
status: done
blocked_by: []
---

# Python stack adapter — trace emitter for behavior checks

Field gap (discord-poc dp-poc run, 2026-07-22): the 9 PoC areas derived ~20
behavior specs whose trace checks SKIP-with-reason because no python stack
adapter exists in `tools/stacks/REGISTRY.yaml` (the PoC harnesses are
python/bash scripts emitting the repo-standard validation-contract JSON).
This is a new INSTANCE of an existing kind (stack adapter) — flows through
the extension protocol, no ADR needed.

## What to build (per extension protocol rules 3-5)

- Research first: 2+ sources or a spike on the cheapest trace-emission shape
  for script-grade python (candidate: a `trace_event()` helper that appends
  JSON-lines {state, event, ts} — the harnesses already emit structured JSON,
  so the emitter may be a thin convention, not instrumentation)
- Registry row `pending` → ★ path: conformance corpus with a passing scenario
  AND a violating scenario that produces FAIL (vacuous-checker rule —
  mandatory per protocol rule 4)
- Golden corpus wired into run-fixture-tests.sh; status computed by the suite
- Activation-gated: checks run only where survey detects the python stack

## Acceptance criteria
- [x] REGISTRY.yaml row for python with computed status ≥ ★
- [x] discord-poc behavior spec (e.g. x1-replay-emission) trace-checkable
      end-to-end against a sample trace
- [x] Violating trace FAILs in the fixture suite

## Resolution (2026-07-25)

Built `tools/stacks/python/trace_emitter/` (trace_recorder.py, 83 lines, stdlib
only) from the TypeScript adapter's pattern, per the Extension Protocol:

- **Research (rule 3):** 3 subagent reports (prior art, best practices, related
  RV ecosystems) — synthesis promoted to `.memory/research-py-trace-emitter.md`.
  Verdict: no prior art emits the `{event, state, clock}` shape (Hypothesis =
  code repr, pytest plugins = test lifecycle, PyModel = Python source); thin
  convention helper confirmed. Adopted from findings: snapshot-at-record-time
  via JSON round-trip (stdlib mock.call_args mutable-argument pitfall; fails
  fast at the offending event on non-serializable state) + atomic
  mkstemp→os.replace write (no truncated JSON on CI-timeout kill).
- **Conformance at birth (rule 4):** guarded-counter corpus mirroring the TS
  adapter (scenario.py emits passing + violating traces via the real recorder);
  violating run FAILs at the capacity breach. Wired into run-fixture-tests.sh
  § Stack Adapter Conformance (3 checks); suite 152/0/0.
- **Registry (rule 5):** REGISTRY.yaml python row, trace_emitter ★★ (computed:
  corpus in suite + measured cost — recorder 83 lines/~57 code, scenario 60ms),
  since: history from birth. ast_grammar/check_patterns registered pending.
- **End-to-end AC:** sample clean-replay trace generated with the recorder for
  discord-poc `x1-replay-emission`, validated pass (6 steps, clean-emission
  checked, no skips); a corrupted-seq run FAILs at position 3 with full
  provenance — non-vacuous on the field spec, not just the fixture. Trace
  committed to discord-poc `design/traces/`.
