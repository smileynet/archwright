# Archwright

Capture design decisions as forces and patterns, derive machine-checkable specs from them, and catch code that drifts from its own design.

## What It Does

Archwright is a design methodology embodied as agent skills. You express design intent in conversation — what the thing wants to be, what bounds it, where those conflict — and the agent resolves that intent into patterns, domain models, and machine-checkable specs. Checks verify the implementation against the stated design; when code violates its own design, the violation routes back to the level that owns it, carrying provenance and a fix direction.

| When I'm... | I want to... | So I can... |
|-------------|-------------|--------------|
| Starting design work on a project | map what forces and decisions already exist | build on intent instead of re-deriving it |
| Facing a design decision | see the tension named, with researched options | decide with evidence, not vibes |
| Done deciding | capture the resolution as a pattern | keep the "why" attached to the architecture |
| Changing code | check it against the design's invariants | catch drift before it ships |
| Looking at a check failure | know whether it's a code bug or a design flaw | fix it at the level that owns it |

## Quick Start

```bash
# Bootstrap the toolchain (mise: https://mise.run)
mise trust && mise install
mise run setup                 # python deps
mise run rehydrate-alloy       # Alloy jar (enables behavior model checks)
mise run test
# === Results: … passed, 0 failed, 0 skipped ===

# Deploy the skills + steering to your agent tool
mise run deploy-skills                          # kiro (default)
bash tools/deploy-skills.sh --tool claude       # or claude | codex | agy
# ✓ skill (symlink): archwright-survey … Done.
```

Then, in any project, ask your agent to **"survey this project"**. The pipeline runs from there:

```
survey → forces → tensions → resolve → formalize → model → contract → derive → check
```

Design artifacts land in the target project under `design/` (forces, patterns, models, specs) — live documents on your current branch, each carrying provenance back to the forces that demanded it.

## What a Catch Looks Like

Checks verify the implementation against the stated design. When code (or an execution trace) violates a design invariant, the violation arrives with everything needed to route it — trimmed real output:

```bash
python3 tools/archwright-check.py --trace game.spec.yaml game.trace.json --json
```

```json
{
  "status": "fail",
  "violations": [{
    "invariant": "count-within-max",
    "confidence": "★★",
    "severity": "error",
    "escalate": true,
    "message": "Invariant 'count-within-max' violated after event 'TICK' at position 1",
    "from_pattern": "pattern:bounded-capacity",
    "from_force": "players-never-stranded",
    "suggested_route": "fix-implementation",
    "contrast_pair": {
      "expected": "Count never exceeds max (always (count <= max))",
      "actual": "event 'TICK' at trace position 1 with state {\"count\": 3, \"max\": 2}"
    }
  }]
}
```

The provenance chain (`invariant → from_pattern → from_force`) is what lets the `archwright-passup` skill route the failure to the level that owns it: most violations are implementation drift; a violation that traces all the way to a force means the design itself needs re-resolution.

## The Thesis

Human design intent — expressed as forces in tension — **resolves into** verified architecture. The resolution is traceable: every architectural commitment carries provenance back to the forces that demanded it. When the architecture violates its own stated forces, corrections route back to the design for re-resolution.

Two vocabularies, one pipeline:

1. **Design domain** — a vocabulary for thinking at the level of intent: what the thing wants to be, what bounds it, and how those are reconciled.
2. **Architecture domain** — the formal target: behavior models, data contracts, service boundaries, dependency rules, and invariants — verified against the stated forces.

The model in one line:

> Forces in tension → resolved Pattern → takes form as architecture (State · Data · Interface · Invariant) → verified against forces → violations surface as contrast pairs → route back to responsible force → re-resolve → … → quiescence.

**Core commitment:** forces stay first-class, and product-level desires (what humans need) are the primary forces. Architectural constraints exist to serve those desires via explicit traceability. The reusable IP is not a catalogue of patterns; it is the method of naming and resolving tensions that trace back to human purpose. The moment patterns become fixed templates disconnected from the desires that generated them, the system dies.

## What's in the Box

- **Skills** (`skills/`, deployed to your agent tool) — the design methodology: force identification, resolution, verification, correction
- **Tools** (`tools/`, invoked via interpreter or `mise run`) — mechanical operations: schema validation, spec → Alloy compilation, checking, trace validation
- **Patterns** (in target project, `design/patterns/`) — captured design intent
- **Models** (in target project, `design/models/`) — domain actors, state machines, event flows, composition
- **Specs** (in target project, `design/specs/`) — verified architectural commitments (behavior, constraint, contract, dependency)

## Documentation

| Document | Contents |
|----------|----------|
| [Lineage](docs/lineage.md) | Where this comes from — Alexander, and what we're keeping vs. what software dropped |
| [Findings](docs/findings.md) | The load-bearing theoretical insights (stable core) |
| [Glossary](docs/glossary.md) | All concepts and terminology |
| [Pattern Schema](docs/pattern-schema.md) | The machine-readable schema for patterns |
| [Worked Examples](docs/worked-examples.md) | Alexander patterns mapped to games/apps |
| [Prior Art](docs/prior-art.md) | The traditions we draw from, with full references |
| [Open Questions](docs/open-questions.md) | Prioritized research backlog |

## Figures

| Figure | Shows |
|--------|-------|
| [compilation.svg](figures/compilation.svg) | Vertical resolution from forces → architecture |
| [invariant_boundary.svg](figures/invariant_boundary.svg) | Invariant-as-no-go-region + pass-up hop |
| [pass_up_tower.svg](figures/pass_up_tower.svg) | Pass-up as level-terminating climb |

## Development

Commands, layout, constraints, and current work status live in [AGENTS.md](AGENTS.md) — the agent-facing guide is also the contributor guide. Validate with `mise run validate`, check specs with `mise run check-static`, run the fixture suite with `mise run test`.

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
