"""archwright check package — modular verification internals.

Modules:
    common      - Shared constants, spec loading, project discovery
    baseline    - Baseline suppression (CK-07) load/discovery
    ledger      - Evidence ledger (ADR 0009) read/write/dedup
    conformance - Check backends: grep, script, semgrep (cycle-breaker)
    alloy       - Alloy behavior/contract checking + probe
    trace       - Trace replay + predicate evaluator
    coverage    - Trace-coverage and spec-coverage reporting
"""
