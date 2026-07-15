# Archwright

A force-resolution design language that resolves into verified architecture.

## The Thesis

Human design intent — expressed as forces in tension — **resolves into** verified architecture. The resolution is traceable: every architectural commitment carries provenance back to the forces that demanded it. When the architecture violates its own stated forces, corrections route back to the design for re-resolution.

Two vocabularies, one pipeline:

1. **Design domain** — a vocabulary for thinking at the level of intent: what the thing wants to be, what bounds it, and how those are reconciled.
2. **Architecture domain** — the formal target: behavior models, data contracts, service boundaries, dependency rules, and invariants — verified against the stated forces.

These are not two systems but one resolution, running in both directions.

## The Model in One Line

> Forces in tension → resolved Pattern → takes form as architecture (State · Data · Interface · Invariant) → verified against forces → violations surface as contrast pairs → route back to responsible force → re-resolve → … → quiescence.

## Core Commitment

Keep *forces* first-class — and product-level desires (what humans need) are the primary forces. Architectural constraints exist to serve those desires via explicit traceability. The reusable IP is not a catalogue of patterns; it is the method of naming and resolving tensions that trace back to human purpose. The moment patterns become fixed templates disconnected from the desires that generated them, the system dies.

## What Archwright Is

Archwright is a **methodology embodied as agent skills**, with supporting tools for mechanical tasks. The AI agent IS the system — it holds the design methodology. Humans express intent through conversation; the agent resolves it into checkable specifications.

- **Skills** (global, `~/.kiro/skills/`) — the design methodology: force identification, resolution, verification, correction
- **Tools** (on PATH, `tools/`) — mechanical operations: schema validation, spec → Alloy compilation, checking, parsing
- **Patterns** (in target project, `design/patterns/`) — captured design intent
- **Models** (in target project, `design/models/`) — domain actors, state machines, event flows, composition
- **Specs** (in target project, `design/specs/`) — verified architectural commitments (behavior, constraint, contract, dependency)

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
| [compilation.svg](figures/compilation.svg) | Vertical resolution from forces → architecture |
| [invariant_boundary.svg](figures/invariant_boundary.svg) | Invariant-as-no-go-region + pass-up hop |
| [pass_up_tower.svg](figures/pass_up_tower.svg) | Pass-up as level-terminating climb |

## Project Status

Research + design phase. Spikes validated: pattern schema, spec layer, Alloy as checking backend (94ms counterexample finding), contrast pair generation, game failure predicates, live validation feasibility.

**Next:** Tracer bullet against lacrosse-bosse — encode existing design decisions as patterns + specs, verify invariants, demonstrate violation detection.

## Lineage

Archwright evolves from:
1. **spec-driven-development** — structured planning (PLAN.md, spec files, validation criteria)
2. **project-overseer** — drift detection between spec and implementation (terraform model)
3. **archwright** — formal verification of design intent (forces → checkable invariants → verified architecture)

## How to Contribute

- Extend the design language → add findings to [findings.md](docs/findings.md), terms to [glossary.md](docs/glossary.md)
- Explore an open question → pick from [open-questions.md](docs/open-questions.md), research, write findings
- Build tooling → scripts in `tools/`
- The **forces-first principle** is the tie-breaker whenever a decision threatens to turn a pattern into a template
