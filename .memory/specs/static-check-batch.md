# Spec: Static Check Batch Mode

**ID:** static-check-batch
**Status:** Draft
**Covers:** T3 (`archwright-check --static`), T5 (constraint spec check extraction)
**Blocks:** drift-gate

## Purpose

Enable `archwright-check --static design/` to walk a directory of specs, extract check strategies from each constraint/dependency spec, execute them against the codebase, and report aggregate results.

## Interface

```bash
archwright-check --static <design-dir> [--target <project-root>]
```

### Inputs

| Input | Description |
|-------|-------------|
| `<design-dir>` | Path to `design/specs/` (or any directory containing spec files) |
| `--target` | Project root for resolving check target paths (default: parent of design-dir) |

### Discovery

1. Walk `<design-dir>` recursively
2. Identify spec files by extension and frontmatter:
   - `.md` files with `kind: constraint` or `kind: dependency` in frontmatter → static-checkable
   - `.yaml` files with `kind: behavior` → skip (these use trace/model checking)
3. For each static-checkable spec, extract the `check` block from frontmatter

### Check Extraction

From constraint spec frontmatter:

```yaml
check:
  method: grep        # grep | ast-grep | script
  target: "project.godot"  # relative to project root
  pattern: "^autoload/"
  expect: absent      # absent | present
```

Execution:
- `method: grep` → `grep -rn <pattern> <target>`. If `expect: absent`, matches mean violation.
- `method: ast-grep` → `ast-grep -p <pattern> <target>`. Same absent/present logic.
- `method: script` → execute `<pattern>` as a shell command. Exit 0 = pass, exit 1 = fail.

### Output (JSON)

```json
{
  "status": "pass",
  "checked": 4,
  "results": [
    {"spec_id": "no-autoloads", "status": "pass", "method": "grep", "duration_ms": 12},
    {"spec_id": "executor-no-resolve", "status": "pass", "method": "grep", "duration_ms": 18},
    {"spec_id": "single-ball-writer", "status": "pass", "method": "grep", "duration_ms": 15},
    {"spec_id": "executor-boundaries", "status": "pass", "method": "grep", "duration_ms": 22}
  ],
  "duration_ms": 67
}
```

On failure:

```json
{
  "status": "fail",
  "checked": 4,
  "passed": 3,
  "failed": 1,
  "results": [
    {"spec_id": "no-autoloads", "status": "fail", "method": "grep", "matches": [
      {"file": "project.godot", "line": 42, "content": "autoload/AudioManager=\"*res://...\""}
    ]}
  ]
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All specs pass |
| 1 | One or more violations |
| 2 | Tool error (bad spec format, missing target) |

## Implementation Notes

### Parsing Constraint Spec Frontmatter

Constraint specs use markdown with YAML frontmatter delimited by `---`. Extract frontmatter with:

```bash
yq --front-matter=extract '.check' spec.md
```

Or parse the `---` delimiters manually and feed to `yq`.

### Target Path Resolution

`check.target` is relative to the project root. The tool resolves:
```
project_root = --target flag || dirname(dirname(design-dir))
full_path = project_root / check.target
```

For glob targets (e.g., `"src/**/*.gd"`), expand before checking.

### Performance

Target: all constraint checks complete in <5s for a typical project. Current LBP fixture (4 constraints) completes in <100ms via the existing `run-fixture-tests` script, so this is achievable.

## Validation Criteria

- [ ] `archwright-check --static design/specs/` discovers all constraint/dependency specs
- [ ] Each spec's check strategy is correctly extracted and executed
- [ ] Aggregate JSON output reports per-spec results
- [ ] Exit code 1 when any spec fails
- [ ] `--target` flag correctly resolves relative paths
- [ ] Specs with malformed `check` blocks produce exit 2 with helpful error
- [ ] Total runtime <5s for 10 specs

## Links

- Consumed by: [drift-gate](drift-gate.md)
- Depends on: existing constraint specs in target project's `design/specs/`
- Prior art: Semgrep multi-rule scanning, ESLint config-driven checking
