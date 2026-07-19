# Trace Instrumentation Guide: GDScript

How to instrument a GDScript state machine to emit JSON traces for archwright behavioral spec validation.

## Overview

Archwright's trace validation (`archwright-check.py --trace`) replays JSON traces against behavior spec state machines. This guide shows how to emit traces from GDScript tests.

## Trace Format

Traces are flat JSON arrays. Each entry carries event, state snapshot, and clock:

```json
[
  {"event": "INITIAL", "state": {"generation": 0, "pending": 0}, "clock": 0},
  {"event": "START_RUN", "state": {"generation": 1, "pending": 0}, "clock": 1},
  {"event": "CHAIN_COMPLETED", "state": {"generation": 1, "pending": 2}, "clock": 2}
]
```

The first entry MUST be `"event": "INITIAL"` with the initial state snapshot.

## GDScript Emitter

A minimal autoload trace recorder:

```gdscript
class_name ArchTraceEmitter
extends RefCounted

var _trace: Array[Dictionary] = []
var _clock: int = 0
var source: StringName

func _init(initial_state: Dictionary) -> void:
    _trace.append({"event": "INITIAL", "state": initial_state, "clock": 0})

func emit(event: StringName, state: Dictionary) -> void:
    _clock += 1
    _trace.append({"event": String(event), "state": state, "clock": _clock})

func save(path: String) -> void:
    var file := FileAccess.open(path, FileAccess.WRITE)
    file.store_string(JSON.stringify(_trace, "  "))
    file.close()
```

Usage in tests:

```gdscript
func test_normal_completion() -> void:
    var trace := ArchTraceEmitter.new({"generation": 0, "pending": 0})
    trace.source = &"test_normal_completion"

    # Exercise the system, recording state after each event
    trace.emit(&"START_RUN", {"generation": 1, "pending": 0})
    trace.emit(&"CHAIN_COMPLETED", {"generation": 1, "pending": 0})
    trace.emit(&"ADVANCE", {"generation": 2, "pending": 0})

    trace.save("res://design/specs/traces/step-advancement-normal.json")
```

## Instrumentation Patterns

### Pattern 1: Test-side recording (recommended)

The test script observes the system under test and records transitions. The SUT itself is unmodified.

```gdscript
func test_with_trace() -> void:
    var trace := ArchTraceEmitter.new({"holder": "", "in_flight": false})
    
    # Exercise the system
    ball_state.request_possession(&"A1")
    trace.emit(&"PICKUP", {"holder": "A1", "in_flight": false})
    
    ball_state.throw_to(&"A2")
    trace.emit(&"THROW", {"holder": "", "in_flight": true})
    
    ball_state.arrive()
    trace.emit(&"ARRIVE", {"holder": "A2", "in_flight": false})

    trace.save("res://design/specs/traces/ball-possession-pass.json")
```

**Pros:** No production code changes. Test is explicit about expected state.
**Cons:** Test and SUT can diverge if test records wrong state.

### Pattern 2: Signal-tap (integration tests)

Attach a trace recorder to actual system signals:

```gdscript
class TraceRecorder extends RefCounted:
    var _emitter: ArchTraceEmitter

    func _init(initial_state: Dictionary) -> void:
        _emitter = ArchTraceEmitter.new(initial_state)

    func on_event(event: StringName, new_state: Dictionary) -> void:
        _emitter.emit(event, new_state)

    func save(path: String) -> void:
        _emitter.save(path)
```

**Pros:** Records actual system behavior.
**Cons:** Requires mapping signals to spec events.

## Validation

After tests produce trace files:

```bash
# Validate a single trace
python3 tools/archwright-check.py --trace design/specs/step-advancement.yaml \
  design/specs/traces/step-advancement-normal.json

# With JSON output (CK-03 document shape)
python3 tools/archwright-check.py --trace design/specs/step-advancement.yaml \
  design/specs/traces/step-advancement-normal.json --json
```

## Trace File Location

```
design/specs/traces/
  step-advancement-normal.json
  step-advancement-stale-gen.json
  ball-possession-pass.json
  ball-possession-rejected.json
```

## Spec Coverage

Each behavior spec scenario should have at least one corresponding trace. Use `--trace-coverage` to audit:

```bash
python3 tools/archwright-check.py --trace-coverage design/specs/ design/specs/traces/
```

## When to Instrument

- After a behavior spec is written and stable
- Before claiming ★★ confidence on behavioral invariants
- When debugging a state machine violation (trace localizes the event)

## Anti-patterns

- ❌ Instrumenting production code with trace emission (tests only)
- ❌ Recording events at finer granularity than the spec models
- ❌ Emitting traces without validating them (dead traces drift from spec)
- ❌ Recording internal implementation states instead of spec states (map to spec vocabulary)
