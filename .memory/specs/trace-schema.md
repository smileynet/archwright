# Spec: Trace Schema

**ID:** trace-schema
**Status:** Draft
**Covers:** U1 (trace JSON schema), U4 (check block in behavior specs)
**Blocks:** trace-validator, conformance-test

## Purpose

Define the JSON schema for event traces that conformance tests emit, and the `check` block that behavior specs use to declare their trace-checkable surface.

## Trace JSON Schema

A trace is an ordered array of events. Each event records a clock, an event name, and a state snapshot.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["clock", "event", "state"],
    "properties": {
      "clock": {
        "type": "integer",
        "description": "Monotonically increasing logical clock (ticks, frame count, or microseconds)"
      },
      "event": {
        "type": "string",
        "description": "Event name matching a transition trigger in the behavior spec, or INITIAL for the first entry"
      },
      "state": {
        "type": "object",
        "description": "Snapshot of all context variables after this event. Keys match spec context variable names.",
        "additionalProperties": true
      }
    }
  },
  "minItems": 1
}
```

### Conventions

- First event MUST have `"event": "INITIAL"` and represent the system's starting state.
- `clock` is opaque to the validator — used only for ordering and error reporting.
- `state` keys MUST include all variables declared in the spec's `context.variables`. Extra keys are ignored.
- Values in `state` MUST be JSON primitives (string, number, boolean, null). Enum values are strings.

### Example

```json
[
  {"clock": 0, "event": "INITIAL", "state": {"holder": "fielder_a", "requester": "none"}},
  {"clock": 1, "event": "REQUEST_TRANSFER", "state": {"holder": "none", "requester": "fielder_b"}},
  {"clock": 2, "event": "VALIDATE_ACCEPT", "state": {"holder": "fielder_b", "requester": "none"}}
]
```

## Behavior Spec `check` Block

Added to behavior spec YAML to declare how the spec can be checked:

```yaml
check:
  trace:
    events: [REQUEST_TRANSFER, VALIDATE_ACCEPT, VALIDATE_REJECT, RELEASE]
    state_vars: [holder, requester]
    invariants: [at-most-one-holder, no-holder-during-flight]
  model:
    backend: alloy
    scope: 4
    steps: 10
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `check.trace.events` | string[] | Events the trace validator accepts. Subset of transitions defined in `states`. |
| `check.trace.state_vars` | string[] | Context variables the trace must report. Subset of `context.variables`. |
| `check.trace.invariants` | string[] | Which invariants to check against traces. References `invariants[].id`. |
| `check.model.backend` | string | Model checking backend (`alloy` or `lean`). |
| `check.model.scope` | int | Alloy scope (atoms per sig). |
| `check.model.steps` | int | Maximum trace length for temporal checking. |

### State Mapping

**Decision: Option C — concrete state vars + optional `_state` hint.**

The trace reports concrete values (e.g., `"holder": "fielder_b"`). The validator determines the abstract state by:

1. If `_state` is present in the event → use it directly (the test knows the state name).
2. If `_state` is absent → evaluate per-state invariants against the state snapshot to infer which abstract state the system is in.
3. If zero or multiple states match → **state mapping error**.

**Rationale (from prior art):**
- XState inspect protocol emits the state node name explicitly alongside context. This is Option A and works because XState IS the implementation.
- TLA+ trace validation (Cirstea 2024) requires the implementation to emit variables matching TLA+ variable names. The spec/impl variable names are aligned by convention. This is Option B.
- Jepsen infers abstract operations from concrete logs (no explicit state labels). This is Option B.
- QuickCheck eqc_statem has the TEST define the model comparison function. The test author maps concrete → abstract.

For archwright: we don't control the implementation (it's arbitrary game code, not a state machine library). The test author is closest to knowing both sides. **Option C** (both) gives flexibility:
- Simple cases: test emits `_state: "held"` because it knows.
- Complex cases: test emits only concrete vars; validator infers from invariants.
- Debugging: both present → validator cross-checks (declared state vs inferred state).

