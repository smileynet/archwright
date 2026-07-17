# Q05 — C4 resolution: Extension Protocol + stack-adapter framework

**Status:** DECIDED — Codify the Extension Protocol (theory + practice); stacks framework is its second axis; T7 → pending registry row
**Date:** 2026-07-17

## Question

C4 asked "prove or descope the GDScript trace emitter." Operator reframed twice: (1) proactively build adapter components as project types are encountered; (2) generalize — archwright's goal is adaptability; research/spikes generate and test new material following existing patterns.

## Research

In-repo: the meta-pattern already instantiated 4× unnamed (B1 overlays, detect-rule tuning, C8 forces, OQ#9 growth rule). T7 target project (lacrosse-bosse-platform) verified absent from this machine; "~20 lines" claim lives only in .memory/PLAN.md.

Subagent research (4 tracks, 20+ sources, `.scratch/research/`):
- **Maturity registries** (Rust tiers, K8s feature gates, BCD): tiers by guarantee; stepwise demotion; history retained; hand-declared status decays — compute it; YAGNI rule-of-two on registry machinery.
- **Adapter architectures** (OTel, LSP, tree-sitter): per-adapter × per-capability matrix; SKIP-with-reason degradation; small neutral contracts; manifest over heavyweight registration.
- **Conformance gating** (K8s, TCK, OTel, tree-sitter): golden-corpus is the lightest gate; capability declarations let partial adapters skip rather than fail; test↔rule traceability; matrix computed from test results.
- **Self-extending methodologies** (CEGAR, Alexander, FORMS/three-layer): failure artifacts identify the missing distinction; extensions are instances of existing kinds — kind changes get separate governance; recursion is level-terminating; refine minimally.

## Decision

**Codify at two levels + instantiate:**

1. **Theory** — findings.md entry: the methodology is self-extending; gaps in archwright's own coverage are counterexamples handled by its own loop (detect → research → generate from pattern → verify → register). Cites CEGAR concretization failure, Alexander piecemeal growth, three-layer meta-level.
2. **Practice** — "Extension Protocol" in steering/archwright-conventions.md, six rules:
   - Gaps are pending-with-reason, never silent; the gap artifact names the missing adapter (stack, kind, what it unblocks)
   - Two-tier governance: new INSTANCES of existing kinds flow through the protocol; new KINDS/axes/format changes require ADR + HITL
   - Research before generating (2+ sources or a spike; spike output IS the conformance scenario)
   - Conformance at birth: golden corpus (scenario source + expected output), wired into run-fixture-tests.sh
   - Tiered status by guarantee, reusing confidence vocabulary: pending → ★ (conformance passed) → ★★ (corpus in fixture suite + measured cost); stepwise demotion; since: history — status COMPUTED by the suite, not hand-declared
   - Activation-gated enforcement + rule-of-two (no axis scaffolding until ≥2 concrete entries)
3. **Instance** — `tools/stacks/` (sibling of `tools/domains/`): REGISTRY.yaml (minimal: trace_emitter, ast_grammar, check_patterns kinds), per-stack dirs with conformance/. Birth entries: gdscript (all pending — T7 converted), typescript (pending; C10 builds trace_emitter as first measured adapter).

## Implications

- C4 closed: T7 neither proven nor descoped — converted to a pending registry row with the claim becoming measured data on first build
- C10 gains scope: builds the TypeScript emitter (first Extension Protocol exercise)
- B6 vocabulary map gains the registry tier scale as a derived use of ★★/★/—
- survey/derive/check skills gain stack-detection + registry-consultation touch points
- Est. ~3h for protocol + registry + skill touch-points (excl. emitters, built per-encounter)
