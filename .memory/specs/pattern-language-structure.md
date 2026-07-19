# Spec: Pattern Language Structure

**ID:** pattern-language-structure
**Status:** Accepted
**Covers:** Pattern schema updates, network model, scale bands, confidence criteria, project language
**Source:** Alexander's *A Pattern Language* (1977), research findings from OCR extraction + analysis

## Purpose

Define how archwright organizes patterns for navigability and scalability at 50-100+ patterns. Based on Alexander's structural decisions (253 patterns, navigable via bidirectional network + scale ordering) adapted for software verification.

---

## Pattern Template (revised)

```markdown
---
kind: pattern
id: <slug>
name: "<Human Name>"
scale: premise | loops-systems | verbs-interactions | feel-finish
confidence: "★★" | "★" | "—"
status: active | fog | deprecated
context:
  - <larger-pattern-id>    # patterns this helps complete (upward links)
completed_by:
  - <smaller-pattern-id>   # patterns needed to fill this out (downward links)
resolves_into:
  - "behavior:<spec-id>"
  - "constraint:<spec-id>"
  - "dependency:<spec-id>"
  - "contract:<spec-id>"
---

# <Pattern Name>

## Problem

**<Single bold sentence: the core tension stated as a human truth. This is the thesis that everything below proves.>**

## Context

<Which larger patterns this helps complete. Where it sits in the hierarchy. One paragraph establishing scope — stated as "in the context of [larger pattern], this pattern addresses [aspect].">

## Forces

- **Desire:** <attractive force — what it wants to become>
- **Desire:** <second desire if multi-force tension>
- **Constraint (<hard|soft>):** <bounding force — what is given>
- **Constraint (<hard|soft>):** <second constraint if needed>

## Evidence

<The longest section. WHY these forces conflict. Includes:>
- Rejected alternatives (configurations that fail, and why)
- Prior art (how others handle this — cite specifically)
- Empirical observations (what happens without a resolution)
- Mechanism (why the tension is structural, not incidental)
- Examples from different scales/contexts (showing the principle is general)

Aim: ~70% of the pattern's length. By the time the reader reaches "Therefore," the resolution should feel inevitable.

## Therefore

**<Named resolution approach.>** <How the forces are balanced. Stated as an instruction — what to DO. Specific enough to derive specs from. Captures the invariant property common to all valid solutions, not one specific implementation.>

<The solution constrains the form without determining it. It specifies RELATIONSHIPS, not artifacts.>

## Consequences

- <What this resolution demands downstream — new forces it introduces>
- <What it explicitly does NOT cover — boundaries of the resolution>
- <Cost: what you give up or what becomes harder>

## Verification

<How to check whether an implementation satisfies this pattern:>
- ★★: <mechanical check — invariant, grep, trace, model>
- ★: <heuristic check — proxy invariant, review criteria>
- —: <advisory — no mechanical check, human judgment>

## Completion

<Which smaller patterns are needed to fill this out. "This pattern is incomplete unless it also contains [X], [Y], [Z]." Stated as incompleteness, not just a list of links.>
```

---

## Scale Bands

| Band | Prefix | Alexander Equivalent | Scope | Typical Spec Kinds |
|------|--------|---------------------|-------|-------------------|
| **Premise** | P## | Regions/Towns | Genre, whole experience, product vision | Constraint (global rules) |
| **Loops & Systems** | L## | Buildings | Component boundaries, data flow, lifecycle | Constraint + Dependency |
| **Verbs & Interactions** | V## | Rooms | State transitions, moment-to-moment actions | Behavior + Constraint |
| **Feel & Finish** | F## | Construction/Ornament | Presentation, affordances, micro-interactions | Constraint (specific rules) |

**Scale determines specificity:**
- P-band: heuristic, directional ("do everything possible to...")
- L-band: constraint-based, specific on boundaries and relationships
- V-band: state machines, transitions, guards — formally checkable
- F-band: near-code-level rules, measurements, thresholds

**Numbering:** Patterns are numbered within bands (L01, L02... V01, V02...). Gaps are allowed — new patterns insert without renumbering. The ordering within a band goes from larger scope to smaller.

---

## Network Model

### Bidirectional Links

Every pattern has:
- **`context`** (upward) — larger patterns this helps complete. These create the ENVIRONMENT the pattern lives in.
- **`completed_by`** (downward) — smaller patterns needed to fill this out. Without these, the pattern is structurally incomplete.

The relationship is **incompleteness**: Pattern A is incomplete unless it contains Pattern B; Pattern B is incomplete unless embedded in Pattern A.

### Traversal

Design-time traversal goes **large → small** (following `completed_by` links). This is the generative direction — each level constrains the solution space further.

Pass-up traversal goes **small → large** (following `context` links). This is the correction direction — violations route upward to the force that was violated.

### Same-Level Siblings

Patterns at the same scale may reference each other laterally. Use `links` in the frontmatter for non-hierarchical relationships:
```yaml
links:
  - target: "pattern:sibling-pattern"
    type: complements | conflicts-with | alternative-to
```

---

## Confidence Criteria (revised)

Confidence is about whether the SOLUTION is an invariant — not whether the PROBLEM is real.

| Level | Meaning | Verification | Agent Behavior |
|-------|---------|--------------|----------------|
| ★★ | True invariant — you CANNOT solve this problem without conforming to this pattern | Mechanical check exists (trace, static, model). Includes a calculation or built evidence. | Must escalate violations |
| ★ | Believed correct — compelling logic, evidence supports it, but solution not exhaustively validated | Heuristic check (proxy invariant, review criteria). May have valid exceptions. | Propose fixes, human confirms |
| — | One approach — names a real problem but the solution is one arrangement among several | Advisory only. No mechanical check. | May auto-adjust or log |

