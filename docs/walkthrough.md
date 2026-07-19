# Walkthrough: From Decision to Verified Architecture

This document traces one design decision through every artifact archwright produces, showing how they link together to form a verifiable chain.

We'll follow **decision #15** from fieldball-coach-platform: "BallStateService as run-scoped source of truth."

---

## The Chain

```
  Conversation → Pattern → Specs → Code → Check → Result
       ↑                                            │
       └────────────── correction ──────────────────┘
```

Each artifact carries a provenance link to the one before it. Violations travel backward along these links to reach the decision that needs revision.

---

## 1. The Conversation

In a design session, the human and agent identify forces:

> **Human:** "Any fielder should be able to catch a pass at any time."
> **Agent:** "What constrains that? Can two players hold the ball simultaneously?"
> **Human:** "No — only one. And architecturally, I want one source of truth for who has it."

Three forces surface:
- Desire: fluidity (free passing)
- Constraint: single holder (physics)
- Constraint: single writer (architecture)

The tension: fluidity pulls toward "anyone can grab" but physics + sanity require "exactly one, managed centrally."

---

## 2. The Pattern

File: `design/patterns/ball-possession.md`

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
  - "constraint:single-ball-writer"
  - "dependency:ball-write-ownership"
---
```

The frontmatter is machine-readable. Tools validate it. The `resolves_into` field points **down** to the specs this pattern produces — these are the provenance links.

The body carries the human-readable reasoning:

```markdown
## Tension

Free passing requires any fielder to receive at any time, but physics
demands exactly one holder...

## Resolution

Request/validate model. Controllers REQUEST transfers,
BallStateService VALIDATES and commits...
```

**What connects to what:**
- `resolves_into: ["behavior:ball-state-lifecycle", ...]` → points to 3 specs below

---

## 3. The Behavior Spec

File: `design/specs/ball-state-lifecycle.yaml`

This is the state machine — the formal model of how ball possession works:

```yaml
kind: behavior
id: ball-state-lifecycle
from_patterns:
  - "pattern:ball-possession"        ← links BACK to the pattern
confidence: "★★"

states:
  held:
    on:
      REQUEST_TRANSFER:
        target: in-flight
        guard:
          predicate: "requester != holder"
          from_force: single-holder    ← guard traces to a specific force
        from_pattern: ball-possession  ← transition traces to the pattern

invariants:
  - id: at-most-one-holder
    predicate: "always (holder == none or holder in {fielder_a, fielder_b, fielder_c})"
    confidence: "★★"
    from_force: single-holder          ← invariant traces to the force that demands it
    from_pattern: ball-possession      ← and the pattern that established it
```

**What connects to what:**
- `from_patterns: ["pattern:ball-possession"]` → links UP to the source pattern
- Each state, transition, guard, and invariant carries `from_force` and `from_pattern`
- This per-element provenance is what enables targeted correction (pass-up)

---

## 4. The Constraint Spec

File: `design/specs/single-ball-writer.md`

A rule about the codebase — not a state machine, but a checkable property:

```markdown
---
kind: constraint
id: single-ball-writer
from_patterns:
  - "pattern:ball-possession"         ← links back to the pattern
confidence: "★★"
check:
  method: grep
  target: "client/src/"
  pattern: "ball_holder\\s*="
  expect: only-in
  only_in: "client/src/services/ball_state_service.gd"
links:
  - target: "behavior:ball-state-lifecycle"   ← links to sibling spec
    type: constrains
---
```

The `check` field tells the tool **how to verify** this constraint. It's self-describing — the spec carries its own test.

**What connects to what:**
- `from_patterns` → links UP to the source pattern
- `links[].target` → links SIDEWAYS to related specs
- `check` → describes how to verify against the codebase

---

## 5. The Dependency Spec

File: `design/specs/ball-write-ownership.md`

A rule about allowed/forbidden relationships between components:

```markdown
---
kind: dependency
id: ball-write-ownership
from_patterns:
  - "pattern:ball-possession"
allowed:
  - source: "BallStateService"
    target: "ball_holder"
    type: writes
forbidden:
  - source: "FielderAIController"
    target: "ball_holder"
    type: writes
check:
  method: grep
  command: "grep -rn 'ball_holder\\s*=' client/src/ | grep -v ball_state_service"
  expect: absent
links:
  - target: "behavior:ball-state-lifecycle"
    type: enforces
  - target: "constraint:single-ball-writer"
    type: enforces
---
```

**What connects to what:**
- `from_patterns` → UP to source pattern
- `links` → SIDEWAYS to the behavior and constraint it enforces
- `allowed`/`forbidden` → declares the rule
- `check` → describes verification

---

## 6. The Code

File: `client/src/services/ball_state_service.gd`

```gdscript
class_name BallStateService
extends RefCounted

