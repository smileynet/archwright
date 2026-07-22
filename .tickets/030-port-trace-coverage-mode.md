---
id: 030
title: "Port --trace-coverage mode into archwright-check.py"
status: done
blocked_by: []
---

# Port --trace-coverage mode into archwright-check.py

Add a `--trace-coverage` mode that reports which behavior spec scenarios have
trace files covering them and which don't.

## What to build

Add to `tools/archwright-check.py`:

1. A `trace_coverage_report(specs_dir, traces_dir)` function that:
   - Scans `specs_dir` for behavior specs (kind: behavior)
   - Scans `traces_dir` for .trace.json files
   - Matches traces to specs by filename convention or explicit `spec:` field
   - Reports: covered scenarios, uncovered scenarios, orphan traces
   - Returns exit code: 0 = all covered, 1 = gaps exist, 2 = error

2. Dispatch in `main()`:
   ```
   if sys.argv[1] == "--trace-coverage":
       ...
       sys.exit(trace_coverage_report(sys.argv[2], sys.argv[3]))
   ```

3. JSON output when `--json` is present (same CK-03 document shape principle).

## Conformance notes

- Place the dispatch BEFORE the general arg parsing loop (same pattern as
  `--trace` and `--probe` early-exit modes)
- Follow the `check_trace()` pattern for early return from main
- Add to the usage string in the `main()` function
- Do NOT add to the AGENTS.md flags note yet (ticket 033 handles docs)

## Acceptance criteria

- [x] `python3 tools/archwright-check.py --trace-coverage <specs-dir> <traces-dir>` works
- [x] Reports covered/uncovered/orphan clearly
- [x] Exit 0 when fully covered, 1 when gaps, 2 on error
- [x] --json emits structured output
- [x] Suite green
