---
kind: force
id: paid-before-dispense
polarity: constraint
hardness: hard
evidence_level: L1
source: "operator economics"
serves: [fair-exchange]
---

# Paid Before Dispense

## Statement

The dispenser never runs unless the session balance covers the selected item's price.

## Who Feels It

The operator's ledger. Every free vend is a direct loss, and a bug that gives product away is exploited within hours of discovery (★★ class — this must be mechanically checkable).

## Evidence

- L1 (observable): a vend with balance < price is directly visible in reconciliation — stock down, cash box unchanged.
- The inverse failure (money kept, nothing dispensed) is the customer-facing half of the same invariant; both reduce to "dispense happens exactly when payment covers price".
