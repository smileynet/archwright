---
kind: constraint
id: hardware-no-session-import
from_patterns:
  - "pattern:payment-gate"
confidence: "★★"
protects_experience: "fair-exchange"
user_story: "When the coin hardware shim lands, it stays a peripheral — it reports events upward and never reaches into the session authority."
check:
  method: grep
  target: "src/hardware"
  target_status: pending    # partial state: hardware shim not yet implemented
  pattern: "import\\s+payment_session|from\\s+payment_session"
  expect: absent
links:
  - target: "constraint:single-balance-writer"
    type: constrains
---

# Hardware Never Imports The Session

## Rule

Nothing under `src/hardware/` imports `payment_session` — peripherals produce
events; the authority consumes them. The dependency arrow points one way.

## Rationale

Derived AFTER implementation began (this spec exists in the partial and
complete states, not in planned): the first dispenser defect showed how easily
a peripheral grows a reference to the authority. This constraint closes the
same hole for the upcoming coin-acceptor shim BEFORE it is written —
`target_status: pending` declares the intent; the check activates the moment
`src/hardware/` exists.

## Violations Look Like

```python
# BAD — peripheral reaching into the authority:
from payment_session import PaymentSession
```

## Correct Usage

```python
# GOOD — peripheral raises events; wiring happens in main:
self.on_coin(CoinInserted(amount))
```
