---
kind: dependency
id: dispenser-isolation
from_patterns:
  - "pattern:payment-gate"
confidence: "★★"
protects_experience: "fair-exchange"
user_story: "When hardware peripherals evolve independently, the dispenser never grows a secret ear on the coin stream — money knowledge stays with the authority."
allowed:
  - source: "PaymentSession"
    target: "Dispenser"
    type: commands
forbidden:
  - source: "Dispenser"
    target: "CoinAcceptor"
    type: imports
  - source: "Dispenser"
    target: "balance"
    type: reads
check:
  method: grep
  target: "src/dispenser.py"
  pattern: "coin_acceptor|balance"
  expect: absent
links:
  - target: "contract:dispense-command"
    type: enforces
---

# Dispenser Isolation

## Rule

`src/dispenser.py` never mentions the coin acceptor or the balance. Its whole
world is: receive `dispense(slot)`, run the motor, report `dispense_done`.

## Why

MDB-style peripheral isolation: peripherals talk to the controller, never to
each other. A dispenser that reads balance duplicates the payment gate's
decision — and the two decisions WILL disagree one day.

## Allowed

- PaymentSession → Dispenser (commands) — the one sanctioned direction.

## Forbidden

- Dispenser → CoinAcceptor (imports) — no peripheral cross-talk.
- Dispenser → balance (reads) — dispensing decisions belong to the gate.
