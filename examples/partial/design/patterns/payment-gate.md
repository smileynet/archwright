---
kind: pattern
id: payment-gate
name: "Payment Gate"
scale: verbs-interactions
confidence: "★★"
status: active
serves: [fair-exchange]
context: []
completed_by: []
resolves_into:
  - "behavior:purchase-session"
  - "contract:dispense-command"
  - "contract:coin-events"
  - "constraint:single-balance-writer"
  - "constraint:no-dispense-outside-session"
  - "dependency:dispenser-isolation"
---

# Payment Gate

## Problem

**The customer wants to browse, insert coins, and change their mind freely — but the moment product moves, the exchange must be irreversibly fair.**

## Context

A Snackbox kiosk: coin acceptor (hardware), one dispenser motor per shelf slot, a small touchscreen UI. One customer session at a time.

## Forces

- **Desire:** Fair exchange — snack or full refund, never neither (`fair-exchange`, L4).
- **Constraint (hard):** Never dispense with balance below price (`paid-before-dispense`, ★★).
- **Desire:** Cancel returns the full balance any time before dispensing starts (`refund-on-cancel`).

## Evidence

- Prior art: payment gateways separate *authorization* from *capture* — money is committed only at an explicit commit point, refundable before it (Stripe docs, 2024; the two-phase shape is decades older in card processing).
- Prior art: vending controllers in the MDB protocol family route all payment events through a single VMC (vending machine controller) — peripherals never talk to each other directly (NAMA MDB/ICP spec, v4.2).
- Rejected alternative: letting the UI drive the dispenser directly on "balance looks sufficient" — races the coin acceptor's async events; the invariant then lives in every caller instead of one authority.
- Mechanism argument: a single commit point (one state transition guarded by `balance >= price`) makes the ★★ invariant checkable on the state machine itself, not on scattered call sites.

## Therefore

Route every coin event and every dispense decision through ONE payment-session
authority:

1. A `payment-session` actor owns `balance` and the session state machine
   (`idle → accepting → dispensing → idle`). It is the ONLY writer of
   `balance`.
2. Dispensing is entered by exactly one guarded transition:
   `VEND (balance >= price)` — the payment gate itself.
3. The dispenser is a dumb servant: it accepts a `dispense` command carrying
   the slot, and reports `dispense_done`. It never reads coins, never touches
   balance.
4. `CANCEL` in `accepting` refunds the full balance and returns to `idle`.
   Once `dispensing` is entered, cancel is no longer offered (the exchange is
   committed — refund of a dispensed item is an operator workflow, not a
   machine state).

## Verification

- ★★ mechanical: the `purchase-session` behavior spec model-checks
  `paid-when-dispensing` and `refund-leaves-nothing-behind` (Alloy).
- ★★ mechanical: `single-balance-writer` and `dispenser-isolation` grep-check
  that the code keeps balance writes and coin reads inside the authority.
