# AGENTS.md — Archwright

AI-assisted design system that resolves human design intent (expressed as a force-resolution language) into verified architecture, with traceable bidirectional flow.

## Project Layout

```
.
├── README.md                      # Project overview & doc index
├── docs/
│   ├── lineage.md                 # Origin: Alexander, what we keep vs. what software dropped
│   ├── findings.md                # Load-bearing theoretical insights (stable core)
│   ├── glossary.md                # All concepts and terminology
│   ├── pattern-schema.md          # Proposed machine-readable schema for patterns
│   ├── worked-examples.md         # Alexander patterns mapped to games/apps
│   ├── prior-art.md              # 5 traditions with full references
│   └── open-questions.md          # Prioritized research backlog
├── skills/                        # Skill source-of-truth (deployed via tools/deploy-skills.sh)
│   ├── archwright-survey/         # Entry point: map project design state
│   ├── archwright-forces/         # Extract desires + constraints from sources
│   ├── archwright-tensions/       # Cluster forces into named tensions
│   ├── archwright-resolve/        # Resolve tensions (HITL: human decides)
│   ├── archwright-formalize/      # Write patterns from resolved tensions
│   ├── archwright-model/          # Identify domains as actors, map state machines
│   ├── archwright-contract/       # Derive typed data contracts from domain model
│   ├── archwright-derive/         # Generate specs from domain models
│   ├── archwright-check/          # Verify specs against implementation
│   ├── archwright-review/         # Review code for design alignment
│   ├── archwright-audit/          # Audit docs for truth (surface contradictions)
│   └── archwright-diagram/        # Render models/patterns as Mermaid diagrams
├── steering/                      # Steering source-of-truth (deployed via tools/deploy-skills.sh)
│   ├── archwright-conventions.md  # Pipeline phase discipline, quality gates
│   └── subagent-reliability.md    # Failure handling for parallel dispatch
├── figures/                       # SVG diagrams
│   ├── compilation.svg            # Fig 1: vertical compile from forces to architecture
│   ├── invariant_boundary.svg     # Fig 2: invariant-as-no-go-region + pass-up hop
│   └── pass_up_tower.svg          # Fig 3: pass-up as level-terminating climb
├── tools/                         # Mechanical operations
│   ├── archwright-validate.py     # Schema + link validation for patterns/specs
│   ├── archwright-check.py        # Check dispatcher: constraint/dependency (grep), behavior (Alloy), --trace, --static
│   ├── archwright-compile-alloy.py# Behavior spec → Alloy 6 model
│   ├── archwright-check-compile.mjs # Intent patterns → check blocks
│   ├── archwright-trace-validate.{sh,mjs} # BROKEN (schema fork w/ check.py --trace; see .memory/audit/tools.md F2)
│   ├── run-fixture-tests.sh       # BROKEN (stale paths + missing fixture design/; see .memory/audit/tools.md F1)
│   ├── deploy-skills.sh           # Sync skills + steering to ~/.kiro/ (or --project <path>)
│   ├── pattern-schema.yaml        # JSON Schema for pattern validation
│   ├── spec-schema.yaml           # JSON Schema for spec validation
│   ├── trace-schema.ts            # Trace event type definitions
│   ├── templates/                 # Document templates
│   │   ├── pattern.md             # New pattern template
│   │   ├── spec-behavior.yaml    # Behavior spec template
│   │   ├── spec-contract.yaml    # Contract spec template
│   │   ├── spec-constraint.md    # Constraint spec template
│   │   └── spec-dependency.md    # Dependency spec template
│   └── domains/                   # Domain-specific overlays
│       └── game/                  # Game design predicates (scales + general/ planned — audit-plan.md B1)
├── .memory/
│   ├── CONTEXT.md                 # Project glossary (quick-reference terms)
│   ├── PLAN.md                    # COMPLETE — historical (live checking for LBP)
│   ├── specs/                     # Specs for the prior plan's deliverables
│   ├── audit/                     # Audit reports (tools, skills, claims)
│   ├── research-*.md              # Research plans & syntheses
│   └── adr/                       # Architecture decision records
├── audit-plan.md                  # Active standalone audit plan (tickets A/B/C/D)
├── .scratch/                      # Ephemeral working notes (gitignored)
├── .references/                   # Reference repos (gitignored)
└── AGENTS.md                      # This file
```

## What Archwright Is

A **methodology embodied as agent skills** with supporting tools. The AI agent IS the system — it holds the design methodology. Tools handle deterministic mechanical tasks.

**Skills** (source in `skills/`, deployed to `~/.kiro/skills/`):
- `archwright-survey` — entry point: map project design state, dispatch specialists
- `archwright-forces` — extract desires and constraints from project sources
- `archwright-tensions` — cluster forces into named tensions
- `archwright-resolve` — resolve a tension (HITL: human decides between options)
- `archwright-formalize` — write a pattern from a resolved tension
- `archwright-model` — identify domains as actors, map state machines and event flows
- `archwright-contract` — derive typed data contracts from domain model
- `archwright-derive` — generate specs from domain models
- `archwright-check` — verify specs against implementation
- `archwright-review` — review code for design alignment (structural + behavioral + semantic)
- `archwright-audit` — audit docs for truth (surface contradictions between docs and code)
- `archwright-diagram` — render models/patterns as Mermaid diagrams

