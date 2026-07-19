# Project Glossary

**Archwright**:
AI-assisted design system that helps humans express design intent (forces) through conversation, resolves that intent into verified architecture specifications, and routes corrections back when violations are found. The agent IS the system; tools handle mechanical tasks.
_Avoid_: "compiler" (implies mechanical transformation), "tool" (archwright is a methodology embodied as skills)

**Force**:
Any pressure acting on a design decision. Split by polarity into Desires (attractive) and Constraints (bounding). Product-level desires (what humans want to accomplish) are primary — architectural constraints exist to serve them.
_Avoid_: "requirement" (too flat), "feature" (no tension)

**Desire**:
An attractive force — the intended feel, quality, aliveness. Spans functional jobs (what it must accomplish), emotional jobs (how it should feel), and social jobs (how it positions the user). Directionless about limits.
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
The upward flow: downstream findings → revised design. Generalizes. Level-terminating, confidence-gated, follows provenance links. Owned by the `archwright-passup` skill (decided 2026-07-17, grill Q02) — check verifies and emits structured violations; passup lifts and routes them.
_Avoid_: "feedback" (too vague), "escalation" (implies hierarchy)

**Provenance link**:
The recorded "this came from that" trace laid down during hands-down; walked backward by pass-up. Per-element annotation (like git blame).

**Counterexample**:
A trace that violates an invariant. Simultaneously the best visualization of an invariant and the payload of pass-up.

**Contrast pair**:
A counterexample paired with the nearest satisfying instance. The diff between them localizes the fault. The primary pass-up payload.
_Avoid_: "error report" (contrast pair carries the fix direction, not just the problem)

**Confidence (★★ / ★ / —)**:
Stated belief that a resolution names a true invariant vs. one workable arrangement. ★★ = mechanically verifiable (model checker, type system, proof). ★ = heuristically checkable (code review, test coverage, playtests). — = advisory (expert judgment, no mechanical check). Gates AI autonomy, pass-up escalation, and checking rigor. Anchor vocabulary — derived scales (autonomy actions, check severities) and related-but-distinct axes (force evidence L1–L5, audit finding severity HIGH/MED/LOW) are mapped in `docs/glossary.md`.
_Avoid_: using error/warn/info or HIGH/MED/LOW as if they were confidence values — they derive from or sit beside it.

**Scenario walk**:
The derivation process for discovering forces from desires: walk a human desire through the current architecture as concrete scenarios, identify where gaps or friction arise, generate architectural questions that expose the underlying tension. The primary method for translating product desires into architectural form.
_Avoid_: "brainstorm" (scenario walks are structured, not free-form)

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

**Baseline**:
Known-debt suppression for check runs (CK-07/08): `.archwright-baseline.json` entries (human-created, never tool-added) suppress fully-fingerprint-matched constraint/dependency violations to warnings with `baselined: true`. A baselined ★★ keeps its escalate flag (no back door around C2); behavior/trace violations are never suppressible. `--update-baseline` is a remove-only ratchet.
_Avoid_: treating a baseline entry as a waiver of the ★★ hard floor, or as applying to behavior/trace FAILs.

**Fingerprint (aw/v1)**:
A violation's stable identity: sha256 over spec_id + invariant + normalized path + normalized evidence content, truncated to 16 hex chars, with a visible `_<n>` occurrence suffix for identical duplicates. Line numbers never enter the hash. Version tag (`algo: aw/v1`) stored alongside; unknown versions are unmatchable, never guessed. Shared plumbing for the baseline and the ADR-0009 evidence ledger.
_Avoid_: file+line as identity (churns on every edit above the match).

**Evidence ledger**:
The baseline's tool-owned sibling (`.archwright-evidence.json`, ADR 0009): check runs auto-append confidence evidence events — demotion-candidate (★★/★ FAIL, never baselined/—) and promotion-candidate (pass streak per `config.promotion_streak`, or a ★/— invariant passing a bounded check). Activation by existence (or `--evidence`); deduped; trace events carry `fingerprints: []`. The ledger never changes a confidence value — ratification is human, in the artifact, and ★★ moves always block for HITL.
_Avoid_: tools editing artifact frontmatter (rejected alternative A — noisy diffs, self-review smell); treating a candidate event as a ratified confidence change.

