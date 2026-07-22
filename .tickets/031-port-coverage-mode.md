---
id: 031
title: "Port --coverage mode into archwright-check.py"
status: done
blocked_by: []
---

# Port --coverage mode into archwright-check.py

Add a `--coverage` mode that reports which source files/directories are watched
by specs and which have no spec coverage.

## What to build

Add to `tools/archwright-check.py`:

1. A `coverage_report(specs_dir, target_root)` function that:
   - Scans `specs_dir` for all spec files (constraint, dependency, behavior)
   - Collects each spec's `check.target` path(s)
   - Walks `target_root` for source files (respecting common ignores: node_modules, .git, build, etc.)
   - Reports: covered files/dirs, uncovered files/dirs, coverage percentage
   - Returns exit code: 0 = report generated, 2 = error

2. Dispatch in `main()`:
   ```
   if sys.argv[1] == "--coverage":
       ...
       sys.exit(coverage_report(specs_dir, target_root))
   ```

3. JSON output when `--json` is present.

## Conformance notes

- This is an informational mode (exit 0 even with gaps — it's a report, not a check)
- Place dispatch alongside --trace-coverage (early-exit modes)
- Reuse `load_spec()` and `extract_frontmatter()` for spec reading
- Use `_project_root_for()` pattern for root discovery if --target not given

## Acceptance criteria

- [ ] `python3 tools/archwright-check.py --coverage <specs-dir> [--target <root>]` works
- [ ] Reports covered/uncovered source files clearly
- [ ] --json emits structured output
- [ ] Handles missing target gracefully (exit 2 with message)
- [x] Suite green
