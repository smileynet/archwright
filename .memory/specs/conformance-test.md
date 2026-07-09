# Spec: Conformance Test

**ID:** conformance-test
**Status:** Draft
**Covers:** S14 (conformance test spike), T7 (GDScript trace emitter), C2 (write one conformance test)
**Type:** Spike → implementation

## Purpose

Prove the trace validation approach works end-to-end: a gdUnit4 test exercises real LBP code, emits a JSON trace, and `archwright-check --trace` validates it against the `ball-state-lifecycle` behavior spec.

## Spike: S14

### Goal

One conformance test in gdUnit4 that:
1. Exercises `BallStateService` through a realistic scenario
2. Emits a JSON event trace via the trace emitter
3. Validates the trace against `ball-state-lifecycle.yaml`
4. Catches a deliberately introduced double-possession violation

### Pass Criteria

1. Normal scenario (request → validate_accept → request → validate_accept) → trace validates, test passes
2. Introduce double-possession (set holder without going through request protocol) → trace validator catches it, reports `invariant:at-most-one-holder` violated at correct position
3. Violation report includes provenance (from_force: single-holder, from_pattern: ball-possession)
4. Total test runtime <2s (including trace write + validation)

### Fail Criteria

- Trace schema can't capture enough state for meaningful validation
- Guard predicates in the spec can't be evaluated against real state snapshots
- Overhead of trace emission measurably slows the test suite
- The state mapping (concrete BallStateService state → abstract spec states) is ambiguous

## T7: GDScript Trace Emitter

```gdscript
class_name ArchTrace extends RefCounted

var _events: Array[Dictionary] = []
var _trace_path: String

func _init(trace_path: String) -> void:
    _trace_path = trace_path

func initial(state: Dictionary) -> void:
    _events.append({"clock": 0, "event": "INITIAL", "state": state})

func emit(event_name: StringName, state: Dictionary) -> void:
    _events.append({
        "clock": _events.size(),
        "event": str(event_name),
        "state": state
    })

func flush() -> void:
    var json := JSON.stringify(_events, "  ")
    var f := FileAccess.open(_trace_path, FileAccess.WRITE)
    f.store_string(json)
    f.close()

func validate(spec_path: String) -> Dictionary:
    flush()
    var output := []
    var exit_code := OS.execute("archwright-check", ["--trace", spec_path, _trace_path], output)
    var result := JSON.parse_string(output[0]) as Dictionary if output.size() > 0 else {}
    result["exit_code"] = exit_code
    return result
```

### Design Decisions

- **Clock is logical** (event index), not wall time. Simpler, deterministic, sufficient for ordering.
- **State snapshot is caller's responsibility.** The test decides what to report. This keeps the emitter trivial.
- **`validate()` shells out to `archwright-check --trace`.** This keeps the GDScript adapter thin and the validation logic in one place.
- **RefCounted, not Node.** No scene tree dependency. Can be used in any test.

## Example Conformance Test

```gdscript
# test/conformance/test_ball_state_lifecycle.gd
extends GdUnitTestSuite

const SPEC_PATH := "res://../../design/specs/ball-state-lifecycle.yaml"
const TRACE_DIR := "res://test/traces/"

func _state(service: BallStateService) -> Dictionary:
    return {
        "holder": service.current_holder if service.current_holder else "none",
        "requester": "none"  # BallStateService doesn't expose requester yet
    }

func test_normal_transfer_conforms() -> void:
    var service := BallStateService.new()
    var trace := ArchTrace.new(TRACE_DIR + "normal_transfer.json")
    
    trace.initial(_state(service))
    
    service.request_possession("slot_B")
    trace.emit("REQUEST_TRANSFER", _state(service))
    
    # BallStateService auto-accepts in current implementation
    trace.emit("VALIDATE_ACCEPT", _state(service))
    
    var result := trace.validate(SPEC_PATH)
    assert_int(result.exit_code).is_equal(0)
    assert_str(result.status).is_equal("pass")

func test_double_possession_caught() -> void:
    var service := BallStateService.new()
    var trace := ArchTrace.new(TRACE_DIR + "double_possession.json")
    
    service.request_possession("slot_A")
    trace.initial({"holder": "slot_A", "requester": "none"})
    
    # Deliberately violate: force a second holder without releasing first
    # (This simulates a bug where holder is set directly)
    service._holder = "slot_B"  # direct write = violation
    trace.emit("REQUEST_TRANSFER", {"holder": "slot_B", "requester": "none"})
    # ^ State reports holder=slot_B but we never went through in-flight
    # The trace validator should catch: no valid transition from held
    # with event REQUEST_TRANSFER that results in holder changing without in-flight
    
    var result := trace.validate(SPEC_PATH)
    assert_int(result.exit_code).is_equal(1)
    assert_str(result.status).is_equal("fail")
    assert_str(result.violation.invariant).is_equal("at-most-one-holder")
```

## Open Questions

1. **State mapping granularity:** BallStateService's internal state may not map 1:1 to spec states. The spec has `held` and `in-flight`; the service has `current_holder` (string). How explicit should the mapping be?
   - Option A: Test manually maps (as shown above)
   - Option B: Spec declares a mapping formula
   - **Recommendation:** Start with Option A. If it's too burdensome after 3+ conformance tests, add Option B.

2. **Trace file location:** Where do trace JSON files go?
   - Option A: `test/traces/` in LBP (committed, reviewable)
   - Option B: Temp directory (not committed, regenerated each run)
   - **Recommendation:** Option B for CI, Option A for reference/debugging. Add `.gitignore` for traces generated during test runs, but commit one "golden" trace per spec as documentation.

3. **Spec path resolution:** The test needs to find the spec file. How?
   - Option A: Hardcoded relative path (fragile)
   - Option B: Environment variable `ARCHWRIGHT_DESIGN_DIR`
   - Option C: Convention: `design/specs/` relative to project root
   - **Recommendation:** Option C with env var override.

## Validation Criteria

- [ ] `ArchTrace` class works in gdUnit4 (emits valid JSON, flushes correctly)
- [ ] Normal scenario test passes (exit 0, status pass)
- [ ] Violation scenario test correctly detects double-possession
- [ ] Violation report includes invariant name, position, provenance
- [ ] Total runtime <2s per conformance test
- [ ] Trace JSON is valid per trace-schema

## Links

- Depends on: [trace-schema](trace-schema.md), [trace-validator](trace-validator.md)
- Tests against: LBP's `ball-state-lifecycle.yaml` behavior spec
- Proves: the trace validation approach works for real game code
