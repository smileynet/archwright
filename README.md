# Archwright

Design decisions that compound in your favor.

## What Archwright Is

A strategic advisor for product design — embodied as AI agent skills. It surfaces the forces shaping your product, helps you resolve tensions at the right altitude, and verifies those resolutions hold over time.

The architecture is the output of the advisory process, not the process itself.

## The Insight

Every product has forces pulling it in different directions — what users want, what the technology allows, what the business needs, what physics demands. Most teams resolve these forces implicitly: whoever commits first wins the architecture.

Archwright makes this explicit. It helps you see what's in tension, resolve it deliberately, and ensure the resolution compounds rather than erodes.

## Two Modes

| Mode | What it does | Role |
|------|-------------|------|
| **Advisor** | Surfaces forces, names tensions, proposes resolutions | Counselor — reveals what you can't see alone |
| **Guardian** | Formalizes decisions, derives specs, verifies alignment | Enforcer — ensures what you decided stays true |

```
┌──────────────── ADVISOR ────────────────┐
│                                          │
│  forces → tensions → resolve → formalize │
│                                          │
│  "What's this trying to become?          │
│   What's in conflict? How do we resolve?"│
│                                          │
├──────────────── GUARDIAN ────────────────┤
│                                          │
│  model → contract → derive → check       │
│                                          │
│  "Now that you've decided —              │
│   I'll make sure it's honored."          │
│                                          │
└──────────────────────────────────────────┘
```

## How It Works

1. **You express a desire** — "I want any fielder to receive a pass at any time"
2. **The advisor surfaces what pushes back** — "But physics says exactly one holder. And your architecture says only BallStateService writes possession."
3. **You resolve the tension** — "Request/validate model. Controllers request, BallStateService commits."
4. **The decision gets formalized** — pattern captured with forces, tension, resolution, provenance
5. **Specs fall out** — the resolution implies checkable structure
6. **The guardian enforces** — three weeks later, when `fielder_ai.gd` writes `ball_holder = self`, the check catches it and routes back to the decision it violated

## The Pipeline

```
survey → forces → tensions → resolve → formalize → model → contract → derive → check
└──────────── advisor ──────────────┘   └──────────── guardian ──────────────┘
```

Each phase produces an artifact. The human reviews before the next begins.

## Core Ideas

**Resolution altitude** — Resolve tensions at the highest level that produces coherence below. A strategic resolution at the top makes thousands of implementation decisions locally obvious. A tension left unresolved at the top becomes a contradiction in every PR.

**Forces stay first-class** — Product-level desires (what humans need) are primary. Architectural constraints exist to serve those desires via explicit traceability.

**The architecture talks back** — When implementation drifts from intent, violations route back through the provenance chain to the specific decision that was violated. The advisor remembers what the team forgets.

**You decide. Always.** — The advisor surfaces, proposes, and verifies. It never decides on anything that matters. Confidence levels (★★/★/—) control how much latitude the advisor has, per decision.

## Verification Tools

```bash
mise run rehydrate-alloy   # or without mise: python tools/install-alloy.py
python tools/archwright-check.py design/specs/example-behavior.yaml
```

Behavior checks compile to Alloy 6 for bounded model checking. Constraint/dependency specs run against the codebase via grep, semgrep, or custom scripts.

## Documentation

| Document | Contents |
|----------|----------|
| [Brief](docs/brief.md) | The full story in one page |
| [Lineage](docs/lineage.md) | Alexander → this, and what software dropped along the way |
| [Findings](docs/findings.md) | The 9 load-bearing theoretical insights |
| [Glossary](docs/glossary.md) | All concepts and terminology |
| [Prior Art](docs/prior-art.md) | The 5 traditions we draw from |
| [Open Questions](docs/open-questions.md) | Prioritized research backlog |

## Project Status

Research + design phase, with working verification tools (schema validation, trace replay, grep conformance, bounded Alloy checking). Field-tested on two projects.

## Lineage

Archwright evolves from:
1. **spec-driven-development** — structured planning
2. **project-overseer** — drift detection
3. **archwright** — strategic design advisory with formal verification
