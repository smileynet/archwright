# Open Questions

Prioritized. Resolved questions marked; new questions added from validation spikes and research.

## Resolved

- ~~#3 Canonical form of the graph~~ → Statecharts. ADR 0002.
- ~~#4 Invariant authoring model~~ → Inline authoring, holistic checking. R3 synthesis.
- ~~#9 Tooling surface~~ → Agent + scripts on PATH. ADR 0001, 0004.
- ~~#5 Confidence Calibration~~ → ★★ = mechanically verifiable, ★ = heuristically checkable, — = advisory. Promotion via evidence accumulation. Formalized in skills and CONTEXT.md.
- ~~Product-level force extraction~~ → JTBD-informed process: read product sources first, Five Whys inversion, L1-L5 confidence classification, HITL validation gate. Formalized in archwright-forces skill.

## Active

### 1. The Lift Contract ← partially addressed

The explicit rule by which a child level translates its failure into the parent's vocabulary. R1 research established the three components (project, summarize, attribute) and S2 proved the provenance roundtrip works. Remaining: formalize the "summarize" step (currently requires AI judgment — can it be made more mechanical?). **Home:** the lift contract now lives in `skills/archwright-passup/` (step 2) and matures there — refinements land in the skill, not here.

### 2. State Explosion Mitigation ← NEW (from V2, Penguin Clash)

Real games hit state explosion (~10^72 states for a simple multiplayer game). Archwright's Alloy checking works only on ABSTRACTED models. How do we:
- Guide the designer/agent in choosing the right abstraction level?
- Assure that the abstraction faithfully represents the real system?
- Detect when an abstraction is too coarse (spurious counterexamples)?

Prior art: Mawhorter 2021 (hand-authored tile abstraction for Super Metroid), CEGAR (automatic refinement), Rezin 2017 (manual model reduction).

### 3. Lean Migration Timing ← NEW (from Lean research)

When does CSLib mature enough to serve as archwright's verification backend? Triggers:
- CSLib has robust LTS formalization with temporal properties
- AI provers reliably handle archwright-sized properties (not just math olympiad)
- Veil or similar provides model-checking mode within Lean

Current status (mid-2026): CSLib has basic LTS + bisimulation. Temporal logics on roadmap. AI provers at 88.9% on math benchmarks but untested on software specs.

### 4. Spurious-vs-Real Adjudication

A model checker can prove a trace infeasible, but "real design flaw vs. modeling artifact" often needs the Desire to adjudicate. Design the AI-proposes / human-confirms handshake, especially for ★★ invariants.

### 5. Desire Validation at Scale ← NEW

When archwright operates on a large project (100+ files, multiple user roles), how do we validate inferred product desires efficiently? Current approach: present L4-L5 desires to user for confirmation. At scale:
- Can we use competitive analysis or domain analysis to auto-promote L5 → L3?
- Should we batch validation (present 10 desires at once) or sequence (one at a time)?
- How do we detect when a product desire CHANGES over time (pivot, scope cut)?

### 6. Counterexample Classification Predicates ← updated

The 12 candidate game failure predicates need formal expression. Three are validated (softlock via Mawhorter's `AG(EF(goal))`, death spiral, degenerate strategy as established terms). Remaining: formalize the others and test on real game models.

### 7. The Abstraction Gap ← NEW

Checking an abstracted model proves properties of the ABSTRACTION, not necessarily the real system. How does archwright communicate this limitation? Options:
- Clearly label confidence as "proven in model" vs "proven in implementation"
- Runtime monitoring bridges the gap (check invariants during actual execution)
- Property-based testing against real implementation complements model checking

### 8. Quiescence / Shipping Criteria

Formalize "stable under its own pass-up": which residual tensions are acceptable to ship as logged zero-star known issues.


### 9. Game-Specific Predicate Library ← NEW (from Catalyst pipeline run)

Game design patterns use domain-specific predicates that recur across projects (e.g., "pacing via scarcity," "locality of mastery," "tonal contrast amplification," "teaching metaphor"). An initial library of 13 predicates exists in `tools/domains/game/predicates.yaml`. Questions:

- Should predicates be formalized with checkable structure (like constraints) or remain advisory?
- How do predicates compose? (e.g., "earned-not-given" + "locality-of-mastery" = "earned route mastery")
- Can predicates be validated empirically (via playtesting metrics) or only by design review?
- How does the predicate library grow? (Add from each pipeline run? Curate quarterly?)
- Relationship to the 12 counterexample classification predicates (#6): are game predicates a superset, subset, or orthogonal?

Current state: `tools/domains/{game,web,general}/predicates.yaml` exist (game: 13 entries from the Catalyst MLP run; web: 7; general: 7). B1 (2026-07-16) settled the overlay STRUCTURE — parallel `scales.yaml` + `predicates.yaml` per domain, advisory shape (statement/applicable_when/prior_art/anti_pattern), growth rule in each file header (append from runs; curate at ~25 entries; promote cross-domain entries to general/). Still open here: checkable formalization, composition, empirical validation, and the relationship to the #6 counterexample predicates.


### 10. Audit Findings as Force Input ← NEW (from Catalyst pipeline run)

Should audit findings ("Damn Lies") feed BACK into the force inventory? A doc that claims X while code does Y means a decision was made but never propagated — that's an unnamed tension between "what we said" and "what we did." Should the audit skill produce force-candidates that the forces phase can consume?

Current state: audit produces fix tickets. Forces are extracted from decisions/grills. These are separate tracks.

### 11. Code Generation from Contract Specs ← NEW

Can the contract phase produce implementation stubs? The typed schemas in contract specs (fields, types, lifecycle) contain enough information to generate:
- GDScript Resource class stubs (`class_name X extends Resource` with @export fields)
- Signal declarations with typed parameters
- Save/load serialization boilerplate

Prior art: Alchemy (Alloy → SQL), Overture (VDM → Java+JML), XState typegen v4 (machine → TypeScript types). All generate implementation from formal specs.

Question: Should this be part of contract, a separate `archwright-scaffold` skill, or left to the developer?

### 12. Architecture-as-Documentation ← NEW (from Jaysen Draney)

Can archwright's pipeline output (patterns + models + specs) serve AS the project's documentation, rather than being separate artifacts that describe the same system the docs describe? If the patterns ARE the architecture documentation, there's no drift to detect — the docs and the design are the same artifact.

Options:
- Generate a browsable docs site from design/ artifacts (patterns → pages, models → diagrams, specs → API reference)
- Make design/ the canonical source, existing docs/ becomes views/exports
- Keep both but generate cross-links (doc references spec, spec references doc)

This is the "docs website as a view of architecture" idea. The pipeline already produces the architecture — rendering it as documentation is a presentation layer.

### 13. Check Tooling Interface (cross-language) ← NEW (from Catalyst check run)

How should archwright-check.py interface with target project languages? Research validated a tiered architecture:
- Tier 1 (text): ripgrep for presence/naming/import checks
- Tier 2 (structural): ast-grep with tree-sitter grammars for structural AST matching
- Tier 3 (formal): Alloy for model checking invariants

Key finding: tree-sitter-gdscript (PrestonKnopp) is production-ready. ast-grep supports custom languages via dynamic .so loading. tree-sitter-language-pack provides 306 languages (including GDScript) for Python-native parsing.

Next step: Build the spec-to-check compiler that routes constraint specs to the appropriate tier based on `check.method`.
