---
id: "046"
title: "Report diagram renders states without transitions — join arrows from behavior specs"
status: done
blocked_by: []
---

# Report diagram renders states without transitions

Found by the 044 visual-conformance run (blind Q3: "boxes have no drawn connectors" —
initially judge-overridden by a wrong proxy check, confirmed real during 045).

## Why

design-system#D006: a non-technical reader should "look at the diagram and understand
how things will behave." A set of disconnected state boxes shows the modes but not the
behavior — the blind answerer had to infer sequence from label wording, which is
exactly the failure D006 names.

Root cause chain: actor models (`design/models/*-actors.yaml`) declare states but no
transition table; `derive.build_model_view` always emits `transitions: []`;
`_diagram_svg` compiles smcat state declarations only.

## What to build

1. Source transitions from behavior specs: `design/specs/*.yaml` (kind: behavior)
   carry `transitions: [{from, on, to}]` and link to actors via the model. Join them
   into `model_view.transitions` and emit smcat arrows (`a => b : EVENT;`).
2. Plain-language event labels on arrows via the vocabulary table (D002 applies to
   arrow labels too).
3. Fallback unchanged when no behavior spec matches (states-only diagram is still
   better than nothing; note stays plain-language).
4. Conformance: extend the suite's report section — generated HTML for a model with
   a matching behavior spec must contain smcat edge markup; a model without one must
   not regress. Non-vacuity: a spec with transitions must produce arrows, and the
   assertion must be on EDGES semantically (path count is the proxy that fooled the
   044 judge).

## Acceptance criteria

- [x] Diagram shows arrows between states when a behavior spec provides transitions
- [x] Arrow labels use vocabulary surface phrases
- [x] Suite check asserts edges semantically (not path-count proxy); suite green
- [x] Blind re-ask of Q3 describes connected flow without inferring from labels

## Out of scope

- Per-element rule joins (v1 granularity note) — separate deferral
- Multi-actor composite diagrams (composition view is its own model decision)

## Resolution (2026-07-24)

Transitions now join from behavior specs into the report diagram on both surfaces.

- `derive._behavior_transitions`: walks `spec_projections` for `behavior:` specs,
  loads the spec YAML (design/ file input — no checker imports; the local
  `_bool_key` helper handles both `on:` spellings), normalizes hyphen/underscore
  state ids to the model's form, labels every event via `vocab.surface("event X")`
  (D002 — unknown event = generation error, per the completeness discipline; ten
  `event *` tokens added to the default table).
- `render_html`: `_smcat_src` emits `a => b : label;` arrows; the diagram now
  renders the first actor WITH verified transitions (D006 — a connected map beats
  actors[0]'s disconnected boxes), falling back to actors[0] states-only when no
  behavior spec matches.
- `render_md`: mermaid `a --> b: label` arrows (projections stay in agreement).
- Suite +3 (now 146 green): semantic edge assertion on (from,to,event) tuples +
  vocab labels + md mirror; smcat-source arrow statements (path-count proxy
  explicitly avoided); non-vacuity — spec removed ⇒ zero transitions, no arrows.
- Blind re-ask of Q3 (fresh session, dogfood capture): answerer described the
  five states, every labeled arrow, the fan-outs, and the reroute cycle, calling
  it "states connected by event-labeled transitions" — connected flow read
  directly from the drawing, not inferred from label wording.
