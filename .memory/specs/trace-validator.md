# Spec: Trace Validator Tool

**ID:** trace-validator
**Status:** Draft
**Covers:** T6 (`archwright-check --trace`)
**Blocks:** conformance-test

## Purpose

A command-line tool that validates a JSON event trace against a behavior spec's state machine and invariants. Language-agnostic — any test framework in any language can produce traces; this single tool validates them all.

## Interface

```bash
archwright-check --trace <spec.yaml> <trace.json>
```

### Inputs

| Input | Format | Description |
|-------|--------|-------------|
| `spec.yaml` | Behavior spec YAML | Must have `kind: behavior`, states, transitions, invariants |
| `trace.json` | JSON array | Conforms to trace schema (see [trace-schema](trace-schema.md)) |

### Output (JSON)

```json
{
  "status": "pass",
  "assurance": "trace",
  "spec_id": "ball-state-lifecycle",
  "steps_checked": 3,
  "final_state": "held",
  "invariants_checked": ["at-most-one-holder", "no-holder-during-flight"]
}
```

On failure:

```json
{
  "status": "fail",
  "assurance": "trace",
  "spec_id": "ball-state-lifecycle",
  "violation": {
    "invariant": "at-most-one-holder",
    "position": 2,
    "clock": 1,
    "event": "REQUEST_TRANSFER",
    "state": {"holder": "fielder_a", "requester": "fielder_a"},
    "expected": "holder == none or holder in {fielder_a, fielder_b, fielder_c}",
    "message": "Invariant 'at-most-one-holder' violated after event REQUEST_TRANSFER at position 2"
  },
  "provenance": {
    "from_force": "single-holder",
    "from_pattern": "pattern:ball-possession"
  }
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All invariants hold for all trace steps |
| 1 | Invariant violation found |
| 2 | Invalid input (bad spec, bad trace, missing fields) |

## Implementation

### Language

Bash + `yq` + `jq` for v1 (consistent with existing tools). Future: rewrite in a compiled language if performance matters.

### Algorithm

See [trace-schema.md](trace-schema.md) R20 section for full pseudocode.

Summary:
1. Parse spec YAML (extract states, transitions, guards, invariants, context variables)
2. Parse trace JSON
3. Validate trace[0] is INITIAL event
4. For each subsequent event: find valid transition, evaluate guard, advance state, check invariants
5. Report pass/fail/inconclusive

### Predicate Evaluation

v1: Simple pattern matching for common predicates:
- `X == Y` → string/number equality
- `X != Y` → inequality
- `X in {a, b, c}` → set membership
- `P implies Q` → `not P or Q`
- `P and Q`, `P or Q` → logical connectives

Predicates are evaluated against the trace's `state` object at each position. Variable names in predicates reference keys in `state`.

v2 (future): Embed a proper expression evaluator (CEL or Expr library) for complex predicates.

### Provenance in Output

On violation, the tool traces back through the spec to report:
- Which invariant was violated (`invariants[].id`)
- Which force demanded it (`invariants[].from_force`)
- Which pattern owns it (`invariants[].from_pattern`)

This enables the archwright correction loop: violation → responsible force → re-resolution.

## Spike: S14 Dependency

This tool must exist before S14 (conformance test) can run. The spike validates that the tool catches a real violation in LBP's BallStateService.

## Validation Criteria

- [ ] `archwright-check --trace ball-state-lifecycle.yaml valid-trace.json` → exit 0, JSON output with status:pass
- [ ] `archwright-check --trace ball-state-lifecycle.yaml violation-trace.json` → exit 1, JSON output identifying the correct invariant and position
- [ ] `archwright-check --trace bad-spec.yaml trace.json` → exit 2 with helpful error
- [ ] `archwright-check --trace spec.yaml incomplete-trace.json` → exit 0 with status:inconclusive (if no violation found before trace ends)
- [ ] Provenance fields populated from spec annotations
- [ ] Runs in <1s for traces up to 1000 events

## Links

- Depends on: [trace-schema](trace-schema.md)
- Consumed by: [conformance-test](conformance-test.md), [drift-gate](drift-gate.md)
- Prior art: TLA+ trace validation (TLC replay), MonPoly online monitoring
