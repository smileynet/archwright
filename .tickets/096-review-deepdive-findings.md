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

Out of scope here: the field run itself (023 owns it), Windows suite gaps
(058–060 own those), packaging manifests (095 owns those).

## What to build

Phase A — Triage (read-only):
1. Re-validate each finding above against the current tree before acting
   (line numbers drift; confirm each claim with fresh evidence).
2. For each finding classify: implement now / defer-with-ticket /
   reject-with-reason. Record the triage table in the Resolution below.

Phase B — Implement the cheap wins (expected to validate):

3. **argparse `--help` for both primary CLIs** — migrate
   `archwright-check.py` + `archwright-validate.py` main-entry flag parsing
   to argparse (or add a help path) without changing any existing flag or
   exit-code semantics (0 pass / 1 violations / 2 tool error). All current
   invocations in `tools/run-fixture-tests.sh` must behave identically.
4. **Decouple Alloy verdict extraction** — isolate solver-output parsing into
   one function with a documented contract; add a fixture test feeding a
   synthetic verdict-format variant to prove a jar-bump fails loud (exit 2)
   rather than silent-passes. Do NOT widen acceptance of malformed output.
5. **Split `archwright-check.py`** — mechanical extraction into modules under
   `tools/check/` (e.g., fingerprints, ledger, scoping, backends/, replay,
   coverage, pbt), keeping the CLI entry stable and `archwright_common.py`
   untouched. No behavior change: `mise run test` stays green at the same
   count with zero skips. If the split proves riskier than valuable mid-work,
   stop at module boundaries that are clean and record why in Resolution —
   partial delivery is acceptable, silent half-refactor is not.

Phase C — Evidence externalization practice:

6. Add a short section to `steering/archwright-conventions.md` (or AGENTS.md
   Key Constraints) establishing that field runs must deposit a sanitized,
   committed digest artifact (counts, violations found/fixed, timings) into
   this repo — so "field-proven" claims become inspectable. One paragraph +
   template pointer; do not invent retroactive digests for past runs.

## Acceptance criteria

- [ ] Triage table recorded in Resolution with fresh evidence per finding
      (validated / rejected + reason)
- [ ] `python3 tools/archwright-check.py --help` and
      `python3 tools/archwright-validate.py --help` print usage and exit 0;
      no flag behavior changed
- [ ] Fixture suite green: same check count as before this ticket, 0 failed,
      0 skipped (count updated in AGENTS.md Commands row if it changes)
- [ ] New fixture proves Alloy-format break → exit 2 (loud), not silent pass
- [ ] check.py split (if completed): imports work standalone, CLI entry
      unchanged, `git diff` shows no semantic edits inside extracted code
- [ ] Evidence-digest convention written into steering/AGENTS.md
- [ ] Scope check: `git diff` touches only files this ticket names plus the
      ticket file itself
