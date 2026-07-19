# Tracer Bullet Plan: fieldball-coach → archwright

## Goal

Prove archwright works end-to-end on real data: encode existing fieldball-coach-platform decisions as patterns + specs, build the first validation tool, run checks, demonstrate violation detection.

## Decisions to Encode

Three decisions chosen to exercise different spec kinds and force types:

| # | Decision | Pattern | Spec kinds exercised |
|---|----------|---------|---------------------|
| 15 | BallStateService as run-scoped source of truth | `ball-possession` | behavior + constraint + dependency |
| 12 | PlayManager3D as pure step executor | `execution-purity` | constraint + dependency |
| 18 | Zero autoloads for v1 | `explicit-dependencies` | constraint |

**Why these three:**
- #15 (ball possession) exercises all three spec kinds and has a clear invariant (single holder)
- #12 (pure executor) exercises the "component must NOT do X" constraint pattern
- #18 (no autoloads) is the simplest possible constraint check (grep against project.godot)

Together they prove: behavior model checking (Alloy), codebase conformance (grep), and dependency analysis.

## Phases

### Phase 1: Encode Patterns (3 files)

Write pattern markdown documents in `design/patterns/` within a tracer-bullet workspace (either in this repo under `.scratch/tracer/` or in the fieldball-coach-platform repo).

**Deliverables:**
```
design/
  patterns/
    ball-possession.md          # Forces: fluidity vs single-holder vs single-writer
    execution-purity.md         # Forces: separation of concerns vs convenience
    explicit-dependencies.md    # Forces: testability vs global convenience
```

**Acceptance:** Each pattern has clear forces, a stated tension, and a resolution that maps to specific architectural commitments.

### Phase 2: Derive Specs (6-7 files)

From the three patterns, derive checkable specs:

**From ball-possession:**
```
design/specs/
  ball-state-lifecycle.yaml     # kind: behavior (states: held, in-flight, returned)
  single-ball-holder.md         # kind: constraint (only BallStateService writes)
  ball-write-ownership.md       # kind: dependency (forbidden: controllers → ball_holder)
```

**From execution-purity:**
```
design/specs/
  executor-no-resolve.md        # kind: constraint (PlayManager3D never calls PlayResolver)
  executor-no-presentation.md   # kind: dependency (forbidden: PlayManager3D → UI/presentation)
```

**From explicit-dependencies:**
```
design/specs/
  no-autoloads.md               # kind: constraint (no autoload registrations in project.godot)
```

**Acceptance:** Each spec has valid frontmatter (passes schema), links back to its pattern, and carries a `check` field (for constraint/dependency kinds).

### Phase 3: Build `archwright-validate` (1 script)

A Python script that:
1. Detects file type (markdown+frontmatter vs YAML)
2. Extracts frontmatter/content
3. Validates against the appropriate schema (pattern-schema.yaml or spec-schema.yaml)
4. Reports pass/fail with specific errors

**Interface:**
```bash
archwright-validate design/patterns/ball-possession.md
archwright-validate design/specs/ball-state-lifecycle.yaml
archwright-validate --links design/    # validate all kind:id references resolve
```

**Output format:**
```
PASS: design/patterns/ball-possession.md (kind: pattern)
FAIL: design/specs/broken.yaml
  - required field 'from_patterns' missing
  - link target 'pattern:nonexistent' does not resolve
```

**Acceptance:** All 9-10 files from phases 1-2 pass validation. Link validation catches broken references.

### Phase 4: Run Alloy Check (behavior spec)

Take `ball-state-lifecycle.yaml` and:
1. Compile it to an Alloy 6 model (by hand or simple script)
2. Run `java -jar alloy6.jar exec` on the model
3. Verify: invariants pass (or if we deliberately introduce a bug, a counterexample is found)

**Acceptance:** Alloy finds no violations for the correct model. When we add an `EXTERNAL_TRANSFER` event that bypasses validation, Alloy finds the counterexample within 500ms.

### Phase 5: Run Conformance Check (constraint specs)

Take the constraint specs and run their `check` field against the fieldball-coach-platform codebase:

```bash
# Simulated — check if the rule holds
grep -rn "ball_holder\s*=" ~/code/fieldball-coach-platform/client/src/
grep "autoload/" ~/code/fieldball-coach-platform/project.godot
grep -rn "PlayResolver" ~/code/fieldball-coach-platform/client/src/execution/
```

**Acceptance:** Each check produces pass/fail. At least one demonstrates a real finding (either a clean pass confirming the constraint holds, or a violation showing where it's broken).

## Ordering & Dependencies

```
Phase 1 (patterns)
  │
  ├──> Phase 2 (specs) — needs patterns to link from_patterns
  │       │
  │       ├──> Phase 3 (validate tool) — needs files to validate
  │       │       │
  │       │       └──> Run validation on phases 1+2 output
  │       │
  │       ├──> Phase 4 (Alloy check) — needs behavior spec
  │       │
  │       └──> Phase 5 (conformance) — needs constraint specs + target codebase
  │
  └──> Phases 4-5 can run in parallel after Phase 3 validates the files
```

## Success Criteria

The tracer bullet is complete when:
- [ ] 3 patterns exist, all passing schema validation
- [ ] 6-7 specs exist, all passing schema validation
- [ ] Link validation confirms all references resolve
- [ ] Alloy finds a counterexample when a violation is introduced
- [ ] At least 1 conformance check runs against actual fieldball-coach code
- [ ] The full loop is demonstrated: pattern → spec → check → violation → provenance trace back to pattern

## Estimated Effort

| Phase | Work | Size |
|-------|------|------|
| 1 | Write 3 pattern .md files | ~30 min |
| 2 | Write 6-7 spec files | ~45 min |
| 3 | Build archwright-validate | ~1-2 hours (Python, YAML/frontmatter parsing, schema validation) |
| 4 | Alloy model + run | ~30 min (similar to S5 spike, already proven) |
| 5 | Grep checks against codebase | ~15 min |
| **Total** | | **~3-4 hours** |

## What This Proves

After the tracer bullet:
- The format works (patterns + specs validate and link)
- The checking works (Alloy finds violations, grep confirms conformance)
- The provenance works (violations trace back to responsible force/pattern)
- The methodology works (real decisions encode cleanly without escape hatches)
- Archwright is ready to use on other projects
