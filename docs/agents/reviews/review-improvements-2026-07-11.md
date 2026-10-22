# Archwright Improvement Recommendations — 2026-07-11

Based on running the first full `archwright-review` on fieldball-coach-platform.

## Session Summary

- Integrated semgrep into `archwright-check` (was a placeholder)
- Updated README + AGENTS.md to reflect current state
- Deployed skills to LBP
- Ran full 3-layer review (first real use)
- Identified 2 spec-ahead gaps, 0 regressions
- Updated LBP PLAN.md with spec clarification ordering

## Improvements Identified

### 1. archwright-check: semgrep --no-git-ignore required

**Problem:** Semgrep defaults to scanning only git-tracked files. If specs target files in gitignored directories (e.g., generated code, build artifacts, or testing scratch), checks silently pass with 0 files scanned.

**Fix applied:** Added `--no-git-ignore` to the semgrep command. Already committed.

**Future consideration:** Add `--metrics=off` to disable semgrep's telemetry in CI contexts. Consider `--quiet` for non-interactive use.

### 2. archwright-check: YAML roundtrip corrupts multiline patterns

**Problem:** When a spec's `check.rule` contains a multiline pattern (e.g., `try { ... } catch { ... }`), YAML parsing → Python dict → `yaml.dump()` adds trailing whitespace/newlines that break semgrep pattern matching.

**Fix applied:** Added `_strip_rule_strings()` to recursively strip all string values before dumping. Already committed.

**Recommendation for spec authors:** Prefer single-line patterns where possible (`try { ... } catch { return $DEFAULT; }`). For complex rules, use `rules_file` pointing to a hand-authored YAML file rather than inline rules.

### 3. archwright-review: Layer 2 has no on-ramp

**Problem:** The skill describes behavioral validation (trace-based), but there's no guidance on HOW to instrument a Godot/GDScript project to emit traces. The review correctly identifies "not executable" but can't help users get there.

**Recommendation:** Create a `tools/templates/trace-instrument-gdscript.md` that shows:
- The 5-line signal-tap pattern for GDScript state machines
- How to emit `{event, state, clock}` JSON from test harness
- Where trace files should land (`design/specs/traces/`)
- Example: instrumenting a simple FSM (PlayManager3D is a good candidate)

### 4. archwright-review: No automated semantic dispatch

**Problem:** Layer 3 (semantic) review was performed manually in the main context. For larger projects, this won't scale — the skill describes subagent dispatch but there's no automation. The agent must read the skill, understand the protocol, and manually apply it.

**Recommendation:** Create a `tools/archwright-review-semantic` script that:
- Reads all specs in `design/specs/`
- Maps each spec to its `check.target` files
- Generates a dispatch plan (spec → files to review)
- Outputs the review prompt for each spec (ready for subagent dispatch)
- Could be a simple YAML generator that `archwright-review` consumes

This separates "what to review" (mechanical, automatable) from "is it aligned?" (AI judgment).

### 5. Spec gap detection should be a first-class check mode

**Problem:** The review found specs that describe features not yet implemented ("spec ahead of implementation"). Currently this is flagged as a semantic finding. But it's actually a common case with a predictable shape: the spec references methods/states that don't exist in the implementation.

**Recommendation:** Add a `--coverage` mode to `archwright-check` that:
- For each behavior spec: checks whether the implementation file contains the state names and transition events
- For each constraint spec: checks whether `check.target` files exist and are non-empty
- Reports: "spec X references method Y which doesn't exist in target" → labeled as "spec-ahead" not "drift"

This would have caught the `request_transfer()` gap mechanically.

### 6. check-compile should support semgrep intent patterns

**Problem:** `archwright-check-compile` only generates grep-based checks. After adopting semgrep, there are intent patterns that should compile to semgrep rules instead:
- `silent_catch` → semgrep (AST-aware catch block detection)
- `no_type_check` → semgrep (type narrowing detection)
- `no_direct_write` → grep is fine for simple patterns, but semgrep for scoped writes

**Recommendation:** Extend `check-compile` with a `method` field in the intent that selects grep vs semgrep output, or auto-select based on pattern complexity.

### 7. Review report should be machine-parseable

**Problem:** The alignment report is pure markdown. It's human-readable but can't be consumed by tooling (e.g., for tracking drift over time, or feeding into CI gates).

**Recommendation:** Add `--json` output mode to the review process. Structure:
```json
{
  "date": "2026-07-11",
  "layers": {
    "structural": {"total": 8, "pass": 8, "fail": 0},
    "behavioral": {"total": 2, "executable": 0, "pass": 0},
    "semantic": {"total": 10, "aligned": 8, "drift": 1, "gap": 1}
  },
  "findings": [...]
}
```
The markdown report remains the primary output; JSON is for automation.

### 8. deploy-skills should verify target project has design/specs/

**Problem:** `deploy-skills --project` deploys skills but doesn't validate that the target project has the expected structure. If someone runs it on a project without `design/specs/`, the deployed skills will fail silently when invoked.

**Recommendation:** Add a post-deploy check: "Warning: target project has no design/specs/ directory — archwright-check will have nothing to verify."

## Priority

| # | Effort | Impact | Recommendation |
|---|--------|--------|----------------|
| 5 | Medium | High | Spec-ahead detection (--coverage mode) |
| 3 | Low | High | Trace instrumentation on-ramp template |
| 4 | Medium | High | Semantic review dispatch automation |
| 7 | Low | Medium | JSON output for reports |
| 6 | Medium | Medium | check-compile semgrep support |
| 8 | Low | Low | deploy-skills validation |
| 1 | Done | — | --no-git-ignore (committed) |
| 2 | Done | — | YAML strip (committed) |

## Next Session Candidates

1. Write the trace instrumentation template (low effort, unblocks LBP Layer 2)
2. Implement `--coverage` mode in archwright-check
3. Create `tools/archwright-review-semantic` dispatch generator
