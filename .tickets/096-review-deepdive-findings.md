---
id: "096"
title: "Triage deep-dive findings; implement validated in-repo improvements"
status: open
blocked_by: []
---

# Triage deep-dive findings; implement validated in-repo improvements

## Context

A full deep-dive review (2026-08-23) verified the tooling is real and working —
`mise run test` → 164 passed, 0 failed, 0 skipped (matches AGENTS.md exactly);
Alloy probe produces genuine counterexamples; implementation depth confirmed by
reading (Kleene three-valued predicate translation, SARIF-style fingerprints,
skip-with-reason everywhere). It also surfaced debts and one credibility gap.
Full notes were in `.scratch/research/{tooling,project-state}.md` (ephemeral,
gitignored — substance carried here).

**Key findings from the review:**

1. `tools/archwright-check.py` is a 2,636-line monolith doing ≥10 jobs
   (fingerprinting, evidence ledger, git scoping, grep/script/semgrep backends,
   trace replay, coverage, PBT dispatch). Wide blast radius per change; the
   suite catches regressions but the monolith taxes evolution.
2. Neither primary CLI has `--help` (hand-rolled argv parsing) — `--help`
   parses as a filename and fails. Hostile to discovery for anyone not
   running via the owning skills.
3. Alloy verdict extraction is regex over solver stdout/stderr
   (`check_behavior`, ~check.py:520) — brittle to any jar bump. Mitigated by
   fail-loud on missing verdict, but still an operational pin.
4. Field-use claims (FBC, TileRush, DemoAR/VR) are detailed and internally
   consistent but leave **zero independently inspectable artifacts** in this
   repo — every cited path lives outside it. Verification loop is fully
   self-referential in-repo (AI-authored specs vs AI-authored fixtures;
   `examples/` explicitly synthetic).
5. GDScript adapters all pending; only python/ts trace_emitters are ★★.
6. Trajectory: backlog exhausted (90/95 done before this ticket), last ADR
   Jul 27, momentum stalled awaiting a field driver.

## Triage (2026-08-23, re-validated against current tree)

| # | Finding | Verdict | Evidence |
|---|---------|---------|----------|
| 1 | check.py monolith (2,636 LOC) | **Defer → ticket 097** (high pri) | `wc -l` = 2636; `main()` is 315 lines of cascading `sys.argv[1] ==` checks |
| 2 | No `--help` on either CLI | **Implement here** | Both use raw `sys.argv` slicing; `--help` would be treated as a filename path |
| 3 | Alloy verdict regex brittle | **Implement here** | Lines 517-522: single inline `re.finditer` over combined stdout+stderr; already fail-loud but not fixture-proven |
| 4 | Field claims have no in-repo artifacts | **Implement here (convention)** | Confirmed: no `design/report/` or digest committed in this repo for any field run |
| 5 | GDScript adapters pending | **Reject** | By design — Extension Protocol allows pending-with-reason; no target project available |
| 6 | Momentum stalled | **Reject** | Observational; not actionable as a code change |

## What to build

With the monolith split deferred to 097, this ticket covers the three cheap wins:

### 1. argparse `--help` for both primary CLIs

Migrate `archwright-check.py` and `archwright-validate.py` main-entry flag
parsing to argparse. Preserve all existing flags and exit-code semantics
(0 pass / 1 violations / 2 tool error). All invocations in
`tools/run-fixture-tests.sh` must behave identically.

### 2. Isolate Alloy verdict extraction + fixture

Extract `parse_alloy_verdicts(combined_output: str) -> dict[str, str]` as a
named function with a docstring documenting the expected format. Add a fixture
test in `tools/run-fixture-tests.sh` that feeds synthetic malformed Alloy
output and asserts exit 2 (loud failure), not silent pass.

### 3. Evidence-digest convention

Add a short section to AGENTS.md Key Constraints (or
`steering/archwright-conventions.md`) establishing that field runs must deposit
a sanitized, committed digest artifact (counts, violations found/fixed,
timings) into this repo — so "field-proven" claims become inspectable. One
paragraph + template pointer; do not invent retroactive digests for past runs.

## Acceptance criteria

- [ ] Triage table recorded (above) with fresh evidence per finding
- [ ] `python3 tools/archwright-check.py --help` and
      `python3 tools/archwright-validate.py --help` print usage and exit 0;
      no flag behavior changed
- [ ] Fixture suite green: 164 passed, 0 failed, 0 skipped
- [ ] New fixture proves Alloy-format break → exit 2 (loud), not silent pass
- [ ] Evidence-digest convention written into AGENTS.md or steering
- [ ] Scope check: `git diff` touches only tools/archwright-check.py,
      tools/archwright-validate.py, tools/run-fixture-tests.sh, AGENTS.md or
      steering/archwright-conventions.md, and this ticket file

## Validation criteria

- `python3 tools/archwright-check.py --help` → exit 0, prints flags
- `python3 tools/archwright-validate.py --help` → exit 0, prints usage
- `mise run test` → 164/0/0 (or count+1 for the new Alloy fixture)
- grep for new fixture in `run-fixture-tests.sh` confirms malformed-verdict test exists
