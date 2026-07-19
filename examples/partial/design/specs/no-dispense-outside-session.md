---
kind: constraint
id: no-dispense-outside-session
from_patterns:
  - "pattern:payment-gate"
confidence: "★"
protects_experience: "paid-before-dispense"
user_story: "When the motor runs, it was the payment gate that started it — no code path hands out product without crossing the guard."
check:
  method: grep
  target: "src"
  pattern: "run_motor\\("
  expect: only-in
  only_in: "dispenser.py"
links:
  - target: "constraint:single-balance-writer"
    type: constrains
---

# No Dispense Outside The Session Protocol

## Rule

`run_motor(` appears only inside `src/dispenser.py` — the motor runs solely in
response to a `dispense` command from the payment session. No UI shortcut, no
maintenance hook in application code.

## Rationale

The guarded VEND transition is the single commit point of the exchange. A
second code path to the motor is a free-vend hole that no state-machine check
can see.

Confidence is ★ (heuristic), not ★★: the grep proves `run_motor(` appears
only in the dispenser module, which *approximates* "no other path starts the
motor" — an indirect call (getattr, event bus) would evade it. The evidence
ledger accumulates pass streaks on this check (see the complete state).

## Violations Look Like

```python
# BAD — UI driving hardware directly:
dispenser.run_motor(slot)
```

## Correct Usage

```python
# GOOD — the session commits, the dispenser obeys:
session.handle(Vend(slot))
```
