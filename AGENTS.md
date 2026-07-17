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
│   ├── run-fixture-tests.sh       # Full check suite vs tests/fixtures/lacrosse-bosse
│   ├── deploy-skills.sh           # Sync skills + steering + domain overlays + glossary to ~/.kiro/ (or --project <path>)
│   ├── pattern-schema.yaml        # JSON Schema for pattern validation
│   ├── spec-schema.yaml           # JSON Schema for spec validation
│   ├── contract-schema.yaml       # JSON Schema for contract specs (from_model, events)
│   ├── trace-schema.ts            # Trace event type definitions
│   ├── templates/                 # Document templates
│   │   ├── pattern.md             # New pattern template
│   │   ├── force.md               # Per-force file template (design/forces/)
│   │   ├── spec-behavior.yaml    # Behavior spec template
│   │   ├── spec-contract.yaml    # Contract spec template
│   │   ├── spec-constraint.md    # Constraint spec template
│   │   └── spec-dependency.md    # Dependency spec template
│   └── domains/                   # Domain overlays: scales + predicates per domain
│       ├── detect.yaml            # Manifest → domain rules (survey applies; override wins)
│       ├── game/                  # Game scales + 13 predicates + research sources
│       ├── web/                   # Web scales + predicates
│       └── general/               # Fallback scales + cross-cutting predicates
├── tools/stacks/                  # Stack adapters: per-language/engine mechanical components (ADR 0008)
│   ├── REGISTRY.yaml              # Adapter kinds × status (pending/★/★★, computed) + since: history
│   ├── gdscript/                  # All pending (T7 converted)
│   └── typescript/                # Pending; C10 builds trace_emitter as first measured adapter
├── .memory/
│   ├── CONTEXT.md                 # Project glossary (quick-reference terms)
│   ├── PLAN.md                    # Phases 0–4 historical; Phase 5 ACTIVE (polyglot check tool — executor assigned, see specs/polyglot-check-tooling.md)
│   ├── specs/                     # Specs for plan deliverables (incl. Phase 5)
│   ├── audit/                     # Audit reports (tools, skills, claims)
│   ├── grill/                     # Grill session decision records (INDEX.md + Q-files per topic)
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
- `archwright-passup` — (planned — audit-plan C12) consume check violations, lift to the owning level, route per confidence

**Steering** (source in `steering/`, deployed to `~/.kiro/steering/`):
- `archwright-conventions.md` — pipeline phase discipline, quality gates
- `subagent-reliability.md` — failure handling for parallel dispatch

**Tools** (`tools/`, invoked via interpreter — see Commands):
- `archwright-validate.py` — schema + link validation; `archwright-check.py` — check dispatcher (static/trace/Alloy)
- `archwright-compile-alloy.py` — behavior spec → Alloy 6 model; `archwright-check-compile.mjs` — intent → check blocks
- Templates for patterns and each spec kind (`tools/templates/`)
- `deploy-skills.sh` — sync skills + steering + domain overlays + glossary from repo to global `~/.kiro/` (or `--project <path>`)

**Workflow:** Edit skills/steering in this repo → commit → run `tools/deploy-skills.sh` to push to global.

## Project Type

Research + design-theory project transitioning to implementation. Primary outputs: skills, tools, schemas, documentation.

## Commands

Tools are not on PATH in this repo — invoke via interpreter (verified 2026-07-16, `.memory/audit/tools.md`):

| Task | Command |
|------|---------|
| Validate pattern/spec | `python3 tools/archwright-validate.py <file>...` — validates all kinds incl. contract; emits non-fatal `WARN:` lines (e.g., missing `protects_experience`) |
| Validate links | `python3 tools/archwright-validate.py --links <dir>` |
| Check spec(s) | `python3 tools/archwright-check.py <spec>... [--json]` |
| Batch static check | `python3 tools/archwright-check.py --static <dir> [--target <root>]` |
| Validate trace | `python3 tools/archwright-check.py --trace <spec.yaml> <trace.json>` |
| Compile to Alloy | `python3 tools/archwright-compile-alloy.py <spec.yaml>` |
| Audit docs vs code | `archwright-audit` (skill-driven, not a script) |
| Run Alloy model | `java -Djava.awt.headless=true -jar .references/alloy6.jar exec <model.als>` (jar not in repo — `.references/` is gitignored; behavior checks SKIP without it) |
| Deploy skills | `bash tools/deploy-skills.sh [--project <path>]` |
| Run fixture tests | `tools/run-fixture-tests.sh` — 22 checks incl. Alloy behavior check (SKIPs with reason if alloy6.jar or java absent) |

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
- Contract phase solely owns contract specs (C7, ratified 2026-07-16) — model emits contract *candidates* (identity/direction, no payloads); one spec per event type, with a one-protocol/one-authority-actor cluster exception; `from_model:` provenance required
- Design artifacts are live documents in the target project — committed to the current branch (no special design branches); large projects/monorepos get per-area pipeline runs + an all-up reconciliation pass (grill Q06)
- Coverage gaps follow the Extension Protocol (ADR 0008): pending-with-reason, new instances flow through, new kinds need ADR + HITL; adapter status in `tools/stacks/REGISTRY.yaml` is computed by the fixture suite, never hand-declared
- The agent IS the system; tools are mechanical servants
- Subagents extract (read files → structured output); main agent synthesizes (dedup, cluster, merge)

## Pipeline Phase Discipline

The archwright pipeline (`survey → forces → tensions → resolve → formalize → model → contract → derive → check`) is a sequence of discrete phases. **Gates block only where human input is needed** (ADR 0007, `.memory/adr/0007-hitl-only-gates.md`):

- **HITL-blocking (always stop):** resolve (decisions; pre-resolved = one batched confirmation), L4/L5 desire validation in forces, any ★★ event (violation / unratified assignment / demotion), fog (unknown forces mid-span), end-of-span digest acceptance.
- **Flow-through (auto-advance):** all other phase transitions — only within a human-pre-authorized span, only when the phase's artifacts pass `archwright-validate.py`, and only with a digest entry written. No span authorized → stop after each phase.

Constants: survey never writes patterns/specs or resolves tensions; a skill's "Does NOT" section is a hard boundary; "proceed" authorizes the next phase or an explicitly accepted span — never a silent run to completion.

## Target Project Artifacts

When archwright operates on a project, it produces:
```
target-project/
  design/
    forces/            # Markdown+frontmatter, one file per force (kind: force) — root of provenance
    patterns/          # Markdown+frontmatter (tensions, resolutions; serves: links to forces)
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
