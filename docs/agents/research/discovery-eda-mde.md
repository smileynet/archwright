# How Mature Engineering Toolchains Separate Creative Design from Mechanical Verification/Synthesis

Research date: 2026-07-18. Domains: EDA/hardware (RTL frontend vs synthesis/backend), model-driven engineering (design-space exploration vs model checking).

## Summary

Mature toolchains do NOT separate "creative" from "mechanical" as a single boundary — they build a **ladder of abstraction levels**, where each level pairs a creative refinement step with a mechanical *equivalence/conformance* check against the level above. The creative act (RTL authoring, architecture selection, design-space exploration) always happens against a **frozen contract from the level above** (spec → Vplan, RTL → SDC/UPF constraints), and the mechanical act (synthesis, place-and-route, model transformation) is only trusted because an **independent checker** (LEC, STA, model checker) re-verifies the output against the input rather than trusting the transformer. Phase transitions are governed by **multi-gate signoff**: a set of simultaneous, individually-owned, waivable-only-with-documentation criteria tied to a frozen artifact version (a specific commit hash). The theoretical backbone is Sangiovanni-Vincentelli's "orthogonalization of concerns": separate *function* (what, creative) from *architecture* (how, explorable) so each can be verified and explored independently, meeting at a platform contract.

## Details

### 1. The EDA frontend/backend split — and what actually crosses the boundary

The digital IC flow: **spec → microarchitecture → RTL design → functional verification → lint/static analysis → synthesis → formal equivalence → physical design (place & route) → timing/physical signoff → tapeout** (open-EDA survey, saadsiddiqui substack; MDPI open-source EDA survey 2026).

- **Frontend** = creative + intent-verified: humans write RTL (Verilog/VHDL) expressing *behavior*; verification (simulation, formal, assertions, coverage) establishes the RTL matches the *spec*. Synthesis itself is usually counted as the last frontend step (yogish.com guide, 2024).
- **Backend** = mechanical + physics-verified: takes the synthesized gate-level netlist and produces layout (floorplan, place, route, extraction, timing closure). "Designs related to process technology are considered back-end" — the boundary is fuzzy in principle but crisp in practice because of the artifact handoff (allpcb.com, 2025).

**What makes the split work is that the handoff artifact is a bundle, not a single file.** The synthesis→backend handoff carries (yogish.com; scribd synthesis guides):

| Artifact | Role in the contract |
|----------|---------------------|
| Gate-level netlist | The design content itself (structure, not behavior) |
| SDC (Synopsys Design Constraints) | Timing/design intent — *updated* by synthesis, not just passed through |
| UPF (Unified Power Format) | Power intent — also updated as synthesis introduces new power structures |
| DEF | Physical placement seed (physical-aware flows) |
| Reports (QoR, timing, area) | Evidence the handoff meets quality bars |

Key insight: **intent artifacts (SDC/UPF) travel WITH the design artifact and are versioned at each phase**. Each phase consumes intent + content, emits refined content + *updated* intent. The creative intent is never re-derived downstream; it is threaded through mechanically.

### 2. Don't trust the transformer — verify the transformation

Synthesis is a mechanical transformation, but the flow does not trust it. **Logic Equivalence Checking (LEC)** formally proves the netlist is functionally identical to the RTL, using an *independent tool* (Cadence Conformal, Synopsys Formality) — never the synthesizer itself (design-reuse.com "Pitfalls for LEC" 2015; Siemens Verification Horizons 2019). The RTL is treated as **golden**: "RTL is considered golden as all functionality has been verified by other methods" (vlsi.pro equivalence flow). LEC is repeated at every downstream mechanical step: RTL vs synthesized netlist, synthesized vs post-scan, synthesized-gates vs placed-gates vs post-route-gates (aminer hierarchical formal verification paper).

This is the deepest structural lesson: **verification effort concentrates once at the creative level (RTL functional verification, ~70% of project time and headcount — allpcb.com), and every mechanical level below only needs cheap equivalence proofs against the level above.** Correctness flows down by transitivity; you never re-verify function at gate level.

