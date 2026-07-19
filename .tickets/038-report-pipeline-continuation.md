---
id: 038
title: "Report pipeline continuation: model/contract/derive from the ui discovery seed"
status: open
blocked_by: []
---

# Report pipeline continuation: model/contract/derive from the ui discovery seed

## Context

The 2026-07-19 UI discovery session designed the archwright report (web primary,
md/json projections) and graduated: `design/discovery/ui/model-seed.md` carries
the screen-flow graph, per-screen state/events, derived-data requirements, and
the compiled TODO list. Five tensions await formalize (design-system.md
Graduates-to-Patterns table). Four flagged desires await the forces phase.

## What to build

Run the verification-track phases on the report design, consuming the seed:

1. **forces** — the four flagged desires (model-seed.md §Flagged Desires) become force files
2. **formalize** — the five Graduates-to-Patterns rows become patterns
3. **model** — screen-flow + per-screen state/events → report UI model; TODO list is the input backlog
4. **contract** — the three new schemas: `model_view` block, `asks` block, response file (ask-ids = aw/v1 fingerprints)
5. **derive** — specs incl. the vocabulary-map constraint (surface phrases checkable against design-system tokens)

Also settle (small, during model): schema nudges from the session findings —
optional `label:` on model states/events, invariant `description` WARN-when-missing,
report home dir in target projects.

## Acceptance criteria

- [ ] design/forces/, patterns/, models/, specs/ populated for the report; --links passes
- [ ] Conservation holds: every model/contract element cites its ledger anchors
- [ ] Session TODOs triaged: consumed by the model or explicitly deferred
