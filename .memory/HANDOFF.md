---
created_at: 2026-07-08T06:17:00-07:00
base_commit: 79c784f
handoff_key: archwright-core
---

# Handoff

## Objective
Build archwright — a force-resolution design methodology (agent skills + tools) that resolves human design intent into verified architecture. Proven end-to-end; now needs real-world scaling validation and deployment.

## Constraints
- Agent IS the system (ADR 0001). Skills hold methodology; tools are mechanical servants on PATH.
- "Resolves into" not "compiles to" (ADR 0003). Creative resolution + formal verification.
- Full architecture scope (ADR 0002). Behavior + contract + constraint + dependency kinds.
- Flat typed specs linked via `kind:id` (ADR 0004). Markdown for human-read, YAML for machine-read.
- Alloy is prototyping backend. Lean is future ★★ path. Neither is permanent dependency.
- State explosion limits Alloy to abstracted models (V2 proved trace length > scope matters for games).

## Prior Decisions
- 14 grill decisions (docs synced, ADRs written, grill scratch deleted)
- Findings 1-12 in `docs/findings.md`; prior art sections 1-8 in `docs/prior-art.md`
- Growth rules + context assembly adopted from Spec Growth Engine paper (Grabowski 2026)

## Current State
- **Skills:** `~/.kiro/skills/archwright/` (SKILL.md + 4 references), `~/.kiro/skills/archwright-check/`
- **Tools:** `tools/archwright-validate` (working), `tools/archwright-check` (working), `tools/archwright-compile-alloy` (scaffold-only)
- **Fixture:** `tests/fixtures/lacrosse-bosse/` — 14/14 checks pass (`tools/run-fixture-tests`)
- **Schemas:** `tools/pattern-schema.yaml` (v0.2), `tools/spec-schema.yaml` (behavior v0.2)
- **Templates:** `tools/templates/` — pattern.md, spec-behavior.yaml, spec-contract.yaml, spec-constraint.md, spec-dependency.md
- **Design artifacts in lacrosse-bosse-platform:** `~/code/lacrosse-bosse-platform/design/` (3 patterns, 6 specs — created but not committed there)

## Next Steps
1. **S9: Abstraction quality** — model real lacrosse-bosse execution subsystem in Alloy. Does it scale? (`next-work-proposals.md`)
2. **S13: Drift gate CI** — make `archwright-check --all` a merge blocker (pre-commit hook or GH Action)
3. **Deploy to lacrosse-bosse-platform** — commit `design/` directory in that repo, run checks against real code
4. **R18/R19 refinement** — test growth rules and context assembly in practice during deployment
5. **V1, V3, V4, V6** — remaining validation spikes (lower priority, in `.memory/validation-spikes.md`)

## Evidence
- Alloy checks: 94ms counterexample finding (S5), contrast pairs in 198ms (S6), game predicates work (S7)
- V2 disproved "scope 3 = 90%" for games (trace length matters more): `.memory/validation-results-v2-v5.md`
- V5 found prior art (Mawhorter 2021 softlock detection): same file
- SGE paper intake: `.scratch/research/spec-growth-engine.md`
- Lean research: `.scratch/research/lean-for-archwright.md`
