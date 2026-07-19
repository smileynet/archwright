# TypeScript Trace Emitter

Stack adapter (Extension Protocol, ADR 0008) — records state transitions during
test execution and writes the JSON consumed by `archwright-check.py --trace`.

**Status:** ★★ (see `../../REGISTRY.yaml`). Conformance: `conformance/` (scenario +
spec; wired into `tools/run-fixture-tests.sh` § Stack Adapter Conformance).
**Measured cost:** 75-LOC recorder, 63 ms scenario run, ~8 lines of test integration
per spec (field data: TileRush, 2026-07-18).

## Field Usage (validated on tilerush-demo)

1. **Copy the recorder into the target project's test helpers** (it has no
   dependencies beyond `node:fs`/`node:path`):

   ```bash
   cp tools/stacks/typescript/trace_emitter/traceRecorder.ts <target>/test/helpers/
   ```

2. **Instrument a test that drives REAL operations.** Record after each
   *successful* domain action, with the observed variable values — read them
   back from the system where possible rather than assuming:

   ```typescript
   import { createTraceRecorder } from "./helpers/traceRecorder.js";

   const rec = createTraceRecorder({ current_players: 0, max_players: 3 });

   await joinSession(sid, "p1");
   rec.record("JOIN", { current_players: (await getSession(sid))!.currentPlayers });

   // Rejected operations are NOT recorded — the guard held, nothing happened:
   await expect(joinSession(sid, "p4")).rejects.toThrow();

   rec.write("design/traces/session-lifecycle.trace.json");   // afterAll or test end
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
- Worked example: `tilerush-demo/test/archwright-traces.test.ts` (session +
  quest lifecycles, real DDB Local operations).

## Shape Reference

`tools/trace-schema.ts` — consumer-authoritative (bare array of
`{event, state, clock}`, first entry `INITIAL`, full snapshots).
