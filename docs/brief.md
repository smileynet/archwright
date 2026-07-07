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
  │ "Players     │         │ onboarding   │
  │  should feel │  ????   │ _tutorial()  │
  │  oriented"   │ ─ ─ ─ >│ _show_all()  │
  │              │         │ _skip()      │
  └──────────────┘         └──────────────┘
        ↕ no connection ↕
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

## How It Works

### 1. Express Intent (Forces)

Through conversation, the human expresses what they want (desires) and what bounds them (constraints). The agent helps name the tensions:

```
┌─ DESIRE ─────────────────────────────────────────┐
│ "Players feel oriented before exposed to depth"  │
└──────────────────────────────────────────────────┘
          ╲                              ╱
           ╲    T E N S I O N           ╱
            ╲                          ╱
             ╲  Depth wants to be     ╱
              ╲ shown; comprehension ╱
               ╲ wants it hidden    ╱
                ╲                  ╱
┌─ CONSTRAINT ─────────────────────────────────────┐
│ "Humans hold ~4 novel concepts simultaneously"   │
└──────────────────────────────────────────────────┘
```

### 2. Resolve (Patterns)

The tension is resolved — a configuration found that balances the forces:

```
PATTERN: Intimacy Gradient
├── Forces:
│   ├── Desire: orientation before depth
│   └── Constraint: attention budget (hard)
├── Tension: depth vs comprehension
├── Resolution: stage exposure shallow → deep
├── Confidence: ★ (some evidence)
└── Resolves into:
    ├── behavior:onboarding-progression
    ├── constraint:max-4-novel-elements-per-tier
    └── contract:tier-unlock-criteria
```

### 3. Formalize (Specs)

The resolution takes form as checkable architecture:

```
┌─────────────────────────────────────────────────┐
│ kind: behavior                                  │
│ id: onboarding-progression                      │
│                                                 │
│   ┌────────┐  ADVANCE   ┌──────────────┐       │
│   │Shallow │───────────>│ Intermediate │       │
│   │tier=1  │  [score≥70]│ tier=2       │       │
│   └────────┘            └──────────────┘       │
│       │                        │                │
│       │ EXPLORE                │ ADVANCE        │
│       └──> (self)              │ [score≥70]     │
│                                ↓                │
│                         ┌──────────────┐        │
│                         │    Deep      │        │
│                         │    tier=3    │        │
│                         └──────────────┘        │
│                                                 │
│ INVARIANT (★★): no tier skip                    │
│   "Deep requires previously(Intermediate)"     │
│                                                 │
│ INVARIANT (★): visibility monotonic             │
│   "features_visible never decreases"            │
└─────────────────────────────────────────────────┘
```

### 4. Verify (Check)

The spec is checked against its own invariants. If a violation exists, it surfaces as a **contrast pair** — the violation alongside the nearest valid alternative:

```
VIOLATION FOUND:
  ┌─ Counterexample ────────────────────────┐
  │ Shallow ──[EXTERNAL_UNLOCK]──> Deep     │
  │ (1 step, skips Intermediate)            │
  └─────────────────────────────────────────┘

  ┌─ Nearest Valid (contrast) ──────────────┐
  │ Shallow → Shallow → Intermediate → Deep │
  │ (proper path via advancement)           │
  └─────────────────────────────────────────┘

  DIFF: externalUnlock bypasses comprehension gate
  RESPONSIBLE: constraint:attention-budget (★★)
  FROM PATTERN: intimacy-gradient
  SUGGESTED: add guard requiring intermediate completion
```

### 5. Correct (Pass-Up)

The violation routes back to the responsible force via provenance links:

```
  Violation: "tier skip via EXTERNAL_UNLOCK"
       │
       │  provenance: from_force = attention-budget
       │              from_pattern = intimacy-gradient
       ↓
  Pattern: intimacy-gradient
       │
       │  Resolution doesn't account for external bypass
       ↓
  RE-RESOLVE: add guard OR remove event OR reroute through intermediate
```

## The Confidence System

Confidence gates how the system behaves:

```
  ★★  TRUE INVARIANT (proof or strong evidence)
  │   • Agent must escalate violations to human
  │   • Deeper checking (unbounded proof)
  │   • Solid boundary in visualizations
  │
  ★   BELIEVED CORRECT (some evidence)
  │   • Agent proposes fixes, human confirms
  │   • Standard bounded checking
  │   • Normal boundary
  │
  —   ONE APPROACH (untested)
      • Agent may auto-fix or log
      • Quick checks only
      • Dashed boundary
```

## What Archwright Produces

In your project:

```
your-project/
  design/
    patterns/
      intimacy-gradient.yaml       # WHY (forces + resolution)
      resource-tension.yaml
    specs/
      onboarding-progression.yaml  # WHAT (kind: behavior)
      tier-unlock-criteria.yaml    # WHAT (kind: contract)
      max-novel-elements.yaml      # WHAT (kind: constraint)
      no-skip-tier.yaml            # WHAT (kind: constraint)
```

Patterns = **why** (design intent, forces, resolutions)
Specs = **what** (checkable architecture: behaviors, contracts, constraints, dependencies)
Tests = **how** (implemented in your language, verifying specs hold in code)

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
                    │  force)       │
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