var ball_holder: Fielder = null      ← the single source of truth

func request_transfer(requester: Fielder) -> void:
    # Validate and commit...
    ball_holder = _requester          ← the ONLY place this is written
```

File: `client/src/fielder/fielder_ai_controller.gd`

```gdscript
func _on_catch_opportunity() -> void:
    _ball_state_service.request_transfer(_fielder)  ← goes through the service
    # NOT: ball_holder = self  ← this would violate single-ball-writer
```

**What connects to what:**
- The code doesn't reference archwright artifacts directly
- The specs describe properties the code must satisfy
- Tests (written in the project's testing framework) verify conformance

---

## 7. The Check

Running `archwright-check` (or the fixture test runner):

```
$ archwright-check design/specs/single-ball-writer.md

  Method: grep
  Target: client/src/
  Pattern: ball_holder\s*=
  Expect: only in ball_state_service.gd

  Found:
    client/src/services/ball_state_service.gd:9   ball_holder = null
    client/src/services/ball_state_service.gd:29  ball_holder = _requester

  All matches are in the allowed file.

  ✓ PASS: single-ball-writer
```

---

## 8. The Violation (When Something Breaks)

Suppose a developer adds a shortcut:

```gdscript
# client/src/fielder/fielder_ai_controller.gd
func _on_catch_opportunity() -> void:
    ball_holder = self  # "just this once, for testing"
```

Now the check fails:

```
$ archwright-check design/specs/single-ball-writer.md

  ✗ FAIL: single-ball-writer

  VIOLATION:
    file: client/src/fielder/fielder_ai_controller.gd:15
    content: "ball_holder = self"
    invariant: single-ball-writer (★★)
    from_pattern: pattern:ball-possession
    from_force: constraint:single-writer

  PROVENANCE CHAIN:
    This violation traces to:
    ├── spec: constraint:single-ball-writer
    │   └── from_pattern: pattern:ball-possession
    │       └── force: "Only BallStateService writes possession"
    │           └── rationale: Multiple writers → split-brain → double-possession bugs
    │
    └── FIX DIRECTION: Use ball_state_service.request_transfer() instead
```

The violation carries the full chain: **code location → violated spec → source pattern → responsible force → rationale for the rule.**

The developer (or agent) now knows:
- WHAT broke (line 15 writes ball_holder)
- WHY it's wrong (single-writer constraint, ★★)
- WHERE the decision lives (pattern:ball-possession)
- HOW to fix it (use request_transfer)

---

## The Link Map

Every artifact points to its neighbors:

```
  ┌──────────────────────────────────────────────────┐
  │ pattern:ball-possession                          │
  │   resolves_into:                                 │
  │     ├── behavior:ball-state-lifecycle            │
  │     ├── constraint:single-ball-writer            │
  │     └── dependency:ball-write-ownership          │
  └───────────────────┬──────────────────────────────┘
                      │ from_patterns (upward)
          ┌───────────┼───────────────┐
          ↓           ↓               ↓
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │ behavior:    │ │ constraint:  │ │ dependency:  │
  │ ball-state-  │ │ single-ball- │ │ ball-write-  │
  │ lifecycle    │ │ writer       │ │ ownership    │
  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
         │                │                 │
         │ links          │ links           │ links
         │ (sideways)     │ (sideways)      │ (sideways)
         └────────────────┴─────────────────┘
                          │
                          │ check (downward to code)
                          ↓
  ┌──────────────────────────────────────────────────┐
  │ Code: ball_state_service.gd                      │
  │       fielder_ai_controller.gd                   │
  │       play_manager_3d.gd                         │
  └──────────────────────────────────────────────────┘
```

- **Downward** (resolves_into): pattern → what it produced
- **Upward** (from_patterns): spec → where it came from
- **Sideways** (links): specs reference each other
- **Checking** (check field): spec → how to verify against code
- **Correction** (pass-up): violation → walks upward via from_pattern → reaches the decision

---

## Summary

| Artifact | Format | Purpose | Links to |
|----------|--------|---------|----------|
| Conversation | (not stored) | Surface forces, find resolution | → Pattern |
| Pattern | Markdown+frontmatter | Record WHY — forces, tension, resolution | → Specs (via resolves_into) |
| Behavior spec | YAML | Record WHAT — state machine, invariants | ← Pattern (via from_patterns) |
| Constraint spec | Markdown+frontmatter | Record RULE — what must hold in code | ← Pattern, → Code (via check) |
| Dependency spec | Markdown+frontmatter | Record BOUNDARY — allowed/forbidden | ← Pattern, → Code (via check) |
| Code | GDScript (or any language) | Implement the architecture | ← Checked by specs |
| Check result | Tool output | PASS or FAIL with provenance | → Pattern (for correction routing) |
