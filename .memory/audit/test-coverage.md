# A5 — Test Coverage Audit (2026-07-16)

What automated coverage exists for the 6 remaining tools, what `run-fixture-tests.sh` (post-B7) actually exercises, and the minimal additions to close the gaps.

## Current Coverage Matrix

| Tool | Happy path | Failure path | Covered by |
|------|:----------:|:------------:|------------|
| `archwright-validate.py` (files) | ✅ 10 fixture files | ❌ no bad-input fixture | run-fixture-tests §Schema |
| `archwright-validate.py --links` | ✅ | ❌ no broken-link fixture | run-fixture-tests §Links |
| `archwright-check.py` (constraint/dependency) | ✅ 5 specs | ⚠️ manual only (B7 inject/revert was by hand) | run-fixture-tests §Conformance |
| `archwright-check.py` (behavior/Alloy) | ⚠️ SKIP-only (no jar) | ❌ | run-fixture-tests §Behavior |
| `archwright-check.py --trace` | ❌ not in suite | ❌ | nothing (verified manually in A1) |
| `archwright-check.py --static/--json` | ❌ not in suite | ❌ | nothing |
| `archwright-compile-alloy.py` | ❌ | ❌ | nothing |
| `archwright-check-compile.mjs` | ❌ | ❌ | nothing |
| `deploy-skills.sh` | ❌ | ❌ | nothing (verified manually in A1) |

**Summary: 4 of 9 tool/mode combinations have any automated coverage; 0 have automated failure-path coverage.** The B7 negative test (inject violation → detect → revert) proved detection works but is not repeatable without a human.

## Known Uncovered Bugs (would be caught by proposed tests)

- A1/F3: unknown `expect:` value → silent pass (needs a bad-spec fixture)
- A1/F7: missing file → raw traceback instead of clean exit 2
- Contract-kind checks ("schema validation only") — never exercised anywhere

## Proposed Minimal Additions (in effort order)

| # | Addition | Method | Effort |
|---|----------|--------|--------|
| 1 | **Violation fixture branch**: add `tests/fixtures/lacrosse-bosse-violations/` overlay (2 files: a rogue `ball_holder =` write + an `[autoload]` project.godot) + suite section asserting FAIL with expected count | Automates the B7 negative test | 45m |
| 2 | **Bad-spec fixtures**: `tests/fixtures/bad-specs/` (unknown kind, bad confidence, unknown `expect`, broken link) + suite section asserting validate/check reject each with exit 1 (and exit 2 for tool errors once implemented) | Locks in A1/F3 fix when Phase 5 CK-05 lands | 45m |
| 3 | **Trace coverage**: commit `trace-ok.json` + `trace-violation.json` under the fixture; suite section runs `--trace` asserting pass and fail respectively | Covers the only verified-but-untested working mode | 30m |
| 4 | **Alloy compile smoke**: suite section runs compile-alloy, asserts `.als` generated + nonzero, deletes it | 10m |
| 5 | **`--json` contract check**: pipe `--static --json` through `python3 -m json.tool`; assert `status` key present (schema conformance grows with Phase 5 CK-03) | 10m |
| 6 | deploy-skills smoke: `--project $(mktemp -d)`, assert 12 skills + 2 steering land | 15m |

Total ≈ 2.5h. Items 1–3 are the high-value core (failure paths). Recommend folding into Phase 5a as **CK-20: fixture test hardening** so the new tool implementation lands with regression protection — Phase 5's CK-05/CK-03 acceptance criteria need exactly these fixtures to be verifiable.

## Not Proposed

- Unit tests for check.py internals — Phase 5 rewrites this tool; test at the CLI contract level instead.
- CI wiring — Phase 5 CK-15 covers it (GitHub Actions + SARIF).