Netlist "quality checks" also gate the handoff mechanically: no unclocked registers, no unconstrained endpoints, no timing loops, no latches, no floating/multi-driven pins, no silently-removed flops (yogish.com). These are exactly "the synthesized netlist should meet all netlist quality checks to reduce multiple iterations" — the contract exists to make backend iterations rare.

### 3. Signoff = multi-gate, simultaneous, waiver-audited, frozen-artifact

Verification signoff (chipverify.com "Sign-Off Criteria", read in full) defines six gates that must ALL clear simultaneously:

1. **Code coverage** (90–100%, block-dependent targets; misses waived only if genuinely unreachable)
2. **Functional coverage** (95–100% against the Vplan; open bins are usually the corner cases most likely to hide bugs, so waiving requires investigation, not plausibility arguments)
3. **Assertion pass rate** (100%; critical-path assertions carry zero-waiver policies; a `cover` property that never fires = a coverage miss)
4. **Zero open Critical/Blocking bugs** (hard gate — no coverage number compensates; severity reclassification under schedule pressure is a named process violation)
5. **Regression green on the frozen commit** ("any RTL change — even a one-line comment fix — invalidates the regression result"; the commit hash is recorded in the signoff record; run twice to prove determinism)
6. **Vplan closure** (the Vplan is "the contract between the design and verification teams", written *before* RTL; every feature verified or explicitly waived)

Governance features worth stealing:
- **Waivers are first-class artifacts**: coverage point + why + who approved. "The waivers list is where the real risks are hidden" — reviewing the 98% is meaningless without reviewing the waived 2%.
- **Each gate has an accountable role** (DV engineer prepares, DV lead audits waivers + commit binding, design lead confirms spec stability, PM records the decision as "the legal record").
- **Signoff is hierarchical and non-transitive**: block signoff → integration signoff → chip signoff, each with its own regression + targets. "Block sign-off does not automatically mean the chip is ready to tape out" — integration-level bugs (interfaces, CDC, arbitration) only appear at the composed level.
- Modern signoff "is no longer a static checklist... a full pipeline that validates logical intent, physical correctness, manufacturability, and test readiness" (Tessolve, 2026). The Vplan-first practice ("map every specified feature to test scenarios, coverage goals, and sign-off criteria before a single line of RTL is written" — chipverify) means the verification contract is authored *during* the creative phase, not after.
- The whole apparatus exists because **tapeout is irreversible** (chipverify tapeout checklist). Gate rigor scales with the irreversibility of the transition it guards.

### 4. Model-driven engineering: exploration vs checking

- **Platform-based design / orthogonalization of concerns** (Sangiovanni-Vincentelli, IEEE TCAD 2000; Ferrari & SV): "separation of the various aspects of design to allow more effective exploration of alternative solutions." Specifically: separate **function** (what the design does, expressed in terms of platform services) from **architecture** (a configured collection of primitives providing those services), and computation from communication. Design proceeds as a **meet-in-the-middle**: top-down refinement of function meets bottom-up characterization of platforms at a "platform contract" — the same role SDC+netlist plays at the EDA boundary. Exploration (creative) happens in the mapping of function onto architecture; each mapping candidate is then evaluated/verified mechanically.
- **Verification-Driven Engineering** (Kordon & Hugues, SEUS 2008; Springer): argues MDE is "incomplete — 'just' an implementation framework... a conceptual gap to fill to know 'what' to do with models," and proposes inverting the priority: **model the system the way the verifier needs it** (VDE). Lesson: if verification is bolted on after free-form modeling, the models are often unanalyzable; the creative phase must author artifacts in a verification-ready formalism from the start (parallel to synthesizable-RTL coding rules + lint).
- **Design-space exploration with MBSE** (MDPI Systems 2018, set-based design): exploration is a distinct early phase evaluating *many* candidates against a cost/tradespace model in near-real-time — a breadth activity with cheap, approximate evaluation, deliberately separated from the depth activity of verifying one chosen point design.
- **Early V&V in MBSE** (ACM Computing Surveys systematic review, 2024): the field's acknowledged gap is "a lack of common understanding for how formal analyses for V&V could be placed in an MBSE setting" — i.e., MDE has models-from-early-phases but no standardized gate structure; EDA is the more mature reference precisely because its gates are standardized.
- **AI-era instance** (arXiv 2606.22413, 2026): "The LLM is the draft generator, the MDE chain is the discriminator" — generator/discriminator framing where the creative producer is untrusted and the mechanical verification chain is the arbiter. Same shape as VeriMaAS (arXiv 2509.20182): formal verification feedback from HDL tools wired directly into agentic RTL generation.

