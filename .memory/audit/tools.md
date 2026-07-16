# A1 — Tool Functional Audit (2026-07-16)

Method: every tool executed against `tests/fixtures/lacrosse-bosse` and synthetic good/bad inputs in `.scratch/a1/`. All claims below are backed by captured output from this session. Environment: Python 3.12.13 + PyYAML, Node v22.22.2, no `.references/alloy6.jar`.

## Verdict Summary

| Tool | Status | Headline |
|------|--------|----------|
| `archwright-validate.py` | ✅ Works | Correct pass/fail + multi-error reporting; crashes (traceback) on missing file |
| `archwright-check.py` (constraint) | ✅ Works | grep checks correct incl. `only-in`; silent false-pass on unknown `expect` value |
| `archwright-check.py --trace` | ✅ Works | Rich JSON violations w/ `valid_events` + partial provenance |
| `archwright-check.py --static` | ✅ Works | Batch mode fine; `--json` summary is impoverished |
| `archwright-check.py` (behavior) | ⚠️ Degrades | SKIP (exit 0) when alloy6.jar missing — hardcoded home path |
| `archwright-compile-alloy.py` | ✅ Works | Generated `.als` from behavior spec |
| `archwright-check-compile.mjs` | ✅ Works | Generates check blocks from intent patterns |
| `archwright-trace-validate.sh` | ❌ Broken | Crashes: expects `trace.events` object; check.py uses bare array — schema mismatch |
| `archwright-trace-validate.mjs` | ❌ Broken | Contains TypeScript syntax (`interface`) — cannot run under plain node |
| `run-fixture-tests.sh` | ❌ Broken | Dies silently (exit 1, no output) — 3 independent breakages |
| `deploy-skills.sh` | ✅ Works | `--project` deploys all 12 skills + steering to `<path>/.kiro/` |

## Detailed Findings

### F1. `run-fixture-tests.sh` triple breakage (HIGH)
1. **Silent death:** `set -euo pipefail` + `patterns=$(find …/design/patterns …)` — `find` exits 1 because `design/` doesn't exist in the fixture → script dies at that line with **no output, exit 1**. The intended "fixture is empty — clean slate, exit 0" path is unreachable.
2. **Stale tool paths:** internally invokes `tools/archwright-validate` and `tools/archwright-check` (extensionless) — those files no longer exist post-rename (`6cb54f3`). Would fail even past breakage 1.
3. **Fixture README lies (Damn Lie):** README documents `design/` with 3 patterns + 6 specs and "All 14 checks should pass." No `design/` directory exists in the fixture at all. → feeds A4.

### F2. Trace tooling schema fork (HIGH)
`archwright-check.py --trace` consumes a **bare JSON array** of `{event, state}` (verified: pass + violation runs). `archwright-trace-validate.sh` expects `trace.events` (object wrapper) → `TypeError: Cannot read properties of undefined (reading 'length')`, exit 1. Two trace validators, two incompatible trace shapes. `.mjs` variant additionally contains TS syntax (`interface TraceEvent`) — syntax error under node 22. Which is canonical? check.py's implementation matches `.memory/specs/trace-schema.md` intent; the sh/mjs pair looks like the S3 spike left in place.
**Recommendation:** delete or fix the S3 spike pair; single source of truth = `archwright-check.py --trace`.

### F3. Silent false-pass on unknown `expect` (MEDIUM)
In `_check_grep`, `expect` values other than `absent`/`present`/`only-in` fall through to `{"status": "pass"}`. A typo (`expect: absnet`) yields a passing check. Also `expect: only-in` requires the separate `only_in` key; `exclude` (natural guess) is silently ignored → check runs as `absent` and fails confusingly (observed). Templates only document `absent | present`.
**Recommendation:** error on unknown `expect`; document `only-in`+`only_in` in the constraint template.

### F4. `--json` output impoverished (MEDIUM — feeds C2)
`--static --json` emits `{"status": "fail", "checked": 1}` — no violations array, no provenance, no assurance. Does not conform to `.memory/specs/check-results.md`. Meanwhile the internal result dicts already carry `confidence`, `assurance`, `violations`, `from_pattern` — the data exists, the JSON emitter drops it.

### F5. Provenance is partial (MEDIUM — feeds C2/A4)
- Constraint FAIL (human output): shows `invariant: … (★★)` — no pattern→force route, no fix direction.
- Trace FAIL (JSON): has `provenance: {from_force: null, from_pattern: "ball-possession"}` — pattern captured, force lost even though the spec's transitions carry `from_force`. Plus `valid_events` list = a genuine contrast-pair primitive already present.
- No ★★ escalation flag anywhere.

### F6. Alloy jar path hardcoded (LOW)
`archwright-check.py` looks only at `~/code/archwright/.references/alloy6.jar`. No env var / flag override. Behavior checks SKIP (exit 0) when absent — reasonable degradation, but a CI would silently never model-check.

### F7. Validator quality notes (LOW)
- Good: multi-error reporting (`from_patterns` missing + invalid confidence in one run); correct exit codes 0/1; `--links` catches unresolved `kind:id` refs.
- Bad: missing file → raw `FileNotFoundError` traceback (should be a clean error, exit 2 per validation contract).
- `VALID_SCALES` hardcodes game scales (`premise/loops-systems/verbs-interactions/feel-finish`) — tool-level confirmation of B1: non-game patterns cannot validate with domain-appropriate scales.

### F8. Flag naming drift (`--static` vs `--structural`) (MEDIUM — feeds A2/D1)
`archwright-check.py` implements `--static`, `--all`, `--trace`, `--target`, `--json` (no `--model`). Zero occurrences of `structural` in the tool. But upstream skill edits (`archwright-derive`) now instruct `archwright-check --structural` — following the skill fails. Damn-Lie class: agent-facing instruction that cannot work.

### F9. Undocumented `--json` flag (LOW)
Usage docstring omits `--json` (and `--target`). Docstring also claims dispatch "contract → schema validation only (for now)" — untested this session.

## Verified Invocations (post-rename)

```
python3 tools/archwright-validate.py <file>...        # exit 0 pass / 1 fail (2 not implemented — tracebacks)
python3 tools/archwright-validate.py --links <dir>
python3 tools/archwright-check.py <spec>... [--json]
python3 tools/archwright-check.py --static <dir> [--target <root>] [--json]
python3 tools/archwright-check.py --trace <spec.yaml> <trace.json>   # always JSON
python3 tools/archwright-compile-alloy.py <spec.yaml>                # writes <spec>.als
node tools/archwright-check-compile.mjs <intent.yaml>
bash tools/deploy-skills.sh [--project <path>]
```
None are executable-by-name on PATH from this repo (no mise.toml here; prior plan's T1 put them on PATH in the *target* project). AGENTS.md Commands table (`archwright-validate <pattern.yaml>`) does not work as written → D1.

## Ticket Impacts

| Finding | Feeds |
|---------|-------|
| F1 fixture breakage + README lie | New fix (this batch, D1-adjacent) + A4 claims |
| F2 trace tool fork | New ticket candidate or fold into B4/C2 scope |
| F3 expect fall-through | B4 (check hardening) |
| F4 JSON output | C2 (correction routing) |
| F5 partial provenance | C2, A4 |
| F6 jar path | A5/B4 minor |
| F7 scales hardcoded | B1 |
| F8 --static/--structural | A2, D1, upstream skill fix |
