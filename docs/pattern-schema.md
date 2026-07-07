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
above:
  - practice-execution
resolves_into:
  - "behavior:ball-state-lifecycle"
  - "constraint:single-ball-holder"
  - "dependency:ball-write-ownership"
---

# Ball Possession

## Forces

- **Desire:** Any fielder can receive a pass at any time (fluidity)
- **Constraint (★★):** Exactly one entity holds the ball (physics)
- **Constraint (★★):** Only BallStateService writes possession (single source of truth)

## Tension

Free passing requires any fielder to receive at any time, but physics demands
exactly one holder. The architecture needs a single source of truth to prevent
split-brain.

## Resolution

Request/validate model. Controllers REQUEST transfers, BallStateService VALIDATES
and commits. Ball is "in flight" during transfer (no holder).

## Consequences

- Recovery path needed: what happens when validation rejects a transfer?
- In-flight duration becomes a tuning parameter (too long = unresponsive)

## Evidence

- Prior art: every team sport game uses single-authority possession
- 12 playtest sessions with request model, zero double-possession bugs
```

## Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `kind` | yes | Always `pattern` |
| `id` | yes | Unique slug — the token to reference this pattern |
| `name` | yes | Human-readable name |
| `scale` | yes | Design tower level: premise / loops-systems / verbs-interactions / feel-finish |
| `confidence` | yes | ★★ / ★ / — |
| `above` | no | IDs of larger patterns this helps complete |
| `resolves_into` | no | `kind:id` references to specs this pattern produces |

## Body Sections

| Section | Purpose |
|---------|---------|
| **Forces** | Desires and constraints — what's pulling in different directions |
| **Tension** | The explicit conflict statement — this IS the problem |
| **Resolution** | The generative move that balances forces |
| **Consequences** | New forces spawned by the resolution |
| **Evidence** | Why you believe this works (playtests, prior art, proof) |

The body is free-form markdown. Sections are conventional but not enforced by tools — the human (and agent) need the flexibility to express the resolution in whatever structure fits.

## Design Principles

- Frontmatter is **for machines** — validated, linked, indexed.
- Body is **for humans** — read, discussed, revised in conversation.
- `resolves_into` is the provenance link downward — specs trace back here.
- `confidence` gates everything: checking rigor, pass-up escalation, AI autonomy.
- Every pattern must name at least one tension. No tension = not a pattern, just a feature.
