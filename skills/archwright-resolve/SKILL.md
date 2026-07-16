---
name: archwright-resolve
description: "Resolve a design tension. Researches prior art, presents 2-3 options with tradeoffs, human decides. The core of the archwright methodology — where forces meet and a resolution is found. Use when a tension needs a decision, when someone says 'how should we handle this?', 'what are the options?', 'resolve this conflict'. Trigger: resolve, design decision, what should we do, how to balance, options, tradeoffs."
metadata:
  type: process
  invocation: both
  practice: null
---

# Archwright Resolve

Resolve a design tension. Research prior art, present options, get a human decision, hand off to formalization.

**Core principle:** Forces stay first-class. Every resolution traces back to the forces it balances. No pattern without a tension. The human decides — the agent researches, frames, and presents.

## Process

### 1. Understand the tension

Read the forces. State the conflict clearly: "X wants Y, but Z demands W."

If the tension comes from the pipeline (`archwright-tensions`), it arrives pre-articulated. If it comes directly from a human, articulate it first — name the forces, then the conflict.

**Determine resolution state:**
- **Fully resolved** (grill/ADR decided) → confirm with human, proceed to formalize
- **Partially resolved** (desire clear, architectural form unclear) → use the Scenario → Gap → Questions process below
- **Open** (desire unclear or forces not yet named) → route back to grilling

**When all tensions arrive pre-resolved (mature projects):** This phase becomes a CONFIRMATION PASS — present each resolution to the human, get explicit acknowledgment that it still holds. Do NOT skip this phase. Its value for mature projects is ensuring that decisions made months ago still reflect current intent. Present the resolutions grouped by confidence level, and ask: "Do these still hold, or has anything shifted?"

### 2. For partially-resolved tensions: Derive architectural form from desire

When the product desire is clear but the architecture hasn't taken shape yet:

**a) Write 3-5 concrete scenarios** demonstrating the desire working:
```
Scenario: [Name]
Given [existing system state]
When [user action or event]
Then [observable outcome that satisfies the desire]
```

**b) Event-storm each scenario** — extract:
- Domain Events (what happened — past tense)
- Commands (what intent triggered it)
- Policies (what rule connects event → next command)
- Read Models (what information is needed to act)

**c) Gap matrix** — map extracted elements against existing architecture:
| Element from scenario | Existing architecture | Gap type |
|-|-|-|
| DecisionPointReached event | ExecutionStateMachine | Extend (new event from existing state) |
| PlayerChoice data | (nothing) | NEW entity needed |
| OutcomeEvaluation logic | (nothing) | NEW service needed |

**d) Express gaps as architectural questions:**
- State: "What entity tracks X? Created when? Destroyed when?"
- Transitions: "What event triggers Y? Who is authorized? What guards?"
- Invariants: "What must always/never be true about Z?"
- Interfaces: "How does the system communicate X to the user?"
- Data: "What fields extend the existing contract?"

**e) Present the questions (not pre-formed options) to the human.** The answers become the resolution.

### 3. For open (unresolved) tensions: Research and present options

(Standard path when architecture isn't yet decided but the tension is clear. Fully-resolved tensions take the confirmation pass in step 1 — never this path.)

- Domain conventions (how does the sport/industry handle this?)
- Software patterns (what do similar systems do?)
- Formal methods (can this be modeled? What does the model say?)
- Prior decisions in this project (have we solved something similar?)

Cite sources with confidence levels. See source-authority hierarchy.

Propose 2-3 resolution approaches. For each:
- **Name** the approach (bold, descriptive)
- **How** it balances the forces
- **What it costs** (consequences, new constraints)
- **Confidence level** (★★/★/—)
- **Prior art** supporting it

Do NOT present more than 3. If you can't narrow to 3, you don't understand the tension well enough.

### 4. Human decides

Present options or questions clearly. Wait for the human's choice/answers. Do not proceed without a decision. If the human asks for more research or a different framing, iterate — don't force a choice.

### 5. Verify against existing invariants

Before committing a new resolution:
- List existing invariants that could be affected
- For each new state/transition/interface, confirm it doesn't violate them
- Prefer composition (orthogonal regions, new entities) over modification (changing existing transitions)
- If a new invariant conflicts with an existing one, surface it as a NEW tension — don't silently override

### 5b. Resolution type: Scope Deferral

When a tension is real but not yet active (the system doesn't exist, or it's explicitly post-MVP/MLP scope):

1. **Record the tension and its forces** — they're architecturally real even if not yet implemented
2. **Record the CONSTRAINT as a quality gate** — "when this IS built, it must satisfy X"
3. **Name the activation trigger** — "becomes active when spike S2 executes" or "when multi-character play is built"
4. **Do NOT research options or make decisions** — the decision is "not yet" and that's sufficient

Deferred tensions still proceed to formalization (the constraint is load-bearing). Their patterns get `resolves_into` declarations. Their specs get written (to guide future implementation). But the resolve phase itself is fast: acknowledge the deferral, record the quality gate, move on.

**When to defer vs decide:**
- Defer if: the system literally doesn't exist yet AND no near-term work depends on the decision
- Decide if: the decision affects how CURRENT work is structured (even if the full system is future)

### 6. Hand off

Once decided:
- If the resolution should be a pattern → dispatch `archwright-formalize`
- If specs should be derived → dispatch `archwright-derive`
- If the resolution is small/local → record inline (ADR or grill decision, update CONTEXT.md)

## Growth Rules

When artifacts change, related artifacts MUST co-update. See [references/growth-rules.md](references/growth-rules.md).

## Context Assembly

What to read is a deterministic function. See [references/context-assembly.md](references/context-assembly.md).

## Confidence

| Level | Meaning | Agent behavior |
|-------|---------|----------------|
| ★★ | True invariant | Must escalate violations to human |
| ★ | Believed correct | Propose fixes, human confirms |
| — | One approach | May auto-adjust or log |

## Proxy Invariants

When a force is experiential, decompose into checkable proxies:
- "Feels oriented" → `novel_elements ≤ threshold`
- "Meaningful choices" → no dominant strategy
- "Not frustrated" → recovery path within N steps

## The Correction Loop (Pass-Up)

When a violation is found (by `archwright-check`):
1. Read provenance: which invariant → which force → which pattern
2. Assess: is the code wrong, or is the spec wrong?
3. If code wrong → fix code (implementation task)
4. If spec wrong → the resolution may need revision (dispatch back to this skill)
5. If pattern wrong → the tension wasn't understood (rare, requires re-grilling)

## The Skill Pipeline

```
archwright-survey → archwright-forces → archwright-tensions → archwright-resolve (this) → archwright-formalize → archwright-model → archwright-contract → archwright-derive → archwright-check
```

## Does NOT

- Project planning (use `spec-driven-development` for phases/tasks)
- Implementation (specs tell you WHAT, coding does HOW)
- Running checks (use `archwright-check`)
- Extracting forces (use `archwright-forces`)
- Writing patterns (use `archwright-formalize`)
- Deriving specs (use `archwright-derive`)
