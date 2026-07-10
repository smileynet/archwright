---
name: archwright-derive
description: "Derive checkable specs from a pattern. Takes a formalized pattern and produces behavior, constraint, dependency, and contract specs as declared in its resolves_into. Use when a pattern exists but its specs haven't been written. Trigger: derive specs, write specs from pattern, what specs does this pattern need."
metadata:
  type: process
  invocation: both
  practice: null
---

# Archwright Derive

Produce checkable specs from a formalized pattern. Each spec is a downstream projection of the pattern's resolution — one facet of the architecture made verifiable.

**Core principle:** Specs are flat, typed, linked via `kind:id` references. Each spec checks ONE concern. A pattern typically resolves into 2-5 specs of different kinds.

## Process

### 1. Receive input

A formalized pattern (from `archwright-formalize`) with its `resolves_into` declarations.

### 2. Read the pattern

Extract from the pattern:
- The resolution (what architecture was committed to)
- The consequences (what downstream constraints exist)
- The forces (for provenance: `from_force` on each spec element)
- The confidence (inherited as starting point for spec confidence)

### 3. For each `resolves_into` entry, write the spec

Route by kind:

#### Behavior specs (YAML)

When the resolution commits to states, transitions, or lifecycle:

1. Identify the states (modes the system can be in)
2. Identify the transitions (events that move between states)
3. Identify guards (constraints that gate transitions)
4. Identify invariants (properties that must always hold)
5. Add `check.trace` block (events, state_vars, invariants for trace validation)
6. Add `check.model` block (backend, scope, steps for Alloy)
7. Add `abstraction_notes` (what's included/excluded/why)

Use template: `tools/templates/spec-behavior.yaml`

#### Constraint specs (Markdown)

When the resolution commits to a rule the code must never violate:

1. State the rule (what must be true)
2. State the rationale (which force demands it)
3. Give a violation example (code that would break it)
4. Give a correct example (code that respects it)
5. Add `check` block (method: grep/ast-grep/script, target, pattern, expect)

Use template: `tools/templates/spec-constraint.md`

#### Dependency specs (Markdown)

When the resolution commits to allowed/forbidden relationships:

1. List allowed dependencies (source → target, type)
2. List forbidden dependencies (source → target, type)
3. State rationale for each forbidden
4. Add `check` block (grep/script that detects violations)

Use template: `tools/templates/spec-dependency.md`

#### Contract specs (YAML)

When the resolution commits to a data shape:

1. Define the fields (name, type, required/optional)
2. Define lifecycle constraints (when fields are valid)
3. Define producer/consumer roles
4. Add validation rules

Use template: `tools/templates/spec-contract.yaml`

### 4. Wire provenance

Every element in a spec traces back:

```yaml
states:
  held:
    from_pattern: ball-possession  # which pattern demanded this state
    from_force: single-holder       # which force this state satisfies

invariants:
  - id: at-most-one-holder
    from_force: single-holder       # the force that demands this invariant
    from_pattern: ball-possession   # the pattern that resolved it
```

### 5. Wire links

Specs reference each other:

```yaml
links:
  - target: "constraint:single-ball-writer"
    type: constrained-by
  - target: "behavior:execution-lifecycle"
    type: depends-on
```

Link types:
- `constrained-by` — this spec is bounded by that constraint
- `enforces` — this spec enforces that other spec's contract
- `depends-on` — this spec assumes that other spec holds
- `consumes` — this spec's component reads that spec's output

### 6. Validate

- Every spec passes `archwright-validate`
- Every `from_pattern` references an existing pattern
- Every `links[].target` references an existing or co-created spec
- Every constraint spec has a `check` block that can execute
- Every behavior spec has at least one invariant
- Behavior spec `check.trace.state_vars` matches `context.variables` keys
- **Traceability check:** spec.from_patterns → pattern.serves → product desire. If this chain is broken (pattern has no `serves`), flag the pattern as needing a `serves` link before the spec is committed.

## Output Location

Specs are written to the target project's `design/specs/` directory:
- Behavior: `design/specs/<id>.yaml`
- Constraint: `design/specs/<id>.md`
- Dependency: `design/specs/<id>.md`
- Contract: `design/specs/<id>.yaml`

## Does NOT

- Write patterns (receives them from `archwright-formalize`)
- Resolve tensions (that's decided before derivation)
- Implement code (specs declare WHAT, not HOW)
- Run checks (hand off to `archwright-check` after writing)
- Set confidence higher than the parent pattern's confidence

## Pre-Commit Verification

Before committing constraint specs, verify check targets against the actual codebase:
1. Run `find` or `ls` to confirm the `check.target` path exists
2. If using `expect: absent`, verify the grep pattern would match violations (test against a known-bad example if possible)
3. If using `expect: present`, verify the pattern matches something that currently exists
4. Run `archwright-check --static` against the batch before committing — fix target paths before the pre-commit hook rejects

**Common pitfall:** File/directory names in the target project may differ from spec names (e.g., `practice_setup/` vs `setup/`). Always verify.

## Spec Sizing

- **One spec per concern.** Don't put multiple independent invariants in one behavior spec.
- **Specs are flat.** No nested specs. Use links for relationships.
- **Prefer constraint specs when a grep can check it.** Don't model a full state machine for "X must never import Y."
- **Behavior specs for temporal properties only.** If the property is point-in-time ("this field is never null"), it's a constraint, not a behavior.
