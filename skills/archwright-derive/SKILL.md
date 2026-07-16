---
name: archwright-derive
description: "Derive checkable specs from a pattern. Takes a formalized pattern and produces behavior, constraint, and dependency specs as declared in its resolves_into (contract specs come from archwright-contract). Use when a pattern exists but its specs haven't been written. Trigger: derive specs, write specs from pattern, what specs does this pattern need."
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

**Primary sources (either or both):**
- Formalized patterns (from `archwright-formalize`) with `resolves_into` declarations
- Domain model (from `archwright-model`) with actor boundaries, invariants, and event flows

**Also check:** existing contract specs from `archwright-contract` phase.
- Contract specs are owned exclusively by the contract phase — this phase NEVER writes or re-derives them (state schemas, event payloads, persistence schemas)
- DO cross-reference: behavior specs link to contract specs via `consumes` type
- If a contract spec defines event payloads, behavior specs reference those payload shapes in their transitions — never restate the field list
- The derive phase produces BEHAVIOR specs (temporal/FSM), CONSTRAINT specs (rules), and DEPENDENCY specs (relationships). If a needed contract spec doesn't exist, flag the gap back to `archwright-contract` rather than filling it here.

**When both exist:** The domain model is authoritative for actor boundaries, state machines, and composition. Patterns provide provenance (which force demanded what). Use both together — the model's invariant summary is the spec dispatch list.

### 2. Read the input

**From patterns**, extract:
- The resolution (what architecture was committed to)
- The consequences (what downstream constraints exist)
- The forces (for provenance: `from_force` on each spec element)
- The confidence (inherited as starting point for spec confidence)

**From the domain model** (`design/models/*-actors.yaml`), extract:
- Actor state machines → behavior specs
- Actor invariants → constraint specs
- Composition rules (lifecycle, spawn/invoke) → dependency specs
- Key invariants summary → spec dispatch list (what to derive first)
- (`contract_candidates` are consumed by `archwright-contract`, not here)

### 3. For each `resolves_into` entry (or model invariant), write the spec

Route by kind:

#### Model-driven derivation (preferred when model exists)

When a domain model exists, derive specs from actor definitions:

| Model element | Spec kind | What to check |
|---|---|---|
| `actor.state_machine` | behavior | States, transitions, guards match implementation |
| `actor.invariants` | constraint | Rule holds in codebase (grep/ast-grep) |
| `actor.owns` (single writer) | constraint | Only this actor writes the field |
| `composition.children` (lifecycle) | dependency | Child cannot exist without parent |
| `boundary_entities` (injected policy) | constraint | Policy object is read-only to consumers |
| `contract_candidates` | — | Handled by `archwright-contract`, not derived here |

Priority: derive from the Key Invariants Summary first (these are the highest-value specs).

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

### 4. Wire provenance and experience

Every spec must declare:

```yaml
# Required on ALL specs:
protects_experience: "experience-id"    # which user experience this spec protects
user_story: "When a player does X, they see Y"  # one sentence, user's perspective

# Required on behavior specs:
scenarios:
  - name: "Human-readable scenario name"
    narrative: "What the user experiences in this scenario"
    trace: [EVENT_1, EVENT_2, EVENT_3]
    verifies: [invariant-1, invariant-2]
```

