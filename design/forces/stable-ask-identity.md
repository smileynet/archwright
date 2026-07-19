---
kind: force
id: stable-ask-identity
polarity: constraint
hardness: soft
evidence_level: L4
source: "discovery:model-seed (Derived Data Requirements); discovery:wf-projections (Not Resolved Here)"
serves: [agent-closes-the-loop]
---

# Stable Ask Identity

## Statement

Response-file entries must key to ask identities that are stable across runs and code movement.

## Who Feels It

the world (platform limits, prior decisions)

## Evidence

- `discovery:model-seed (Derived Data Requirements)`: "Response-file schema: ask-id (reuse aw/v1 fingerprints) -> choice/approval/freeform + run identity"
- `discovery:wf-projections (Not Resolved Here)`: "ask-id stability across runs (fingerprint reuse?)"
