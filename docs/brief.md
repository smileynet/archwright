# Archwright: A Brief

## What It Is

A design methodology — embodied as AI agent skills — that captures *why* you made design decisions, then verifies your architecture actually honors them.

You express intent as **forces** (what you want vs. what constrains you). The agent helps **resolve** those forces into checkable specs. When something violates the stated intent, the system tells you *what* broke, *why*, and *which decision* to revisit.

## The Problem

Design intent gets lost. You decide "only one entity can hold the ball" in a planning session. Three weeks later, a controller writes `ball_holder = self` directly. Nobody catches it because the decision lives in a doc nobody re-reads.

```
  Decision                     Code (3 weeks later)
  ┌────────────────┐          ┌──────────────────────┐
  │ "Only one      │          │ // BallStateService  │
  │  entity holds  │   ???    │ ball_holder = player_a│
  │  the ball"     │──────>   │                      │
  └────────────────┘          │ // FielderAI (oops)  │
                              │ ball_holder = self    │
                              └──────────────────────┘
```

Archwright makes decisions **checkable** — they're not just documentation, they're verification contracts.

## How It Works

### Step 1: Name the Forces

In conversation, you express what you want and what limits you. The agent helps make it precise:

```
  DESIRE:     "Any fielder can receive a pass at any time"
  CONSTRAINT: "Exactly one entity holds the ball" (physics — ★★)
  CONSTRAINT: "Only BallStateService writes possession" (architecture — ★★)
```

The ★★ means "true invariant — this must never be violated."

### Step 2: Resolve the Tension

Forces pull in different directions. You find a configuration that satisfies all of them:

```
  RESOLUTION: Request/validate model.
  Controllers REQUEST transfers.
  BallStateService VALIDATES and commits.
  Ball is "in flight" during transfer (no holder).
```

This gets captured as a **pattern** — a YAML file recording the forces, the tension, and how you resolved it.

### Step 3: Express as Checkable Specs

The resolution becomes concrete specs — each one verifiable:

```
  ┌─ behavior:ball-state-lifecycle ──────────────────┐
  │                                                  │
  │  Held ──[REQUEST]──> In-Flight ──[VALIDATE]──>  │
  │   ↑                      │              Held    │
  │   │                      │ [invalid]    (new)   │
  │   └──────────────────────┘                      │
  │            (returned to sender)                  │
  │                                                  │
  │  INVARIANT: at most one holder at any time (★★)  │
  └──────────────────────────────────────────────────┘

  ┌─ constraint:single-ball-holder ──────────────────┐
  │  "Only BallStateService writes ball_holder"      │
  │  check: grep for ball_holder assignments         │
  │  expect: only in ball_state_service.gd           │
  └──────────────────────────────────────────────────┘

  ┌─ dependency:ball-write-ownership ────────────────┐
  │  allowed: BallStateService → ball_holder (write) │
  │  forbidden: anything else → ball_holder (write)  │
  └──────────────────────────────────────────────────┘
```

### Step 4: Check

The agent runs verification. Behavior specs get model-checked (Alloy finds counterexamples in <500ms). Constraint and dependency specs get checked against the actual codebase:

```
  $ archwright-check ball-state-lifecycle.yaml
    ✓ at-most-one-holder: PASS

  $ archwright-check single-ball-holder.yaml
    ✗ FAIL: ball_holder assigned outside BallStateService
      src/controllers/fielder_ai.gd:183
      content: "ball_holder = self"
```

### Step 5: Route the Correction

Every spec element traces back to the force that created it. The violation tells you exactly what to fix and why:

```
  VIOLATION: fielder_ai.gd writes ball_holder directly
  INVARIANT: single-ball-holder (★★)
  FROM: pattern:ball-possession → constraint:single-writer
  FIX DIRECTION: use BallStateService.request_transfer() instead

  ★★ = must escalate to human before changing
```

## What Lives Where

```
  your-project/
    design/
      patterns/                        # WHY — forces + resolutions
        ball-possession.md               (markdown — humans read these)
        practice-execution.md
      specs/                           # WHAT — checkable architecture
        ball-state-lifecycle.yaml        (kind: behavior — YAML)
        resolved-play-view.yaml          (kind: contract — YAML)
        single-ball-holder.md            (kind: constraint — markdown)
        ball-write-ownership.md          (kind: dependency — markdown)
```

**Patterns** = markdown with YAML frontmatter. Humans read the prose; tools validate the frontmatter.
**Specs** = YAML for machine-processed specs (behavior, contract). Markdown+frontmatter for human-read specs (constraint, dependency).
Your test suite verifies the implementation matches the specs.

## The Confidence System

Not all decisions are equally sacred:

```
  ★★  This must ALWAYS hold. Physics. Security. Data integrity.
      → Checked rigorously. Violations escalate to human.

  ★   We believe this is right. Evidence supports it.
      → Checked normally. Agent proposes fixes.

  —   One approach. Untested. Might change.
      → Checked lightly. Agent may auto-adjust.
```

Confidence can be promoted (evidence accumulates) or demoted (counterexample found).

## The Agent's Role

The agent holds the methodology. It:

- Helps you **name forces** from conversation (what do you want? what bounds you?)
- Helps you **find resolutions** (proposes options, researches prior art)
- **Formalizes** ratified decisions as patterns + specs
- **Checks** specs against each other and against your code
- **Routes corrections** back to the responsible decision when violations are found

You decide. The agent prepares, proposes, and verifies.

## Key Ideas

1. **Forces stay first-class.** The reusable knowledge is the method of naming and resolving tensions — not a template library.

2. **"Resolves into" not "compiles to."** Design intent doesn't mechanically transform into architecture. It's creatively resolved, then formally verified.

3. **The agent IS the system.** Intelligence lives in skills (methodology). Tools handle only deterministic operations (schema validation, model checking, grep).

4. **Trust via verification.** Once specs are proven consistent, you review the *intent* (pattern), not the *output* (spec). The checking handles correctness.

5. **Contrast pairs over raw errors.** When something breaks, show the violation next to the nearest valid alternative. The *diff* is the diagnosis.

## Limitations & Honest Claims

**What archwright CAN do:**
- Catch structural violations in abstracted models (dead-ends, unreachable states, constraint breaches)
- Verify codebase conformance to stated rules (grep/AST checks against real code)
- Route violations back to responsible design decisions via provenance
- Provide a disciplined vocabulary for design intent that both humans and agents can use

**What archwright CANNOT do:**
- Verify full game simulations (state explosion makes real games intractable without abstraction)
- Prove properties hold in the actual implementation (model checking proves properties of the MODEL, not the code — runtime monitoring or Lean-based code proofs bridge this gap)
- Replace playtesting for experience qualities (proxies approximate but don't prove "feels good")

**What already exists (archwright builds on, not invents):**
- Formal methods applied to games (Mawhorter 2021, Rezin 2017)
- Softlock detection via CTL: `AG(EF(goal))` is published
- State machine model checking (Alloy, SPIN, TLC — decades of prior art)
- AI-assisted proof generation (DeepSeek-Prover, AlphaProof)

**What archwright uniquely adds:**
- A unified library of game/app failure predicates (not just softlock)
- Provenance routing from violations back to design forces
- The force-resolution methodology connecting Alexander's theory to formal verification
- Multi-kind specs (behavior + constraint + dependency) with self-describing checks
- Confidence-gated AI autonomy for correction routing
