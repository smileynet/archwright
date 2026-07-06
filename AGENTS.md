# AGENTS.md — Archwright

AI-assisted design system that compiles human design intent (expressed as a force-resolution language) into architecture (state graphs), with traceable bidirectional flow.

## Project Layout

```
.
├── design-system-working-doc.md   # Living design document (core theory & vocabulary)
├── compilation.svg                # Fig 1: vertical compile from forces to architecture
├── invariant_boundary.svg         # Fig 2: invariant-as-no-go-region + pass-up hop
├── pass_up_tower.svg              # Fig 3: pass-up as level-terminating climb
├── .memory/
│   ├── CONTEXT.md                 # Project glossary
│   └── adr/                       # Architecture decision records
├── .scratch/                      # Ephemeral working notes (gitignored)
├── .references/                   # Reference repos (gitignored)
├── tools/                         # Project scripts and automation
└── AGENTS.md                      # This file
```

## Project Type

Research / design-theory project. No build system yet — primarily Markdown documents, SVG figures, and conceptual modeling.

## Commands

None configured yet. When tooling is added:

| Task | Command |
|------|---------|
| Validate YAML schemas | `yq '.' <file>` |
| Link check | `markdown-link-check design-system-working-doc.md` |

## Workflows

1. **Extend the design language** — add findings to §3, terms to §4, update `.memory/CONTEXT.md`
2. **Explore an open question** — pick from §9, research, write findings, produce ADR if decision-worthy
3. **Build tooling** — scripts in `tools/` for schema validation, compilation pipeline, visualization

## Key Constraints

- Forces stay first-class — never reduce patterns to fixed templates
- The design language and architecture domain are one compilation, not two systems
- Pass-up is level-terminating (signals stop at the level that owns the violated force)
- Confidence (★★/★/—) gates AI autonomy and escalation

## References

Reference materials live in `.references/`. Relevant prior art:
- Alexander's *A Pattern Language* (1977) and *The Timeless Way of Building* (1979)
- Harel statecharts / XState
- Alloy / lightweight formal methods (counterexample-driven)
- CEGAR (Clarke et al., 2000/2003)

## Customization

- Project-specific steering: add to `.kiro/steering/` in this repo
- Domain terms: keep `.memory/CONTEXT.md` current
- Decisions: record in `.memory/adr/` using ADR format
