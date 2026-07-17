---
id: 008
title: Compile transition guards into Alloy models (currently comments)
status: open
blocked_by: []
created: 2026-07-17
---

# Compile transition guards into Alloy models

## Why (field finding, ExposeAR behavior checks 2026-07-17)

`archwright-compile-alloy.py` emits transition guards as comments (`-- guard: ...`),
so generated models can take guarded transitions unconditionally. This blocked
rendering ExposeAR's `solved-iff-win-condition` (★★): the model can enter `Solved`
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

ExposeAR `placement-lifecycle.yaml` `solved-iff-win-condition` gains
`alloy: "always (M.current = Solved implies M.zonesCorrect = M.zonesTotal)"`
and PASSes bounded check; removing the guard from the model makes it FAIL.
