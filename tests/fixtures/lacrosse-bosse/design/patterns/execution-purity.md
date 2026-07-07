---
kind: pattern
id: execution-purity
name: "Execution Purity"
scale: loops-systems
confidence: "★★"
above:
  - practice-execution
resolves_into:
  - "constraint:executor-no-resolve"
  - "dependency:executor-boundaries"
---

# Execution Purity

## Forces

- **Desire:** The execution pipeline should be simple to reason about — when debugging "why did the fielder go there?", you look in one place, not three.
- **Desire:** Each component should be testable in isolation — mock its inputs, verify its outputs, without standing up the whole system.
- **Constraint (hard):** PlayManager3D is the step executor. It advances through steps, manages chains of objectives, and signals completion. That's ALL it does.
- **Constraint (soft):** Adding responsibilities to the executor (resolving play data, constructing UI, building objectives) creates coupling that makes each responsibility harder to change independently.

## Tension

Convenience pulls toward putting resolution/presentation/objective-construction into the executor (it's already there, it has the data). But testability and debuggability demand that the executor be a pure step-cursor — it reads pre-computed data and advances through it. Mixing concerns makes the executor both harder to test and harder to debug.

## Resolution

**PlayManager3D is a pure step executor.** It does: cursor advancement, chain management, step completion signals. It does NOT: resolve play data (that's PlayResolver), present to UI (that's RuntimeUI), construct objectives (that's ObjectivePlanBuilder). Each seam is a testable boundary.

Pre-computed data (ResolvedPlayView) is handed IN. Signals go OUT. The executor never reaches back upstream.

## Consequences

- **ObjectivePlanBuilder must exist** as a separate seam — it translates resolved actions into RuntimeObjectives before execution starts.
- **ResolvedPlayView must be complete** before execution begins — no lazy resolution during the run.
- **Debugging is local:** if fielder movement is wrong, check ObjectivePlanBuilder. If step sequencing is wrong, check PlayManager3D. Never both.

## Evidence

- Architecture interview decisions #11-13 (2026-06-17): "RuntimePlay carries pre-computed ResolvedPlayView", "PlayManager3D as pure step executor (cursor, chains, signals)", "ObjectivePlanBuilder translates resolved actions → RuntimeObjectives".
- Game Programming Patterns, Command pattern: separate the what (command) from the when (executor).
