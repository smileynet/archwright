# Project Glossary

**Archwright**:
AI-assisted design system that helps humans express design intent (forces) through conversation, resolves that intent into verified architecture specifications, and routes corrections back when violations are found. The agent IS the system; tools handle mechanical tasks.
_Avoid_: "compiler" (implies mechanical transformation), "tool" (archwright is a methodology embodied as skills)

**Force**:
Any pressure acting on a design decision. Split by polarity into Desires (attractive) and Constraints (bounding).
_Avoid_: "requirement" (too flat), "feature" (no tension)

**Desire**:
An attractive force — the intended feel, quality, aliveness. Directionless about limits.
_Avoid_: "goal" (implies measurable target)

**Constraint**:
A bounding force — platform, budget, ruleset, capacity. Tagged hard (inviolable) or soft (negotiable).
_Avoid_: "limitation" (implies negative-only)

**Tension**:
The explicit conflict between forces that constitutes the actual design problem.
_Avoid_: "trade-off" (implies compromise rather than resolution)

**Pattern**:
A recurring, reusable resolution of a named tension that hands specific commitments down to architecture. Not a template.
_Avoid_: "template", "blueprint"

**Resolution**:
The generative move that balances forces. A rule for making form, never a fixed artifact.

**Resolves into**:
The process by which design intent takes form as verified architecture. Not mechanical compilation — involves creative resolution + formal verification.
_Avoid_: "compiles to" (too mechanical, implies deterministic lossless transformation)

**Hands-down**:
The downward direction: forces → pattern → sub-patterns → architecture. Concretizes.
_Avoid_: "top-down" (implies hierarchy without the reciprocal)

**Pass-up**:
The upward flow: downstream findings → revised design. Generalizes. Level-terminating, confidence-gated, follows provenance links.
_Avoid_: "feedback" (too vague), "escalation" (implies hierarchy)

**Provenance link**:
The recorded "this came from that" trace laid down during hands-down; walked backward by pass-up. Per-element annotation (like git blame).

**Counterexample**:
A trace that violates an invariant. Simultaneously the best visualization of an invariant and the payload of pass-up.

**Contrast pair**:
A counterexample paired with the nearest satisfying instance. The diff between them localizes the fault. The primary pass-up payload.
_Avoid_: "error report" (contrast pair carries the fix direction, not just the problem)

**Confidence (★★ / ★ / —)**:
Stated belief that a resolution names a true invariant vs. one workable arrangement. Gates AI autonomy, pass-up escalation, and checking rigor.

**Quiescence**:
The practical "done" state — the system is stable under its own pass-up; only low-confidence, low-severity signals still circulate.

**State graph**:
The central architectural anchor. States (modes) + transitions (guarded verbs). Simultaneously human-designable, AI-generable, and formally checkable.

**Behavior (spec kind)**:
A spec describing how a component behaves — its modes, transitions, and guards. The formal model is a statechart.
_Avoid_: "machine" (overloaded, mechanical)

**Spec**:
A formal expression of architectural commitments with typed `kind` field. Flat, self-contained, linked via `kind:id` references. Kinds: behavior, contract, constraint, dependency, boundary, protocol. Format varies by kind: YAML for machine-primary (behavior, contract), markdown+frontmatter for human-primary (constraint, dependency).
_Avoid_: "design doc" (specs are checkable, not prose)

**Contract (spec kind)**:
A typed data shape with lifecycle constraints — what fields exist, when they're valid, who produces/consumes them.

**Constraint (spec kind)**:
A global architectural rule that applies across components. Self-describing: carries its own check strategy.

**Dependency (spec kind)**:
An allowed or forbidden relationship between components. Checked via static analysis of the codebase.

**Proxy invariant**:
A checkable structural/behavioral property that approximates an experience quality. "Feels oriented" → "novel_elements ≤ threshold."
_Avoid_: confusing with direct experience measurement (proxies are approximations, not proofs of feel)

**Lift (re-abstraction)**:
Translating a signal into the parent level's vocabulary at each up-hop. The hardest cognitive work in the system.

**Promotion**:
Turning implicit into explicit — e.g., extended-state variable → discrete mode, or unwritten Desire → explicit invariant.

**CEGAR**:
Counterexample-Guided Abstraction Refinement. The formal-methods loop that archwright generalizes to a design tower.
