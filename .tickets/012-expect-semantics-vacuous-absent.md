---
id: 012
title: "Check schema: expect present/absent semantics ambiguous for positive-condition checks"
status: done
blocked_by: []
created: 2026-07-17
---

# Check schema: expect present/absent semantics ambiguous

Field-driven (DemoVR phase-1 review 2026-07-17): two DemoAR dependency specs
written the same day by the same derive run use INVERTED expect semantics for
structurally identical positive-condition checks (`owned-accessibility-assembly`
vs `thin-orchestrator` — "this thing must exist" expressed once as
`expect: present` on the artifact and once as `expect: absent` on its negation).
The schema permits both readings, so authors guess — and a wrong guess produces a
check that silently passes forever. Related silent-pass hazard from the same
review: `expect: absent` against a not-yet-existing target directory vacuously
PASSes when the spec activates (three inconsistent future-path variants across
DemoAR dependency specs would all "pass" on wrong paths).

## What to build

- Document normative guidance: when to use expect:present vs expect:absent for
  positive conditions (recommend: present-on-artifact; absent only for
  forbidden-pattern greps).
- Guard the vacuous case: `expect: absent` whose target path matches zero files
  should WARN (or SKIP with reason), not PASS — a check that scanned nothing
  proved nothing.
- Update: spec-constraint/dependency templates, derive skill guidance,
  archwright-check.py.

## Acceptance criteria

- [x] absent-check over a nonexistent target reports WARN/SKIP, not PASS
- [x] Fixture suite gains a vacuous-absent violating scenario
- [x] Template guidance shows one canonical example of each polarity