**Steering** (source in `steering/`, deployed to `~/.kiro/steering/`):
- `archwright-conventions.md` — pipeline phase discipline, quality gates
- `subagent-reliability.md` — failure handling for parallel dispatch

**Tools** (`tools/`, invoked via interpreter — see Commands):
- `archwright-validate.py` — schema + link validation; `archwright-check.py` — check dispatcher (static/trace/Alloy)
- `archwright-compile-alloy.py` — behavior spec → Alloy 6 model; `archwright-check-compile.mjs` — intent → check blocks
- Templates for patterns and each spec kind (`tools/templates/`)
- `deploy-skills.sh` — sync skills + steering from repo to global `~/.kiro/` (or `--project <path>`)

**Workflow:** Edit skills/steering in this repo → commit → run `tools/deploy-skills.sh` to push to global.

## Project Type

Research + design-theory project transitioning to implementation. Primary outputs: skills, tools, schemas, documentation.

## Commands

Tools are not on PATH in this repo — invoke via interpreter (verified 2026-07-16, `.memory/audit/tools.md`):

| Task | Command |
|------|---------|
| Validate pattern/spec | `python3 tools/archwright-validate.py <file>...` |
| Validate links | `python3 tools/archwright-validate.py --links <dir>` |
| Check spec(s) | `python3 tools/archwright-check.py <spec>... [--json]` |
| Batch static check | `python3 tools/archwright-check.py --static <dir> [--target <root>]` |
| Validate trace | `python3 tools/archwright-check.py --trace <spec.yaml> <trace.json>` |
| Compile to Alloy | `python3 tools/archwright-compile-alloy.py <spec.yaml>` |
| Audit docs vs code | `archwright-audit` (skill-driven, not a script) |
| Run Alloy model | `java -Djava.awt.headless=true -jar .references/alloy6.jar exec <model.als>` (jar not in repo — `.references/` is gitignored; behavior checks SKIP without it) |
| Deploy skills | `bash tools/deploy-skills.sh [--project <path>]` |
| Run fixture tests | `tools/run-fixture-tests.sh` — BROKEN, see `.memory/audit/tools.md` F1 (repair = audit-plan.md B7) |

Note: `archwright-check.py` flags are `--static`, `--trace`, `--all`, `--target`, `--json` only — there is no `--structural`, `--deep`, `--project`, or `--model` flag (verified 2026-07-16, `.memory/audit/tools.md`).

## Workflows

1. **Extend the design language** — add findings to docs/, terms to `.memory/CONTEXT.md`
2. **Explore an open question** — pick from docs/open-questions.md, research, produce ADR
3. **Build tooling** — scripts in `tools/` for validation, compilation, checking
4. **Tracer bullet** — encode lacrosse-bosse decisions as patterns + specs, verify
5. **Pipeline on new project** — run full pipeline (survey→check) on a target project, producing patterns + models + specs in `design/`

## Key Constraints

- Forces stay first-class — product-level desires (what humans need) are primary; architectural constraints serve those desires via explicit `serves` links
- Every pattern traces to a product desire — orphaned constraints (no `serves` link) are flagged for review
- "Resolves into" not "compiles to" — the process is creative + verified, not mechanical
- Pass-up is level-terminating (signals stop at the level that owns the violated force)
- Confidence (★★/★/—) gates AI autonomy, checking rigor, and escalation
- Specs are flat, typed (kind field), linked via `kind:id` references
- The agent IS the system; tools are mechanical servants
- Subagents extract (read files → structured output); main agent synthesizes (dedup, cluster, merge)

## Pipeline Phase Discipline

The archwright pipeline (`survey → forces → tensions → resolve → formalize → model → contract → derive → check`) is a sequence of **discrete phases with human checkpoints between them**.

**Rules:**
1. Each skill invocation = one phase. Produce its artifact, present it, STOP.
2. After presenting the phase output, ask whether to proceed to the next phase — never auto-advance.
3. "Proceed" after orientation means "run the current phase" (the one named in Next Steps[1]), not "run all phases."
4. The survey skill explicitly does NOT write patterns, specs, or resolve tensions. It produces an intake outline and dispatch queue.
5. Phases that require human input (resolve, grill) are HITL gates — they cannot be skipped even if prior decisions exist.
6. A skill's "Does NOT" section is a hard boundary, not a suggestion.

**Why:** Each phase produces an artifact the human should review before it feeds the next. Pattern quality depends on force quality. Spec quality depends on pattern quality. Skipping review compounds errors silently.

## Target Project Artifacts

When archwright operates on a project, it produces:
```
target-project/
  design/
    patterns/          # Markdown+frontmatter (forces, tensions, resolutions)
    models/            # YAML (machine-readable) + MD (human-readable with Mermaid diagrams)
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
