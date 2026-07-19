---
kind: pattern
id: explicit-dependencies
name: "Explicit Dependencies"
scale: loops-systems
confidence: "★"
status: active
serves: [testable-in-isolation]
context: []
completed_by: []
resolves_into:
  - "constraint:no-autoloads"
---

# Explicit Dependencies

## Problem

**Godot autoloads are convenient global singletons, but every autoload is a hidden dependency that makes components untestable in isolation.**

## Context

Project-wide convention for how components acquire their collaborators.

## Forces

- **Desire:** Any component testable headless with mock collaborators.
- **Constraint (soft):** Godot's autoload mechanism registers globals in `project.godot` — accessible from anywhere, mockable from nowhere.

## Evidence

- Autoloaded services in an earlier iteration made gdUnit tests order-dependent (global state leaked between tests).
- Prior art: dependency injection over service locators — widely documented tradeoff; Godot community guidance favors explicit injection for testability.
- Rejected alternative: autoload + reset hooks — every test must know every global to reset.

## Therefore

**No autoloads.** `project.godot` contains no `[autoload]` section. Services are injected explicitly (constructor/initialize parameters).

## Consequences

- Wiring is more verbose at scene setup.
- Every dependency is visible in the component's interface.

## Verification

- `constraint:no-autoloads` — grep: no `[autoload]` section in `project.godot` (★, mechanical)

## Completion

- Completed by a service-wiring pattern (not included in this fixture).
