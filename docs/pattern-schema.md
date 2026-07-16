# Pattern Schema

Patterns are **markdown documents with YAML frontmatter**. The frontmatter carries structured metadata (validated by tools). The body carries prose (forces, tensions, resolution narrative, evidence).

## Format

```markdown
---
kind: pattern
id: ball-possession
name: "Ball Possession"
scale: verbs-interactions
confidence: "★★"
status: active
serves:
  - practice-any-position
context:
  - practice-execution
completed_by: []
resolves_into:
  - "behavior:ball-state-lifecycle"
  - "constraint:single-ball-holder"
  - "dependency:ball-write-ownership"
---

# Ball Possession

## Problem

**A player wants any fielder to receive a pass at any time, but physics demands exactly one holder and architecture demands a single possession authority.**

## Context

In the context of practice-execution, where players practice from any position
and the system must support both human and AI controllers uniformly.

## Forces

- **Desire:** A player wants fluid passing — any fielder can receive at any time (practice-any-position)
- **Desire:** Possession changes should feel immediate and responsive (feel-like-real-practice)
- **Constraint (★★ hard):** Exactly one entity holds the ball (physics)
- **Constraint (★★ hard):** Only BallStateService writes possession (single source of truth)

## Evidence

(~70% of the pattern body)

- Prior art: every team sport game uses single-authority possession
- Rejected: direct writes from controllers → double-possession bugs in 3/12 playtests
- Rejected: event-sourced possession → unnecessary complexity for single-ball constraint
- Mechanism: the tension is structural, not incidental — physics REQUIRES single-holder

## Therefore

**Request/validate model.** Controllers REQUEST transfers via BallStateService.
BallStateService VALIDATES and commits. Ball is "in flight" during transfer
(no holder). This preserves fluidity (any controller can request) while
guaranteeing single-holder (only the service commits).

## Consequences

- Recovery path needed: what happens when validation rejects a transfer?
- In-flight duration becomes a tuning parameter (too long = unresponsive)
- All controllers must use the request API — no direct writes

## Verification

- Grep: `ball_holder` assignments occur only in `ball_state_service.gd`
- Model check: at-most-one-holder invariant across all reachable states
- Test: concurrent transfer requests never produce double-possession

## Completion

This pattern is incomplete unless it also contains:
- Transfer timing contract (how long can ball be in-flight?)
```

## Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `kind` | yes | Always `pattern` |
| `id` | yes | Unique slug — the token to reference this pattern |
| `name` | yes | Human-readable name |
| `scale` | yes | Design tower level: `premise` / `loops-systems` / `verbs-interactions` / `feel-finish` — canonical IDs, domain-invariant. Domain overlays (`tools/domains/<domain>/scales.yaml`) provide native labels per domain; the stored value is always the canonical ID. |
| `confidence` | yes | `★★` (mechanically verifiable) / `★` (heuristically checkable) / `—` (advisory, no mechanical check) |
| `status` | yes | `active` / `fog` (known gap) / `deprecated` (superseded) |
| `serves` | yes | IDs of product-level desires this pattern helps satisfy — **every pattern must trace to a human need** |
| `context` | no | IDs of larger patterns this helps complete (upward network links) |
| `completed_by` | no | IDs of smaller patterns needed to fill this out (downward links) |
| `resolves_into` | no | `kind:id` references to specs this pattern produces |
| `resolution_source` | no | References to existing decision records (ADRs, grills, tenets) that this pattern formalizes. Use when the pattern captures an EXISTING decision rather than introducing a new one. Format: `["adr:ADR-004", "tenet:4"]` |
| `links` | no | Same-level sibling relationships (`complements`, `conflicts-with`, `alternative-to`) |

## Body Sections

| Section | Purpose | Guidance |
|---------|---------|----------|
| **Problem** | The core tension as a single bold sentence — stated as a user/domain truth | Start with the human desire being constrained |
| **Context** | Where this sits in the pattern network | Which larger patterns it helps complete |
| **Forces** | Desires and constraints — what's pulling in different directions | List desires FIRST (product-level), then constraints. Desires span functional, emotional, and social jobs |
| **Evidence** | WHY these forces conflict — the longest section (~70% of body) | Rejected alternatives, prior art, empirical observations, mechanism |
| **Therefore** | The named resolution — what to DO | Specific enough to derive specs from. Constrains form without determining it |
| **Consequences** | New forces introduced, what's NOT covered, costs | Honest — includes what you give up |
| **Verification** | How to check compliance | Mechanical check (★★) or review criteria (★/—) |
| **Completion** | What smaller patterns are needed to fill this out | Stated as incompleteness |

The body is free-form markdown. Sections are conventional but not enforced by tools — the human (and agent) need the flexibility to express the resolution in whatever structure fits.

## Design Principles

- Frontmatter is **for machines** — validated, linked, indexed.
- Body is **for humans** — read, discussed, revised in conversation.
- **Desires are primary.** List them first in Forces. They initiate the pattern. Constraints respond to desires; they don't stand alone.
- **Forces span functional, emotional, and social dimensions.** A player wanting to "feel in control" (emotional) is as real a force as "exactly one holder" (physics).
- `serves` is the upward link to human purpose — patterns without it are architectural indulgence.
- `resolves_into` is the downward link to checkable specs — the provenance chain.
- `confidence` gates checking rigor: ★★ = model checker / proof / grep, ★ = tests / review, — = judgment.
- Every pattern must name at least one tension. No tension = not a pattern, just a feature.
- **Forces are discovered through scenario walks** — tracing a desire through the system until friction reveals the tension. The pattern documents the discovered tension and its resolution, not a pre-existing template.