**Commit-binding (code_state)**:
The git identity `{commit, dirty}` stamped on every check `--json` document and evidence-ledger event (ticket 018, EDA signoff precedent). Staleness is soft decay by affectedness, judged at consumption: evidence at commit C is fresh iff the spec + its `check.target` are unchanged since C (CK-19's predicate with `--base C`); `dirty: true` = unverifiable for signoff-grade claims. Git absent = null fields with reason, never a crash. Dedup identity excludes code_state (ADR 0009 amendment).
_Avoid_: hard EDA-style invalidation (any change voids all evidence — kills pass streaks under normal commit cadence); mechanically deleting stale events (append-only stands).

**Force file**:
The durable per-force artifact (`design/forces/<id>.md`, kind: force) — the root of provenance. `serves:` and `from_force:` resolve against these once at least one exists.
_Avoid_: calling the working YAML inventory (`.memory/archwright-forces-*.yaml`) "the forces" — that's extraction scaffolding.

**HITL-blocking gate**:
A pipeline gate that always stops for the human: resolve, L4/L5 desire validation, ★★ events that survive the research gate (ADR 0010 — noise/known dispositions are proposed/logged instead; hard floor always blocks), fog, end-of-span digest. All other gates are **flow-through** (ADR 0007).

**Gated (pattern status)**:
Pattern status meaning the resolution is RATIFIED but activation is gated on a named future event (`gated_on:` required — e.g. an engine migration, a spike verdict). Validation rejects `gated` without `gated_on:` (ticket 011).
_Avoid_: `status: fog` for a ratified deferral — fog means unresolved tension and HITL-blocks; repurposing it corrupts the signal.

**Span**:
A human-pre-authorized run of contiguous flow-through phases ("forces through derive"). Auto-advance never crosses the span boundary; each phase writes a digest entry.

**Protocol cluster (contract exception)**:
The tightly-coupled messages of ONE protocol, owned by one authority actor, that evolve in lockstep (e.g., request/accept/reject of a transfer — the counterparty's request leg belongs to the same protocol) — may share one contract spec, named for the protocol. The only sanctioned bend of one-spec-per-file (C7 R2, ratified 2026-07-16).

**Contract candidate**:
Model-phase output naming an event's identity/direction/producer WITHOUT payload shape — the contract phase (sole owner of contract specs) formalizes it, carrying `from_model:` provenance (C7 R1, ratified 2026-07-16).

**Domain overlay**:
Per-domain vocabulary pack (`tools/domains/<domain>/` — game, web, general): `scales.yaml` maps the four canonical scale IDs to domain-native labels/examples; `predicates.yaml` holds advisory, prior-art-backed design rules. Detected via `detect.yaml` manifest rules (architecture over theme — a game-themed express backend is `web`); explicit override wins. Deployed with the survey skill (`references/domains/`).
_Avoid_: per-domain scale IDs — the enum is canonical; only labels vary.

**Extension Protocol**:
How archwright extends itself when it encounters a situation its material doesn't cover (grill Q05, 2026-07-17): gaps surface as pending-with-reason → research (2+ sources or spike) → generate a new INSTANCE from the axis's existing template → conformance-test at birth (golden corpus in the fixture suite; status computed, not declared) → register with tiered status (pending → ★ → ★★) → activation-gated enforcement. New KINDS/axes/format changes bypass the protocol and require ADR + HITL (two-tier governance).
_Avoid_: treating coverage gaps as descope candidates — a gap is a counterexample against archwright's own abstractions (CEGAR applied to the methodology).

**Stack adapter**:
Per-language/engine mechanical component (`tools/stacks/<stack>/`): trace emitter, ast-grep grammar, check-pattern library. Orthogonal to domain overlays (tilerush-demo = web domain + typescript stack). Tracked in `tools/stacks/REGISTRY.yaml` with guarantee-tiered status and measured cost; built on first encounter per the Extension Protocol.
_Avoid_: conflating stack (language/engine) with domain (vocabulary).

**Discovery track**:
The HITL-dense, divergent half of the methodology (grill, wireframes, WoZ, concierge, spikes, future feature intake) feeding the verification track (survey→check) at the `resolve` seam. Same agent, same repo, same `design/` space — two kinds of WORK, never two pipelines (ADR 0011).
_Avoid_: "design pipeline" (the two-pipeline framing is dual-track agile's documented failure mode)

**Seam contract**:
What discovery hands to verification: resolved decisions + evidence + an explicit unresolved list — never bare artifacts (wireframes/prototypes are evidence; the decision record is the deliverable). Format: the decision ledger.
_Avoid_: "handoff" (implies separate owners)

**Decision ledger**:
The seam's capture format (adopted from wizard_of_oz `contract:decision-entry`): append-only `D{NNN}` entries with phase, category (core 5 + domain extensions), origin (user | suggested | inferred), decision, rationale verbatim, alternatives; reversals via `SUPERSEDES D{NNN}`; entries are truth — projections regenerate from them, never the reverse.
_Avoid_: free-prose session notes (unparseable, no origin audit)

**Artifact gap**:
The explicit "Not resolved here" section every discovery artifact carries (states, edge cases, error/loading, interaction rules — what wireframes deliberately omit). First-class output: becomes the model phase's TODO input.
_Avoid_: treating omissions as implicitly resolved (the #1 design-to-dev handoff failure)

**Conservation check**:
The LEC-equivalent for non-deterministic agent transforms (grill Q6): mechanical citation-graph verification that nothing was invented (every output element cites a source) and nothing was lost (every active input decision is consumed or explicitly deferred). Independent of the transform's reasoning; pairs with golden-corpus conformance (process-level).
_Avoid_: attempting semantic equivalence checks on creative transforms (impossible); trusting the transformer (the Alloy vacuous-model failure class)

**Rubber-stamp guard (calibration)**:
Origin-counting agency tripwire from wizard_of_oz `facilitated-agency`, calibrated by session type (grill Q4): creative sessions (wireframes, WoZ) keep the strict 3+-consecutive-suggested stop; grill sessions get periodic decision-surfacing instead — agreement with researched recommendations is the system working, never penalized.
_Avoid_: applying the strict tripwire to grills (punishes legitimate agreement)

**Reconciliation pass**:
For large projects/monorepos: after per-area pipeline runs, an all-up synthesis that dedupes forces across areas, surfaces cross-area tensions, and unifies models. Only used when scale forces area partitioning — normal projects run full-project/all-areas in one pipeline (grill Q06, 2026-07-17). Design artifacts are live documents committed branch-agnostically to the current project branch unless the user specifies otherwise.
_Avoid_: area-scoping small projects (partition is the exception for scale, not the norm); special design branches by default.
