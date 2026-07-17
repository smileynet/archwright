# ADR 0008: The Extension Protocol — Archwright Extends Itself Through Its Own Loop

**Status:** Accepted (2026-07-17)
**Source:** Grill Q05 (`.memory/grill/audit-plan-closeout/Q05-extension-protocol.md`); research in `.memory/research-extension-protocol/` (4 tracks, 20+ sources)

## Context

C4 asked "prove or descope the GDScript trace emitter." The operator reframed the question twice, landing on: archwright's goal is adaptability — when the methodology encounters a project type, language, or situation its material doesn't cover, it should generate and test new material following its own existing patterns, rather than treating each gap as a one-off descope decision.

The meta-pattern had already been instantiated four times without a name: B1 domain overlays, detect-rule tuning, C8 game-force predicates, and the OQ#9 growth rule. Each followed the same unwritten sequence — notice a gap, research prior art, generate an instance of an existing kind, verify it, register it.

Prior art (four research tracks) converges on a shared structure:
- **CEGAR:** a coverage gap (spurious counterexample) is a machine-checkable signal that the abstraction vocabulary is too coarse; the failure artifact itself identifies the missing distinction; refinement is minimal and local.
- **Alexander:** a pattern language cannot be invented top-down — new patterns are discovered in use; the pattern format is itself the extension mechanism; growth is piecemeal.
- **Self-adaptive systems (FORMS, three-layer):** the meta-level is a first-class architectural element; recursion is bounded (three layers, then human); guarantees degrade up the tower — direct precedent for confidence-gated autonomy.
- **Registries/conformance (Rust tiers, K8s feature gates, OTel matrix, tree-sitter corpora):** tiers by guarantee, cumulative requirements, stepwise demotion, status computed from test results rather than hand-declared, golden-corpus as the lightest conformance gate, YAGNI rule-of-two on registry machinery.

## Decision

**Archwright is self-extending: a gap in its own coverage is a counterexample against its own abstractions, handled by its own loop.** Codified at two levels plus one instance:

1. **Theory** — findings.md entry 13: the methodology applies CEGAR to itself. Detect → research → generate from existing pattern → verify → register.
2. **Practice** — "Extension Protocol" section in `steering/archwright-conventions.md`, six rules:
   1. Gaps are **pending-with-reason**, never silent. The gap artifact names the missing adapter (stack, kind, what it unblocks).
   2. **Two-tier governance:** new INSTANCES of existing kinds flow through the protocol; new KINDS, axes, or format changes bypass it and require ADR + HITL.
   3. **Research before generating:** 2+ sources or a spike; spike output IS the conformance scenario.
   4. **Conformance at birth:** golden corpus (scenario source + expected output), wired into `run-fixture-tests.sh`.
   5. **Tiered status by guarantee**, reusing confidence vocabulary: `pending` → ★ (conformance passed) → ★★ (corpus in fixture suite + measured cost). Stepwise demotion; `since:` history retained. Status is COMPUTED by the suite, not hand-declared.
   6. **Activation-gated enforcement + rule-of-two:** an adapter's checks only run where its stack is detected; no axis scaffolding until ≥2 concrete entries need it.
3. **Instance** — `tools/stacks/` (sibling of `tools/domains/`): `REGISTRY.yaml` with three adapter kinds (trace_emitter, ast_grammar, check_patterns), per-stack dirs with `conformance/`. Birth entries: gdscript (all pending — T7 converted), typescript (pending; C10 builds the trace emitter as the first measured adapter).

## Consequences

- C4 closes: the GDScript trace emitter is neither proven nor descoped — it converts to a pending registry row whose "~20 lines" claim becomes measured data on first build.
- C10 gains scope: builds the TypeScript emitter as the first full Extension Protocol exercise.
- The confidence vocabulary map (docs/glossary.md) gains the registry tier scale as a derived use of ★★/★/—.
- survey/derive/check skills gain stack-detection and registry-consultation touch points; missing adapters SKIP with a declared reason (LSP-style graceful degradation), never fail.
- Coverage gaps stop being descope candidates by default — descoping a gap now requires the same explicitness as extending (a reasoned pending row or an ADR).

## Rejected Alternatives

- **Prove-or-descope per gap (original C4 framing):** treats each gap as terminal; loses the reusable method; contradicts the adaptability goal.
- **Proactive adapter building (operator's first reframe):** builds adapters before a project needs them; violates YAGNI rule-of-two and Alexander's discovered-in-use principle.
- **Hand-declared adapter status:** MDN deprecated its `experimental` boolean because vague hand-set flags decay; K8s/Rust compute or review status against evidence. Status must come from the fixture suite.
