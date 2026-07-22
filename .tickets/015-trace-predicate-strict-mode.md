---
id: 015
title: "Trace predicates: untranslatable atoms silently pass — report SKIP-with-reason instead"
status: done
blocked_by: []
created: 2026-07-18
---

# Trace predicates: untranslatable atoms silently pass

## Problem

`translate_predicate` in `tools/archwright-check.py` returns `True` for any atom it
cannot translate (final fall-through). This is a silent-pass default: a predicate the
translator doesn't understand is treated as satisfied, so guards never reject and
invariants never fire.

**Field evidence (2026-07-18):** numeric comparisons (`<`, `<=`, `>`, `>=`) had no
atom handler — every trace guard and invariant using them passed vacuously since the
tracer bullet. Caught only because the TS trace emitter's Extension Protocol rule-4
corpus required a violating trace to FAIL and it passed instead. The specific operators
are now fixed, but the fall-through default that HID the gap remains: the next
unsupported construct (string methods, arithmetic in comparisons, nested collection
access) will vacuously pass the same way.

Two residual instances of the same default inside the fix itself:
- non-numeric operands to a comparison → `return True`
- the terminal fall-through → `return True`

## What to build

Mirror the Alloy-side taint discipline (ticket 008) at the trace layer:

1. `translate_predicate` returns a third value (or raises a typed signal) for
   "untranslatable" instead of `True`.
2. `check_trace` reports untranslatable predicates as **SKIP-with-reason at the
   invariant/guard granularity**: the check result lists which invariants were
   actually evaluated vs skipped (extend `invariants_checked` with an
   `invariants_skipped: [{id, reason}]` sibling). Guards that are untranslatable
   SKIP the guard (transition accepted, noted) rather than silently passing it.
3. Exit code stays 0 for pass-with-skips (consistent with behavior-check SKIPs),
   but the JSON output makes skips visible so `--json` consumers and the fixture
   suite can assert on them.
4. Conformance (rule 4): a fixture spec with a deliberately-untranslatable
   predicate must produce the SKIP entry — and a violating trace against a
   TRANSLATABLE predicate must still FAIL.

## Acceptance criteria

- [x] Untranslatable invariant predicate → listed in `invariants_skipped` with reason; not in `invariants_checked`
- [x] Untranslatable guard → transition accepted with a skip note in output, never a silent pass
- [x] Fixture suite gains golden checks for both (incl. the still-FAILs case)
- [x] `docs/`/AGENTS.md check-output contract (CK-03 schema) updated if the JSON shape grows a field

## Context

- `.memory/lessons/trace-predicate-vacuity.md` — the incident record
- Ticket 008 — the Alloy-side precedent (taint-based SKIP)
- Second vacuous-checker catch by a rule-4 corpus (first: transition-less Alloy models, 2026-07-17)
