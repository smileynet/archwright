# Spec: Check Results Schema

**ID:** check-results
**Status:** Draft
**Covers:** U2 (assurance qualifiers), U3 (abstraction_notes field)

## Purpose

Standardize what archwright check results mean. Prevent false confidence from a "pass" result by reporting what level of assurance the check provides and what was excluded from checking.

## Assurance Levels

| Level | Meaning | Backend | Guarantee |
|-------|---------|---------|-----------|
| `static` | Structural pattern check passed | grep, ast-grep | Code matching pattern absent/present |
| `trace` | No violation in observed execution | trace validator | Invariants held for this specific run |
| `bounded` | No counterexample within model bounds | Alloy | No violation in scope N, steps M |
| `proven` | Theorem proved for all reachable states | Lean | Universal correctness |

Each level subsumes confidence from the levels below it:
- `static` < `trace` < `bounded` < `proven`

A spec may have results at multiple levels simultaneously (e.g., static constraint passes AND trace test passes).

## Result Schema

Every check result (from any tool) conforms to:

```json
{
  "status": "pass | fail | inconclusive | error",
  "assurance": "static | trace | bounded | proven",
  "spec_id": "string (kind:id)",
  "duration_ms": 0,
  "details": {}
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `pass` | Check completed, no violation found at this assurance level |
| `fail` | Violation found — includes violation details |
| `inconclusive` | Check ran but couldn't determine (e.g., trace too short for liveness property) |
| `error` | Tool failure (bad input, crash) — not a spec verdict |

### Per-Assurance Details

**Static:**
```json
{"method": "grep", "target": "project.godot", "matches": []}
```

**Trace:**
```json
{"steps_checked": 42, "final_state": "held", "invariants_checked": ["at-most-one-holder"]}
```

**Bounded:**
```json
{"backend": "alloy", "scope": 4, "steps": 10, "states_explored": 847}
```

**Proven:**
```json
{"backend": "lean", "theorem": "ball_state.at_most_one_holder", "proof_time_ms": 3200}
```

## Abstraction Notes (on Behavior Specs)

Behavior specs SHOULD include `abstraction_notes` documenting what's excluded from checking:

```yaml
abstraction_notes:
  included:
    - "Possession states (held, in-flight)"
    - "Transfer protocol (request, validate, accept/reject)"
  excluded:
    - "Physics proximity checks (when transfers can be requested)"
    - "Animation timing (how long transitions take visually)"
    - "Network latency (replication delay between clients)"
  justification: >
    Properties checked (single holder, no double possession) are independent of
    physics/proximity/animation. Those affect WHEN transfers happen, not WHETHER
    the invariant holds.
  scope_limit: >
    Trace checks cover observed executions only. Bounded model checking at scope 4,
    10 steps. Properties requiring longer sequences would need larger bounds.
```

### Why This Matters

Without abstraction notes, a "pass" result is ambiguous:
- Does it mean "no bugs possible"? No.
- Does it mean "no bugs in the areas we checked"? Yes.
- Which areas? Read `abstraction_notes`.

This is honest reporting of verification limitations.

## Schema Update to spec-schema.yaml

Add to the behavior spec schema:

```yaml
# New optional fields
abstraction_notes:
  type: object
  properties:
    included: {type: array, items: {type: string}}
    excluded: {type: array, items: {type: string}}
    justification: {type: string}
    scope_limit: {type: string}

check:
  type: object
  properties:
    trace:
      type: object
      properties:
        events: {type: array, items: {type: string}}
        state_vars: {type: array, items: {type: string}}
        invariants: {type: array, items: {type: string}}
    model:
      type: object
      properties:
        backend: {type: string, enum: [alloy, lean]}
        scope: {type: integer}
        steps: {type: integer}
```

## Validation Criteria

- [ ] `spec-schema.yaml` updated with `abstraction_notes` and `check` blocks
- [ ] Existing fixture spec (`ball-state-lifecycle.yaml`) extended with both fields
- [ ] `archwright-validate` accepts specs with the new fields
- [ ] All tool outputs conform to the result schema
- [ ] Human-readable mode translates assurance levels into plain English

## Links

- Consumed by: all check tools (trace-validator, static-check-batch, archwright-compile-alloy)
- Updates: `tools/spec-schema.yaml`
- Updates: fixture spec `tests/fixtures/fieldball-coach/design/specs/ball-state-lifecycle.yaml`
