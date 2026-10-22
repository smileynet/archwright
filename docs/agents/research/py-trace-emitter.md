# Research Synthesis: Python Trace Emitter (ticket 049, 2026-07-25)

Extension Protocol research pass (rule 3) for `tools/stacks/python/trace_emitter/`.
Condensed from three subagent reports (raw: `.scratch/research/py-trace-*.md`,
ephemeral). Sources are cited in the raw reports; load-bearing ones repeated here.

## Verdict

A thin stdlib-only convention helper mirroring the TypeScript recorder is the
cheapest correct shape. No mainstream Python tool emits a first-class
`{event, state, clock}` transition trace as data — nothing to adopt, nothing to
wrap.

## Prior art (what exists, why it doesn't fit)

- **Hypothesis stateful testing** (RuleBasedStateMachine): has the exact
  vocabulary (`@precondition` = guards, `@invariant` = invariants) but represents
  failing runs as reproducible Python CODE, not a data trace. Extracting a
  machine trace requires wrapping rules — a possible future integration, not a
  base.
- **pytest ecosystem** (pytest-reportlog, pytest-replay, pytest-instrument):
  JSONL event streams at TEST-lifecycle granularity (setup/call/teardown), never
  domain state. Convention worth noting: per-line type discriminator
  (`$report_type`), ignore-unknown-keys forward compat.
- **PyModel** (dormant ~2011): clearest conceptual precedent — behavior = traces
  of actions, specs define allowed/forbidden traces — but traces are Python
  source, no JSON interchange. AltWalker/GraphWalker produce labeled paths but
  need a Java service.

## Best practices adopted (visible in trace_recorder.py)

1. **Snapshot at record time, never dump time.** Storing live dict references
   and serializing at teardown records the FINAL state in every entry — the
   stdlib-documented `mock.call_args` mutable-argument pitfall
   ([L2] docs.python.org unittest.mock-examples, "Coping with mutable
   arguments"; documented fix = copy at call time). Shallow `dict(state)` is a
   trap (top-level only). Adopted: `json.loads(json.dumps(state))` at append
   time — faster than deepcopy for plain data AND fails fast at the offending
   event when state isn't JSON-serializable.
2. **Atomic write:** `tempfile.mkstemp(dir=target_dir)` → write → `os.replace`
   (atomic cross-platform since 3.3; same-filesystem requirement satisfied by
   dir=). A CI-timeout kill never leaves truncated JSON. No reflexive
   `default=str` (hides recording bugs).
3. **Plain dicts over dataclasses** for a 3-field record: `dataclasses.asdict()`
   deep-copies internally (~10x slower), json can't serialize dataclasses
   natively.
4. **Parallel writers:** `os.replace` is silent last-writer-wins — one trace
   file per worker (documented in the adapter README).

## Related ecosystems (positioning, future backends)

- **Sismic** property statecharts: live-monitoring only (interpreter
  meta-events, fail-fast on safety violations) — no offline replay of recorded
  traces. Closest conceptual neighbor; explicitly scoped to safety properties
  on finite prefixes, same as archwright trace mode.
- **PyContract** (Havelund/JPL): closest MECHANICS to `--trace` — offline
  event-stream replay through extended-FSMs with data variables, explicit
  verdicts. Specs are Python code, not declarative.
- **RTAMT**: offline+online STL monitoring with quantitative
  distance-to-violation robustness — a richer verdict than pass/fail, relevant
  to contrast-pair generation someday.
- **pm4py/Declare4Py** (process mining): XES event logs vs Petri
  nets/LTLf rules; LTLf finite-trace 3-valued verdicts parallel our
  SKIP-with-reason design. Alignment-based conformance (minimal edit to a
  conforming trace) is prior art for contrast pairs.

## Open questions carried

- Hypothesis rule-interception as an auto-instrumenting layer (stability of the
  hook surface unverified).
- JSONL-on-disk folded to bare array at check time for long-running harnesses
  (current shape: in-memory accumulate, single dump — fine at test scale).
- Alignment-style contrast pairs (pm4py precedent) as a future check output.
