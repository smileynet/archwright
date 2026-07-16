---
name: archwright-tensions
description: "Cluster forces into tensions and identify which are resolved vs open. Takes a force inventory and produces named tension clusters with resolution status. Use when forces exist but tensions haven't been named, or to find gaps between what's decided and what's formalized. Trigger: name the tensions, what conflicts exist, cluster these forces, what's unresolved."
metadata:
  type: process
  invocation: both
  practice: null
---

# Archwright Tensions

Cluster extracted forces into named tensions. A tension is the explicit conflict between forces that constitutes the actual design problem.

**Core principle:** No tension = no design problem. If forces don't conflict, there's nothing to resolve. The interesting work lives at the intersections.

## Process

### 1. Receive input

A force inventory (from `archwright-forces`) for one or more areas.

### 2. Identify conflicts

For each desire, ask: "Which constraints push against this?"
For each constraint, ask: "Which desires does this limit?"

A tension exists when:
- A desire pulls toward X
- A constraint demands not-X (or bounds X)
- You can't satisfy both naively

### 3. Name each tension

A tension name should be readable as a design problem:
- "data-purity-vs-runtime-needs" — authored data wants to stay clean, execution needs mutable state
- "expressiveness-vs-plausibility" — coach wants to draw anything, execution demands physical feasibility
- "fluidity-vs-single-holder" — anyone should get the ball, but only one can have it

Format: `<desire-slug>-vs-<constraint-slug>` or a domain-meaningful phrase.

### 4. Check resolution status

For each tension, determine:

| Status | Meaning | Evidence |
|--------|---------|----------|
| `resolved` | A decision was made | Grill decision, ADR, or existing pattern |
| `partially-resolved` | Decision made but incomplete | Covers some cases, edge cases open |
| `open` | No decision yet | Area needs grilling |

For resolved tensions, identify the resolution source and write a one-line gist.

### 5. Check formalization status

For resolved tensions, determine:

| Formalization | Meaning |
|---------------|---------|
| `formalized` | Pattern exists in `design/patterns/` |
| `decided-not-formalized` | Decision made in grill/ADR but no pattern file |
| `coded-not-formalized` | Resolution is in the code but never written as a pattern |
| `none` | No decision and no pattern — the tension is open |

### 6. Output tension map

Write to `.memory/archwright-tensions-<area>.yaml` (working scaffolding, same convention as the forces inventory — durable resolutions later become patterns in `design/patterns/`):

```yaml
area: <area-name>

tensions:
  - id: <tension-slug>
    desire: "<the desire force id>"
    constraint: "<the constraint force id>"
    statement: "<one sentence: X wants Y, but Z demands W>"
    status: resolved | partially-resolved | open
    formalization: formalized | decided-not-formalized | coded-not-formalized | none
    resolution_source: "grill:Q03" | "adr:0002" | "pattern:ball-possession" | null
    resolution_gist: "<one line: how it was resolved>" | null
    pattern_id: "ball-possession" | null
    open_questions: [] | ["what about edge case X?"]

  - id: <tension-slug>
    ...

summary:
  total: 8
  resolved: 5
  partially_resolved: 1
  open: 2
  formalized: 3
  needs_formalization: 2
  needs_grilling: 2
```

## Clustering Heuristics

Forces cluster into tensions along these lines:
- **Same component, opposing pulls** — one desire says "do X here," one constraint says "never X here"
- **Same resource, competing consumers** — two desires want the same thing differently
- **Cross-boundary conflict** — a user desire vs a platform constraint
- **Temporal conflict** — correct now vs correct later (lifecycle mismatch)
- **Scale conflict** — works for 1 instance, breaks for N

## Does NOT

- Extract forces (that's `archwright-forces`)
- Resolve tensions (that's `archwright-resolve`)
- Write patterns or specs
- Invent tensions not supported by the force inventory
- Declare a tension "open" without checking all grill/ADR sources

## When All Tensions Are Pre-Resolved

If the force inventory comes from a mature grill corpus (every question decided), all tensions may arrive pre-resolved. This is normal — the output is still valuable because it:
- Names the tensions explicitly (they were implicit across scattered decisions)
- Confirms which decisions resolve which force-conflicts
- Identifies whether any tension was resolved by multiple independent decisions (possible inconsistency)
- Reveals missed tensions (force pairs that conflict but were never addressed)

In this case, the output serves as a confirmation map, not a discovery tool. The subsequent `archwright-resolve` phase becomes a human confirmation pass rather than a decision session.

## Judgments

- **One tension per conflict pair.** Don't split "fluidity vs single-holder" into sub-tensions unless the sub-resolutions are genuinely independent.
- **Multiple forces can contribute to one tension.** A 3-way conflict is still one tension if it resolves as one pattern.
- **A force can appear in multiple tensions.** "Testability" often conflicts with several constraints independently.
