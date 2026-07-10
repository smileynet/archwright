---
name: archwright-forces
description: "Extract desires and constraints from project sources. Reads grills, ADRs, specs, and decisions to produce a structured force inventory. Use when forces need naming, when decisions exist but aren't captured as forces, or when an area has implicit but unnamed pressures. Trigger: extract forces, name the forces, what desires exist, what constrains this."
metadata:
  type: process
  invocation: both
  practice: null
---

# Archwright Forces

Extract and name the desires and constraints acting on a project area. Scan source material (grills, ADRs, specs, decisions) and produce a structured force inventory.

**Core principle:** Forces are first-class. A desire is an attractive force (what it wants to become). A constraint is a bounding force (what is given). Neither is a design — design exists only at the resolution of a tension between them.

## Process

### 1. Receive scope

The orchestrator or user provides:
- An area name (e.g., "play-data-pipeline", "editor-authoring")
- Source files to read (grill Q-files, ADRs, spec requirements)

### 2. Read sources — PRODUCT LEVEL FIRST

**Start with why.** Before reading architectural decisions, establish the product-level desires — what humans want to accomplish, not what the code wants to be.

Product-level sources (read FIRST):
- Project README — what the product IS and who it's FOR
- GitHub issues (especially user stories, closed features) — what users asked for
- Product backlogs, roadmaps, milestone descriptions — what's valued
- Domain rules (sport rules, coaching conventions) — what's given by the world

Then read architectural sources:
- Grill Q-files: extract the **decision**, **rationale**, and **rejected alternatives**
- ADRs: extract the **context** (forces), **decision**, and **consequences**
- Spec requirements: extract the **requirement** and its **justification**

**The key question for every architectural decision:** "Which human desire does this serve?" If you can't trace an architectural constraint back to a product-level desire, either the desire is unnamed (name it) or the constraint is unmotivated (flag it).

### 3. Extract forces at BOTH levels

#### Product-level desires (the WHY)
For each capability/feature, identify:
- Who wants it (coach, player, team admin)
- What they want to accomplish (JTBD — job to be done)
- What quality they expect (feel, speed, correctness, learnability)

These are phrased as human needs:
- "A player wants to practice running plays from any position to learn their responsibilities"
- "A coach wants to express any play they can draw on a whiteboard"
- "Practice should feel like real lacrosse, not a quiz or animation viewer"

#### Architectural forces (the HOW and WHAT)
For each decision/requirement found, identify:
- What **desire** motivated it (the pull — "we want X")
- What **constraint** bounded it (the push — "but Y is given")
- Whether the constraint is **hard** (inviolable) or **soft** (negotiable)

### 4. Link levels

Every architectural force should trace upward to a product-level desire:

```yaml
- id: play-manager-agnostic
  polarity: constraint-hard
  statement: "PlayManager3D must remain controller-type-agnostic"
  serves: practice-any-position  # ← this is what was missing
  # WHY: because players practice from any position, so the system must
  # support player AND AI controllers uniformly
```

If an architectural force has no `serves` link, it's either:
- An orphaned constraint (may be over-engineering)
- Serving an unnamed product desire (name it)

### 4. Classify and deduplicate

Forces recur across multiple sources. Cluster them:
- Same force stated differently in multiple grills → one force, multiple provenance entries
- A force that appears in code (an assertion, a guard) but was never stated → name it, tag as `inferred`
- A force implied by a rejected alternative → name it, tag as `implicit`

### 5. Output the force inventory

```yaml
area: <area-name>
sources_read:
  - path: "README.md"
    type: product
  - path: "GitHub issues (closed features)"
    type: product
  - path: ".memory/grills/play-data-schema/Q01-spec-authority.md"
    type: grill
  - path: ".memory/adr/0001-from-scratch.md"
    type: adr

product_forces:
  - id: <slug>
    polarity: desire
    statement: "<one sentence: what a human wants to accomplish>"
    who: coach | player | team-admin
    provenance:
      - source: "issue:#34"
        quote: "I want to be able to run plays as a given fielder, being shown the play to run"
    tags: [explicit]

forces:
  - id: <slug>
    polarity: desire | constraint-hard | constraint-soft
    statement: "<one sentence: what this force demands>"
    serves: <product-force-id>
    provenance:
      - source: "grill:play-data-schema/Q01"
        quote: "<exact quote from source>"
      - source: "adr:0001"
        quote: "<exact quote>"
    tags: [explicit | implicit | inferred]

  - id: <slug>
    ...
```

## Quality Checks

Before presenting output:
- **Product forces exist.** If the inventory has zero product-level desires, you skipped the most important sources. Go read the README, issues, and user stories.
- Every product force names WHO wants it and WHAT they want to accomplish
- Every architectural force has a `serves` link to a product force (or is flagged as orphaned)
- Every force has at least one provenance entry with a quote
- No force is stated as a solution (forces are pressures, not decisions)
- Desires are phrased as "X wants Y" (attractive)
- Constraints are phrased as "Y is given/required/inviolable" (bounding)
- Hard vs soft is justified (could you violate it and still ship?)

## Does NOT

- Cluster forces into tensions (that's `archwright-tensions`)
- Propose resolutions (that's `archwright-resolve`)
- Write patterns or specs
- Read implementation code (forces live in stated decisions)
- Make up forces that aren't in the sources (tag `inferred` if reading between lines)

## Subagent Dispatch (at scale)

When multiple areas each have 5+ source files, dispatch one subagent per area for **extraction only**. See `subagent-reliability` steering.

**Per-stage prompt shape (extraction — good for subagents):**
```
Read ALL files in [directory]. For each file, extract:
- Desires (what the system wants to be)
- Constraints (hard bounds)
Include exact quotes as provenance. Output as structured YAML.
```

**Deduplication — do directly, not via subagent:**
Synthesis tasks (merging, deduplicating, clustering) should be done in the main context. Subagents read well but synthesize provided text poorly.

**If survey already extracted raw forces:** Skip re-extraction. Read the survey subagent results from `.scratch/archwright-raw/` or the survey output directly. The forces phase becomes pure dedup + validation — done directly.

**Validation after subagent return:**
- Count forces vs files read. Expect ≥1 force per source file on average.
- Check every source file is mentioned in the output.
- Thin output (< 50% expected volume) = flag for re-read or retry.

**On failure:** Report which areas failed, retry once with smaller scope, then do directly with explicit "fallback" documentation in the output.

## Common Force Sources

| Source type | Where forces hide | Level |
|-------------|-------------------|-------|
| User stories / issues | "As a [user], I want [X] so that [Y]" | Product |
| Product README | What the thing IS and who it serves | Product |
| Domain rules | Physical laws, sport rules, coaching conventions | Product |
| User expectations | "A coach expects..." / "A player needs..." | Product |
| Grill decision | In the rationale ("we chose X because Y") | Architecture |
| Grill rejection | In the rejected alternative ("not Z because W") | Architecture |
| ADR context | Explicitly listed forces | Architecture |
| Spec requirement | The "why" behind each R-number | Architecture |

**If your inventory has no product-level forces, you haven't looked in the right places.** Every project exists to serve someone. Name those desires first — they're what gives architectural constraints meaning.
