---
name: archwright-formalize
description: "Write a pattern document from a resolved tension. Takes a tension with its resolution and produces a formal pattern (forces, tension, resolution, consequences, evidence) in archwright format. Use when a decision has been made but not captured as a pattern. Trigger: formalize this, write the pattern, capture this decision as a pattern."
metadata:
  type: process
  invocation: both
  practice: null
---

# Archwright Formalize

Write a pattern from a resolved tension. The pattern captures the forces, names the tension, states the resolution, and declares what specs it resolves into.

**Core principle:** A pattern is a reusable resolution of a named tension. Not a template, not a blueprint — a rule for making form that balances specific forces.

## Process

### 1. Receive input

- A tension (from `archwright-tensions`) with status `resolved` or `decided-not-formalized`
- The force inventory entries for the forces involved
- The resolution source (grill decision, ADR, or human confirmation)

### 2. Determine scale

Where does this pattern sit in the design hierarchy?

| Scale | Applies to |
|-------|-----------|
| `verbs-interactions` | Single operations, state transitions, data transforms |
| `loops-systems` | Component boundaries, data flow, lifecycle management |
| `arcs-journeys` | User-facing flows, multi-step processes, session lifecycle |

### 3. Write the pattern

Use the template at `tools/templates/pattern.md`. The pattern MUST contain:

```markdown
---
kind: pattern
id: <slug>
name: "<Human Name>"
scale: <scale>
confidence: "★★" | "★" | "—"
above:
  - <parent-pattern-id if any>
resolves_into:
  - "behavior:<spec-id>"
  - "constraint:<spec-id>"
  - "dependency:<spec-id>"
---

# <Pattern Name>

## Forces

- **Desire:** <the attractive force — what it wants to become>
- **Constraint (hard|soft):** <the bounding force — what is given>
- (more forces if the tension involves >2)

## Tension

<One paragraph: the explicit conflict. "X wants Y, but Z demands W. Without a resolution, [what goes wrong].")

## Resolution

**<Resolution name>.** <How the forces are balanced. What configuration satisfies the desire while respecting the constraint. Specific enough to derive specs from.>

## Consequences

- <What this resolution demands downstream>
- <What new constraints it creates>
- <What it explicitly does NOT cover>

## Evidence

- <Prior art, domain rules, interview decisions, test results>
- <Cite with provenance: "Architecture interview decision #N", "grill:Q-file", "ADR-NNNN">
```

### 4. Set confidence

| Confidence | Criteria |
|------------|----------|
| ★★ | Multiple independent sources confirm. Prior art exists. Alloy/formal check passes. |
| ★ | One credible source (grill decision, ADR). Believed correct. May be revised. |
| — | Plausible arrangement. One approach among several. Low switching cost. |

### 5. Declare `resolves_into`

For each architectural commitment in the Resolution section, identify what spec kind it demands:

| Commitment type | Spec kind | Example |
|----------------|-----------|---------|
| "X has states A, B with transitions" | `behavior` | Ball possession state machine |
| "Only Y may write Z" | `constraint` | Single ball writer |
| "X must not import Y" | `dependency` | Executor boundaries |
| "Data shape must include fields A, B, C" | `contract` | Play data contract |

List each as `"<kind>:<proposed-id>"` in the frontmatter.

### 6. Validate

- Pattern has at least one desire AND one constraint
- Tension is stated as a conflict, not a solution
- Resolution is specific enough to derive specs from (not "do it well")
- Consequences are honest (include costs, not just benefits)
- Evidence cites actual sources, not assertions
- `resolves_into` links name specs that don't exist yet (they'll be created by `archwright-derive`)

## Does NOT

- Extract forces (receives them from `archwright-forces`)
- Identify tensions (receives from `archwright-tensions`)
- Derive specs (outputs `resolves_into` links; `archwright-derive` creates the specs)
- Resolve open tensions (only formalizes already-resolved ones)
- Set confidence to ★★ without formal verification evidence

## Batch Discipline

When formalizing multiple patterns in one session:
- Present patterns in groups of **3-4 max** for review
- After each group, pause for human feedback before writing the next group
- Cross-check network links (`context`, `completed_by`) across the batch — don't create orphan references
- If a pattern's `resolves_into` targets overlap with another pattern's, flag the overlap

## Writing Quality

- **Forces section:** Polarity is clear. Each force is one sentence. No solutions disguised as forces.
- **Tension section:** Reads as a problem statement. Someone unfamiliar can understand what's at stake.
- **Resolution section:** A named approach, bolded, followed by how it works. Specific enough that two developers would implement the same architecture from it.
- **Consequences section:** Honest. Includes "you'll also need X" and "this doesn't cover Y."
- **Evidence section:** Cited. Not "it's standard practice" but "FIFA/NBA2K use this pattern [source]."
