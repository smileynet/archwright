---
id: "097"
title: "Split archwright-check.py into modules under tools/check/"
status: in_progress
blocked_by: []
priority: high
---

# Split archwright-check.py into modules under tools/check/

## Progress

| Step | Module | LOC | Status |
|------|--------|-----|--------|
| 1 | `check/common.py` | 152 | ✓ Done |
| 2 | `check/baseline.py` | 35 | ✓ Done |
| 3 | `check/ledger.py` | 161 | ✓ Done |
| 4 | `check/coverage.py` | 225 | ✓ Done |
| 5 | `check/conformance.py` | ~450 | Next |
| 6 | `check/alloy.py` | ~320 | Pending |
| 7 | `check/trace.py` | ~550 | Pending |

**Current:** check.py at 2,109 LOC (from 2,643). Target: ≤1,057.

## Detailed extraction plan for steps 5–7

### Step 5: `check/conformance.py` (lines 434–916 + `_first_pattern` at 917)

**Functions to move:**
- `check_conformance` (42 LOC) — dispatches to grep/script/semgrep
- `_find_bash` (14 LOC) — bash discovery (shutil.which + fallbacks)
- `_include_match` (18 LOC) — glob matching for include filters
- `_python_grep` (61 LOC) — pure-Python grep with comment stripping
- `_check_grep` (156 LOC) — grep/bash-grep + Python-grep backend
- `_check_script` (45 LOC) — script execution backend
- `_check_semgrep` (133 LOC) — semgrep backend with temp rule files
- `_first_pattern` (3 LOC) — trivial helper, moves into this module
- Constants: `_SKIP_DIRS` (set), `_LINE_COMMENT` (dict)

**Import block:**
```python
import fnmatch, json, os, re, subprocess, sys, yaml
from pathlib import Path
from check.common import _EVIDENCE_CAP, _project_root_for
```

**Key findings from review:**
- No SCRIPT_DIR or __file__ references — all paths use project_root
- All subprocess calls specify `cwd=str(project_root)` — location-independent
- `_first_pattern` is the only external reference (3-line trivial — move it in)
- `_fingerprint_base` is NOT needed (fingerprints are added by enrich_results in the dispatch layer, not in the backends)

**Risk:** Low. Self-contained subprocess wrappers with clean interfaces.

### Step 6: `check/alloy.py` (lines 135–433 + `probe_behavior` at 1729)

**Functions to move:**
- `_find_alloy_jar` (15 LOC) — jar discovery (env, script-relative, legacy path)
- `check_behavior` (129 LOC) — compile to Alloy + run solver
- `parse_alloy_verdicts` (20 LOC) — regex verdict extraction
- `_alloy_field_name` (5 LOC) — slug→camelCase for assertion names
- `_check_structural_invariants` (104 LOC) — contract structural checking
- `check_contract` (25 LOC) — bridges structural + conformance
- `probe_behavior` (73 LOC) — non-vacuity probe

**Import block:**
```python
import os, re, subprocess, sys, yaml
from pathlib import Path
from check.common import SCRIPT_DIR, _fingerprint_base, load_spec
from check.conformance import check_conformance
from archwright_common import state_events
```

**Key findings from review:**
- SCRIPT_DIR resolves 3 paths: alloy jar, compile-alloy.py, compile-contract-alloy.py
- check.common.SCRIPT_DIR = `Path(__file__).resolve().parent.parent` (= tools/) — correct for all 3
- `check_contract` → `check_conformance`: one-way dep, cycle broken by design
- `parse_alloy_verdicts` needs tombstone re-export in check.py for 096 fixture
- `probe_behavior` uses `state_events` (from archwright_common) + `check_behavior` (same module) + `load_spec` (common)

**Risk:** Medium. Path resolution is the main concern — SCRIPT_DIR definition in common.py must resolve to `tools/` not `tools/check/`. Already verified: `Path(__file__).resolve().parent.parent` from common.py = `tools/`.

### Step 7: `check/trace.py` (lines 1018–1596)

**Functions to move:**
- `_find_op` (14 LOC) — operator position search
- `_split_op` (16 LOC) — operator split respecting parens
- `Untranslatable` class (15 LOC) — three-valued sentinel
- `_unquote` (9 LOC) — enum literal quote stripping
- `translate_predicate` (116 LOC) — predicate evaluator
- `build_trace_document` (104 LOC) — CK-03 document construction
- `check_trace` (305 LOC) — full trace replay

**Import block:**
```python
import json, re, sys, yaml
from pathlib import Path
from check.common import _SEVERITY, _expected_for, _code_state, _project_root_for, load_spec
from check.ledger import find_evidence_ledger, load_evidence_ledger, record_evidence, write_evidence_ledger
from archwright_common import state_events
```

**Key findings from review:**
- Predicate engine (Untranslatable + translate_predicate + helpers) has zero
  external consumers — fully self-contained cluster
- `check_trace` has 3 nested closures capturing 7 mutable locals — safe for
  mechanical move (closures stay intact)
- `archwright_common` import works because the entry point sets up sys.path
  before importing anything from check/ — no additional path manipulation needed
- Only one external call site: `sys.exit(check_trace(...))` in main

**Risk:** Medium. Largest extraction but cleanly self-contained. The nested
closures are the complexity, not the module boundary.

### After all 3 steps: check.py retains (~685 LOC)

- `_git_changed_files`, `_spec_affected` (git scoping, CK-19)
- `enrich_results`, `format_result` (result enrichment + formatting)
- `check_file` (dispatch: loads spec → routes to alloy/conformance by kind)
- `build_document` (assembles the CK-03 output document)
- `_CheckParser`, `_build_check_parser`, `main` (CLI entry)
- Import block for all check/ modules

**Final LOC estimate:** ~685 (74% reduction from 2,643)

## Acceptance criteria

- [x] `tools/check/` package exists with at least 5 extracted modules (4 done, need 1 more minimum)
- [ ] `archwright-check.py` reduced by ≥60% LOC (from 2,643 → ≤1,057)
- [x] `mise run test` green: 165 passed, 0 failed, 0 skipped
- [x] No flag or exit-code behavior changed
- [x] `archwright_common.py` unchanged
- [ ] No circular imports verified
- [ ] Dependency layering holds
- [ ] Scope check passes

## Validation criteria

- `mise run test` → 165/0/0 after EVERY extraction step
- `python3 tools/archwright-check.py --help` → same output
- `python3 tools/archwright-check.py --static examples/planned/design/specs` → same
- `python3 tools/archwright-check.py --probe examples/planned/design/specs/purchase-session.yaml` → same
- `wc -l tools/archwright-check.py` ≤ 1,057
- `python3 -c "import sys; sys.path.insert(0,'tools'); from check import common, baseline, ledger, conformance, alloy, trace, coverage; print('OK')"` → OK
