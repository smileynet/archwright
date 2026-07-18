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
│   ├── archwright-passup/         # Lift check violations to owning level, route per confidence
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
│   ├── archwright-forces-gen.py   # Force inventory YAML → design/forces/*.md (mechanical projection)
│   ├── archwright-check.py        # Check dispatcher: constraint/dependency (grep), behavior (Alloy), --trace, --static; baseline suppression + ratchet (CK-07/08); evidence ledger (ADR 0009)
│   ├── archwright-compile-alloy.py# Behavior spec → Alloy 6 model
│   ├── archwright-check-compile.mjs # Intent patterns → check blocks
│   ├── run-fixture-tests.sh       # Full check suite vs tests/fixtures/ (lacrosse-bosse + guarded-counter + trace-strict)
│   ├── deploy-skills.sh           # Sync skills + steering + domain overlays + glossary to the target tool's discovery dirs (--tool kiro|claude|codex|agy, --project <path>)
│   ├── pattern-schema.yaml        # JSON Schema for pattern validation
│   ├── spec-schema.yaml           # JSON Schema for spec validation
│   ├── contract-schema.yaml       # JSON Schema for contract specs (from_model, events)
│   ├── check-output-schema.yaml   # CK-03 output contract (check/validate --json shape: skips[] coverage reasons, aw/v1 fingerprints, baselined flag)
│   ├── trace-schema.ts            # Trace types (input: bare array of {event, state, clock}; result: invariants_skipped/guards_skipped per ticket 015)
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
│   └── typescript/                # trace_emitter ★★ (conformance in suite + field-proven on DynamoRush); ast_grammar/check_patterns pending
├── .memory/
│   ├── CONTEXT.md                 # Project glossary (quick-reference terms)
│   ├── PLAN.md                    # Phases 0–4 historical; Phase 5 partially shipped (DoD-5 chain CK-03→04→05→09→10 + CK-21 done; open: CK-06/07/08, 11–19 — see specs/polyglot-check-tooling.md)
│   ├── specs/                     # Specs for plan deliverables (incl. Phase 5)
│   ├── audit/                     # Audit reports (tools, skills, claims)
│   ├── grill/                     # Grill session decision records (INDEX.md + Q-files per topic)
│   ├── lessons/                   # One durable lesson per file + README index/session log
│   ├── research-*.md              # Research plans & syntheses
│   └── adr/                       # Architecture decision records
├── audit-plan.md                  # Audit plan — CLOSED 2026-07-18 (all 7 DoD verified; see §Plan Close-Out)
├── mise.toml                      # Managed toolchain + env + tasks (see Dependency Rehydration)
├── .tickets/                      # Frontier tickets (frontmatter status/blocked_by)
├── .scratch/                      # Ephemeral working notes (gitignored)
├── .references/                   # Reference repos (gitignored)
└── AGENTS.md                      # This file
```

## What Archwright Is

A **methodology embodied as agent skills** with supporting tools. The AI agent IS the system — it holds the design methodology. Tools handle deterministic mechanical tasks.

**Skills** (source in `skills/`, deployed to the target tool's skills dir — kiro: `~/.kiro/skills/`, claude: `~/.claude/skills/`, codex/agy: `.agents/skills/`):
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
- `archwright-passup` — consume check violations, lift to the owning level, route per confidence (★★→HITL, ★→propose, —→auto-adjust)

**Steering** (source in `steering/`, deployed to the tool's rules dir — kiro: `~/.kiro/steering/`, claude: `~/.claude/rules/`; codex/agy have no native equivalent — deploy prints wiring guidance):
- `archwright-conventions.md` — pipeline phase discipline, quality gates
- `subagent-reliability.md` — failure handling for parallel dispatch

**Tools** (`tools/`, invoked via interpreter — see Commands):
- `archwright-validate.py` — schema + link validation; `archwright-check.py` — check dispatcher (static/trace/Alloy)
- `archwright-compile-alloy.py` — behavior spec → Alloy 6 model; `archwright-check-compile.mjs` — intent → check blocks
- Templates for patterns and each spec kind (`tools/templates/`)
- `deploy-skills.sh` — sync skills + steering + domain overlays + glossary from repo to the target tool's discovery dirs (`--tool kiro|claude|codex|agy`, default kiro global; `--project <path>` for project scope)

**Workflow:** Edit skills/steering in this repo → commit → run `tools/deploy-skills.sh` to push to global.

## Project Type

Research + design-theory project transitioning to implementation. Primary outputs: skills, tools, schemas, documentation.

## Commands

Preferred: `mise run <task>` (managed toolchain + env — see Dependency Rehydration). Tasks: `validate`, `validate-links`, `check-static`, `test`, `deploy-skills`, `setup`, `rehydrate-alloy`. Without mise, tools are not on PATH — invoke via interpreter (verified 2026-07-16, `.memory/audit/tools.md`):

| Task | Command |
|------|---------|
| Validate pattern/spec | `python3 tools/archwright-validate.py [--json] <file>...` — validates all kinds incl. contract; emits non-fatal `WARN:` lines (e.g., missing `protects_experience`); `--json` emits the CK-03 document shape |
| Validate links | `python3 tools/archwright-validate.py [--json] --links <dir>` |
| Check spec(s) | `python3 tools/archwright-check.py <spec>... [--json] [--baseline <file>] [--update-baseline] [--evidence <file>]` — exit 0 pass / 1 violations / 2 tool error; `--json` emits status/scope/violations (w/ provenance, severity, escalate, contrast_pair, aw/v1 fingerprints)/coverage/remaining_delta. Baseline (CK-07/08): `.archwright-baseline.json` (auto-discovered up-tree or `--baseline`) suppresses known constraint/dependency violations to warnings (★★ keeps escalate; behavior/trace never suppressed); `--update-baseline` removes resolved entries, never adds (refuses on errored runs). Evidence ledger (ADR 0009): an EXISTING `.archwright-evidence.json` up-tree (or `--evidence`) auto-appends demotion/promotion candidates (deduped; malformed = exit 2; ratification stays human) |
| Batch static check | `python3 tools/archwright-check.py --static <dir> [--target <root>]` |
| Validate trace | `python3 tools/archwright-check.py --trace <spec.yaml> <trace.json> [--json]` — untranslatable predicates SKIP-with-reason (`invariants_skipped`/`guards_skipped` in output), never silent-pass (ticket 015); `--json` emits the CK-03 document (violations w/ full routing fields, skips[]) instead of the bespoke replay shape (ticket 016) |
| Non-vacuity probe | `python3 tools/archwright-check.py --probe <behavior-spec.yaml>` — injects a false invariant; exit 0 = counterexample produced (good), 1 = vacuous model, 2 = not probeable |
| Generate force files | `python3 tools/archwright-forces-gen.py <inventory.yaml> [-o <dir>]` — working inventory → design/forces/*.md |
| Compile to Alloy | `python3 tools/archwright-compile-alloy.py <spec.yaml>` |
| Audit docs vs code | `archwright-audit` (skill-driven, not a script) |
| Run Alloy model | `java -Djava.awt.headless=true -jar .references/alloy6.jar exec <model.als>` (jar not in repo — `.references/` is gitignored; behavior checks SKIP without it) |
| Deploy skills | `mise run deploy-skills` or `bash tools/deploy-skills.sh [--project <path>]` |
| Run fixture tests | `mise run test` (or `tools/run-fixture-tests.sh`) — 85 checks incl. Alloy behavior + guard-compilation + forces-gen/probe conformance + stack-adapter conformance (ts trace emitter) + check-tool feature tests + pending-coverage (CK-06) + baseline fingerprints/suppression/ratchet (CK-07/08) + evidence ledger (ADR 0009 / ticket 017) + trace strict-mode (ticket 015) + trace CK-03 document (016) + vacuous-absent guard (012) + from_model boundary-producer/fold resolution (013) + pattern-status gated (011) (SKIPs with reason if alloy6.jar, java, or node absent; green = 85/0/0 — **this row is the single source for the count; elsewhere say "suite green"**) |

Note: `archwright-check.py` flags are `--static`, `--trace`, `--probe`, `--all`, `--target`, `--json`, `--baseline`, `--update-baseline`, `--evidence` only — there is no `--structural`, `--deep`, `--project`, or `--model` flag (verified 2026-07-16, `.memory/audit/tools.md`; baseline flags added CK-07/08, `--evidence` added ticket 017, 2026-07-18).

## Dependency Rehydration

`.references/` is gitignored — external binaries must be re-fetched on a fresh clone or new machine.

**Primary path — mise** (`mise.toml` at repo root manages tools, env, and tasks):

```bash
# Bootstrap mise once: winget install jdx.mise | brew install mise | https://mise.run
mise trust && mise install     # python 3.12, temurin-21, node 22, smcat
mise run setup                 # pyyaml
mise run rehydrate-alloy       # Alloy 6.2.0 dist jar → .references/alloy6.jar
mise run test                  # verify: suite green, 0 failed, 0 skipped (count in Commands table)
```

`mise.toml` also sets `PYTHONIOENCODING=utf-8` and `ARCHWRIGHT_ALLOY_JAR` automatically inside the repo. Prefer `mise run <task>` (see Commands) — tasks run with the managed toolchain on PATH.

**Fallback — manual installs** (machines without mise):

| Dependency | Needed for | Rehydrate |
|------------|-----------|-----------|
| `alloy6.jar` (Alloy ≥ 6.2.0 — the `exec` CLI was added in 6.2.0) | behavior checks | `curl -L -o .references/alloy6.jar https://github.com/AlloyTools/org.alloytools.alloy/releases/download/v6.2.0/org.alloytools.alloy.dist.jar` |
| Java (JVM, `java` on PATH) | running the Alloy jar | `winget install EclipseAdoptium.Temurin.21.JRE` / `brew install temurin` / `apt-get install default-jre` |
| Python 3 + PyYAML | all tools | `pip install pyyaml` |
| `smcat` (state-machine-cat) | model/diagram FSM rendering (optional) | `npm i -g state-machine-cat` — PNG output also needs Graphviz `dot` |
| `merman-cli` | model/diagram Mermaid rendering (optional) | `cargo install merman-cli` (not in mise.toml — avoids pulling a Rust toolchain for an optional renderer) |
| `semgrep` | review AST checks (optional) | `pipx install semgrep` |

