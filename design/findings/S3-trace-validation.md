# Spike S3 Findings: Trace Validation

**Date:** 2026-07-10
**Tool built:** `archwright-trace-validate` (bash + Node, uses yq for YAML)
**Spec tested:** behavior:deployment-lifecycle (15 states, oci-vercel)
**Traces tested:** 3 (1 valid, 2 violations)

---

## Key Finding

A **92-line bash/Node script** (no dependencies beyond `yq` and `node`) validates JSON traces against YAML behavior specs. It catches both invalid transitions (event not allowed from state) and invalid targets (event goes to wrong state). No formal methods backend needed for flat FSMs.

## Results

| Trace | Expected | Actual | Violation detected |
|-------|----------|--------|-------------------|
| happy-path.json (8 events) | pass | ✅ pass | — |
| skip-database-violation.json | fail | ✅ fail | `RUNTIME_DEPLOYED → healthy` (should → `binding_preview_url`) |
| promote-from-failed-violation.json | fail | ✅ fail | `PROMOTE` not allowed in `failed` state |

## Validator Design

**Input:** YAML behavior spec + JSON trace file
**Process:** Walk trace events, check each against spec's `states[state].on[event].target`
**Output:** Structured JSON with violations (event_index, kind, allowed alternatives, message)
**Performance:** Instant (<100ms for 8-event traces)

## Trace Format (validated)

```json
{
  "spec_id": "deployment-lifecycle",
  "initial_state": "queued",
  "source": "test:happy-path-deploy-with-database",
  "events": [
    { "state": "queued", "event": "DETECT_APP", "next_state": "detecting_app" }
  ]
}
```

Minimal: 3 required fields per event (state, event, next_state). Optional: context (variable updates), ts (timestamp).

## Instrumentation Cost Assessment

To emit traces from a real test suite:
```typescript
// ~5 lines per state machine:
const trace: TraceEvent[] = [];
controlPlane.on("statusChange", (from, to, event) => {
  trace.push({ state: from, event, next_state: to });
});
// After test: write trace to JSON file
```

Estimated cost: **5-10 lines per instrumented state machine** (even lower than the "~20 lines" decision estimate).

## What This Catches That Other Methods Can't

| Method | Catches |
|--------|---------|
| grep/semgrep | Structural patterns (imports, object shapes, catch blocks) |
| AI review | Semantic drift (intent misalignment, edge case reasoning) |
| **Trace validation** | **Behavioral conformance** (actual transitions match declared FSM) |

This is the only method that validates **runtime behavior** against a spec. Grep checks code structure; trace validation checks what the code *actually does* when it runs.

## Limitations

- Requires test instrumentation (tests must emit traces)
- Only validates flat FSMs (no nested/parallel state checking yet)
- Guard evaluation not implemented (can't check `guard.predicate` — just transition validity)
- Needs traces from real tests (not useful without test coverage of the state machine)

## Decision

**ADOPT** — add `archwright-trace-validate` to tools. Extend `archwright-check` to support `check.method: trace` for behavior specs. Next step: instrument oci-vercel's deployment test suite to emit traces and validate against the spec automatically.

## Future Extensions

1. Guard evaluation (parse predicate, check against context values in trace)
2. Invariant checking (verify predicates hold at every state in the trace)
3. Coverage reporting (which states/transitions were exercised by the trace)
4. Contrast pair generation (when violation found, show nearest valid trace)
