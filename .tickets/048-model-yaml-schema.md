---
id: "048"
title: "Validator: schema for model YAML (kind: model) — direct validation currently impossible"
status: done
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
- [x] `archwright-validate.py design/models/x.yaml` gives a real PASS/FAIL, not "unknown kind"
- [x] Violating fixture fails loudly in the fixture suite
- [x] Both field projects' existing models pass unmodified (or the delta is documented)

## Resolution (2026-07-24)

**Convention decided:** models are shape-detected — a YAML mapping with a
top-level `actors` key IS a model (the same test `collect_model_index` and the
report generator already use). No `kind` field required; explicit `kind: model`
accepted. Existing field models therefore validate UNMODIFIED.

- `validate_model` in archwright-validate.py. Errors: empty/missing actors,
  actor without id / duplicate / non-slug, dict state without id, non-`pattern:`
  from_patterns ref, candidate without event or producer, duplicate candidate
  event within the file (cross-model is ticket 050), fold to unknown target,
  fold chains (must target the cluster owner directly), fold-to-self, malformed
  spec_projections ref, boundary entity without id. Unknown candidate producer =
  WARN.
- **Documented delta from the ticket text:** `experiences` and `composition`
  are advisory WARNs, not required — the whole local corpus (3 snackbox
  lifecycle models) and both field projects' models omit them; hard-requiring
  them would fail AC3. The archwright-model skill still emits them; the WARN
  nudges older models forward.
- Models stay excluded from the generic `--links` ref collector (indexed by
  `collect_model_index` as before) — all four local `--links` runs verified
  unchanged.
- Conformance: `tests/fixtures/model-schema/{valid,violating}.yaml`; suite +3
  (149 green) — valid passes as `(kind: model)`, violating FAILs with all 11
  error classes asserted individually (non-vacuous), corpus models pass
  unmodified. Steering + AGENTS command row updated (the "direct validation
  impossible" gotcha note now states the new behavior).
