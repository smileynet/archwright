# Trace predicates silently passed numeric comparisons (vacuous)

`translate_predicate` in archwright-check.py had atoms for `==`/`!=`/`in {}` but NO
numeric comparisons — any trace guard or invariant using `<`, `<=`, `>`, `>=` fell
through to `return True`. Every trace check with a capacity/range predicate passed
vacuously since the tracer bullet.

**Caught by:** Extension Protocol rule 4 — the TS trace emitter's conformance corpus
required a violating trace to FAIL; it passed instead (2026-07-18). Second time a
deliberately-violating fixture exposed a vacuous checker (first: the Alloy compiler's
transition-less models, 2026-07-17). The rule pays for itself.

**Fix:** numeric comparison atoms (var-to-var + var-to-literal, float coercion,
two-char ops before one-char). Non-numeric operands still fall through open — the
fall-through-True default remains a design smell; a strict mode that reports
untranslatable predicates as SKIP-with-reason would be the durable fix (candidate
ticket).

**Durable fix landed (2026-07-18, ticket 015):** `translate_predicate` is now
three-valued (True/False/`Untranslatable(reason)`, Kleene propagation through
not/and/or/implies; the sentinel raises on bool() so unaudited call sites fail
loudly). `check_trace` reports `invariants_skipped: [{id, reason}]` (sticky —
excluded from `invariants_checked`) and `guards_skipped` (transition accepted
with note). Exit 0 on pass-with-skips; conformance fixture at
`tests/fixtures/trace-strict/` with 5 golden checks incl. the still-FAILs case.
