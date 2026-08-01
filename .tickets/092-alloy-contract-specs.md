---
id: 092
title: "Alloy structural verification for contract specs (data model invariants)"
status: open
blocked_by: []
---

# Alloy structural verification for contract specs

## Context

Hillel Wayne demonstrates Alloy's sweet spot: static structure verification —
data models, access control, transitive relationships. His `readable_by` example
(finding non-transitive access in a resource hierarchy) is structurally identical
to archwright contract specs: typed schemas with relationships and constraints.

Currently contract specs only get schema validation (validate.py). Structural
invariants on data models (e.g., "no circular ownership," "every event has
exactly one authority actor," "all contract fields are reachable from a root")
could be Alloy-checked like behavior specs already are.

## What to build

Extend `archwright-compile-alloy.py` (or a new `compile-contract-alloy.py`) to:

1. Read a contract spec (kind: contract)
2. Translate its schema (types, relationships, constraints) to Alloy signatures
3. Translate its `invariants:` section to Alloy assertions
4. Run the model checker — counterexample = structural bug in the data model

## Example mapping

```yaml
# contract spec
kind: contract
id: resource-access
schemas:
  Resource:
    fields:
      readable_by: [User]
      parent: Resource?
invariants:
  - id: transitive-read
    predicate: "user in resource.readable_by implies user in resource.children.readable_by"
```

→ Alloy:
```alloy
sig Resource { readable_by: set User, parent: lone Resource }
sig User {}
assert TransitiveRead {
  all u: User, r: Resource |
    u in r.readable_by implies all c: r.~parent | u in c.readable_by
}
check TransitiveRead for 5
```

## Acceptance criteria

- [ ] Contract spec schema supports `structural_invariants:` section (grill 2026-08-01: coexists with `check:`)
- [ ] At least one contract spec compiles to Alloy and checks successfully
- [ ] Counterexample generation works (planted bug produces visual output)
- [ ] Integrated into `archwright-check.py` dispatch (kind: contract + has structural_invariants → Alloy path)
- [ ] Both paths run in one invocation: structural_invariants (Alloy) + check (grep/semgrep)
- [ ] Suite green
