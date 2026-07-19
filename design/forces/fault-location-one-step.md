---
kind: force
id: fault-location-one-step
polarity: constraint
hardness: soft
evidence_level: L4
source: "discovery:wf-all-clear#D005; discovery:wf-all-clear#D005 (alternatives)"
serves: [actionable-without-literacy]
---

# Fault Location One Step

## Statement

When something fails, the affected behavior must be locatable from the front door in one step — the behavior map stays constant and violations pin to it.

## Who Feels It

the world (platform limits, prior decisions)

## Evidence

- `discovery:wf-all-clear#D005`: "the same diagram renders with the affected step/arrow marked ✗ — the behavior map is constant across report states; only the badges change"
- `discovery:wf-all-clear#D005 (alternatives)`: "Diagram only in all-clear (map disappears exactly when orientation matters most)"
