---
id: "096"
title: "Triage deep-dive findings; implement validated in-repo improvements"
status: done
blocked_by: []
---

# Triage deep-dive findings; implement validated in-repo improvements

## Context

A full deep-dive review (2026-08-23) verified the tooling is real and working —
`mise run test` → 164 passed, 0 failed, 0 skipped (matches AGENTS.md exactly);
Alloy probe produces genuine counterexamples; implementation depth confirmed by
reading (Kleene three-valued predicate translation, SARIF-style fingerprints,
skip-with-reason everywhere). It also surfaced debts and one credibility gap.

**Key findings from the review:**

1. `tools/archwright-check.py` is a 2,636-line monolith doing ≥10 jobs →
   **deferred to ticket 097** (high priority)
2. Neither primary CLI has `--help` (hand-rolled argv parsing)
3. Alloy verdict extraction is regex over undocumented solver output
4. Field-use claims leave zero independently inspectable artifacts in this repo
5. GDScript adapters all pending — by design (Extension Protocol)
6. Trajectory stalled — observational, not actionable

## Triage (2026-08-23, re-validated against current tree)

| # | Finding | Verdict | Evidence |
|---|---------|---------|----------|
| 1 | check.py monolith (2,636 LOC) | **Defer → ticket 097** | `wc -l` = 2636; `main()` is 315 lines of cascading `sys.argv[1] ==` |
| 2 | No `--help` on either CLI | **Implement here** | Both use raw `sys.argv`; `--help` treated as filename |
| 3 | Alloy verdict regex brittle | **Implement here** | Lines 517-522: inline `re.finditer`; format undocumented/unversioned |
| 4 | Field claims no in-repo artifacts | **Implement here (convention)** | No digest committed for any field run |
| 5 | GDScript adapters pending | **Reject** | Extension Protocol allows pending-with-reason |
| 6 | Momentum stalled | **Reject** | Observational; not actionable as code |

## What to build

### 1. argparse `--help` for both primary CLIs

**Scope:** Migrate `archwright-check.py` and `archwright-validate.py`
main-entry flag parsing to argparse. All existing flags, exit codes, and
`run-fixture-tests.sh` invocations must behave identically.

**Design (from research + code review):**

check.py (17 flags, 5 early-return modes + main loop):
- Subclass `ArgumentParser`, override `error()` → always exit 2
- `allow_abbrev=False` — **critical**: `--trace` and `--trace-coverage` share
  a prefix; without this, `--trace` becomes ambiguous
- Mode flags via `store_const` with shared `dest='mode'`:
  `--trace`, `--probe`, `--trace-coverage`, `--coverage`, `--pbt`,
  `--all`, `--static` → `args.mode` is one string or None (bare files)
- `--json` as top-level flag (used across all modes)
- Per-mode required args validated in post-parse (e.g., `--trace` needs
  spec + trace file; `--pbt` needs `--step`)
- Cross-flag exclusion: `--update-baseline` + `--changed-only` → exit 2
  (custom validator, not argparse group — same existing error message)
- Positional spec files: `nargs='*'` — empty list = exit 0 (no specs = pass)
- `--evidence` shared between `--trace` and main loop modes

validate.py (simpler — 2 modes + 1 modifier):
- `--links <dir>` as a mutually exclusive alternative to positional files
- `--json` as global modifier
- Positional files: `nargs='+'` in default mode, `nargs=1` after `--links`

**Risk:** 5 fixture invocations put flags after positional args (e.g.,
`$CHECK <spec.md> --target <dir>`). argparse handles this naturally with
`parse_known_args` or positional `nargs='*'` — but must be verified against
the suite. If any break, investigate `parse_known_args` + manual residual
handling for those specific patterns.

### 2. Isolate Alloy verdict extraction + fixture

**Design (from research):**

The Alloy 6.2.0 `exec` CLI output format is **undocumented and unversioned**.
No JSON mode exists. All non-Java consumers parse via regex — archwright's
approach is standard. The pin-and-fixture defense is the best available.

Implementation:
- Extract `parse_alloy_verdicts(combined_output: str) -> dict[str, str]` from
  the inline regex at line ~520. Document the expected format in docstring:
  `NN. check <assertName> ... SAT|UNSAT`
- Return `{}` for no-verdict (caller already handles this as error)
- Add fixture in `run-fixture-tests.sh`: feed synthetic malformed output
  (e.g., remove SAT/UNSAT tokens, change format to `SATISFIABLE`/`UNSATISFIABLE`)
  through a spec check and assert exit 2. This proves format-break detection
  is loud, not silent.
- Optionally: add a version-assertion comment referencing
  `tools/alloy-runtime.json` SHA, so future jar bumps trigger a manual review
  of the regex

### 3. Evidence-digest convention

**Design (from research — no standard exists; ETIS + Veselov principles):**

Two placements:
1. **AGENTS.md Key Constraints bullet 14** (after "Sanitized field references"):
   > Field-evidence convention — field runs deposit a sanitized digest into
   > this repo; "field-proven" claims require inspectable committed artifacts
   > (see `steering/archwright-conventions.md`)

2. **`steering/archwright-conventions.md` new section** after "Report Reference
   Commits" (shares the commit-as-proof pattern):

   Format: one YAML file per field run at `field-evidence/<alias>-<date>.yaml`:
   ```yaml
   alias: tilerush-demo
   date: 2026-07-18
   duration_h: 3.2
   specs_checked: 14
   violations_found: 3
   violations_fixed: 3
   trace_coverage: 12/14
   notable: "rule-4 violating scenario exposed translate_predicate defect"
   expires: 2027-01-18  # 6-month decay
   ```

   Principles:
   - Failure-and-recovery evidence is more credible than success counts
   - Evidence expires (6-month decay — re-run or delete)
   - Sanitized aliases only (per existing bullet 12)
   - No retroactive fabrication — convention applies forward only
   - Digests are committed to THIS repo; raw traces stay in target projects

## Acceptance criteria

- [x] Triage table recorded (above) with fresh evidence per finding
- [x] `python3 tools/archwright-check.py --help` and
      `python3 tools/archwright-validate.py --help` print usage and exit 0;
      no flag behavior changed
- [x] Fixture suite green: 164 passed, 0 failed, 0 skipped (or count+1 for
      the new Alloy fixture — update AGENTS.md Commands row if count changes)
- [x] New fixture proves Alloy-format break → exit 2 (loud), not silent pass
- [x] Evidence-digest convention written into AGENTS.md Key Constraints +
      steering/archwright-conventions.md
- [x] Scope check: `git diff` touches only tools/archwright-check.py,
      tools/archwright-validate.py, tools/run-fixture-tests.sh, AGENTS.md,
      steering/archwright-conventions.md, and this ticket file

## Validation criteria

- `python3 tools/archwright-check.py --help` → exit 0, prints all 17 flags
- `python3 tools/archwright-validate.py --help` → exit 0, prints usage
- `python3 tools/archwright-check.py --trace` (no args) → exit 2 (usage)
- `python3 tools/archwright-check.py` (no args) → exit 2 (unchanged)
- `mise run test` → 164/0/0 (or 165/0/0 with new fixture)
- grep `parse_alloy_verdicts` in check.py confirms extraction is a named function
- grep `field-evidence` in conventions.md confirms new section exists

## Resolution (2026-08-24)

Implemented all 3 cheap wins: argparse --help for both CLIs (preserving all flag/exit semantics), Alloy verdict extraction isolated as parse_alloy_verdicts() with format-break fixture (165th check), field-evidence convention written. Monolith split deferred to ticket 097 (high priority).