## Research: R20 (Trace Validation Algorithm)

### Algorithm Pseudocode

```
function validate(spec, trace):
  current_state = spec.initial
  
  for i, entry in enumerate(trace):
    if i == 0:
      assert entry.event == "INITIAL"
      verify_state_matches(spec, current_state, entry.state)
      check_invariants(spec, entry.state)
      continue
    
    # Find valid transitions from current_state for this event
    transitions = spec.states[current_state].on[entry.event]
    if transitions is empty:
      FAIL("no transition for event {entry.event} in state {current_state}", position=i)
    
    # Evaluate guard (if present)
    for transition in transitions:
      if transition.guard:
        if not evaluate(transition.guard.predicate, prev_state):
          continue  # guard failed, try next transition
      # Guard passed (or no guard)
      current_state = transition.target
      break
    else:
      FAIL("all guards failed for event {entry.event} in state {current_state}", position=i)
    
    # Verify reported state is consistent with new abstract state
    verify_state_matches(spec, current_state, entry.state)
    
    # Check all declared invariants
    check_invariants(spec, entry.state)
  
  PASS(steps=len(trace), final_state=current_state)
```

### Guard Predicate Language

**Decision: jq expressions for v1, celq for v1.5 if needed.**

Spec predicates are written in a human-readable syntax:
- Comparisons: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`, `implies`
- Membership: `in {a, b, c}`
- Variables: bare names from `context.variables`
- Literals: strings, numbers, booleans, `none`

The trace validator translates these to jq expressions at runtime:

| Spec syntax | jq translation |
|-------------|---------------|
| `requester != holder` | `.requester != .holder` |
| `holder == none` | `.holder == "none"` |
| `holder in {fielder_a, fielder_b, fielder_c}` | `.holder \| IN("fielder_a","fielder_b","fielder_c")` |
| `A implies B` | `((.A \| not) or .B)` |
| `A and B` | `(.A and .B)` |

Evaluation: `echo "$state_json" | jq -e "$translated_expr"` — exit 0 = true, exit 1 = false.

**Rationale:** jq is already a dependency, is safe (no I/O side effects), handles JSON natively, and is fast enough (~1-5ms per evaluation). The translation layer is ~20 lines of bash. If predicates become complex enough to need richer syntax, swap to `celq` (Rust CEL binary, same pipe pattern, same safety guarantees).

### Temporal Invariants on Finite Traces

For safety properties (`always P`): check P at every step. If P holds at all steps → pass. If P fails at any step → fail with position.

For liveness properties (`eventually P`): check if P holds at least once. If trace ends without P → **inconclusive** (not fail — the trace might be too short).

Three-valued verdict: `pass | fail | inconclusive`.

### Edge Cases

| Case | Handling |
|------|----------|
| Incomplete trace (test crashed) | Report last-seen state. Verdict is `inconclusive` if no violation found. |
| Extra state variables in trace | Ignored (trace may report more than spec requires). |
| Missing state variables | FAIL with "missing required variable X at position N". |
| Non-deterministic (multiple valid transitions for same event) | Try all; if any valid path exists, take it. If none work, fail. |
| Extended state (counters) | State vars can be integers. Predicates support arithmetic comparison. |

## Validation Criteria

- [ ] JSON Schema validates the example trace above
- [ ] A behavior spec with `check.trace` block passes `archwright-validate`
- [ ] The trace validator pseudocode handles the ball-state-lifecycle example correctly
- [ ] Edge cases (incomplete, missing var, guard failure) produce clear errors

## Links

- Implements: U1 (trace schema), U4 (check block)
- Consumed by: [trace-validator](trace-validator.md), [conformance-test](conformance-test.md)
- Prior art: TLA+ trace validation (Cirstea 2024), MonPoly MFOTL monitoring, XState inspect protocol
