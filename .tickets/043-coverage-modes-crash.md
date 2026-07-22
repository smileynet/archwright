---
id: "043"
title: "Coverage modes crash: --coverage on any parseable spec, --trace-coverage on bare-array traces"
status: done
blocked_by: []
---

# Coverage modes crash: --coverage on any parseable spec, --trace-coverage on bare-array traces

Found by the AC decay cleanup (2026-07-22, subagent verification of tickets 030/031, verdicts in `.scratch/ac-cleanup/stage-5.md`; both crashes spot-verified live in main session).

## Why

Tickets 030 (`--trace-coverage`) and 031 (`--coverage`) are `status: done`, but both modes crash on real inputs. Neither has fixture-suite coverage — this is exactly the vacuous-checker failure class the Extension Protocol's "corpus MUST include a violating scenario" rule exists for, applied to tool modes instead of specs.

## Reproduction (verified 2026-07-22 at 21043d3)

1. `--coverage` crashes on ANY directory containing a parseable spec: `load_spec` returns a `(data, kind)` tuple; `coverage_report` calls `.get` on the tuple (`tools/archwright-check.py:390` / `:2100`).
   `python3 tools/archwright-check.py --coverage examples/complete/design/specs --target examples/complete` → `AttributeError: 'tuple' object has no attribute 'get'`
   (Missing specs-dir alone is graceful: exit 2 + message.)
2. `--trace-coverage` crashes on the repo's canonical bare-array trace format: `data.get("spec_id", ...)` on a list (`tools/archwright-check.py:1993`).
   `python3 tools/archwright-check.py --trace-coverage tests/fixtures/trace-strict tests/fixtures/trace-strict` → `AttributeError: 'list' object has no attribute 'get'`
3. Both exit 1 with a traceback instead of honoring the exit-code contract (2 = tool error).

## What to build

1. Fix `coverage_report` to unpack the `(data, kind)` tuple from `load_spec`.
2. Fix `--trace-coverage` to accept the canonical bare-array trace shape (`trace-schema.ts`: input is a bare array of `{event, state, clock}`) — and the enveloped shape if that was ever intended, or reject it loudly.
3. Uncaught exceptions in these modes → exit 2 (tool error), per the exit-code contract.
4. Fixture-suite coverage for BOTH modes, each with at least one gap/violating scenario (non-vacuity rule) — e.g. a spec with no matching trace, a spec-ahead target.

## Acceptance criteria

- [x] `--coverage` runs green against `examples/complete` (and reports gaps against `examples/partial`)
- [x] `--trace-coverage` runs against `tests/fixtures/trace-strict` bare-array traces without crashing
- [x] Crash paths exit 2, not 1-with-traceback
- [x] Suite tests for both modes incl. a gap scenario; AGENTS.md count row updated
- [x] Tickets 030/031 residual unchecked ACs re-verified and checked once fixed

## Out of scope

- New coverage features; this is repair + conformance for what 030/031 claimed.

## Resolution (2026-07-22)

- `coverage_report` unpacks `(data, kind)` from `load_spec`; non-dict/kind-less files skipped (also filters stray .md without frontmatter).
- `trace_coverage_report` is shape-aware per ticket 030's original intent: enveloped dict traces associate by `spec_id`/`spec` field; canonical bare-array traces (trace-schema.ts) associate by filename convention (spec-id slug substring of the trace stem). Orphans = traces claimed by no spec, both shapes.
- Both mode dispatches wrap in exit-2-on-exception (tool error contract); missing specs-dir remains graceful exit 2 + message.
- New fixture `tests/fixtures/coverage/` (bare-array match + enveloped match + deliberate gap + orphan) — 6 suite checks incl. the non-vacuous gap (exit 1) and both 043 crash reproductions. Suite green 140/0/0.
- 030/031 residual ACs re-verified live and checked; AGENTS.md coverage rows updated (BROKEN notes removed), count row 134→140.
