---
id: "097"
title: "Split archwright-check.py into modules under tools/check/"
status: open
blocked_by: []
priority: high
---

# Split archwright-check.py into modules under tools/check/

## Context

`tools/archwright-check.py` is 2,636 lines doing ≥10 distinct jobs:
fingerprinting, evidence ledger, git scoping, grep/script/semgrep backends,
trace replay, Alloy compilation+verdict, coverage reporting, PBT dispatch.
Wide blast radius per change — the suite catches regressions but the monolith
taxes evolution and onboarding.

Surfaced in deep-dive review (096). Extracted as its own ticket because the
split is the highest-value structural improvement and deserves focused attention.

## What to build

Mechanical extraction into modules under `tools/check/` (package with
`__init__.py`). Proposed module boundaries:

- `tools/check/__init__.py` — re-exports for backward compat
- `tools/check/fingerprints.py` — aw/v1 fingerprint generation
- `tools/check/ledger.py` — evidence ledger read/write/dedup
- `tools/check/scoping.py` — git-based `--changed-only` logic
- `tools/check/backends/` — grep, script, semgrep check backends
- `tools/check/trace.py` — trace replay + strict-mode
- `tools/check/alloy.py` — Alloy compilation, verdict parsing, probe
- `tools/check/coverage.py` — `--trace-coverage` and `--coverage`
- `tools/check/pbt.py` — PBT harness generation + dispatch
- `tools/check/baseline.py` — baseline suppression + ratchet

The CLI entry point (`archwright-check.py`) becomes a thin dispatcher importing
from the package. `archwright_common.py` stays untouched.

**Constraints:**
- No behavior change: `mise run test` stays green at 164/0/0
- No flag or exit-code semantics change
- Partial delivery acceptable — extract what's clean, document what wasn't
- If a boundary proves risky mid-work, stop and record why in Resolution

## Acceptance criteria

- [ ] `tools/check/` package exists with at least 3 extracted modules
- [ ] `archwright-check.py` reduced by ≥40% LOC (imports from `tools/check/`)
- [ ] `mise run test` green: 164 passed, 0 failed, 0 skipped
- [ ] No flag or exit-code behavior changed (all fixture invocations identical)
- [ ] `archwright_common.py` unchanged
- [ ] Scope check: changes limited to `tools/archwright-check.py`, `tools/check/`, this ticket, and AGENTS.md tool ownership table if needed

## Validation criteria

- Run `mise run test` → 164/0/0
- `python3 tools/archwright-check.py --static examples/planned/design/specs` → same output as before split
- `python3 tools/archwright-check.py --probe examples/planned/design/specs/turn-lifecycle-behavior.yaml` → same output
- `wc -l tools/archwright-check.py` shows ≥40% reduction
