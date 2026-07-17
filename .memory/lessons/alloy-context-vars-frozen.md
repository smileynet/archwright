# Context vars are frozen in generated Alloy models

One-line: guards/actions don't compile — `alloy:` expressions over context vars get checked against a model where they cannot change.

**Date:** 2026-07-17 · **Source:** Alloy wiring session

`archwright-compile-alloy.py` emits guards as comments and frame-freezes all
context variables. `alloy:` expressions must reference `M.current` + PascalCase
state sigs only; the compiler warns on context-var references. Lifting this
requires compiling guards/actions (future work).
