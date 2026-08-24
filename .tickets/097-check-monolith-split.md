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

## Code Analysis (2026-08-23)

Function-level analysis reveals 5 natural extraction boundaries with low
cross-module coupling:

| Module | Functions | LOC | External deps |
|--------|-----------|-----|---------------|
| **trace.py** | `Untranslatable`, `_unquote`, `translate_predicate`, `_find_op`, `_split_op`, `build_trace_document`, `check_trace` | ~549 | `_fingerprint_base`, ledger functions, `_code_state` |
| **backends.py** | `_find_bash`, `_include_match`, `_python_grep`, `_check_grep`, `_check_script`, `_check_semgrep` | ~441 | `_fingerprint_base`, project_root |
| **coverage.py** | `trace_coverage_report`, `coverage_report` | ~217 | `load_spec`, `extract_frontmatter` |
| **alloy.py** | `_find_alloy_jar`, `check_behavior`, `parse_alloy_verdicts`, `_alloy_field_name`, `probe_behavior`, `_check_structural_invariants` | ~316 | `_fingerprint_base`, YAML schema |
| **ledger.py** | `_fingerprint_base`, `_split_evidence`, `_find_up`, `find_baseline`, `load_baseline`, `find_evidence_ledger`, `load_evidence_ledger`, `_event_identity`, `record_evidence`, `write_evidence_ledger` | ~238 | none (leaf module) |

**Total extractable: ~1,761 LOC (67% of file)**

Remaining in check.py (~882 LOC): `_git_changed_files`, `_spec_affected`,
`_code_state`, `extract_frontmatter`, `load_spec`, `check_conformance`,
`_first_pattern`, `_extract_section`, `_expected_for`, `enrich_results`,
`format_result`, `check_file`, `build_document`, `_CheckParser`,
`_build_check_parser`, `main`.

## Proposed execution order (risk-ordered: lowest risk first)

### Phase 1: Leaf modules (zero reverse deps)

1. **`tools/check/ledger.py`** — fingerprints + evidence + baseline.
   Zero callers outside check.py. Pure data manipulation. Safest first extraction.

2. **`tools/check/coverage.py`** — both coverage report modes.
   Self-contained dispatch targets (called from main, return exit codes).
   Only need `load_spec` and `extract_frontmatter` imported back from check.py.

### Phase 2: Backend extraction (moderate coupling)

3. **`tools/check/backends.py`** — grep/script/semgrep checkers.
   Called by `check_conformance` (which stays in check.py). Need
   `_fingerprint_base` from ledger.py. Clean interface: each takes a check
   block + returns results.

### Phase 3: Complex modules (higher coupling)

4. **`tools/check/alloy.py`** — behavior checking + probe + contract alloy.
   Needs `_fingerprint_base`, `_find_alloy_jar`, alloy-runtime.json. The probe
   function is called from main as an early-return mode.

5. **`tools/check/trace.py`** — trace replay.
   Most complex extraction: `translate_predicate` is 116 LOC with the
   `Untranslatable` class; `check_trace` is 305 LOC that uses evidence/ledger
   functions. Highest risk but highest LOC payoff.

### Stop conditions

- If suite breaks during a phase and the fix isn't obvious within 10 min → revert that phase, document why, deliver partial
- If a circular import emerges → resolve by moving the shared function to a `tools/check/common.py` (not `archwright_common.py` which stays untouched)

## What to build

Create `tools/check/` as a Python package. Each module gets the functions
listed above, with imports adjusted. `archwright-check.py` becomes the CLI
entry point importing from the package.

**Import strategy:** `tools/check/` is NOT on `sys.path` by default (scripts
in `tools/` add their own directory). The CLI entry point will do:
```python
from check.ledger import find_baseline, load_baseline, ...
from check.backends import _check_grep, _check_script, _check_semgrep
from check.alloy import check_behavior, probe_behavior, parse_alloy_verdicts
from check.trace import check_trace, translate_predicate
from check.coverage import trace_coverage_report, coverage_report
```

This works because `tools/` is on the path (the script's own directory) and
`tools/check/` is a package within it.

## Acceptance criteria

- [ ] `tools/check/` package exists with at least 3 extracted modules
- [ ] `archwright-check.py` reduced by ≥40% LOC (from 2,643 → ≤1,586)
- [ ] `mise run test` green: 165 passed, 0 failed, 0 skipped
- [ ] No flag or exit-code behavior changed (all fixture invocations identical)
- [ ] `archwright_common.py` unchanged
- [ ] No circular imports (each module imports only from check.* or stdlib)
- [ ] Scope check: changes limited to `tools/archwright-check.py`, `tools/check/`,
      this ticket, and AGENTS.md if ownership table needs updating

## Validation criteria

- `mise run test` → 165/0/0
- `python3 tools/archwright-check.py --help` → same output as before
- `python3 tools/archwright-check.py --static examples/planned/design/specs` → same output
- `python3 tools/archwright-check.py --probe examples/planned/design/specs/purchase-session.yaml` → same output
- `wc -l tools/archwright-check.py` ≤ 1,586
- `python3 -c "from check import ledger, backends, alloy, trace, coverage"` succeeds (from tools/ dir)
