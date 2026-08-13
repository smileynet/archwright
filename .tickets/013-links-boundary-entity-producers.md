---
id: "013"
title: "validate-links: accept boundary entities as from_model contract producers (C9)"
status: done
blocked_by: []
created: 2026-07-17
---

# validate-links: accept boundary entities as from_model contract producers

Field-driven (DemoAR run, digest 2026-07-17 "Open" note; root cause confirmed in
DemoVR phase-1 review 2026-07-17): `puzzle-definition.yaml` carries
`from_model: "model:content-authority"` and validate-links FAILs it — but the model
is not wrong. `content-authority` exists in `demoar-actors.yaml` as a
**boundary_entity** (classification: configuration-authority) and is listed in
`contract_candidates` as the producer of puzzle-definition. The validator only
resolves from_model against actors and contract candidates-as-actors, so a
legitimate "configuration authority produces a contract" relationship cannot be
expressed without a false FAIL.

## What to build

- validate-links resolves `from_model:` refs against boundary_entities in addition
  to actors, when the boundary entity is named as a producer in contract_candidates.
- Decide + document whether plain boundary entities (not contract producers) are
  valid from_model targets, or whether that stays an error.
- Second C9 sub-finding from the same digest note: candidate↔spec event-name
  matching (e.g. `placement-verdict` folded into `placement-command` cluster) —
  either support a `folded_into:` annotation or document the convention.

## Acceptance criteria

- [ ] DemoAR `design/` link check passes with from_model pointing at
      content-authority (no spec edit required)
- [x] A from_model ref to a nonexistent id still FAILs (no vacuous acceptance)
- [x] Fixture suite gains a violating scenario that FAILs (conformance-at-birth rule)
- [x] Folded-candidate convention documented or annotated

## Close-out (2026-07-18)

Shipped: producer boundary entities resolve as `from_model` targets; plain
boundary entities FAIL with a precise producer-rule message (decision: an
element that produces nothing has no contract-provenance role); `folded_into:`
annotation supported on candidates (coverage follows the fold; fold + own spec
= double-ownership error; unknown fold target = error). 4 golden checks in the
suite reproduce the exact DemoAR shape (configuration-authority producing
puzzle-definition) — AC 1 verified structurally. **DemoAR itself is not
cloned in this lane** — its `--links` run will pass without spec edits on the
next check in that lane; flag there if it doesn't. Conventions documented in
contract + model skills.
