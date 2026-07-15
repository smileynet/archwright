---
marp: true
theme: default
paginate: true
header: "**ARCHWRIGHT**"
footer: "Make design intent checkable."
style: |
  section { font-family: system-ui, -apple-system, sans-serif; }
  h1 { color: #1a1a2e; }
  h2 { color: #16213e; }
  strong { color: #0f3460; }
  blockquote { border-left: 4px solid #0f3460; padding-left: 1em; font-style: italic; }
  table { font-size: 0.85em; }
  code { background: #f0f0f0; padding: 0.1em 0.3em; border-radius: 3px; }
---

<!-- _header: "" -->
<!-- _footer: "" -->
<!-- _paginate: false -->

# ARCHWRIGHT

## Make design intent checkable.

A design methodology, embodied as AI agent skills, that captures *why* you made a decision — then verifies your architecture actually honors it.

**Human desires → Forces in tension → Resolved patterns → Verified architecture**

---

# Part One: The Problem

A decision gets made, gets lost, and gets violated — silently.

---

## A decision gets made

In a planning session, the team agrees on a rule.

> **DECISION · DAY 1**
> "Only one entity can hold the ball."

Made in a planning session. Written down. Everyone nods.

---

## Three weeks later, it breaks

```gdscript
// FielderAI  (oops)
ball_holder = self
```

No verification step ever compares this line back to the decision made three weeks earlier.

**Day 1** — decision made → **Day 21** — bug ships silently

---

## What this actually costs you

| Symptom | What it looks like |
|---------|-------------------|
| **Silent bugs** | Violations ship straight to production, undetected |
| **Wasted debugging** | Hours rediscovering intent that already existed somewhere |
| **Eroded trust** | Design docs become theater — nobody re-reads them |

None of this shows up as an error. It shows up later, as a symptom with no obvious cause.

---

# Part Two: The Solution

Archwright makes intent checkable — name what you want, resolve the tension, verify it holds.

---

## From intent to verified architecture

```
Human desires → Forces (what you want vs what constrains you)
                  → Resolve (a configuration that satisfies both)
                      → Checkable specs (verifiable commitments)
```

Not documentation — **verification contracts.**

---

## What changes

| Without Archwright | With Archwright |
|---|---|
| Decisions live in docs nobody re-reads | Decisions become checkable specs |
| Violations ship silently | Violations caught before they ship |
| Debugging rediscovers intent | You review intent once — not endless diffs |

---

# Part Three: See It Work

The same `ball_holder` bug — resolved step by step in four moves.

---

## Step 1: Name the Forces

**Start with what the human wants:**

> **DESIRE** (product-level)
> "A player wants any fielder to be able to receive a pass at any time."

This desire creates a force that pushes the design toward freedom of motion.

---

## Step 1: Name the Constraints

Two forces push back against that freedom:

| | Force | Confidence |
|---|---|---|
| ★★ | **PHYSICS:** "Exactly one entity holds the ball" | True invariant |
| ★★ | **ARCHITECTURE:** "Only BallStateService writes possession" | True invariant |

Every architectural constraint traces back to the human desire it **serves**.

---

## Step 2: Resolve the Tension

Freedom to receive AND exactly one holder are not in conflict — if you separate the moment of transfer.

**RESOLUTION: Request / Validate model**

```
Controller → REQUEST → BallStateService → VALIDATES & commits
```

While the transfer is pending, the ball is "in flight" — no entity holds it.

---

## Step 2: Captured as a Pattern

The forces, tension, and resolution get written once — as a file with a `serves` link back to the product desire.

```yaml
# design/patterns/ball-possession.md
serves: [practice-any-position]  # ← traces to human need
forces:
  desire:     "Any fielder can receive a pass at any time"
  constraint: "Exactly one entity holds the ball"        (★★)
  constraint: "Only BallStateService writes possession"  (★★)
resolution:
  model: request_validate
```

---

## Step 3: Express as Specs

The lifecycle becomes a checkable state machine:

```
Held(sender) → IN_FLIGHT(no holder) → Held(receiver)
                                    → if invalid: rejected → Held(sender)

INVARIANT: at most one holder at any time (★★)
```

Plus constraint specs:
- `single-ball-holder`: Only BallStateService writes `ball_holder`
- `ball-write-ownership`: Grep for assignments, expect only in `ball_state_service.gd`

---

## Step 4: Check — and catch the bug

```bash
$ archwright-check single-ball-holder.yaml
  ✗ FAIL: ball_holder assigned outside BallStateService
      src/controllers/fielder_ai.gd:183
      content: "ball_holder = self"
```

**Violation detected.** The exact bug from Part One — caught before code review.

| | |
|---|---|
| **Broke:** | `fielder_ai.gd` writes `ball_holder` directly |
| **Invariant:** | `single-ball-holder` ★★ (must escalate to human) |
| **Traces to:** | pattern:ball-possession → constraint:single-writer |
| **Fix:** | Use `BallStateService.request_transfer()` instead |

---

# Part Four: Under the Hood

The mechanics that make it work.

---

## Human Desires Are Primary

> "Most of the forces which occur in an environment are the ones which people experience inside themselves."
> — Christopher Alexander

**Product desires** drive the system. Architectural constraints exist to serve them.

```
Product Desire → Tension → Pattern (serves: [...]) → Spec (from_patterns: [...])
```

Every spec can be traced back to **why it exists** — which human need it ultimately serves.

---

## The Confidence System

Not all decisions are equally sacred.

| Level | Meaning | Checked how | Agent behavior |
|---|---|---|---|
| ★★ | Must always hold | Model checker, proof, grep | Violations escalate to human |
| ★ | Believed correct | Tests, code review, heuristic | Agent proposes fixes |
| — | One approach | Advisory only | Agent may auto-adjust |

Confidence can be **promoted** (evidence accumulates) or **demoted** (counterexample found).

---

## What Lives Where

| | Patterns — WHY | Specs — WHAT |
|---|---|---|
| **Purpose** | Record the reasoning: forces, tensions, resolutions | Record commitments: what must be true, how to check |
| **Location** | `design/patterns/` | `design/specs/` |
| **Format** | Markdown + frontmatter | YAML (behavior, contract) or Markdown (constraint, dependency) |
| **Linked by** | `serves` → product desire, `resolves_into` → specs | `from_patterns` → pattern |

---

## The Agent's Role

| Step | What the agent does |
|---|---|
| **Names forces** | From product sources, issues, grills — product desires FIRST |
| **Finds resolutions** | Researches prior art, proposes options, derives architectural form from desires |
| **Formalizes** | Writes patterns + specs from ratified decisions |
| **Checks** | Verifies specs against code (static + trace) |
| **Routes corrections** | Back to the responsible decision via provenance links |

**You decide. The agent prepares, proposes, and verifies.**

---

## The Pipeline (Phase-Gated)

```
survey → forces → tensions → resolve → formalize → model → derive → check
```

Each phase produces an artifact. Human reviews before the next phase begins.

| Phase | Produces | Human checkpoint |
|---|---|---|
| survey | Intake outline | "Is this complete?" |
| forces | Product desires + architectural forces | "Are these the right desires?" |
| tensions | Named conflicts | "Are these truly in tension?" |
| resolve | Options or architectural questions | "Which resolution?" |
| formalize | Pattern documents | "Does this capture the decision?" |
| derive | Checkable specs | "Are targets correct?" |
| check | Pass/fail results | "Fix or revise?" |

---

## Deriving Architecture from Desires

When the desire is clear but architecture isn't:

```
1. Write concrete scenarios (the desire working)
2. Event-storm each scenario (events, commands, data)
3. Gap matrix (what exists vs what's needed)
4. Express gaps as questions (state? transitions? invariants?)
5. Human answers → resolution → pattern → specs
```

This is how **partially-resolved tensions** get completed.

---

## Corrections Rise Only As Far As They Need To

The ball-possession bug lived at the Architecture rung.

The same loop repeats at every scale:
- **Premise** — genre, whole experience
- **Loops & Systems** — component boundaries, data flow
- **Verbs & Interactions** — actions, state transitions
- **Feel & Finish** — rendering, accessibility, polish

Each rung only escalates as far up as the decision that owns it.

---

# Key Ideas

---

## Three ideas about knowledge and truth

**Forces stay first-class** — product desires are primary. The reusable knowledge is the method of naming and resolving tensions that trace back to human purpose.

**"Resolves into," not "compiles to"** — intent doesn't mechanically transform into architecture. It's creatively resolved, then formally verified.

**The agent is the system** — intelligence lives in skills. Tools handle only deterministic operations.

---

## Two ideas about trust and diagnosis

**Trust via verification** — once specs are proven consistent, you review intent — not output. Checking handles correctness automatically.

**Contrast pairs over raw errors** — when something breaks, show the violation next to the nearest valid alternative. The diff is the diagnosis.

---

<!-- _header: "" -->
<!-- _paginate: false -->

# ARCHWRIGHT

## Decisions become checkable. Architecture stays honest.

**You decide. The agent prepares, proposes, and verifies.**

---

*Human desires → Forces in tension → Resolved patterns → Verified architecture*
