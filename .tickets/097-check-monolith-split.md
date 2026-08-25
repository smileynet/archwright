---
id: "097"
title: "Split archwright-check.py into modules under tools/check/"
status: open
blocked_by: []
priority: high
---

# Split archwright-check.py into modules under tools/check/

## Context

`tools/archwright-check.py` is 2,643 lines (post-096 argparse migration) doing
≥10 distinct jobs. Wide blast radius per change; the suite catches regressions
but the monolith taxes evolution and onboarding.

## Analysis (2026-08-24)

Dependency graph analysis revealed:
- **One circular dependency**: alloy ↔ backends (`check_contract` calls
  `check_conformance`; `check_file` calls `check_behavior`/`check_contract`)
- **No mutable module-level state** — all immutable constants, no globals
- **10 module-level constants** used across boundaries (SCRIPT_DIR,
  FINGERPRINT_ALGO, _SEVERITY, etc.)
- **5 shared utility functions** used by 3+ areas (load_spec,
  _project_root_for, extract_frontmatter, _code_state, _expected_for)
- **Single library import of check.py**: the ticket-096 Alloy verdict fixture
  uses `importlib.util.spec_from_file_location` to access
  `parse_alloy_verdicts` — must remain accessible or test updated

**Circular dependency solution**: Extract `check_conformance` + its private
helpers (grep/script/semgrep checkers) into `conformance.py`. Both `alloy.py`
(for contract specs' check sections) and the dispatch layer import from it.
Neither imports the other.

## Module architecture

```
tools/
├── archwright-check.py          # CLI entry point (~500 LOC): parser, main(),
│                                # build_document, git scoping, dispatch
├── archwright_common.py         # UNCHANGED (state_events)
└── check/
    ├── __init__.py              # Package marker (thin — no re-exports needed)
    ├── common.py                # Shared constants + utilities (~200 LOC):
    │                            # SCRIPT_DIR, FINGERPRINT_ALGO, _SEVERITY,
    │                            # _EVIDENCE_CAP, load_spec, extract_frontmatter,
    │                            # _project_root_for, _code_state, _expected_for,
    │                            # _extract_section, _find_up
    ├── baseline.py              # Baseline load/discovery (~90 LOC):
    │                            # _fingerprint_base, _split_evidence,
    │                            # find_baseline, load_baseline, BASELINE_FILENAME
    ├── ledger.py                # Evidence ledger (~170 LOC):
    │                            # find_evidence_ledger, load_evidence_ledger,
    │                            # record_evidence, write_evidence_ledger
    ├── conformance.py           # Check backends — THE CYCLE BREAKER (~450 LOC):
    │                            # _find_bash, _include_match, _python_grep,
    │                            # _check_grep, _check_script, _check_semgrep,
    │                            # check_conformance, _SKIP_DIRS, _LINE_COMMENT
    ├── alloy.py                 # Alloy behavior + contract checking (~320 LOC):
    │                            # _find_alloy_jar, check_behavior,
    │                            # parse_alloy_verdicts, _alloy_field_name,
    │                            # _check_structural_invariants, check_contract,
    │                            # probe_behavior
    ├── trace.py                 # Trace replay (~550 LOC):
    │                            # Untranslatable, _unquote, _find_op, _split_op,
    │                            # translate_predicate, build_trace_document,
    │                            # check_trace
    └── coverage.py              # Coverage reporting (~220 LOC):
                                 # trace_coverage_report, coverage_report
```

**Dependency layering (each module imports only from layers above):**
```
stdlib + yaml + archwright_common
         ↓
    check/common.py
         ↓
    check/baseline.py
         ↓
    check/ledger.py       check/coverage.py
         ↓
    check/conformance.py
         ↓
    check/alloy.py
         ↓
    check/trace.py
         ↓
    archwright-check.py (CLI entry)
```

No circular imports possible — strict downward-only layering.

## Execution plan (git-bisect-friendly: one module per commit, suite green each step)

| Step | Extract | LOC out | Risk | Stop condition |
|------|---------|---------|------|----------------|
| 1 | `check/common.py` | ~200 | Low | Constants + pure utilities, no callers change |
| 2 | `check/baseline.py` | ~90 | Low | Leaf module, only common.py dep |
| 3 | `check/ledger.py` | ~170 | Low | One-way dep on common + baseline |
| 4 | `check/coverage.py` | ~220 | Low | Self-contained dispatch targets |
| 5 | `check/conformance.py` | ~450 | Med | Cycle-breaker — alloy.py will import this |
| 6 | `check/alloy.py` | ~320 | Med | Imports conformance; probe is early-return |
| 7 | `check/trace.py` | ~550 | Med | Largest chunk; needs ledger + common |

**Total extraction: ~2,000 LOC → check.py drops to ~640 LOC (76% reduction)**

Each step: move functions → add tombstone re-exports (temporarily) → update
internal imports → run suite → green → commit → remove tombstone in next step.

## Import strategy

- `tools/` is on `sys.path` (script's own directory) — `import check.common`
  works naturally from `archwright-check.py`
- The ticket-096 fixture test uses `importlib.util.spec_from_file_location` to
  load the file — `parse_alloy_verdicts` must either (a) stay importable from
  the original file via re-export, or (b) test updated to import from
  `check.alloy`. Option (a) is the move+reexport pattern; option (b) is
  cleaner long-term. **Do (a) first for safety, remove in a follow-up.**
- `archwright_common.py` unchanged — `check/trace.py` adds `sys.path` to find
  it, same as the CLI entry does today

## Acceptance criteria

- [ ] `tools/check/` package exists with at least 5 extracted modules
- [ ] `archwright-check.py` reduced by ≥60% LOC (from 2,643 → ≤1,057)
- [ ] `mise run test` green: 165 passed, 0 failed, 0 skipped
- [ ] No flag or exit-code behavior changed (all fixture invocations identical)
- [ ] `archwright_common.py` unchanged
- [ ] No circular imports (verified: `python3 -c "from check import common, baseline, ledger, conformance, alloy, trace, coverage"` from tools/ dir)
- [ ] Dependency layering holds (each module only imports from layers above it)
- [ ] Scope check: changes limited to `tools/archwright-check.py`, `tools/check/`,
      `tools/run-fixture-tests.sh` (if test import path changes), this ticket,
      and AGENTS.md if needed

## Validation criteria

- `mise run test` → 165/0/0 after EVERY extraction step
- `python3 tools/archwright-check.py --help` → same output
- `python3 tools/archwright-check.py --static examples/planned/design/specs` → same
- `python3 tools/archwright-check.py --probe examples/planned/design/specs/purchase-session.yaml` → same
- `wc -l tools/archwright-check.py` ≤ 1,057
- `python3 -c "import sys; sys.path.insert(0,'tools'); from check import common, baseline, ledger, conformance, alloy, trace, coverage; print('OK')"` → OK
- No `from archwright` or `from tools` in any `check/*.py` (only relative `from check.X` or stdlib)
