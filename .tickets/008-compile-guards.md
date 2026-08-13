---
id: "008"
title: Compile transition guards into Alloy models (currently comments)
status: done
blocked_by: []
created: 2026-07-17
closed: 2026-07-17
---

# Compile transition guards into Alloy models

## Resolution (2026-07-17)

Shipped in `archwright-compile-alloy.py`:
- Guard predicates compile into transition preds — translatable subset: enum `==`/`!=`,
  int comparisons (`==`, `!=`, `<`, `>`, `<=` → Alloy `=<`, `>=`), var-to-var,
  `&&`/`and` conjunctions. Alloy int syntax empirically verified against the jar
  before codegen (`plus[a,b]`, `=<`).
- `assign:` maps on transitions (new schema surface, in spec-behavior template):
  int/enum literals, var copy, `var + N` / `var - N` → primed updates replacing
  frame conditions for assigned vars.
- Non-translatable guards/assigns stay comments and TAINT their referenced vars +
  target state; invariants touching tainted elements are skipped with reason via
  `SKIP-INVARIANT:` stdout lines that `archwright-check.py` consumes (skipped
  result, not "no verdict" error). Blanket frozen-var WARN removed — constant
  vars are now legitimately checkable (e.g. `zones_total`).
- Conformance corpus at `tests/fixtures/guarded-counter/` (3 specs), wired into
  the suite (+4 assertions, 35/0/0): guarded PASS, unguarded twin FAILs with
  counterexample (rule 4 violating scenario), opaque-guard twin SKIPs with taint
  reason (rule 1). Vacuity probe run in-session: deliberately-false
  `always M.current != Solved` FAILed, proving Solved reachable under the guard.
- Acceptance case verified with the exact expression from this ticket:
  `alloy: "always (M.current = Solved implies M.zonesCorrect = M.zonesTotal)"`
  PASSes bounded check; removing the guard makes it FAIL.
- Docs: spec-behavior template + derive skill step 4 updated (context vars no
  longer forbidden in `alloy:` expressions).

DemoAR's `placement-lifecycle.yaml` can now carry the invariant — that edit
belongs to the DemoAR lane.

## Why (field finding, DemoAR behavior checks 2026-07-17)

`archwright-compile-alloy.py` emits transition guards as comments (`-- guard: ...`),
so generated models can take guarded transitions unconditionally. This blocked
rendering DemoAR's `solved-iff-win-condition` (★★): the model can enter `Solved`
without `zones_correct == zones_total`, so the assert would spuriously fail against
model weakness rather than design error. The invariant sits prose-only (trace-check
owned) until guards are enforced.

## What to build

- Compile guard predicates over modeled context vars (enum equality, int
  comparison) into the transition preds. Non-translatable guards stay comments
  with a SKIP-with-reason on any invariant that references them (Extension
  Protocol rule 1).
- Var updates on transitions are the sibling gap (e.g., `zones_correct: 0` on
  PROGRESS_RESET) — same treatment.
- Conformance corpus at birth: fixture spec with a guarded transition + an
  invariant provable ONLY with the guard enforced (and a non-vacuity twin).

## Concrete acceptance case

DemoAR `placement-lifecycle.yaml` `solved-iff-win-condition` gains
`alloy: "always (M.current = Solved implies M.zonesCorrect = M.zonesTotal)"`
and PASSes bounded check; removing the guard from the model makes it FAIL.
