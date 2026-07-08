# AGENTS.md — Archwright

AI-assisted design system that resolves human design intent (expressed as a force-resolution language) into verified architecture, with traceable bidirectional flow.

## Project Layout

```
.
├── README.md                      # Project overview & doc index
├── docs/
│   ├── lineage.md                 # Origin: Alexander, what we keep vs. what software dropped
│   ├── findings.md                # 9 load-bearing theoretical insights (stable core)
│   ├── glossary.md                # All concepts and terminology
│   ├── pattern-schema.md          # Proposed machine-readable schema for patterns
│   ├── worked-examples.md         # Alexander patterns mapped to games/apps
│   ├── prior-art.md              # 5 traditions with full references
│   └── open-questions.md          # Prioritized research backlog
├── figures/                       # SVG diagrams
│   ├── compilation.svg            # Fig 1: vertical compile from forces to architecture
│   ├── invariant_boundary.svg     # Fig 2: invariant-as-no-go-region + pass-up hop
│   └── pass_up_tower.svg          # Fig 3: pass-up as level-terminating climb
├── tools/                         # Mechanical operations (on PATH)
│   ├── pattern-schema.yaml        # JSON Schema for pattern validation
│   ├── spec-schema.yaml           # JSON Schema for spec validation
│   ├── templates/                 # Document templates
│   │   ├── pattern.md             # New pattern template
│   │   ├── spec-behavior.yaml    # Behavior spec template
│   │   ├── spec-contract.yaml    # Contract spec template
│   │   ├── spec-constraint.md    # Constraint spec template
│   │   └── spec-dependency.md    # Dependency spec template
│   └── domains/                   # Domain-specific overlays
│       ├── game/                  # Game design predicates + scales
│       └── general/               # General structural predicates
├── .memory/
│   ├── CONTEXT.md                 # Project glossary (quick-reference terms)
│   ├── research-plan.md           # Research topics & spike proposals
│   ├── research-synthesis.md      # R1-R5 findings
│   ├── research-synthesis-2.md    # R6-R11 findings
│   ├── spike-results-s5-s8.md    # Alloy validation results
│   └── adr/                       # Architecture decision records
├── .scratch/                      # Ephemeral working notes (gitignored)
├── .references/                   # Reference repos (gitignored)
└── AGENTS.md                      # This file
```

## What Archwright Is

A **methodology embodied as agent skills** with supporting tools. The AI agent IS the system — it holds the design methodology. Tools handle deterministic mechanical tasks.

**Skills** (global, `~/.kiro/skills/`):
- `archwright` — full design methodology: identify forces, resolve tensions, formalize as patterns + specs
- `archwright-check` — verification loop: check specs, report violations, route corrections

**Tools** (on PATH, `tools/`):
- Schema validation, spec → Alloy compilation, Alloy execution, counterexample parsing, spec → XState
- Templates for patterns and each spec kind (`tools/templates/`)

## Project Type

Research + design-theory project transitioning to implementation. Primary outputs: skills, tools, schemas, documentation.

## Commands

| Task | Command |
|------|---------|
| Validate pattern | `archwright-validate <pattern.yaml>` |
| Validate spec | `archwright-validate <spec.yaml>` |
| Check spec (Alloy) | `archwright-check <spec.yaml>` |
| Run Alloy model | `java -Djava.awt.headless=true -jar .references/alloy6.jar exec <model.als>` |

## Workflows

1. **Extend the design language** — add findings to docs/, terms to `.memory/CONTEXT.md`
2. **Explore an open question** — pick from docs/open-questions.md, research, produce ADR
3. **Build tooling** — scripts in `tools/` for validation, compilation, checking
4. **Tracer bullet** — encode lacrosse-bosse decisions as patterns + specs, verify

## Key Constraints

- Forces stay first-class — never reduce patterns to fixed templates
- "Resolves into" not "compiles to" — the process is creative + verified, not mechanical
- Pass-up is level-terminating (signals stop at the level that owns the violated force)
- Confidence (★★/★/—) gates AI autonomy, checking rigor, and escalation
- Specs are flat, typed (kind field), linked via `kind:id` references
- The agent IS the system; tools are mechanical servants

## Target Project Artifacts

When archwright operates on a project, it produces:
```
target-project/
  design/
    patterns/          # Markdown+frontmatter (forces, tensions, resolutions)
    specs/             # Behavior/contract: YAML. Constraint/dependency: Markdown+frontmatter.
```

## References

- Alexander's *A Pattern Language* (1977) and *The Timeless Way of Building* (1979)
- Harel statecharts / XState
- Alloy / lightweight formal methods (counterexample-driven)
- CEGAR (Clarke et al., 2000/2003)
- Mawhorter & Smith (FDG 2021) — softlock detection via CTL
- Rezin et al. (2017) — model checking multiplayer games
- Lean 4 / CSLib / Veil — future unbounded verification backend
- Kleppmann (2025) — AI + formal verification mainstream prediction

## Customization

- Project-specific steering: add to `.kiro/steering/` in this repo
- Domain terms: keep `.memory/CONTEXT.md` current
- Decisions: record in `.memory/adr/` using ADR format
