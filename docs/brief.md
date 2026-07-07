# Archwright: A Brief

## What It Is

Archwright is a design methodology — embodied as AI agent skills — that helps you express what you want a system to be, then verifies the architecture actually delivers it.

You state your intent as **forces** (desires and constraints in tension). The system **resolves** those forces into checkable architecture specs. When the architecture violates its own stated intent, corrections **route back** to the responsible design decision.

## The Problem It Solves

Design intent gets lost between "what we decided" and "what we built."

```
Traditional:

  Design Decisions          Implementation
  ┌──────────────┐         ┌──────────────┐
  │ "Only one    │         │ ball_holder  │
  │  entity can  │  ????   │ = player_a   │
  │  hold the    │ ─ ─ ─ >│              │
  │  ball"       │         │ ball_holder  │
  └──────────────┘         │ = player_b   │ ← bug!
                           └──────────────┘
  decisions drift from reality
  violations go undetected
  corrections have no target
```

Archwright closes the loop:

```
Archwright:

  Forces              Patterns           Specs              Code
  ┌──────────┐       ┌──────────┐      ┌──────────┐      ┌──────────┐
  │ Desires  │       │ Resolved │      │ Verified │      │ Tested   │
  │ Constr-  │──────>│ Tensions │─────>│ Architec-│─────>│ Implemen-│
  │ aints    │       │ (intent) │      │ ture     │      │ tation   │
  └──────────┘       └──────────┘      └──────────┘      └──────────┘
       ↑                   ↑                 │                 │
       │                   │                 ↓                 ↓
       │                   │           ┌──────────┐      ┌──────────┐
       │                   └───────────│ Check:   │<─────│ Tests    │
       │                    re-resolve │ Violations│      │ (native) │
       └───────────────────────────────│ found    │      └──────────┘
                route to force         └──────────┘
```

Every architectural commitment traces back to the force that demanded it.
Every violation routes back to the decision that needs revision.

## How It Works: Ball Ownership in a Sports Game

A lacrosse practice app needs to track who has the ball. Sounds simple — until it isn't.

### 1. Express Intent (Forces)

Through conversation, the human expresses what they want and what constrains them:

```
┌─ DESIRE ─────────────────────────────────────────┐
│ "Any fielder can receive a pass at any time"     │
│ (gameplay fluidity — the ball moves freely)      │
└──────────────────────────────────────────────────┘
          ╲                              ╱
           ╲    T E N S I O N           ╱
            ╲                          ╱
             ╲ Free passing vs.       ╱
              ╲ single possession    ╱
               ╲                    ╱
┌─ CONSTRAINT ─────────────────────────────────────┐
│ "Exactly one entity holds the ball at any time"  │
│ (physics — a ball can't be in two places)        │
└──────────────────────────────────────────────────┘
```

A second constraint emerges from the architecture interview:

```
┌─ CONSTRAINT ─────────────────────────────────────┐
│ "Only BallStateService writes ball ownership"    │
│ (single source of truth — no conflicting writes) │
└──────────────────────────────────────────────────┘
```

### 2. Resolve (Pattern)

The tension is resolved — a configuration that satisfies all forces:

```
PATTERN: Ball Possession
├── Forces:
│   ├── Desire: any fielder can receive (fluidity)
│   ├── Constraint: exactly one holder (physics, ★★)
│   └── Constraint: single writer (architecture, ★★)
├── Tension: free passing vs. exclusive possession
├── Resolution: request/validate model — controllers REQUEST
│   transfers, BallStateService VALIDATES and commits.
│   Ball is "in flight" during transfer (no holder).
├── Confidence: ★★ (invariant of the domain)
└── Resolves into:
    ├── behavior:ball-state-lifecycle
    ├── constraint:single-ball-holder
    └── dependency:ball-write-ownership
```

### 3. Formalize (Specs)

The resolution takes form as three checkable specs:

```
┌─────────────────────────────────────────────────────────┐
│ kind: behavior                                          │
│ id: ball-state-lifecycle                                │
│                                                         │
│  ┌────────┐ REQUEST  ┌───────────┐ VALIDATE ┌────────┐ │
│  │ Held   │─────────>│ In-Flight │─────────>│  Held  │ │
│  │(one    │          │ (no       │  [valid] │ (new   │ │
│  │holder) │          │  holder)  │          │holder) │ │
│  └────────┘          └───────────┘          └────────┘ │
│      ↑                     │                            │
│      │                     │ VALIDATE [invalid]         │
│      │                     ↓                            │
│      │               ┌───────────┐                      │
│      └───────────────│ Returned  │                      │
│        (back to      │ (original │                      │
│         sender)      │  holder)  │                      │
│                      └───────────┘                      │
│                                                         │
│ INVARIANT (★★): exactly-one-holder                      │
│   "always (state != InFlight implies #holders == 1)"    │
│                                                         │
│ INVARIANT (★★): no-double-possession                    │
│   "always (#holders <= 1)"                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ kind: constraint                                        │
│ id: single-ball-holder                                  │
│                                                         │
│ rule: "At most one entity's ball_holder field is true"  │
│ check:                                                  │
│   method: grep                                          │
│   pattern: "ball_holder\s*="                            │
│   target: "src/"                                        │
│   expect: only in BallStateService                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ kind: dependency                                        │
│ id: ball-write-ownership                                │
│                                                         │
│ rule: "Only BallStateService writes ball_holder"        │
│ allowed:                                                │
│   - BallStateService → ball_holder (write)              │
│ forbidden:                                              │
│   - FielderController → ball_holder (write)             │
│   - PlayManager → ball_holder (write)                   │
│   - ANY other component → ball_holder (write)           │
└─────────────────────────────────────────────────────────┘
```

