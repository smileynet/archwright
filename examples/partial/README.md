# Snackbox — partial state

**Lifecycle state:** implementation underway. Same design as `../planned/`
(plus two specs derived after code began), first code in `src/`, and the
checks now have something real to say.

## What's here beyond planned/

```
src/
  payment_session.py   the authority — clean
  dispenser.py         DELIBERATE DEFECT: settles the balance itself
  kiosk_ui.py          KNOWN DEBT: bench-test dispenser import (baselined)
design/specs/
  ui-no-hardware-import.md      new since planned (derived after code began)
  hardware-no-session-import.md new since planned; still pending (no src/hardware yet)
.archwright-baseline.json       the known debt, as aw/v1 fingerprints
```

## Run the checks

```bash
python3 tools/archwright-check.py --static examples/partial/design/specs
```

Expected picture (exit 1 — the run FAILS on the new violations only):

| Spec | Result | Why |
|------|--------|-----|
| `single-balance-writer` | **FAIL** (error, escalate) | `dispenser.py:24` assigns the balance |
| `dispenser-isolation` | **FAIL** (error, escalate) | same line — the dispenser knows about money |
| `ui-no-hardware-import` | warning, `baselined: true` | the bench-test import is recorded debt |
| `no-dispense-outside-session` | pass | `run_motor(` stays inside the dispenser |
| `hardware-no-session-import` | pending | `src/hardware/` doesn't exist yet |

## What to notice at this state

1. **One defect, two specs.** `dispenser.py:24` violates both the constraint
   and the dependency rule — the check output carries each violation's own
   provenance chain (`from_pattern: payment-gate`, `from_force:
   paid-before-dispense` / `fair-exchange`) so pass-up can route them.
2. **Baseline ≠ waiver.** The baselined warning KEEPS `escalate: true` — a
   ★★ violation never gets a back door (CK-07); it just stops failing the
   build while it's known debt. `remaining_delta: 2` is the number being
   driven to zero.
3. **Pending activates by existence.** The hardware spec was written BEFORE
   its module; the moment `src/hardware/` lands, the check runs (see
   `../complete/`).
4. **The behavior spec still passes** — the design didn't regress; the code
   did:

   ```bash
   python3 tools/archwright-check.py examples/partial/design/specs/purchase-session.yaml
   ```

## The fix

`../complete/` is the after picture: the dispenser line and the UI import are
gone, `src/hardware/` exists, every check passes, and the baseline entry has
been ratcheted away.