### 5. Cross-cutting principles (what makes the split work)

1. **Ladder, not wall.** Many levels; each transition pairs {creative refinement OR mechanical transform} with {mechanical conformance check against the level above}.
2. **Golden-artifact discipline.** At each transition, one side is declared golden (spec over Vplan, RTL over netlist, netlist over layout). All disagreement resolves toward golden; changing golden reopens the gate.
3. **Intent travels as a typed sidecar.** Constraints (SDC/UPF/Vplan) are machine-readable, versioned, updated-not-rewritten at each phase, and consumed by both the transformer and the independent checker.
4. **Independent checking of mechanical steps.** Never let the transformer certify its own output (LEC by a separate tool/vendor).
5. **Verify function once, prove equivalence thereafter.** Expensive verification lives at the most abstract level where the property is expressible; downstream levels get cheap equivalence obligations.
6. **Gates are simultaneous, owned, and waiver-audited.** No single metric; every exception is documented with rationale and approver; the exception list is reviewed as carefully as the pass list.
7. **Freeze before you gate.** Signoff binds to an exact artifact version (commit hash); any change invalidates the evidence.
8. **Gate rigor scales with irreversibility** (tapeout ≫ netlist handoff ≫ RTL check-in).
9. **The verification contract is authored during design, not after** (Vplan-first; VDE's "model for the verifier").
10. **Composition needs its own gates** — component-level signoff never implies system-level signoff.

### Mapping to archwright (observations, not directives)

- Archwright's `forces → patterns → models → specs → check` mirrors the ladder; `from_patterns`/`from_force` provenance ≈ SDC/UPF intent sidecars; `archwright-check` ≈ LEC/STA; baseline suppression + waivers ≈ signoff waiver discipline (archwright's evidence ledger + human ratification already matches the "documented approver" rule).
- Gaps EDA practice would highlight: (a) archwright gates on HITL decision points but has no *frozen-commit binding* of check evidence to artifact versions; (b) no explicit "golden" declaration per level (which artifact wins on disagreement is implicit in pass-up routing); (c) no composed-level signoff distinct from per-area runs — though the Q06 reconciliation pass is the embryo of exactly that.

## Sources