**Promotion criteria (— → ★ → ★★):**
- — → ★: Evidence from one credible source (implementation proves it works)
- ★ → ★★: Multiple independent sources + formal verification passes + no known exceptions

---

## Fog Patterns

For areas where we know a pattern SHOULD exist but can't yet formalize:

```yaml
---
kind: pattern
id: player-embodiment
scale: verbs-interactions
confidence: "—"
status: fog
context:
  - practice-session-lifecycle
completed_by: []
resolves_into: []
---

# Player Embodiment

## Problem

**How does a player feel present on a virtual field — what separates "watching dots" from "being there"?**

## Forces
(not yet extracted — needs grilling)

## Therefore
(open — no resolution yet)
```

Fog patterns are:
- Visible in the INDEX (gaps are explicit, not hidden)
- Listed as `status: fog` so tools skip them during checking
- Don't generate specs until resolved
- Graduate to `active` when forces are named and resolution is found

---

## Project Language

Each project speaks a SUBSET of the full pattern catalog. The project's language is defined by which patterns it traverses, starting from its scope.

**Artifact:** `design/LANGUAGE.md`

```markdown
# Pattern Language: <Project Name>

## Starting Scope
<The pattern that defines the overall project — the entry point for traversal>

## Active Patterns
<Ordered list, large → small, showing the traversal path this project takes>

| # | Pattern | Scale | Confidence |
|---|---------|-------|------------|
| L01 | [Practice session lifecycle](patterns/L01-practice-session-lifecycle.md) | Loops | ★ |
| L02 | [Execution purity](patterns/L02-execution-purity.md) | Loops | ★★ |
| V01 | [Ball possession](patterns/V01-ball-possession.md) | Verbs | ★★ |
| ... | | | |

## Custom Patterns
<Patterns specific to this project, not from the general catalog>

## Fog
<Known gaps — areas where patterns should exist but don't yet>
```

**Subset selection procedure** (adapted from Alexander):
1. Find the pattern matching your project's overall scope (starting pattern)
2. Follow its `completed_by` links — almost all will be relevant. Add them.
3. For each added pattern, follow ITS `completed_by` links. Add relevant ones.
4. When in doubt, don't include it — the list can easily get too long.
5. Add project-specific patterns at appropriate scale positions.
6. Modify patterns as needed — they're hypotheses, not scripture.

---

## Compression / Density

Quality metric: how many patterns does a single architectural element resolve?

**Assembly** (low density): each pattern maps to a separate component. The architecture feels like a checklist — functional but not cohesive.

**Compression** (high density): one component resolves multiple patterns simultaneously. The architecture feels inevitable — each element earns its place by satisfying several forces at once.

Track via `satisfies_patterns` in specs:
```yaml
# In a behavior spec:
satisfies_patterns:
  - "pattern:ball-possession"      # the state machine satisfies this
  - "pattern:explicit-dependencies" # the injection model also satisfies this
```

**Design guidance:** Prefer architectures where fewer elements satisfy more patterns. If you find yourself creating a component solely for one pattern, ask whether it could be compressed into an existing element.

---

## File Naming

```
design/
├── LANGUAGE.md                         # This project's pattern subset
├── patterns/
│   ├── INDEX.md                        # Network map (all patterns, links, status)
│   ├── L01-practice-session-lifecycle.md
│   ├── L02-execution-purity.md
│   ├── L03-explicit-dependencies.md
│   ├── V01-ball-possession.md
│   ├── V02-kind-first-action-model.md
│   └── ...
└── specs/
    ├── ball-state-lifecycle.yaml
    ├── no-autoloads.md
    └── ...
```

Band prefix + number + slug. The prefix provides visual scale filtering. Numbers are stable references (like Alexander's `(12)`).

---

## Schema Updates Required

Add to `tools/pattern-schema.yaml`:

```yaml
# New/renamed fields
context:
  type: array
  items: {type: string}
  description: "Larger patterns this helps complete (upward network links)"

completed_by:
  type: array
  items: {type: string}
  description: "Smaller patterns needed to fill this out (downward network links)"

status:
  type: string
  enum: [active, fog, deprecated]
  default: active

links:
  type: array
  items:
    type: object
    properties:
      target: {type: string}
      type: {type: string, enum: [complements, conflicts-with, alternative-to]}
```

Rename in existing patterns:
- `above:` → `context:`
- Add `completed_by:` (new, was implicit)
- Add `status: active` (new, default)

---

## Validation Criteria

- [ ] Pattern schema updated with new fields
- [ ] Existing 3 patterns in FBC renamed with band prefixes and updated to new template
- [ ] INDEX.md created showing the network
- [ ] LANGUAGE.md created showing the project's pattern subset
- [ ] `archwright-validate` accepts the new fields
- [ ] Fixture tests still pass after schema update
- [ ] At least one pattern demonstrates the full new template (Problem → Forces → Evidence → Therefore → Consequences → Verification → Completion)

## Links

- Prior art: Alexander's *A Pattern Language* (1977) — `.references/a-pattern-language/`
- Prior art: POSA vol. 1 three-level hierarchy (Architectural/Design/Idiom)
- Prior art: Björk & Holopainen Game Design Patterns (200+ patterns, category-based)
- Consumed by: `archwright-formalize`, `archwright-derive`, `archwright-survey`
- Implements: Finding #3 (invariant = compiled form of resolved force)
