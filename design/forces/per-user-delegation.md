---
kind: force
id: per-user-delegation
polarity: constraint
hardness: soft
evidence_level: L4
source: "discovery:design-system#D004"
serves: [human-owns-judgment]
---

# Per User Delegation

## Statement

Approval delegation is configured per user/machine and is off by default.

## Who Feels It

the world (platform limits, prior decisions)

## Evidence

- `discovery:design-system#D004`: "approval appetite is per-developer/per-machine, mise.local.toml is gitignored by convention"
