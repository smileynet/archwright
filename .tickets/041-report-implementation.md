---
id: 041
title: "Implement the archwright report generator against the ticket-038 specs"
status: done
blocked_by: []
---

# Implement the report generator

## Context

Ticket 038 produced the full design for the report system (`design/forces/`,
`design/patterns/`, `design/models/report-actors.{yaml,md}`, `design/specs/`):
three planned actors (report-generator, report-page, ask-card), 4 contracts,
6 constraint specs with `target_status: pending`, and the Alloy-proven
`behavior:ask-lifecycle`. The specs are the acceptance criteria — this is the
`examples/planned` → `partial` transition for a real feature.

## What to build

1. **Settle packaging first** (open decision, flagged in the model TODO triage):
   ships with archwright core (`tools/report/`) vs separate projection tool.
   Constraint spec targets assume `tools/report/` + `design/report/` output —
   update targets if the decision lands elsewhere.
2. **report-generator**: canonical CK-03 doc + model YAML + vocabulary map +
   `ARCHWRIGHT_AUTO_APPROVE` → `design/report/` bundle (self-contained web,
   md mirror, json + `model_view`/`asks` blocks). Postures: all-clear /
   needs-attention / tool-error / empty-project; front-door modes incl.
   promise-grouped fallback and composition view (model decisions 1–2).
3. **report-page interactivity**: in-page response accumulation, response bar,
   response-file export per `contract:response-file` (envelope v1).
4. **Flip the six pending constraints live**: remove `target_status: pending`
   as each target lands; every one must FAIL on a deliberately-violating
   fixture before trusting its pass (Extension Protocol rule 4).
5. **Agent consumption**: the consuming agent reads the response file
   (staleness per-ask, supersede-not-merge) — likely a skill edit
   (archwright-check or a new report skill owns the tool contract; update the
   AGENTS.md ownership table).

## Acceptance criteria

- [x] Generator produces a bundle for a real project (dogfood: archwright's own design/)
- [ ] All 6 constraint specs active (no pending) and green, each proven non-vacuous on a violating fixture
- [x] `behavior:ask-lifecycle` trace-validated against a real page interaction trace
- [x] Response file round-trip: export → agent consumes → digest acknowledges
- [x] Vocabulary-map completeness invariant enforced at generation (untranslated term = error)
