# Archwright: A Brief

## Design decisions that compound in your favor.

Archwright is a strategic advisor for product design. It surfaces competing forces in what you're building, helps you resolve them at the right altitude, and verifies those resolutions hold over time.

Decide at the top. The architecture stays honest.

---

## The Problem Isn't Bugs — It's Unexamined Decisions

Most teams don't fail because they violated a good decision. They fail because they never examined the decision in the first place.

Forces pull in opposite directions — but nobody names them. Tensions resolve implicitly (whoever commits first wins). Architecture accumulates without strategy. And when something finally breaks, the symptom is three layers removed from the cause.

```
  What looks like:          What it actually is:
  ┌──────────────┐          ┌────────────────────────┐
  │ A bug in     │          │ A tension that was     │
  │ fielder_ai   │  ← ← ←  │ never surfaced, let    │
  │              │          │ alone resolved         │
  └──────────────┘          └────────────────────────┘
```

The cost isn't one bug. It's every decision downstream that compounded on the wrong assumption.

---

## What Archwright Does

### It's two things:

**1. An advisor** — helps you see the shape of what you're building: what forces are at play, where they conflict, and what your options are for resolving them.

**2. A guardian** — once you've decided, it formalizes the decision as checkable structure and tells you when the architecture drifts from your intent.

### The pipeline:

```
┌─────────── ADVISOR ───────────┐  ┌─────────── GUARDIAN ──────────┐
│                                │  │                                │
│  survey → forces → tensions   │  │  model → contract → derive    │
│       → resolve → formalize   │  │       → check                 │
│                                │  │                                │
│  "What does this want to be?" │  │  "Is it still what you said?" │
└────────────────────────────────┘  └────────────────────────────────┘
```

---

## See It Work

### A designer expresses a desire:

> "I want any fielder to be able to receive a pass at any time."

This is a force — a pull toward freedom of motion.

### The advisor surfaces what pushes back:

| Force | Type |
|-------|------|
| "Any fielder can receive a pass" | Desire |
| "Exactly one entity holds the ball" | Constraint — physics (★★) |
| "Only BallStateService writes possession" | Constraint — architecture (★★) |

"These are in tension. Freedom to receive vs. exclusivity of possession. Here are three ways to resolve it..."

### The human decides:

> **Resolution: Request/Validate model.**
> Controllers REQUEST. BallStateService VALIDATES and commits.
> During transfer: ball is "in flight" — no holder.

This is the strategic moment. Everything below flows from this.

### The decision gets captured:

A pattern file records the forces, the tension, and the resolution — with provenance tracing back to the human desire it serves.

### Architecture falls out:

The resolution *implies* checkable specs:
- **Behavior:** Held → In-Flight → Held (state machine)
- **Constraint:** Only BallStateService writes `ball_holder`
- **Invariant:** At most one holder at any time (★★)

### Three weeks later, the guardian catches drift:

```
$ archwright-check single-ball-holder.yaml
  ✗ FAIL: ball_holder assigned outside BallStateService
      src/controllers/fielder_ai.gd:183
      content: "ball_holder = self"

  TRACES TO: pattern:ball-possession → force:single-possession (★★)
  FIX: Use BallStateService.request_transfer() instead
```

The violation routes back to the decision that owns it. The ★★ means: escalate to human.

---

## Why "At the Top" Matters

A tension resolved at the strategic level makes thousands of implementation decisions locally obvious. A tension left unresolved at the top becomes a contradiction in every PR, every sprint, every refactor.

```
  Resolved at the top:              Unresolved at the top:

  ┌─── ONE resolution ───┐         ┌── same argument ──────┐
  │  "Request/Validate"   │         │  PR #47: "who writes?" │
  └───────┬───────────────┘         │  PR #63: "who writes?" │
          │ implies                  │  PR #91: "who writes?" │
  ┌───────┴───────────────┐         │  Sprint 8: "who owns?" │
  │  spec, check, routing │         │  Retro: "why is this   │
  │  all fall out for free│         │          still broken?" │
  └───────────────────────┘         └────────────────────────┘
```

This is what "compound in your favor" means. One good resolution, properly captured and verified, saves you from re-litigating it forever.

---

## The Confidence System

Not all decisions are equally sacred:

| Level | Meaning | When violated |
|-------|---------|--------------|
| ★★ | Must always hold — true invariant | Escalate to human. Never auto-fix. |
| ★ | Believed correct — evidence supports it | Advisor proposes fix, waits for approval |
| — | One approach — might change | Advisor may adjust autonomously |

Confidence can be promoted (evidence accumulates) or demoted (counterexample found). The advisor earns trust incrementally.

---

## The Advisor's Role

| It does | It doesn't |
|---------|-----------|
| Surfaces forces you haven't named | Decide what your product should be |
| Names tensions between your desires | Override your resolution |
| Proposes resolutions with trade-offs | Auto-fix ★★ violations |
| Captures decisions with provenance | Forget why something exists |
| Verifies alignment over time | Replace judgment with automation |

**You decide. The advisor surfaces, proposes, and verifies.**

---

## What Lives Where

```
your-project/
  design/
    forces/     # What you want and what constrains you
    patterns/   # How tensions were resolved (WHY)
    models/     # Actors, state machines, event flows
    specs/      # Checkable commitments (WHAT must hold)
```

---

## Limitations

**What archwright can do:**
- Surface forces and tensions from conversation and code
- Verify conformance to stated rules (grep, semgrep, Alloy)
- Route violations back to the responsible decision
- Provide bounded model checking for behavior specs

**What archwright cannot do:**
- Replace human judgment on resolution
- Prove implementation correctness beyond the model's abstraction
- Validate experience qualities ("feels good") — only structural proxies

**What archwright uniquely adds:**
- Bidirectional traceability: architecture talks back to strategy
- Resolution altitude: strategic decisions produce architectural coherence
- Force-first methodology: desires are primary, constraints serve them