**protects_experience** accepts either reference kind:
- A modeled-experience ID from the model's experience layer (**preferred** — the model names what users feel)
- A product-force ID (**acceptable** when the experience lives at product-force level and no experience layer entry exists — don't invent a hollow experience just to fill the field)

If you can't name which experience OR product desire a spec protects, the spec may be an implementation detail, not a design guarantee. `archwright-validate.py` warns (never fails) when the field is absent.

**user_story** tells the story from the user's (coach or player) perspective. Not "the system does X" but "the user sees/feels/experiences X."

**scenarios** (behavior specs only) are the design intent made concrete. Each scenario is a story the user would recognize, paired with the event trace that verifies it. The state machine is the mechanical verification; scenarios are why it matters.

Every element also traces back to patterns and forces:

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
- Contract: written by `archwright-contract` (same directory) — never by this phase

**One spec per file — no exceptions.** Each `resolves_into` target becomes its own file. Never group specs into shared files, even when they share a parent pattern. Reasons: addressability (`kind:id` references need unique files), independent lifecycle (specs evolve separately), clean git blame, and tooling compatibility (`archwright-check` targets individual files).

## Check Method Guidance (for constraint specs)

When writing the `check` block, prefer structural checks over text grep:

| Language | Recommended check method | Why |
|----------|------------------------|-----|
| TypeScript/JavaScript | `ast-grep` (structural AST matching) | Grep produces false positives on comments, `import type`, string literals |
| Python | `ast-grep` or `semgrep` | Same — comments and docstrings confuse grep |
| YAML/JSON | `yq`/`jq` (structural query) | Path-based queries are precise |
| Config files (turbo.json, tsconfig) | `node -e` script (parse + assert) | Handles nested structure |
| Shell scripts | `grep` (acceptable — less structured) | Comments are rare enough |

**When using grep:** exclude comment lines with patterns like `^[^/]*<target>` (no leading `//`). Note that `import type` in TypeScript is compile-time-only and should NOT be flagged as a runtime import.

## Does NOT

- Write patterns (receives them from `archwright-formalize`)
- Write contract specs (that's `archwright-contract` — flag gaps back, never fill them here)
- Resolve tensions (that's decided before derivation)
- Implement code (specs declare WHAT, not HOW)
- Run checks (hand off to `archwright-check` after writing)
- Set confidence higher than the parent pattern's confidence

## Pre-Commit Verification

Before committing constraint specs, verify check targets against the actual codebase:
1. Run `find` or `ls` to confirm the `check.target` path exists — **if it doesn't, either fix the path or mark the spec as `check.target_status: pending` (target not yet implemented)**
2. If using `expect: absent`, verify the grep pattern would match violations (test against a known-bad example if possible)
3. If using `expect: present`, verify the pattern matches something that currently exists — if nothing matches because the system isn't built yet, set `check.target_status: pending`
4. Run `python3 tools/archwright-check.py --static` against the batch before committing — fix target paths before the pre-commit hook rejects (note: the flag is `--static`; there is no `--structural` flag)

**Target status field:** When a spec's check target doesn't yet exist in the codebase (system not implemented), add:
```yaml
check:
  method: grep
  target: "game/addons/catalyst_framework/narrative/"
  target_status: pending  # Target path doesn't exist yet. Check activates when it does.
  pattern: "..."
  expect: present
```

This makes it explicit which specs are checkable NOW vs which activate later — preventing false "N/A" results that hide real issues.

**Common pitfall:** File/directory names in the target project may differ from spec names (e.g., `practice_setup/` vs `setup/`). Always verify.

## Spec Sizing

- **One spec per concern.** Don't put multiple independent invariants in one behavior spec.
- **Specs are flat.** No nested specs. Use links for relationships.
- **Prefer constraint specs when a grep can check it.** Don't model a full state machine for "X must never import Y."
- **Behavior specs for temporal properties only.** If the property is point-in-time ("this field is never null"), it's a constraint, not a behavior.

## Write All Declared Specs Regardless of Implementation Timeline

Every `resolves_into` entry in a formalized pattern should have its spec written during the derive phase — even if the system won't be built for months. Do NOT withhold specs as "not yet needed."

**Rationale:**
- Specs GUIDE implementation (they're acceptance criteria written BEFORE code, not post-hoc checks)
- Specs reveal design gaps cheaply (finding a contradiction at spec time is free; finding it during implementation is expensive)
- Specs are not sacred — they update when spikes produce findings or decisions change
- A spec that exists but needs revision is more useful than a spec that doesn't exist yet

**The only reason to defer a spec:** The PATTERN isn't resolved yet (forces unclear, tension open). If the pattern is formalized with `resolves_into` entries, derive every spec immediately.
