---
kind: pattern
id: explicit-dependencies
name: "Explicit Dependencies"
scale: loops-systems
confidence: "★"
above: []
resolves_into:
  - "constraint:no-autoloads"
---

# Explicit Dependencies

## Forces

- **Desire:** Components should be testable without standing up the full application — unit tests instantiate a component, provide mock dependencies, and verify behavior.
- **Desire:** When reading code, dependencies should be visible at the point of use — no hidden globals that affect behavior invisibly.
- **Constraint (soft):** Godot's autoload system provides convenient global access to services. Some patterns (input handling, audio) genuinely benefit from global availability.
- **Constraint (hard):** The practice execution runtime is short-lived and run-scoped — autoloads live for the entire app lifetime, which is the wrong lifecycle.

## Tension

Autoloads are convenient (any node can access any service) but they hide dependencies (you can't see what a component needs without reading its implementation), break testability (can't mock a global), and have the wrong lifecycle for run-scoped state (a practice run starts and ends; an autoload persists across runs).

## Resolution

**Zero autoloads for v1.** All dependencies are explicit — injected downward via RuntimeExecutionContext (a RefCounted bundle). Promotion to autoload requires meeting defined criteria: the service must be app-wide, persistent across all contexts, and genuinely needed by components that can't receive injection.

This gives testability (mock the context bundle) and visibility (dependencies declared at construction) while allowing future promotion if a service truly earns global status.

## Consequences

- **RuntimeExecutionContext must be threaded through** — coordinators pass it to execution, execution passes it to subsystems. More wiring code, but explicit.
- **Future autoload promotion is allowed** — this isn't "autoloads are evil", it's "default to explicit, promote when justified."
- **Testing is straightforward** — instantiate component + mock context = isolated test.

## Evidence

- Architecture interview decisions #16, #18 (2026-06-17): "RuntimeExecutionContext as RefCounted bundle, injected downward. No autoloads for run state; explicit dependencies; testable." / "Zero autoloads for v1; promotion criteria defined."
- Godot docs recommend autoloads only for "broad, self-owned systems" (verified in .references/godot-docs).
- Standard dependency injection pattern — Spring, Dagger, and every testable architecture uses explicit injection over globals.
