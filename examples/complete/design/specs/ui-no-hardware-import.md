---
kind: constraint
id: ui-no-hardware-import
from_patterns:
  - "pattern:payment-gate"
confidence: "★★"
protects_experience: "fair-exchange"
user_story: "When a customer uses the touchscreen, every action travels through the session authority — the UI has no wire of its own to the hardware."
check:
  method: grep
  target: "src/kiosk_ui.py"
  pattern: "import\\s+dispenser"
  expect: absent
links:
  - target: "dependency:dispenser-isolation"
    type: enforces
---

# UI Never Imports Hardware

## Rule

`src/kiosk_ui.py` never imports the dispenser module. The UI raises intents
(`vend`, `cancel`); only the payment session commands hardware.

## Rationale

Same MDB-style isolation as `dependency:dispenser-isolation`, pointed at the
other side of the authority: a UI with a direct hardware wire is a free-vend
path waiting for a maintenance shortcut to ship to production.

## Baseline Note (partial state)

In the partial state this check's one violation — the bench-test
`import dispenser` — is KNOWN DEBT, recorded in `.archwright-baseline.json`.
The check reports it as a warning with `baselined: true` and exit 0; only NEW
violations fail the run. The complete state removes the import, and
`--update-baseline` then deletes the stale entry (the ratchet never adds).

## Violations Look Like

```python
# BAD — UI wired straight to hardware:
import dispenser
```

## Correct Usage

```python
# GOOD — the UI raises the intent; the session decides:
self.session.vend()
```
