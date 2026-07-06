# Archwright

A force-resolution design language that compiles to architecture.

## The Thesis

Human design intent — expressed as forces in tension — **compiles down** into architecture (a state graph and its supporting structure). The compilation is **traceable and reversible**: what is learned downstream routes back up to revise the design.

Two halves, one pipeline:

1. **Design domain** — a vocabulary for thinking at the level of intent: what the thing wants to be, what bounds it, and how those are reconciled.
2. **Architecture domain** — the executable target: a state machine / graph as the central anchor, with data, interfaces, and invariants as supporting pillars.

These are not two systems but one compilation, running in both directions.

## The Model in One Line

> Desires + Constraints → resolved Pattern → hands-down (with provenance) → State · Data · Interface · Invariant → check → counterexample → pass-up (lift, confidence-gated, level-terminating) → revised Pattern/Force → recompile → … → quiescence.

## Core Commitment

Keep *forces* first-class. The reusable IP is not a catalogue of patterns; it is the method of naming and resolving tensions. The moment patterns become fixed templates, the system dies.

## Documentation

| Document | Contents |
|----------|----------|
| [Lineage](docs/lineage.md) | Where this comes from — Alexander, and what we're keeping vs. what software dropped |
| [Findings](docs/findings.md) | The 9 load-bearing theoretical insights (stable core) |
| [Glossary](docs/glossary.md) | All concepts and terminology |
| [Pattern Schema](docs/pattern-schema.md) | The proposed machine-readable schema for patterns |
| [Worked Examples](docs/worked-examples.md) | Alexander patterns mapped to games/apps |
| [Prior Art](docs/prior-art.md) | The 5 traditions we draw from, with full references |
| [Open Questions](docs/open-questions.md) | Prioritized research backlog |

## Figures

| Figure | Shows |
|--------|-------|
| [compilation.svg](figures/compilation.svg) | Vertical compile from forces → architecture |
| [invariant_boundary.svg](figures/invariant_boundary.svg) | Invariant-as-no-go-region + pass-up hop |
| [pass_up_tower.svg](figures/pass_up_tower.svg) | Pass-up as level-terminating climb |

## Project Status

Research / design-theory phase. No implementation yet.

**Next thread:** The lift contract — the explicit rule by which a child level translates its failure into the parent's vocabulary. See [Open Questions #1](docs/open-questions.md) and [Research Plan](/.memory/research-plan.md).

## How to Contribute

- Extend the design language → add findings to [findings.md](docs/findings.md), terms to [glossary.md](docs/glossary.md)
- Explore an open question → pick from [open-questions.md](docs/open-questions.md), research, write findings
- Build tooling → scripts in `tools/`
- The **forces-first principle** is the tie-breaker whenever a decision threatens to turn a pattern into a template
