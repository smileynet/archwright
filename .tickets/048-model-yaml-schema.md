---
id: "048"
title: "Validator: schema for model YAML (kind: model) — direct validation currently impossible"
status: in_progress
blocked_by: []
---

# Validator schema for model YAML files

Field finding (discord-poc dp-poc run, 2026-07-22, 9 areas): `design/models/
*.yaml` files cannot be validated directly — `archwright-validate.py` reports
"unknown kind 'None'" because model files carry no `kind` and no schema exists
for them. Models are validated only implicitly via the `--links` index pass
(candidate coverage, from_model resolution). Same behavior observed on the
crew-research field models — this is the second field run to hit it.

## What to build

- A `kind: model` schema in archwright-validate.py: required top-level fields
  (actors, experiences, contract_candidates, composition — align with the
  archwright-model skill's output format), per-actor required fields, folded
  candidates (`folded_into`) validated at schema level not just links level
- Decide + document the frontmatter/kind convention for model YAML (models
  are pure YAML, not markdown+frontmatter — schema detection may key off
  path `models/` + suffix instead of `kind`)
- Conformance corpus per the extension protocol: at least one valid model
  fixture AND one violating fixture that FAILs (missing actor id, candidate
  without producer) wired into run-fixture-tests.sh

## Acceptance criteria
- [ ] `archwright-validate.py design/models/x.yaml` gives a real PASS/FAIL, not "unknown kind"
- [ ] Violating fixture fails loudly in the fixture suite
- [ ] Both field projects' existing models pass unmodified (or the delta is documented)
