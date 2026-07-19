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

Where does this pattern sit in the design hierarchy? Load the domain overlay's `../archwright-survey/references/domains/<domain>/scales.yaml` (deployed; source: `tools/domains/` in the archwright repo) (domain comes from the survey's intake outline; fallback `general`) and use its labels/examples when discussing scale with the human. The `scale:` frontmatter field always stores the **canonical id** — the enum in `tools/pattern-schema.yaml` is domain-invariant:

| Canonical id (stored) | Level | Domain overlay provides |
|-----------------------|-------|-------------------------|
| `premise` | Foundational commitments that constrain everything below | native label + examples (game: "Premise", web: "Product Vision", general: "Purpose & Commitments") |
| `loops-systems` | Component boundaries, data flow, lifecycle, orchestration | native label + examples |
| `verbs-interactions` | Single operations, state transitions, user-facing actions | native label + examples |
| `feel-finish` | Sensory/ergonomic qualities, accessibility, polish | native label + examples |

Also load `../archwright-survey/references/domains/<domain>/predicates.yaml` (plus `general/predicates.yaml` for non-general domains) — predicates are named prior art for the Evidence section.

### 3. Write the pattern

Use the template at `tools/templates/pattern.md`. The pattern MUST contain:

```markdown
---
kind: pattern
id: <slug>
name: "<Human Name>"
scale: <scale>
confidence: pending  # Set after prior art research (Step 5)
status: active       # active | fog | gated | deprecated. gated = resolution RATIFIED,
                     # activation gated on a named event — add gated_on: "<unblocking event>".
                     # NEVER repurpose fog for a ratified deferral: fog means unresolved
                     # tension and blocks the pipeline (ticket 011).
serves:
  - <product-desire-force-id>   # REQUIRED — validation gate rejects patterns without a serves link
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

### 4. Research prior art

After the full batch of patterns is written and reviewed for correctness, research independent validation of each resolution. This runs ONCE for the batch (not per-pattern) and is parallelizable via subagents.

**Do not assign confidence until this step completes.** Confidence is set once, informed by research.

**Search for (per pattern):**
- Industry implementations of the same resolution (how do other platforms solve this tension?)
- Academic papers formalizing the principle (has anyone proven this works?)
- Cloud provider guidance recommending the approach (AWS Well-Architected, Azure, etc.)
- Documented failures of the rejected alternatives (evidence that NOT doing this breaks things)

**For each source found, record:**
- Name/title and URL
- Year
- Relationship: `confirms` | `contradicts` | `extends` | `similar`
- One-line note on how it relates

**Output:** Add a `prior_art` section to the pattern's Evidence block:

```yaml
prior_art:
  - title: "FrugalGPT: How to Use Large Language Models While Reducing Cost"
    url: https://arxiv.org/abs/2305.05176
    year: 2023
    relationship: confirms
    note: "98% cost reduction with cascade routing. Same exit-at-first-confident-tier principle."
```

**Present results as a summary table for human confirmation:**

```
┌─────────────────────────────┬─────┬─────────────────────────────────┐
│ Pattern                     │ ★   │ Key source                      │
├─────────────────────────────┼─────┼─────────────────────────────────┤
│ tiered-classification       │ ★★  │ FrugalGPT + AWS Well-Architected│
│ shadow-scoring-migration    │ ★   │ Components confirmed, combo novel│
└─────────────────────────────┴─────┴─────────────────────────────────┘
```

The human confirms or overrides (can promote or demote any pattern's confidence).

**When to skip:** If the pattern is a premise-level commitment unique to this project (e.g., a market-position choice like "self-deploy only"), note "deliberate project-specific choice — prior art not applicable" and assign ★ or — based on internal evidence only.

**Grill-embedded research path:** When the source corpus is a researched grill (grill-with-docs output — every decision already carries cited EXTERNAL sources that passed the G1–G3 research gates), a fresh research dispatch may be skipped: reuse the grill's citations in the Evidence section and assign confidence from them (★★ still requires 2+ independent sources from different categories — the grill must actually cite them, not just assert). The confidence table is still presented for human confirm/override — at the batch review, or at the span digest when running inside a pre-authorized span (field-validated: TileRush areas 1–3). Uncited grill decisions get no such shortcut — research them.

**Discovery-ledger citations (ADR 0011):** Evidence sections accept ledger anchors (`<artifact-id>#D{NNN}` from `design/discovery/`) as first-class evidence — the entry's verbatim rationale is the user's own words (empirical, strong) and its Alternatives field is a documented rejected alternative. This is how design-system tension resolutions graduate (their Graduates-to-Patterns rows arrive citing their entries). Ledger citations satisfy the internal-evidence leg; ★★ still needs external prior art per the rule above.

