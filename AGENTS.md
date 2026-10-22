# AGENTS.md — Archwright

AI-assisted design system that resolves human design intent (expressed as a force-resolution language) into verified architecture, with traceable bidirectional flow.

## Where things are

- `skills/archwright-*/`, `steering/`: **shipped** skills and steering (product, not this repo's agent layer). Deployed by `tools/deploy-skills.sh`; the kiro-global copies are symlinks into this repo, so edits go live everywhere at once. One-liners: each SKILL.md `description`; index: §What Archwright Is.
- `tools/`: mechanical servants. Map: `tools/README.md`; usage contract: §Commands. Also `tools/check/` (check internals package, ticket 097: common, baseline, ledger, conformance, alloy, trace, coverage, imported by the `archwright-check.py` dispatcher) and `tools/report/` (report generator, ticket 041: `generate.py` CLI, `derive.py`, `vocab.py` + `vocabulary.yaml`, `render_html/md.py`, `templates/`; reads ONLY the CK-03 doc + `design/` YAML per `dependency:report-reads-canonical-only`; writes `design/report/` in the target project, gitignored here). Templates, domain overlays, stack adapters: `tools/{templates,domains,stacks}/` (adapter status: `tools/stacks/REGISTRY.yaml`, computed by the suite).
- `docs/`: user-facing theory docs (index: `README.md` § docs table) and `docs/glossary.md`, the **shipped** methodology glossary (deployed into `archwright-survey/references/`). `figures/`: SVGs (see `figures/README.md`).
- `GLOSSARY.md`: this repo's agent vocabulary. `docs/adr/`: decision records.
- `docs/agents/`: agent-facing reference — `PLAN.md` (authoritative work status; read its STATUS header, don't duplicate plan state elsewhere), `specs/` (requirements specs for plan deliverables), `grill/` (grill decision records: INDEX.md + Q-files), `audit/`, `lessons/` (one lesson per file + README index), `research/`, `reflections/global.md`, `spikes/`, `reviews/`, `self-run/`, `DEPRECATED.md` (removal queue reviewed by the repo-maintenance audit), `research/adoption-2026-10-22/` (adoption evidence).
- `design/`: archwright run on itself. `examples/{planned,partial,complete}/`: one toy product (Snackbox) at three lifecycle states (see `examples/README.md`). `tests/fixtures/`: suite corpora.
- `audit-plan.md`: audit plan, CLOSED 2026-07-18 (all 7 DoD verified; see §Plan Close-Out).
- `.kiro/skills/repo-maintenance/`: project-local skill for the suite and deploy scripts (never deployed globally).
- `.tickets/`: tkt board. `mise.toml`: toolchain + env + tasks. `.references/`: gitignored (see its README). `.scratch/`: ephemeral.

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
- `archwright-report` — generate, publish, and consume design reports (interactive HTML diagrams, vocabulary overrides, response handling)
- `archwright-review` — review code for design alignment (structural + behavioral + semantic)
- `archwright-audit` — audit docs for truth (surface contradictions between docs and code)
- `archwright-diagram` — render models/patterns as Mermaid diagrams
- `archwright-passup` — consume check violations, lift to the owning level, route per confidence (★★→HITL, ★→propose, —→auto-adjust)
- `archwright-discover-ui` — discovery track: UI sessions producing ledger-backed decisions that graduate at the resolve seam (ADR 0011)
- `archwright-woz-import` — discovery track: import wizard_of_oz session exports (tool converts, skill interprets — ticket 025)

**Steering** (source in `steering/`, deployed to the tool's rules dir — kiro: `~/.kiro/steering/`, claude: `~/.claude/rules/`; codex/agy have no native equivalent — deploy prints wiring guidance):
- `archwright-conventions.md` — pipeline phase discipline, quality gates
- `subagent-reliability.md` — failure handling for parallel dispatch

**Tools** (`tools/`, invoked via interpreter — see Commands):
- `archwright-validate.py` — schema + link validation; `archwright-check.py` — check dispatcher (static/trace/Alloy/semgrep; coverage reports)
- `archwright-compile-alloy.py` — behavior spec → Alloy 6 model; `archwright-check-compile.mjs` — intent → check blocks
- Templates for patterns and each spec kind (`tools/templates/`)
- `deploy-skills.sh` — sync skills + steering + domain overlays + glossary from repo to the target tool's discovery dirs (`--tool kiro|claude|codex|agy`, default kiro global; `--project <path>` for project scope)

**Tool→skill ownership** (which skill carries each tool's usage + output-interpretation contract — keep current when flags or output change):

| Tool | Owning skill |
|------|--------------|
| `archwright-check.py`, `archwright-validate.py`, `archwright-compile-alloy.py` (debug use) | `archwright-check` |
| `tools/report/generate.py` (bundle generation; response-file consumption contract) | `archwright-report` |
| `archwright-check-compile.mjs`, `alloy:` expression authoring | `archwright-derive` |
| `archwright-forces-gen.py` | `archwright-forces` |
| `archwright-import-woz.py` | `archwright-woz-import` |
| `run-fixture-tests.sh`, `deploy-skills.sh` | `.kiro/skills/repo-maintenance` — project-local, never deployed globally (2026-07-18; supersedes "no skill, this file is their home") |
| `tools/templates/discovery-ledger.md`, `wireframe.md`, `design-system.md` (artifact contracts) | `archwright-discover-ui` |
| `tools/report/capture.mjs`, `tools/report/visual-battery.md`, `tools/report/probes/` (visual-conformance harness + validation probes, tickets 044/047 — review-track) | `archwright-review` |
| `tools/templates/pattern.md`, `force.md`, `spec-*.{yaml,md}` (authoring templates) | `archwright-formalize` (pattern), `archwright-forces` (force), `archwright-derive` (behavior/constraint/dependency), `archwright-contract` (contract) |
| `archwright_common.py` | none — shared module, not a CLI |

**Workflow:** Edit skills/steering in this repo → commit. Kiro-global copies are symlinks (live immediately); run `tools/deploy-skills.sh` only for NEW skills, generated references (domains/stacks/glossary), or other tools (claude/codex/agy — their copies go stale silently). Contract details: `.kiro/skills/repo-maintenance`.

## Project Type

Research + design-theory project transitioning to implementation. Primary outputs: skills, tools, schemas, documentation.

## Commands

Preferred: `mise run <task>` (managed toolchain + env — see Dependency Rehydration). Tasks: `validate`, `validate-links`, `validate:tickets`, `check-static`, `test`, `ship` (`mise run ship -- "msg"` — commits STAGED files only + pushes, blocking on upstream divergence; prefer it over hand-rolled add/fetch/commit/push), `deploy-skills`, `setup`, `rehydrate-alloy`. Without mise, tools are not on PATH — invoke via interpreter (verified 2026-07-16, `docs/agents/audit/tools.md`):

| Task | Command |
|------|---------|
| Validate pattern/spec | `python3 tools/archwright-validate.py [--json] <file>...` — validates all kinds incl. contract, discovery, and model (048: shape-detected via top-level `actors`, kind field optional) (ticket 026: frontmatter schema, ledger entry structure, nothing-invented conservation; approved = errors, proposed = warnings); emits non-fatal `WARN:` lines (e.g., missing `protects_experience`); `--json` emits the CK-03 document shape |
| Validate links | `python3 tools/archwright-validate.py [--json] --links <dir>` — incl. discovery citation resolution + nothing-lost conservation (active ledger entries must be consumed or explicitly deferred) |
| Check spec(s) | `python3 tools/archwright-check.py <spec>... [--json] [--baseline <file>] [--update-baseline] [--evidence <file>]` — exit 0 pass / 1 violations / 2 tool error; `--json` emits status/scope/violations (w/ provenance, severity, escalate, contrast_pair, aw/v1 fingerprints)/coverage/remaining_delta. Baseline (CK-07/08): `.archwright-baseline.json` (auto-discovered up-tree or `--baseline`) suppresses known constraint/dependency violations to warnings (★★ keeps escalate; behavior/trace never suppressed); `--update-baseline` removes resolved entries, never adds (refuses on errored runs and under `--changed-only` — a scoped run cannot prove absence). Evidence ledger (ADR 0009): an EXISTING `.archwright-evidence.json` up-tree (or `--evidence`) auto-appends demotion/promotion candidates (deduped; malformed = exit 2; ratification stays human) |
| Batch static check | `python3 tools/archwright-check.py --static <dir> [--target <root>] [--changed-only [--base <ref>]]` — `--changed-only` (CK-19) runs only specs affected by the git diff vs `<ref>` (default HEAD): spec file changed, or changed/untracked file under a `check.target`; no-file-target specs always run; git failure = exit 2 |
| Validate trace | `python3 tools/archwright-check.py --trace <spec.yaml> <trace.json> [--json]` — untranslatable predicates SKIP-with-reason (`invariants_skipped`/`guards_skipped` in output), never silent-pass (ticket 015); `--json` emits the CK-03 document (violations w/ full routing fields, skips[]) instead of the bespoke replay shape (ticket 016) |
| Non-vacuity probe | `python3 tools/archwright-check.py --probe <behavior-spec.yaml>` — injects a false invariant; exit 0 = counterexample produced (good), 1 = vacuous model, 2 = not probeable |
| Trace coverage | `python3 tools/archwright-check.py --trace-coverage <specs-dir> <traces-dir> [--json]` — reports which behavior spec scenarios have matching trace files (bare-array traces associate by filename, enveloped by `spec_id`); exit 0 = all covered, 1 = gaps, 2 = tool error (repaired + conformance-tested, ticket 043) |
| Spec coverage | `python3 tools/archwright-check.py --coverage <specs-dir> [--target <root>] [--json]` — reports spec→implementation coverage (implemented/spec-ahead/no-target); informational, exit 0 on success, 2 on error (repaired + conformance-tested, ticket 043) |
| PBT check | `python3 tools/archwright-check.py --pbt <spec.yaml> --step <step.py> [--emit <dir>] [--examples N] [--json]` — generates Hypothesis stateful test from behavior spec, drives SUT via user step function, checks invariants under random event sequences; exit 0 pass / 1 fail / 2 error (ticket 091) |
| Generate force files | `python3 tools/archwright-forces-gen.py <inventory.yaml> [-o <dir>]` — working inventory → design/forces/*.md |
| Import WoZ session | `python3 tools/archwright-import-woz.py <export.json> [-o <design-dir>] [--force]` — woz-session/v1 JSON → `design/discovery/woz/` artifact (category mapping consumer-side; exit 1 = contract violation, 2 = usage/refusal) |
| Compile to Alloy | `python3 tools/archwright-compile-alloy.py <spec.yaml>` |
| Audit docs vs code | `archwright-audit` (skill-driven, not a script) |
| Run Alloy model | `java -Djava.awt.headless=true -jar .references/alloy6.jar exec <model.als>` (jar not in repo — `.references/` is gitignored; behavior checks SKIP without it) |
| Deploy skills | `mise run deploy-skills` or `bash tools/deploy-skills.sh [--project <path>]` |
| Publish report | `mise run report-publish -- --project <path> [--name <display>]` — generates report bundle (html+md+json) via check --all + generate.py, commits + pushes `design/report/` in the target project. HTML diagram: ELK Direct SVG (interactive, ~1.4MB inlined); markdown diagram: Mermaid stateDiagram-v2. Windows: git commit step may fail with temp-file errors — commit manually in the target project after generation succeeds |
| Run fixture tests | `mise run test` (or `tools/run-fixture-tests.sh`) — 165 checks (per-feature sections: the `=== … (ticket N) ===` headers in `tools/run-fixture-tests.sh`) (SKIPs with reason if alloy6.jar, java, node, or git absent; green = 0 failed, 0 skipped — **the count at the head of this row is the single source; elsewhere say "suite green"**) |

Note: `archwright-check.py` flags are `--static`, `--trace`, `--probe`, `--all`, `--target`, `--json`, `--baseline`, `--update-baseline`, `--evidence`, `--changed-only`, `--base`, `--trace-coverage`, `--coverage`, `--pbt` only — there is no `--structural`, `--deep`, `--project`, or `--model` flag (verified 2026-07-16, `docs/agents/audit/tools.md`; baseline flags added CK-07/08, `--evidence` ticket 017, `--changed-only`/`--base` CK-19, `--trace-coverage`/`--coverage` 2026-07-19, `--pbt` 2026-08-01).

## Dependency Rehydration

`.references/` is gitignored (index: `.references/README.md`) — external binaries must be re-fetched on a fresh clone or new machine.

**Primary path — mise** (`mise.toml` at repo root manages tools, env, and tasks):

```bash
# Bootstrap mise once: winget install jdx.mise | brew install mise | https://mise.run
mise trust && mise install     # python 3.12, uv, temurin-21, node 22, smcat + auto-creates .venv/
mise run setup                 # pyyaml + hypothesis (via uv pip, into .venv — <1s)
mise run rehydrate-alloy       # Alloy 6.2.0 dist jar → .references/alloy6.jar
mise run test                  # verify: suite green, 0 failed, 0 skipped (count in Commands table)
```

`mise.toml` also sets `_.python.venv` (auto-creates `.venv/` on directory entry), `PYTHONIOENCODING=utf-8`, and `ARCHWRIGHT_ALLOY_JAR` automatically inside the repo. Prefer `mise run <task>` (see Commands) — tasks run with the managed toolchain on PATH.

**Fallback — manual installs** (machines without mise):

| Dependency | Needed for | Rehydrate |
|------------|-----------|-----------|
| `alloy6.jar` (Alloy ≥ 6.2.0 — the `exec` CLI was added in 6.2.0) | behavior checks | `python3 tools/install-alloy.py` (pinned URL + SHA-256 verification via `tools/alloy-runtime.json`; the mise task delegates to this script) |
| Java (JVM, `java` on PATH) | running the Alloy jar | `winget install EclipseAdoptium.Temurin.21.JRE` / `brew install temurin` / `apt-get install default-jre` |
| Python 3 + PyYAML + Hypothesis | all tools (hypothesis: PBT) | `python -m venv .venv && . .venv/bin/activate && pip install pyyaml hypothesis` |
| `smcat` (state-machine-cat) | model/diagram FSM rendering (optional) | `npm i -g state-machine-cat` — PNG output also needs Graphviz `dot` |
| `merman-cli` | model/diagram Mermaid rendering (optional) | `cargo install merman-cli` (not in mise.toml — avoids pulling a Rust toolchain for an optional renderer) |
| `semgrep` | review AST checks (optional) | `pipx install semgrep` |
| `playwright` + chromium | report visual-conformance capture (optional, ticket 044) | `npm install && ./node_modules/.bin/playwright install chromium` — use `--registry=https://registry.npmjs.org/` if CodeArtifact auth is stale |

Notes:
- `archwright-check.py` locates the jar via `ARCHWRIGHT_ALLOY_JAR`, then script-relative `.references/alloy6.jar`, then the legacy `~/code/archwright/` path. Behavior checks report SKIP (exit 0) when it's absent — a coverage gap, not a pass.
- Missing diagram renderers never block a phase — skills fall back to presenting unrendered Mermaid/smcat source.
- Windows: bare `python3` resolves to a broken MS Store stub, and mise's python ships only `python.exe` — use `mise exec -- python` or `mise run` tasks (`run-fixture-tests.sh` has its own python3→python guard). Without mise, real Python is at `%LOCALAPPDATA%\Programs\Python\Python312\python.exe` and `PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1` must be set manually (★/— glyphs vs cp1252 console; `PYTHONIOENCODING` alone only fixes stdout, `PYTHONUTF8` fixes `open()` default encoding too).
- Windows: Smart App Control (SAC) blocks mise.exe (unsigned, no ISG reputation). Disable via Settings → Windows Security → App & browser control → Smart App Control → Off. Since April 2026 (KB5083769) this is **reversible** — no longer a permanent decision. Known Windows-specific suite gaps: tickets 058–060.
- After ANY merge from upstream — and BEFORE any push that touches `tools/` — `mise run test` (suite green at the final tree; commit messages are not evidence — see `docs/agents/lessons/port-diffs-not-files.md`), plus `mise run sanitize-check` (merges reintroduce real names — 2 hits on 2026-07-19; SKIPs without the machine-local denylist). Kiro-global skills are symlinked into this repo (since 5d450bf) and track edits automatically — re-run `mise run deploy-skills` only for newly added skills or when deploying to other tools (claude/codex/agy), whose copies go stale silently.
- After rehydrating the jar, run `mise run test` — the behavior + guard-conformance skips become active checks (green = 0 failed, 0 skipped; count in Commands table).

## Workflows

| Situation | Use |
|---|---|
| Extend the design language | add findings to `docs/`, terms to `GLOSSARY.md` (`domain-modeling`) |
| Explore an open question | pick from `docs/open-questions.md`, `research`, then an ADR in `docs/adr/` (`domain-modeling` ADR section) |
| Build tooling | scripts in `tools/` for validation, compilation, checking; run the suite (`repo-maintenance`) |
| Tracer bullet | encode fieldball-coach decisions as patterns + specs, verify |
| Pipeline on a new project | run the full pipeline (survey→check) on a target project, producing patterns + models + specs in its `design/` (rules: `steering/archwright-conventions.md`) |
| Planning a larger piece of work | `wayfinder`, then `to-spec` / `to-tickets` |
| Starting / ending a session | `orient` / `handoff` (wrap-up: `wrap-session`) |

## Tickets

`.tickets/` is tkt-managed (commands: the tkt block below; `tkt --help`). Repo rules tkt doesn't encode:

- Shared frontmatter contract (historical authority: crew-research `.memory/specs/ticket-cli-spec.md`); status vocabulary is frozen contract. Unknown fields (`created`, `closed`, `lane`, …) are preserved verbatim; ids are 3-digit `NNN-slug.md`.
- Claim before allocating (a pushed ticket is a claim). Motivating incidents: 005 double-implementation, 009/010 id race (`docs/agents/lessons/concurrent-sessions.md`).
- Manual fallback (tkt absent): same shapes by hand — rescan before allocating, set `status: in_progress` on claim and push, dated Resolution on close, merge into the lower/pushed ticket on collision.
- `docs/agents/PLAN.md` stays the authoritative status narrative; ticket frontmatter is the machine-readable layer. `mise run validate:tickets` checks the corpus (warnings advisory).
- Never use `tk` (unrelated third-party tool: reads `deps` not `blocked_by`, silently omits unparseable tickets).

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
- Discovery track (ADR 0011, `docs/adr/0011-discovery-track.md`) — HITL-dense discovery work feeds the mechanical pipeline at the `resolve` seam via decision ledgers; see the ADR for the seam contract and grill verdicts
- The agent IS the system; tools are mechanical servants
- Sanitized field references — committed content never names real target projects; field runs, fixtures, and lesson notes use the established invented aliases (fieldball-coach/FBC, fieldball-practice, TileRush, tilerush-demo, DemoAR, DemoVR — sanitized repo-wide 2026-07-19 and 2026-10-22). The real↔alias mapping lives outside the repo (formerly recall, now retired; machine-local `.sanitization-denylist` drives `mise run sanitize-check`; its home is under review, see `migration-finding` tickets). New field work aliases at the source, not in a cleanup pass
- Field-evidence convention — field runs deposit a sanitized digest into this repo (`field-evidence/<alias>-<date>.yaml`); "field-proven" claims require inspectable committed artifacts with expiry (see `steering/archwright-conventions.md` § Field-Evidence Convention). No retroactive fabrication
- Subagents extract (read files → structured output); main agent synthesizes (dedup, cluster, merge)

## Pipeline rules

The pipeline (`survey → forces → tensions → resolve → formalize → model → contract → derive → check`), its HITL-blocking vs flow-through gates (ADR 0007, `docs/adr/0007-hitl-only-gates.md`; ADR 0010 research gate), and the `design/{forces,patterns,models,specs}/` artifacts it writes into a target project are defined in `steering/archwright-conventions.md` (§Pipeline Phase Discipline, §Target Project Artifacts). That file is the single home; don't restate it here.

## References

- Alexander's *A Pattern Language* (1977) and *The Timeless Way of Building* (1979)
- Harel statecharts / XState
- Alloy / lightweight formal methods (counterexample-driven)
- CEGAR (Clarke et al., 2000/2003)
- Mawhorter & Smith (FDG 2021) — softlock detection via CTL
- Rezin et al. (2017) — model checking multiplayer games
- Lean 4 / CSLib / Veil — future unbounded verification backend
- Kleppmann (2025) — AI + formal verification mainstream prediction

## Gotchas

- **Tickets tagged `migration-finding`** are unconfirmed outside-audit findings from the
  grey-matter adoption (2026-10-22). Review first: reproduce each point, then confirm, reject, or
  re-scope it before changing anything.
- **`.memory/` in shipped skills and steering means the *target project's* `.memory/`**, not this repo's (this repo's moved to `GLOSSARY.md`, `docs/adr/`, `docs/agents/` on 2026-10-22). Don't bulk-rewrite those mentions.
- **Fresh venv:** `mise run test` needs `mise run setup` first (pyyaml + hypothesis); without it nearly every check fails on `ModuleNotFoundError: yaml`.

## Customization

- Project-specific steering: add to the tool's project rules dir in this repo (kiro: `.kiro/steering/`, claude: `.claude/rules/`)
- Domain terms: keep `GLOSSARY.md` current
- Decisions: record in `docs/adr/` using ADR format

<!-- tkt:begin -->
## Tickets

This project uses [tkt](https://github.com/smileynet/tkt) for work tracking. Tickets live in `.tickets/`.

```
tkt ready                                         # what to work on next
tkt claim <id>                                    # mark as in_progress (shared repos)
tkt close <id> --check-all --evidence "..." --resolution "..."  # mark done (--evidence: 1 per validation criterion, repeatable)
tkt new <slug> --title "..." [--tags stream]      # create work (defaults to open, on the frontier)
tkt edit <id> --status backlog                    # park a ticket off the frontier (deferred work)
tkt validate --brief                              # check for issues
```

### Status lifecycle

`open` (frontier-eligible, the default) → `in_progress` → `done`; `backlog` = parked, invisible to `ready`.

New work defaults to `open`. Use `--status backlog` only for work deliberately deferred out of this cycle — not for discovered work that's actually actionable.

Reach `done` only via `tkt close` — never edit a ticket's status to `done` by hand (it skips the close gates).

### Workflow

Single-agent: `tkt ready` → `tkt close <id> --check-all --resolution "..."`
Shared-repo: `tkt ready` → `tkt claim <id>` → work → `tkt close <id> --check-all --resolution "..."`
Discovered work: `tkt new <slug> --title "..."` (open — a separate, actionable ticket; add `--blocked-by` if it depends on current work)
Migrated work: `tkt close <id> --force --resolution "Migrated to <project> #<id>"` (don't check ACs)

Tag new tickets with their work stream (`--tags <stream>`) in multi-stream projects — one tag is the norm.
If a claim push is rejected, someone else got there first — pick the next frontier ticket.
<!-- tkt:end -->
