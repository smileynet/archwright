# Spec: Growth Rules

**ID:** growth-rules
**Status:** Draft
**Covers:** U5 (growth rules table), S15 (selective re-checking spike), R18 (growth rules research)
**Type:** Research → implementation

## Purpose

Codify when code/spec/pattern changes require which checks to re-run. Without this, "live checking" means "run everything every time." With it, a typical commit checks only the relevant subset in <3s.

## Research: R18

### Prior Art

| System | Approach | Granularity |
|--------|----------|-------------|
| Make | File timestamps + declared dependencies | File-level |
| Bazel/Buck | Content hashing + declared dependency graph | Target-level |
| Nx `affected` | Git diff + project dependency graph → affected projects | Project-level |
| Terraform | Resource dependency graph → plan shows what changes | Resource-level |
| SGE (Grabowski 2026) | 6 growth rules: change type → required updates | Artifact-level |

### Key Insight from Nx

Nx's `affected` command:
1. Computes git diff (changed files)
2. Maps files → owning projects (via workspace config)
3. Walks the project dependency graph to find all transitively affected projects
4. Runs only affected project tasks

Archwright needs the same pattern:
1. Git diff → changed files
2. Map files → relevant specs (via `check.target` declarations)
3. Walk spec links to find transitively affected specs
4. Run only affected checks

### Key Insight from SGE

SGE's 6 rules map change types to mandatory updates. The rules are *prescriptive* (you MUST update X when Y changes) rather than reactive. This ensures nothing is missed.

## Growth Rules

### Rule 1: Code Change → Static Re-check

**Trigger:** File in `check.target` path of a constraint/dependency spec is modified.
**Action:** Re-run that spec's static check.
**Scope:** Only specs whose target path matches the changed file.

Example: `src/execution/play_manager3d.gd` changes → re-check `constraint:executor-no-resolve` (target: `src/execution/`) and `constraint:executor-boundaries` (target: `src/execution/`).

### Rule 2: Code Change → Trace Re-check

**Trigger:** File in a behavior spec's `check.trace.scope` is modified.
**Action:** Re-run conformance tests for that behavior spec.
**Scope:** Only behavior specs whose scope includes the changed component.

Example: `src/ball/ball_state_service.gd` changes → re-run conformance tests for `behavior:ball-state-lifecycle`.

### Rule 3: Spec Change → Self Re-check

**Trigger:** A spec file in `design/specs/` is modified.
**Action:** Re-validate the spec (`archwright-validate`) + re-run its own checks.
**Scope:** The changed spec only.

### Rule 4: Spec Change → Dependent Re-check

**Trigger:** A spec that other specs link to (via `links[].target`) is modified.
**Action:** Re-run checks for all specs that reference it.
**Scope:** Direct dependents (one hop). Transitive dependents only if the change affects the public contract.

Example: `behavior:ball-state-lifecycle` changes its states → `constraint:single-ball-writer` (which links to it) should be re-checked.

### Rule 5: Pattern Change → Linked Spec Review

**Trigger:** A pattern in `design/patterns/` is modified.
**Action:** Flag all specs with `from_patterns` referencing it for human review. Re-run their checks.
**Scope:** All specs descended from the pattern.

This is NOT fully automatable — a pattern change may require spec revision, not just re-checking.

### Rule 6: New File → Constraint Scan

**Trigger:** A new file is added to the project.
**Action:** Check if any constraint spec's target pattern matches the new file's path.
**Scope:** All constraint specs with glob targets.

Example: new file `src/services/audio_global.gd` added + registered as autoload → `constraint:no-autoloads` catches it.

## Spec Field: `scope`

Behavior specs need a `scope` field declaring which code paths they cover:

```yaml
check:
  trace:
    scope: ["src/ball/", "src/execution/play_manager3d.gd"]
    events: [REQUEST_TRANSFER, VALIDATE_ACCEPT, VALIDATE_REJECT]
    state_vars: [holder, requester]
    invariants: [at-most-one-holder, no-holder-during-flight]
```

Constraint specs already have this via `check.target`.

## Algorithm: Git Diff → Relevant Checks

```
function affected_checks(changed_files, all_specs):
  affected = []
  
  for spec in all_specs:
    if spec.kind in [constraint, dependency]:
      # Rule 1: static re-check
      if any(file matches spec.check.target for file in changed_files):
        affected.append({spec: spec, layer: "static"})
    
    if spec.kind == behavior:
      # Rule 2: trace re-check
      if any(file matches scope for file in changed_files for scope in spec.check.trace.scope):
        affected.append({spec: spec, layer: "trace"})
    
    if spec.path in changed_files:
      # Rule 3: self re-check
      affected.append({spec: spec, layer: "self"})
      # Rule 4: dependent re-check
      for dependent in find_dependents(spec, all_specs):
        affected.append({spec: dependent, layer: "dependent"})
  
  # Rule 5: pattern changes
  for file in changed_files:
    if file starts with "design/patterns/":
      pattern_id = extract_id(file)
      for spec in all_specs:
        if pattern_id in spec.from_patterns:
          affected.append({spec: spec, layer: "pattern-review"})
  
  # Rule 6: new files
  for file in new_files(changed_files):
    for spec in all_specs where spec.kind == constraint:
      if file matches spec.check.target:
        affected.append({spec: spec, layer: "new-file"})
  
  return deduplicate(affected)
```

## Spike: S15

### Goal

Prove selective re-checking works: a change in `src/ball/` triggers ball-related checks only; a change in `src/setup/` triggers no design checks (no specs cover setup yet).

### Pass Criteria

1. `git diff --name-only` piped to the affected-checks algorithm produces correct subset
2. Running only affected checks takes <3s for typical commits
3. No false negatives: a violation in affected code IS caught
4. Unaffected specs are NOT re-run (verified by checking which specs appear in output)

### Fail Criteria

- Algorithm is too coarse (everything fires on every change)
- Algorithm is too fine (misses a real violation because scope was too narrow)
- Spec `scope` declarations are so burdensome to maintain that developers won't do it

## Granularity Recommendation

**Directory-level** for v1. Not file-level (too many declarations), not function-level (too fragile).

Specs declare scope as directory prefixes: `["src/ball/", "src/execution/"]`. A change to any file in that directory triggers the spec's checks.

Rationale:
- Directory boundaries in LBP already correspond to architectural boundaries (ball/, execution/, fielder/, play_data/)
- Easy to maintain (handful of paths per spec)
- False-positive rate is low (a change in `src/ball/` probably IS relevant to ball-state-lifecycle)
- False-negative risk is low (components don't typically reach across directory boundaries without explicit imports, which dependency specs catch)

## Validation Criteria

- [ ] Growth rules table covers all artifact types (pattern, behavior, constraint, dependency, code)
- [ ] Algorithm correctly identifies affected specs for: code change, spec change, pattern change, new file
- [ ] Running affected-only checks on a typical commit takes <3s
- [ ] A violation in affected code is caught (no false negatives)
- [ ] Unaffected specs are skipped (verified in output)

## Links

- Depends on: [static-check-batch](static-check-batch.md), [drift-gate](drift-gate.md)
- Consumed by: CI integration (extends drift-gate with selectivity)
- Prior art: Nx affected, Bazel dependency tracking, SGE growth rules (Grabowski 2026)
