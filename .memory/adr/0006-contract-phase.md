# ADR-0006: Contract Phase as Discrete Pipeline Step

**Date:** 2026-07-15
**Status:** Accepted

## Context

Running the full pipeline on catalyst-mono revealed that the derive phase under-produced data contracts and interface specs. The model phase already identified what actors own and what events carry, but nothing projected that into typed specs. Research across 5 traditions (Event Modeling, DDD, Z/VDM, TLA+, CQRS) confirmed data models are derived from behavior, not designed independently — and the derivation is mechanical once boundaries are drawn.

## Decision

Add `archwright-contract` as a discrete pipeline phase between model and derive. Pipeline is now: `survey → forces → tensions → resolve → formalize → model → contract → derive → check`.

Contract produces: state schemas (from actor.owns), event payloads (from actor.emits_events), persistence schemas (from lifecycle + authoritative-vs-reconstructible decision), interface surfaces (public vs internal events).

## Why not extend model or derive?

- Model is creative (identifies actors/boundaries). Contract is mostly mechanical (projects owned state into typed specs). Different cognitive modes.
- Derive produces behavior specs (FSMs) and constraint specs (rules). Contract produces structural specs (data shapes). Different spec kinds.
- Discrete phases have human checkpoints. The persistence decision ("what survives save/load?") warrants review before behavioral specs are derived from it.
