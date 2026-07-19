---
kind: pattern
id: execution-purity
name: "Execution Purity"
scale: loops-systems
confidence: "★"
status: active
serves: [predictable-practice-runs]
context: []
completed_by: []
resolves_into:
  - "constraint:executor-no-resolve"
  - "dependency:executor-boundaries"
---

# Execution Purity

## Problem

**Practice execution must be replayable and testable, but resolution logic and UI concerns keep leaking into the executor.**

## Context

The practice loop: plays are RESOLVED (decisions computed) before execution begins; the executor only steps through pre-resolved data.

## Forces

- **Desire:** Deterministic, replayable practice runs (same resolved play → same execution).
- **Constraint (soft):** Executor code paths must not re-enter resolution — resolution during execution makes runs non-reproducible.
- **Constraint (soft):** Executor must not depend on UI or builder layers — headless test runs.

## Evidence

- A prototype where PlayManager3D called PlayResolver mid-step produced different outcomes per run (resolution consumed live state).
- Rejected alternative: "resolve lazily during execution" — couples step timing to resolution cost and breaks replay.
- Prior art: command-pattern executors (resolved command list → pure interpreter).

## Therefore

**The executor executes; it never resolves.** `execution/` consumes `ResolvedPlayView` (pre-computed) and never references `PlayResolver`, UI, or builder types.

## Consequences

- Resolution changes require re-resolving before re-running (no hot re-resolve mid-step).
- `play_data/` owns all resolution; `execution/` is mechanically checkable for purity.

## Verification

- `constraint:executor-no-resolve` — grep: no `PlayResolver` reference in `execution/` (★, mechanical)
- `dependency:executor-boundaries` — grep: no UI/builder/resolver imports in `play_manager_3d.gd` (★, mechanical)

## Completion

- Completed by a resolved-play-view contract pattern (not included in this fixture).