### 5. Set confidence

Confidence is assigned AFTER research completes:

| Confidence | Criteria |
|------------|----------|
| ★★ | 2+ independent sources confirm from different categories (industry + academic, or industry + cloud guidance). OR Alloy/formal check passes. |
| ★ | One credible source (grill decision, single prior art reference, ADR). Believed correct. May be revised. Resolution is novel or project-specific. |
| — | No prior art found. Plausible arrangement. One approach among several. Low switching cost. |

A contradicting source does not automatically prevent ★★ — it may reveal a scope boundary ("this works in context X but not Y"). Flag contradictions in the Evidence section and explain why the resolution still holds for this project's context.

### 6. Declare `resolves_into`

For each architectural commitment in the Resolution section, identify what spec kind it demands:

| Commitment type | Spec kind | Example |
|----------------|-----------|---------|
| "X has states A, B with transitions" | `behavior` | Ball possession state machine |
| "Only Y may write Z" | `constraint` | Single ball writer |
| "X must not import Y" | `dependency` | Executor boundaries |
| "Data shape must include fields A, B, C" | `contract` | Play data contract |
| "Event X carries fields Y, Z" | `contract` | Fragment delivery events |
| "Actor state must persist across save/load" | `contract` | Zone persistence schema |

List each as `"<kind>:<proposed-id>"` in the frontmatter.

**Include contract specs proactively.** Every pattern that introduces actors with owned state or cross-boundary events should declare contract specs in `resolves_into` alongside behavior/constraint specs. The `archwright-contract` phase produces these, but they need to be declared here so the pipeline knows to expect them.

### 7. Validate

- Pattern has at least one desire AND one constraint
- Tension is stated as a conflict, not a solution
- Resolution is specific enough to derive specs from (not "do it well")
- Consequences are honest (include costs, not just benefits)
- Evidence cites actual sources, not assertions
- `resolves_into` links name specs that don't exist yet (created downstream: contract specs by `archwright-contract`, the rest by `archwright-derive`)
- `serves` links to at least one product-level desire from the force inventory — patterns without a human purpose are architectural indulgence

### 8. Audit tension coverage (batch runs)

When formalizing from a tension map, close the loop before finishing: every tension in the map must have (a) a pattern, (b) an explicit fold note ("folds into pattern X — same resolution"), or (c) an explicit defer note with reason. Silent gaps hide easily in batches — a field run wrote 9 patterns for a 9-tension map and still missed one tension (two patterns had come from the same tension, one from an unopposed given); only a mechanical tension→pattern recount caught it.

## Does NOT

- Extract forces (receives them from `archwright-forces`)
- Identify tensions (receives from `archwright-tensions`)
- Derive specs (outputs `resolves_into` links; downstream phases create them — `archwright-model` structures actors, `archwright-contract` writes contract specs, `archwright-derive` writes behavior/constraint/dependency specs)
- Resolve open tensions (only formalizes already-resolved ones)
- Set confidence to ★★ without prior art research or formal verification evidence

## Batch Discipline

When formalizing multiple patterns in one session:
- Present patterns in groups of **3-4 max** for review
- After each group, pause for human feedback before writing the next group
- Cross-check network links (`context`, `completed_by`) across the batch — don't create orphan references
- If a pattern's `resolves_into` targets overlap with another pattern's, flag the overlap
- **Research runs ONCE after ALL patterns in the batch are written and approved.** Dispatch one subagent per pattern (or per cluster of related patterns) in parallel. Do not research between groups — it interrupts the writing flow.

## Writing Quality

- **Forces section:** Polarity is clear. Each force is one sentence. No solutions disguised as forces.
- **Tension section:** Reads as a problem statement. Someone unfamiliar can understand what's at stake.
- **Resolution section:** A named approach, bolded, followed by how it works. Specific enough that two developers would implement the same architecture from it.
- **Consequences section:** Honest. Includes "you'll also need X" and "this doesn't cover Y."
- **Evidence section (substance, not volume — ticket 014):** Every Therefore commitment traces to at least one Evidence item (prior art, rejected alternative, or mechanism argument) — a commitment with no supporting evidence fails the gate. Citations are locatable ("FIFA/NBA2K use this pattern [source]", never "it's standard practice") and carry a year/version so staleness is visible. There is NO length quota — a short Evidence section that covers every commitment beats a long one that doesn't.