### 4. Verify (Check)

The behavior spec is checked via Alloy. The constraint and dependency specs are checked against the codebase:

```
$ archwright-check design/specs/ball-state-lifecycle.yaml
  ✓ exactly-one-holder: PASS (94ms, Alloy bounded scope 5)
  ✓ no-double-possession: PASS

$ archwright-check design/specs/single-ball-holder.yaml
  ✗ FAIL: ball_holder assigned in 2 files
    src/services/ball_state_service.gd:47    ← expected
    src/controllers/fielder_ai.gd:183        ← VIOLATION

  VIOLATION:
    invariant: single-ball-holder (★★)
    from_pattern: ball-possession
    from_force: constraint:single-writer
    location: src/controllers/fielder_ai.gd:183
    content: "ball_holder = self"
```

### 5. Correct (Pass-Up)

The violation routes back via provenance:

```
  Violation: "fielder_ai.gd writes ball_holder directly"
       │
       │ provenance: from_force = constraint:single-writer
       │             from_pattern = ball-possession
       ↓
  Pattern: ball-possession
       │
       │ Resolution says: "controllers REQUEST, service VALIDATES"
       │ But fielder_ai is writing directly — bypassing the service
       ↓
  FIX: fielder_ai must call BallStateService.request_transfer()
       instead of assigning ball_holder directly.

  Confidence: ★★ → MUST escalate to human before resolving
```

The human reviews, confirms the fix direction, and the agent corrects the code.

## The Confidence System

```
  ★★  TRUE INVARIANT (proof or strong evidence)
  │   • A ball can't be in two places — this is physics
  │   • Agent MUST escalate violations to human
  │   • Checked rigorously (formal model + code analysis)
  │
  ★   BELIEVED CORRECT (some evidence)
  │   • "In-flight state should last < 500ms" — probably right
  │   • Agent proposes fixes, human confirms
  │   • Standard bounded checking
  │
  —   ONE APPROACH (untested)
      • "Return to sender on invalid pass" — one option among several
      • Agent may auto-adjust or log
      • Quick checks only
```

## What Archwright Produces

In your project:

```
your-project/
  design/
    patterns/
      ball-possession.yaml         # WHY: forces + resolution
      practice-execution.yaml
      step-sequencing.yaml
    specs/
      ball-state-lifecycle.yaml    # WHAT (kind: behavior)
      single-ball-holder.yaml      # WHAT (kind: constraint)
      ball-write-ownership.yaml    # WHAT (kind: dependency)
      resolved-play-view.yaml      # WHAT (kind: contract)
      execution-boundary.yaml      # WHAT (kind: boundary)
```

**Patterns** = why (design intent, forces, resolutions)
**Specs** = what (checkable architecture commitments)
**Tests** = how (implemented in your language, verifying specs hold)

## The Full Loop

```
            HUMAN                          AGENT
         ┌─────────┐                  ┌─────────────┐
         │ Express │                  │  Research   │
         │ forces  │─────────────────>│  Propose    │
         │         │<─────────────────│  Resolutions│
         │ Decide  │                  │             │
         └────┬────┘                  └──────┬──────┘
              │                              │
              │  ratified pattern             │ formalize
              ↓                              ↓
         ┌─────────────────────────────────────────┐
         │            Pattern YAML                  │
         │     (forces + resolution + confidence)   │
         └───────────────────┬─────────────────────┘
                             │ resolves into
                             ↓
         ┌─────────────────────────────────────────┐
         │             Spec YAML                    │
         │   (behavior + contract + constraints)    │
         └───────────────────┬─────────────────────┘
                             │ check
                             ↓
         ┌─────────────────────────────────────────┐
         │           Verification                   │
         │  Alloy (formal) │ Scripts (conformance)  │
         └───────────┬─────────────────────────────┘
                     │
              ┌──────┴───────┐
              ↓              ↓
         ┌────────┐    ┌──────────┐
         │  PASS  │    │   FAIL   │
         │  done  │    │ contrast │
         └────────┘    │  pair    │
                       └────┬─────┘
                            │ route via provenance
                            ↓
                    ┌───────────────┐
                    │ Re-resolve    │
                    │ (adjust       │
                    │  pattern or   │
                    │  fix code)    │
                    └───────────────┘
```

## Lineage

```
  spec-driven-development (2024)
  │  Structured planning: PLAN.md + spec files + validation criteria
  │  Problem: specs capture WHAT but not WHY; no verification loop
  │
  ├──> project-overseer (2025)
  │    Drift detection: terraform model (plan → apply → detect divergence)
  │    Problem: detects drift but can't route corrections back to intent
  │
  └──> archwright (2026)
       Force-resolution + formal verification
       Captures WHY (forces), verifies WHAT (specs), routes corrections
       The AI agent holds the methodology; tools are mechanical servants
```

## Key Principles

1. **Forces stay first-class.** The reusable knowledge is the method of naming and resolving tensions, not a catalogue of solutions.

2. **"Resolves into" not "compiles to."** The process is creative (finding resolutions) + verified (checking they hold). Not a mechanical transformation.

3. **The agent IS the system.** Intelligence lives in the skills (methodology), not in a binary. Tools handle only deterministic operations.

4. **Trust via verification.** Once invariants are proven to hold, you review the spec (intent), not the output (architecture). Like trusting a compiler's output without reading assembly.

5. **Contrast pairs over raw errors.** Show the violation alongside the nearest valid alternative. The diff IS the diagnosis.
