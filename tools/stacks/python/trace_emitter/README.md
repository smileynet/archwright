# Python Trace Emitter

Stack adapter (Extension Protocol, ADR 0008) — records state transitions during
test/harness execution and writes the JSON consumed by `archwright-check.py --trace`.

**Status:** see `../../REGISTRY.yaml` (computed by the fixture suite). Conformance:
`conformance/` (scenario + spec; wired into `tools/run-fixture-tests.sh`
§ Stack Adapter Conformance).

## Usage

1. **Copy the recorder into the target project's test helpers** (stdlib only —
   json/os/tempfile; Python ≥ 3.6):

   ```bash
   cp tools/stacks/python/trace_emitter/trace_recorder.py <target>/tests/helpers/
   ```

2. **Instrument a test or harness that drives REAL operations.** Record after
   each *successful* domain action, with the observed variable values — read
   them back from the system where possible rather than assuming:

   ```python
   from helpers.trace_recorder import TraceRecorder

   rec = TraceRecorder({"current_players": 0, "max_players": 3})

   join_session(sid, "p1")
   rec.record("JOIN", current_players=get_session(sid).current_players)

   # Rejected operations are NOT recorded — the guard held, nothing happened:
   with pytest.raises(SessionFullError):
       join_session(sid, "p4")

   rec.write("design/traces/session-lifecycle.trace.json")  # teardown or test end
   ```

3. **Validate against the behavior spec:**

   ```bash
   python3 <archwright>/tools/archwright-check.py --trace \
     design/specs/session-lifecycle.yaml design/traces/session-lifecycle.trace.json
   ```

## Rules of Use

- **Snapshot vars use the spec's snake_case `context.variables` keys.** Include
  any EXTRA variables the spec's invariant predicates reference (e.g. a `status`
  string) even if undeclared — otherwise the predicate translator treats the
  bare name as a literal and the implication evaluates wrong.
- **Record consequences, not intentions.** Read values back from the real system
  after the operation; a trace of assumed values validates your assumptions, not
  the implementation.
- **Rejected operations don't appear.** A guard that held = no transition = no
  entry. (Recording a rejected op as if it happened is how you fake a violation.)
- **State values must be JSON-serializable at record time.** The recorder
  snapshots via a JSON round-trip — a non-serializable value raises at the
  offending `record()` call, naming the event, instead of corrupting the file
  at write time. Convert rich types (datetime, Decimal) to primitives yourself.
- Writes are atomic (`os.replace`) — a killed run never leaves truncated JSON.
  Parallel writers to the SAME path are last-writer-wins; give each worker its
  own trace file.

## Shape Reference

`tools/trace-schema.ts` — consumer-authoritative (bare array of
`{event, state, clock}`, first entry `INITIAL`, full snapshots). Shared with
the TypeScript adapter (`../typescript/trace_emitter/`).

## Design Notes (research pass, ticket 049)

- **No prior art emits this shape.** Hypothesis stateful testing represents
  runs as reproducible Python code, pytest-reportlog logs test lifecycle (not
  domain state), PyModel traces are Python source. A thin convention helper is
  the cheapest correct shape for script-grade Python.
- **Snapshot at record time, never at dump time** — storing live dict
  references and serializing at teardown records the final state in every
  entry (the stdlib-documented `mock.call_args` mutable-argument pitfall).
- Full findings: archwright `.memory/research-py-trace-emitter.md` (prior art,
  best practices, related runtime-verification ecosystems).
