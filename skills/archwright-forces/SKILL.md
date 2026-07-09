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

### 2. Read sources

For each source file:
- Grill Q-files: extract the **decision**, **rationale**, and **rejected alternatives**
- ADRs: extract the **context** (forces), **decision**, and **consequences**
- Spec requirements: extract the **requirement** and its **justification**
- Domain docs: extract **rules**, **physical constraints**, **user expectations**

### 3. Extract forces

For each decision/requirement found, identify:
- What **desire** motivated it (the pull — "we want X")
- What **constraint** bounded it (the push — "but Y is given")
- Whether the constraint is **hard** (inviolable) or **soft** (negotiable)

### 4. Classify and deduplicate

Forces recur across multiple sources. Cluster them:
- Same force stated differently in multiple grills → one force, multiple provenance entries
- A force that appears in code (an assertion, a guard) but was never stated → name it, tag as `inferred`
- A force implied by a rejected alternative → name it, tag as `implicit`

### 5. Output the force inventory

```yaml
area: <area-name>
sources_read:
  - path: ".memory/grills/play-data-schema/Q01-spec-authority.md"
    type: grill
  - path: ".memory/adr/0001-from-scratch.md"
    type: adr

forces:
  - id: <slug>
    polarity: desire | constraint-hard | constraint-soft
    statement: "<one sentence: what this force demands>"
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

| Source type | Where forces hide |
|-------------|-------------------|
| Grill decision | In the rationale ("we chose X because Y") |
| Grill rejection | In the rejected alternative ("not Z because W") |
| ADR context | Explicitly listed forces |
| Spec requirement | The "why" behind each R-number |
| Domain rules | Physical laws, sport rules, platform constraints |
| User expectations | "A coach expects..." / "A player needs..." |
