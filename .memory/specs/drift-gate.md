# Spec: Drift Gate

**ID:** drift-gate
**Status:** Draft
**Covers:** S13 (drift gate CI check), T1 (PATH accessibility), C3 (pre-commit hook)
**Type:** Spike → implementation

## Purpose

Wire archwright's static checking as a merge-blocking gate in lacrosse-bosse-platform. Prove that spec-code drift is catchable at commit time.

## Spike: S13

### Goal

A commit that introduces a constraint violation is automatically blocked by a pre-commit hook running `archwright-check --static design/`.

### Pass Criteria

1. Add `autoload/Test="*res://test.gd"` to `project.godot` → hook blocks with clear error naming `constraint:no-autoloads`
2. Remove the line → hook passes
3. Total hook runtime <5s
4. Error output identifies: which spec, what was found, where

### Fail Criteria

- Hook takes >10s (unusable friction)
- False positives on clean code
- Error messages are cryptic or don't identify the responsible spec

## Implementation

### T1: PATH Accessibility

Add to lacrosse-bosse-platform's `mise.toml`:

```toml
[env]
ARCHWRIGHT_HOME = "~/code/archwright"
_.path = ["~/code/archwright/tools"]
```

Or symlink tools to `~/.local/bin`:
```bash
ln -sf ~/code/archwright/tools/archwright-check ~/.local/bin/
ln -sf ~/code/archwright/tools/archwright-validate ~/.local/bin/
```

Decision: use `mise.toml` PATH entry (project-scoped, doesn't pollute global PATH).

### C3: Pre-commit Hook

Option A — git hook (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
archwright-check --static design/ --target .
exit $?
```

Option B — mise task:
```toml
[tasks.check-design]
run = "archwright-check --static design/ --target ."
```

Then wire into pre-commit via `mise run check-design` or a `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: archwright-check
        name: archwright design check
        entry: archwright-check --static design/ --target .
        language: system
        pass_filenames: false
```

Decision: use `.pre-commit-config.yaml` with `pre-commit` framework (standard, shareable, skip-able with `--no-verify` when needed).

### C1: Commit `design/` Directory

The `design/` directory already exists in LBP with 3 patterns + 6 specs. It needs to be committed (currently tracked but specs may need updating to reflect slice 1 completion).

Before committing, verify:
- All 4 constraint specs pass against current code
- `archwright-validate` accepts all specs
- Links between specs are valid

## Validation Criteria

- [ ] `archwright-check --static design/ --target .` passes on clean LBP checkout
- [ ] Introducing a known violation → exit 1 with correct spec identified
- [ ] Pre-commit hook blocks the bad commit
- [ ] Removing the violation → hook passes
- [ ] Hook runtime <5s
- [ ] Other developers can install the hook via `pre-commit install`

## Links

- Depends on: [static-check-batch](static-check-batch.md)
- Uses: existing constraint specs in `design/specs/` (no-autoloads, executor-no-resolve, single-ball-writer, executor-boundaries)
- Consumed by: [growth-rules](growth-rules.md) (selective re-checking builds on this)
