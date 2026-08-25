---
id: "097"
title: "Split archwright-check.py into modules under tools/check/"
status: in_progress
blocked_by: []
priority: high
---

# Split archwright-check.py into modules under tools/check/

## Context

`tools/archwright-check.py` was 2,643 lines (post-096 argparse migration) doing
≥10 distinct jobs. Wide blast radius per change; the suite catches regressions
but the monolith taxes evolution and onboarding.

## Progress (2026-08-24)

Steps 1–4 completed and pushed. Suite green 165/0/0 at each step.

| Step | Module | LOC | Status |
|------|--------|-----|--------|
| 1 | `check/common.py` | 152 | ✓ Done |
| 2 | `check/baseline.py` | 35 | ✓ Done |
| 3 | `check/ledger.py` | 161 | ✓ Done |
| 4 | `check/coverage.py` | 225 | ✓ Done |
| 5 | `check/conformance.py` | ~450 | Next |
| 6 | `check/alloy.py` | ~320 | Pending |
| 7 | `check/trace.py` | ~550 | Pending |

**Current state:** check.py at 2,109 LOC (20% reduction). Target: ≤1,057 (60%).

## Remaining work — proposal for steps 5–7

### Step 5: `check/conformance.py` — the cycle-breaker (~450 LOC)

Extract functions (current line numbers in check.py):
- `_find_bash` (~28 LOC)
- `_include_match` (~18 LOC)
- `_python_grep` (~61 LOC)
- `_check_grep` (~156 LOC)
- `_check_script` (~45 LOC)
- `_check_semgrep` (~133 LOC)
- `check_conformance` (~42 LOC)
- Constants: `_SKIP_DIRS`, `_LINE_COMMENT`

**Imports needed:** `from check.common import SCRIPT_DIR, _EVIDENCE_CAP, _fingerprint_base, _project_root_for`

**Why this is the cycle-breaker:** Currently `check_contract` (alloy domain)
calls `check_conformance` (backend domain), while `check_file` (dispatch)
calls `check_behavior`/`check_contract`. By isolating conformance into its own
module, alloy.py imports from conformance.py — no reverse dep needed.

**Risk:** Medium. These functions use `subprocess.run` for grep/script/semgrep.
Complex include-glob logic in `_python_grep`. But interfaces are clean — each
takes a check block + returns results list.

### Step 6: `check/alloy.py` (~320 LOC)

Extract functions:
- `_find_alloy_jar` (~15 LOC)
- `check_behavior` (~129 LOC)
- `parse_alloy_verdicts` (~20 LOC) — **must keep tombstone re-export in check.py** for the ticket-096 fixture test
- `_alloy_field_name` (~5 LOC)
- `_check_structural_invariants` (~104 LOC)
- `check_contract` (~25 LOC via dispatch)
- `probe_behavior` (~73 LOC)

**Imports needed:** `from check.common import SCRIPT_DIR, _fingerprint_base, load_spec, _project_root_for` + `from check.conformance import check_conformance`

**Risk:** Medium. `check_behavior` shells out to Java (Alloy jar). The
`_check_structural_invariants` function loads a YAML schema from SCRIPT_DIR.
`check_contract` bridges alloy + conformance (the former cycle — now clean
since conformance is a separate import).

### Step 7: `check/trace.py` (~550 LOC)

Extract functions:
- `_find_op` (~14 LOC)
- `_split_op` (~16 LOC)
- `Untranslatable` class (~15 LOC)
- `_unquote` (~9 LOC)
- `translate_predicate` (~116 LOC)
- `build_trace_document` (~104 LOC)
- `check_trace` (~305 LOC)

**Imports needed:** `from check.common import _SEVERITY, _expected_for, _code_state, _project_root_for, load_spec` + `from check.ledger import find_evidence_ledger, load_evidence_ledger, record_evidence, write_evidence_ledger` + `from archwright_common import state_events` (via sys.path)

**Risk:** Medium-high. `check_trace` is 305 lines with a nested closure
(`_maybe_record`) and significant internal state. The predicate evaluator
(`translate_predicate`) is self-contained but large (116 LOC). The `state_events`
import from `archwright_common.py` needs the same sys.path insert the CLI entry
currently does.

### Execution discipline (same as steps 1–4)

- One module per commit
- `mise run test` → 165/0/0 after each extraction
- If suite breaks and fix isn't obvious in 10 min → revert, document, deliver partial
- Tombstone re-export for `parse_alloy_verdicts` in check.py (fixture test compatibility)

## Acceptance criteria

- [x] `tools/check/` package exists with at least 5 extracted modules
- [ ] `archwright-check.py` reduced by ≥60% LOC (from 2,643 → ≤1,057)
- [x] `mise run test` green: 165 passed, 0 failed, 0 skipped
- [x] No flag or exit-code behavior changed (all fixture invocations identical)
- [x] `archwright_common.py` unchanged
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
