---
id: 028
title: "Sanitized example projects across the project-state spectrum"
status: done
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

Decided 2026-07-19 (operator + recommendation accepted as default): **one toy
product expressed at three states**, so browsing the diff between states shows
the lifecycle — plus greenfield as narrative, not a directory (git cannot track
an empty dir; nothing to browse or mechanically assert; survey is skill-driven).

| State | Contents | What it demonstrates |
|-------|----------|----------------------|
| State 0: greenfield | covered in `examples/README.md` only | entry path: survey on an empty project → discovery track; points at `planned/` as the landing state |
| `examples/planned/` | complete `design/` (forces, patterns, models, specs), no code | pipeline output shape; checks SKIP/pending against absent targets |
| `examples/partial/` | `design/` + partial code | mixed check results: passes, real FAILs, pending adapters, baseline usage |
| `examples/complete/` | `design/` + complete code | quiescence: suite green, evidence ledger accumulating pass streaks |

## What to build

- One small, coherent toy product (sanitized — no proprietary/personal
  content) at each state under top-level **`examples/`** (decided 2026-07-19:
  user-documentation placement wins; the suite reads from `examples/`, while
  smaller targeted tool corpora stay in `tests/fixtures/`).
- `examples/README.md`: the lifecycle walkthrough incl. state 0, and what a
  user should notice per state (check output, provenance chains, gaps).
- Each state ships with a README: what state this project is in, what
  archwright phases have run, what to look at.
- Wire into `run-fixture-tests.sh`: each state validates (`validate` +
  `--links`) and checks (`--static`) with EXPECTED results asserted —
  including the partial state's deliberate FAILs (Extension Protocol rule 4:
  violating scenarios prevent vacuous checkers).
- Existing fixtures (fieldball-coach, guarded-counter, discovery corpus) stay
  as-is — they are targeted tool corpora, not lifecycle examples. Reuse
  content where it helps, don't consolidate.

## Acceptance criteria

- [ ] Toy product exists at planned/partial/complete under `examples/`, sanitized, with per-state README
- [ ] `examples/README.md` covers the lifecycle incl. state-0 greenfield entry path
- [ ] Suite asserts expected validate/check results per state (incl. deliberate FAILs in partial)
- [ ] Suite green; count updated in AGENTS.md Commands test row only
- [ ] Top-level README or AGENTS.md points users at the examples
