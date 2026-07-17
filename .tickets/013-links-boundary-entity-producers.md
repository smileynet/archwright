---
id: 013
title: "validate-links: accept boundary entities as from_model contract producers (C9)"
status: open
blocked_by: []
created: 2026-07-17
---

# validate-links: accept boundary entities as from_model contract producers

Field-driven (ExposeAR run, digest 2026-07-17 "Open" note; root cause confirmed in
AwsArchVR phase-1 review 2026-07-17): `puzzle-definition.yaml` carries
`from_model: "model:content-authority"` and validate-links FAILs it — but the model
is not wrong. `content-authority` exists in `exposear-actors.yaml` as a
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

- [ ] ExposeAR `design/` link check passes with from_model pointing at
      content-authority (no spec edit required)
- [ ] A from_model ref to a nonexistent id still FAILs (no vacuous acceptance)
- [ ] Fixture suite gains a violating scenario that FAILs (conformance-at-birth rule)
- [ ] Folded-candidate convention documented or annotated
