# Project Glossary

**Archwright**:
AI-assisted design system that compiles human design intent (expressed as forces) into architecture (state graphs). The project itself.

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

**Hands-down**:
The downward compile direction: forces → pattern → sub-patterns → state/data/interface/invariant. Concretizes.
_Avoid_: "top-down" (implies hierarchy without the reciprocal)

**Pass-up**:
The upward flow: downstream findings → revised design. Generalizes. Level-terminating, confidence-gated, follows provenance links.
_Avoid_: "feedback" (too vague), "escalation" (implies hierarchy)

**Provenance link**:
The recorded "this came from that" trace laid down during hands-down; walked backward by pass-up. The routing table for corrections.

**Counterexample**:
A trace that violates an invariant. Simultaneously the best visualization of an invariant and the payload of pass-up.

**Confidence (★★ / ★ / —)**:
Stated belief that a resolution names a true invariant vs. one workable arrangement. Gates AI autonomy and pass-up escalation height.

**Quiescence**:
The practical "done" state — the tower is stable under its own pass-up; only low-confidence, low-severity signals still circulate.

**State graph**:
The central architectural anchor. States (modes) + transitions (guarded verbs). Simultaneously human-designable, AI-generable, and formally checkable.

**Lift (re-abstraction)**:
Translating a signal into the parent level's vocabulary at each up-hop. The hardest cognitive work in the system.

**Promotion**:
Turning implicit into explicit — e.g., extended-state variable → discrete mode, or unwritten Desire → explicit invariant.

**CEGAR**:
Counterexample-Guided Abstraction Refinement. The formal-methods loop that archwright generalizes to a design tower.
