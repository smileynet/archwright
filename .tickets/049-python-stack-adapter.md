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

TBD
