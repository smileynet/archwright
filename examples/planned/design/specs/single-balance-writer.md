---
kind: constraint
id: single-balance-writer
from_patterns:
  - "pattern:payment-gate"
confidence: "★★"
protects_experience: "fair-exchange"
user_story: "When money moves, one component decides — the customer's balance has exactly one writer of truth."
check:
  method: grep
  target: "src"
  target_status: pending    # planned state: no code yet — activates when src/ exists
  pattern: "\\.balance\\s*=(?!=)"
  expect: only-in
  only_in: "payment_session.py"
links:
  - target: "behavior:purchase-session"
    type: constrains
---

# Single Balance Writer

## Rule

Only `PaymentSession` (src/payment_session.py) assigns `.balance`. Every other
component reads it or raises events that the session applies.

## Rationale

The payment gate's ★★ invariant (`paid-when-dispensing`) is checked on the
session state machine. That check is only meaningful if the state machine is
the ONLY place balance changes — N writers reintroduce the races the pattern
exists to eliminate.

## Violations Look Like

```python
# BAD — any file except payment_session.py:
session.balance = session.balance - price
```

## Correct Usage

```python
# GOOD — raise the event; the session is the authority:
session.handle(CoinInserted(amount))
```