- [L4:verified] ChipVerify — Sign-Off Criteria (read in full): https://chipverify.com/verification/sign-off-criteria — six gates, waiver discipline, commit-hash binding, hierarchical signoff
- [L4:verified] Yogish/VLSICourses — Simplest Guide to RTL Design, Verification and Synthesis (read in full, 2024): http://yogish.com/blog/vlsi-blog/simplest-guide-to-rtl-design-verification-and-synthesis-vlsi-verification-flow — frontend/backend boundary, synthesis I/O artifact bundle (SDC/UPF/DEF updated per phase), netlist quality checks, LEC
- [L4:reported] ChipVerify — Tapeout Checklist: https://chipverify.com/verification/tapeout-checklist — "RTL sign-off = verification complete; tapeout is irreversible"
- [L4:reported] ChipVerify — Verification In Chip Design Flow: https://chipverify.com/verification/verification-in-chip-design-flow — Vplan written before RTL
- [L4:reported] AnySilicon — Ultimate Signoff (TapeOut) Checklist: https://anysilicon.com/the-ultimate-signoff-tapeout-checklist/
- [L4:reported] Tessolve — Optimizing SoC Signoff Process (2026): https://www.tessolve.com/blogs/from-gdsii-to-tape-out-optimizing-data-integrity-and-layout-signoff-for-complex-socs/ — signoff as pipeline, not checklist
- [L5:reported] Design-Reuse — Pitfalls for Logical Equivalence Check (2015): https://www.design-reuse.com/article/60607-pitfalls-for-logical-equivalence-check/
- [L5:reported] Siemens Verification Horizons — The Many Flavors of Equivalence Checking Part 1 (2019): https://blogs.sw.siemens.com/verificationhorizons/2019/07/11/the-many-flavors-of-equivalence-checking-part-1-synthesis-validation-with-lec-and-slec-a-k-a-the-most-popular-formal-apps-ever/
- [L5:reported] VLSI.pro — Equivalency Checking Flow: https://vlsi.pro/physical-design-flow/equivalency-checking-flow-basics/ — RTL-as-golden
- [L4:reported] Sangiovanni-Vincentelli et al. — System-Level Design: Orthogonalization of Concerns and Platform-Based Design (IEEE TCAD 2000): http://vmknoll82.in.tum.de/2018/pub/Main/TeachingWs2013MSE/SystemLevelDesign-OrthogonalizationOfConcernsAndPlatformBasedDesign.pdf ; Metro II/DVCon summary: http://ptolemy.eecs.berkeley.edu/projects/chess/pubs/228/metroII_dvcon.pdf
- [L4:reported] Kordon & Hugues — From Model Driven Engineering to Verification Driven Engineering (SEUS 2008): https://link.springer.com/chapter/10.1007/978-3-540-87785-1_34 ; PDF: https://fkordon.perso.lip6.fr/pdf/2008-SEUS.pdf
- [L4:reported] MDPI Systems — Early Design Space Exploration with MBSE and Set-Based Design (2018): https://mdpi.com/2079-8954/6/4/45
- [L4:reported] ACM Computing Surveys — Early Validation and Verification of System Behaviour in MBSE: SLR (2024): https://dl.acm.org/doi/full/10.1145/3631976
- [L5:reported] arXiv 2606.22413 — Closing the Verification Loop on AI-Generated Safety-Critical Software Through MDE (2026): https://arxiv.org/abs/2606.22413
- [L5:reported] arXiv 2509.20182 — VeriMaAS: Automated Multi-Agent Workflows for RTL Design: https://www.arxiv.org/pdf/2509.20182
- [L5:reported] AllPCB — Verification: the Heavy Burden in SoC Design / Digital Chip Design Flow (2025): https://www.allpcb.com/allelectrohub/verification-the-heavy-burden-in-soc-design , https://www.allpcb.com/allelectrohub/digital-chip-design-flow
- [L5:reported] Saad Siddiqui — Breaking Open-EDA for ASIC chip flow (substack): https://saadsiddiqui138117.substack.com/p/the-state-of-open-source-eda-tools
- [L4:reported] MDPI Electronics — Survey of Open-Source EDA Tools and PDKs (2026): https://www.mdpi.com/2079-9292/15/5/1048

## Open Questions

1. **Commit-binding for design checks:** EDA ties signoff evidence to an exact frozen artifact hash and invalidates it on any change. Should archwright's evidence ledger / baseline record the git commit of both spec and target, and invalidate baselines when either moves?
2. **Golden declaration per level:** EDA makes "which artifact is golden" explicit at every equivalence check (RTL golden vs netlist). Archwright's pass-up routes by confidence — is there value in an explicit per-seam golden declaration (e.g., pattern golden over spec, spec golden over code) to make disagreement resolution mechanical?
3. **Independent-checker principle:** LEC uses a different vendor's tool than synthesis. Archwright's Alloy compiler and checker are the same codebase — the vacuous-model incident (2026-07-17) is exactly the failure mode independent checking prevents. Is the non-vacuity probe sufficient, or does a second-opinion backend (e.g., Lean/Veil) earn its cost?
4. **Waiver review as a distinct ritual:** EDA reviews the waived 2% line-by-line at signoff. Archwright baselines suppress known debt — is there an equivalent "review the baseline, not just the delta" checkpoint at span digests?
5. **Composed-level signoff:** block→integration→chip signoff each have their own gates. Does the Q06 all-up reconciliation pass need its own check gate class (cross-area invariants) rather than reusing per-area checks?
6. **How much of the EDA split depends on the transformation being deterministic?** Synthesis is deterministic-enough for equivalence checking; agent-driven "resolution" is not. What is the LEC-equivalent for a creative transform — is it exactly archwright's provenance-chain + contrast-pair check, and is that strong enough?
7. **MDE's unfinished business:** the ACM SLR says formal early V&V placement in MBSE is still unstandardized. Worth tracking whether SysML v2's analysis-integration features change this.
