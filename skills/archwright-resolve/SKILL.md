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

### 2. Research prior art

- Domain conventions (how does the sport/industry handle this?)
- Software patterns (what do similar systems do?)
- Formal methods (can this be modeled? What does the model say?)
- Prior decisions in this project (have we solved something similar?)

Cite sources with confidence levels. See source-authority hierarchy.

### 3. Present options

Propose 2-3 resolution approaches. For each:
- **Name** the approach (bold, descriptive)
- **How** it balances the forces
- **What it costs** (consequences, new constraints)
- **Confidence level** (★★/★/—)
- **Prior art** supporting it

Do NOT present more than 3. If you can't narrow to 3, you don't understand the tension well enough.

### 4. Human decides

Present options clearly. Wait for the human's choice. Do not proceed without a decision. If the human asks for more research or a different framing, iterate — don't force a choice.

### 5. Hand off

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
archwright-survey → archwright-forces → archwright-tensions → archwright-resolve (this) → archwright-formalize → archwright-derive → archwright-check
```

## Does NOT Cover

- Project planning (use `spec-driven-development` for phases/tasks)
- Implementation (specs tell you WHAT, coding does HOW)
- Running checks (use `archwright-check`)
- Extracting forces (use `archwright-forces`)
- Writing patterns (use `archwright-formalize`)
- Deriving specs (use `archwright-derive`)
