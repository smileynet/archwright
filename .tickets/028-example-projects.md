---
id: 028
title: "Sanitized example projects across the project-state spectrum"
status: open
blocked_by: []
---

# Sanitized example projects (fixtures + browsable documentation)

Create a set of small, sanitized example projects demonstrating how archwright
interacts with projects at different lifecycle states. Dual purpose:

1. **Fixtures** — test corpora for the suite that evolve as current-state
   examples whenever the methodology or schemas change (unlike frozen golden
   corpora, these track "what good looks like today").
2. **User documentation** — browsable references so users can see what
   archwright produces and expects at each state, before running it on their
   own project.

## Project states to cover

| State | Contents | What it demonstrates |
|-------|----------|----------------------|
| Greenfield | no design, no code | survey on empty project → discovery track entry |
| Fully planned | complete `design/` (forces, patterns, models, specs), no code | pipeline output shape; checks SKIP/pending against absent targets |
| Partially implemented | `design/` + partial code | mixed check results: passes, real FAILs, pending adapters, baseline usage |
| Fully implemented | `design/` + complete code | quiescence: suite green, evidence ledger accumulating pass streaks |

(User phrasing "fully planned, no code, partially implemented, fully
implemented" — resolve at implementation whether greenfield is a distinct
fourth state or folded into fully-planned; the table above assumes distinct,
since empty-project survey behavior is otherwise undemonstrated.)

## What to build

- One small, coherent example domain (sanitized — no proprietary/personal
  content; invent a toy product) expressed at each state, under
  `tests/fixtures/examples/<state>/` (or `examples/<state>/` if user-facing
  placement wins — decide at implementation; browsability argues for a
  top-level `examples/` with the suite reading from it).
- Each state ships with a README: what state this project is in, what
  archwright phases have run, what a user should notice (check output,
  provenance chains, gaps).
- Wire into `run-fixture-tests.sh`: each state validates (`validate` +
  `--links`) and checks (`--static`) with EXPECTED results asserted —
  including the partial state's deliberate FAILs (Extension Protocol rule 4:
  violating scenarios prevent vacuous checkers).
- Existing fixtures (lacrosse-bosse, guarded-counter, discovery corpus) stay
  as-is — they are targeted tool corpora, not lifecycle examples. Reuse
  content where it helps, don't consolidate.

## Acceptance criteria

- [ ] Example project exists at each agreed state, sanitized, with per-state README
- [ ] Suite asserts expected validate/check results per state (incl. deliberate FAILs in partial)
- [ ] Suite green; count updated in AGENTS.md Commands test row only
- [ ] Top-level README or AGENTS.md points users at the examples
