# Python PBT Harness (Hypothesis Adapter)

Property-based testing of behavior specs against real implementations using
Hypothesis stateful testing.

## How it works

1. You have a **behavior spec** (YAML) declaring states, transitions, and invariants
2. You write a **step function** (3-10 lines) that maps events to your system calls
3. The adapter generates random valid event sequences from the spec's state machine
4. After each event, invariants are checked against the real system state
5. Failures are shrunk to minimal counterexamples

## Architecture (grill 2026-08-01, Option D — Hybrid)

```
┌─────────────────────────────────────────────────┐
│ Hypothesis RuleBasedStateMachine (generated)     │
│   - Generates random events valid in current     │
│     model state (from spec)                      │
│   - Calls step() for each event                  │
│   - Checks invariants after each step            │
│   - Shrinks failures to minimal sequences        │
└────────────┬────────────────────┬───────────────┘
             │ calls              │ checks
             ▼                    ▼
┌────────────────────┐  ┌────────────────────────┐
│ step(event, ctx)   │  │ spec.invariants[]      │
│ (user provides)    │  │ evaluated against       │
│ maps event → SUT   │  │ returned state dict     │
└────────────────────┘  └────────────────────────┘
```

## Quick start

```bash
# Run PBT inline (fast feedback)
python3 tools/archwright-check.py --pbt design/specs/my-behavior.yaml --step my_step.py

# Generate a portable test file for CI
python3 tools/archwright-check.py --pbt design/specs/my-behavior.yaml --step my_step.py --emit tests/
```

## Writing a step function

```python
def step(event: str, context: dict) -> dict:
    """Apply event to SUT, return new state snapshot."""
    if event == "INITIAL":
        my_system.reset()
        return {"counter": 0, "active": True}
    elif event == "INCREMENT":
        my_system.increment()
        return {"counter": my_system.count, "active": True}
    elif event == "DEACTIVATE":
        my_system.deactivate()
        return {"counter": my_system.count, "active": False}
```

The step function:
- Receives the event name and current context variables
- Applies the event to your system (however that works — method call, HTTP, signal)
- Returns the new state snapshot as a dict (keys = spec's context variables)

See `template_step.py` for a full template.

## Requirements

- Python >= 3.8
- `hypothesis` (`pip install hypothesis`)

## Conformance

The `conformance/` directory contains a golden corpus proving the adapter works:
- A toy behavior spec (guarded counter)
- A correct step function (PBT passes)
- A buggy step function (PBT finds the invariant violation and shrinks it)

Run: `python3 conformance/scenario.py`
