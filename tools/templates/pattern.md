---
kind: pattern
id: pattern-slug
name: "Human-Readable Name"
scale: loops-systems       # premise | loops-systems | verbs-interactions | feel-finish
confidence: "—"            # ★★ | ★ | —
status: active             # active | fog | deprecated
serves: []                 # IDs of product-level desires this pattern helps satisfy
context: []                # IDs of larger patterns this helps complete (upward links)
completed_by: []           # IDs of smaller patterns needed to fill this out (downward links)
resolves_into: []          # kind:id references to specs this produces
---

# Pattern Name

## Problem

**Single bold sentence: the core tension stated as a user/domain truth.**

## Context

Which larger patterns this helps complete. Where it sits in the hierarchy. "In the context of [larger pattern], this pattern addresses [aspect]."

## Forces

- **Desire:** (what you want — the attractive force, stated as a user need)
- **Constraint (hard|soft):** (what bounds you — the limiting force, stated as a given)

## Evidence

(The longest section — ~70% of the pattern. WHY these forces conflict.)

- Rejected alternatives (configurations that fail, and why)
- Prior art (how others handle this — cite specifically)
- Empirical observations (what happens without a resolution)
- Mechanism (why the tension is structural, not incidental)

## Therefore

**Named resolution.** The instruction — what to DO. Specific enough to derive specs from. Captures the invariant property common to all valid solutions, not one implementation.

(Constrains form without determining it. Specifies relationships, not artifacts.)

## Consequences

- (What this resolution demands downstream — new forces it introduces)
- (What it explicitly does NOT cover)
- (Cost: what you give up or what becomes harder)

## Verification

How to check compliance:
- (What mechanical check exists, or what review criteria apply)

## Completion

This pattern is incomplete unless it also contains:
- (Smaller patterns needed to fill it out — stated as incompleteness)
