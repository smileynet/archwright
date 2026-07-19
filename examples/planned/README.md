# Snackbox — planned state

**Lifecycle state:** design complete, zero code. The full archwright pipeline
(survey → forces → tensions → resolve → formalize → model → contract → derive)
has run; implementation hasn't started.

## What's here

```
design/
  forces/     fair-exchange (the L4 product desire), paid-before-dispense,
              refund-on-cancel — the root of all provenance
  patterns/   payment-gate — the resolved tension, with evidence and Therefore
  models/     snackbox.yaml (actors, candidates) + snackbox.md (diagrams)
  specs/      purchase-session (behavior, 2 ★★ invariants)
              dispense-command + coin-events (contracts)
              single-balance-writer + no-dispense-outside-session (constraints)
              dispenser-isolation (dependency)
```

## What to notice at this state

1. **Checks run before any code exists.** The behavior spec model-checks NOW
   (Alloy proves both ★★ invariants on the design itself). Try it:

   ```bash
   python3 tools/archwright-check.py examples/planned/design/specs/purchase-session.yaml
   ```

2. **Code-facing checks are `pending`, not passing.** The constraint and
   dependency specs declare `target_status: pending` — their `src/` target
   doesn't exist yet. Check reports them as `coverage.pending`: a declared
   intent that activates the moment code lands, never a silent pass:

   ```bash
   python3 tools/archwright-check.py --static examples/planned/design/specs/
   ```

3. **The provenance chain is complete before implementation.** Every spec
   traces `from_patterns` → `pattern:payment-gate` → `serves: fair-exchange`.
   When a check fails later (see `../partial/`), the violation will carry this
   chain back to the force that owns it.

## Diff against the other states

- `../partial/` = this design + first code, with real violations and a baseline
- `../complete/` = this design + code at quiescence (all checks pass)