Notes:
- `archwright-check.py` locates the jar via `ARCHWRIGHT_ALLOY_JAR`, then script-relative `.references/alloy6.jar`, then the legacy `~/code/archwright/` path. Behavior checks report SKIP (exit 0) when it's absent — a coverage gap, not a pass.
- Missing diagram renderers never block a phase — skills fall back to presenting unrendered Mermaid/smcat source.
- Windows: bare `python3` resolves to a broken MS Store stub, and mise's python ships only `python.exe` — use `mise exec -- python` or `mise run` tasks (`run-fixture-tests.sh` has its own python3→python guard). Without mise, real Python is at `%LOCALAPPDATA%\Programs\Python\Python312\python.exe` and `PYTHONIOENCODING=utf-8` must be set manually (★ output vs cp1252 console).
- After ANY merge from upstream: `mise run test` (suite green). Kiro-global skills are symlinked into this repo (since 5d450bf) and track edits automatically — re-run `mise run deploy-skills` only for newly added skills or when deploying to other tools (claude/codex/agy), whose copies go stale silently.
- After rehydrating the jar, run `mise run test` — the behavior + guard-conformance skips become active checks (green = 0 failed, 0 skipped; count in Commands table).

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

- **HITL-blocking (always stop):** resolve (decisions; pre-resolved = one batched confirmation), L4/L5 desire validation in forces, ★★ events surviving the ADR-0010 research gate (genuine new decisions arrive w/ research + recommendation; noise/known are proposed/logged; unratified assignment & demotion always block), fog (unknown forces mid-span), end-of-span digest acceptance.
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

- Project-specific steering: add to the tool's project rules dir in this repo (kiro: `.kiro/steering/`, claude: `.claude/rules/`)
- Domain terms: keep `.memory/CONTEXT.md` current
- Decisions: record in `.memory/adr/` using ADR format
