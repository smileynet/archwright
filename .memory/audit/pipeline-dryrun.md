# A3 — End-to-End Pipeline Dry Run (2026-07-16)

Target: `tests/fixtures/lacrosse-bosse` (7 code files, post-B7: 3 patterns + 7 specs). All 9 phases walked in compressed form — the fixture's artifacts stand in for phase outputs where they exist; friction recorded where the skill's demands and the artifacts diverge. Tool timings measured; agent-phase durations are approximate (compressed run).

## Per-Phase Log

| # | Phase | Output state | Friction found |
|---|-------|-------------|----------------|
| 1 | survey | Coverage map trivial (1 area/pattern each; all ✓ through specs). Step 1b auto-audit ran conceptually — fixture README now truthful post-B7 | Survey's coverage questions assume `.memory/grills`/ADR sources; fixture has none — "source quality assessment" (B3) would have flagged this upfront. Survey template has no row for **models** coverage despite model being "ALWAYS" |
| 2 | forces | Forces recoverable from patterns' Forces sections (6 forces, 3 desires) | Force IDs (`ball-always-somewhere`, `single-holder`, …) exist only as strings inside pattern/spec fields. **No force inventory artifact exists or is defined for `design/`** — `serves:` and `from_force:` reference IDs that resolve to nothing. `--links` passes because those fields aren't link-checked. Provenance chain has a hollow root |
| 3 | tensions | 3 tensions, all pre-resolved (fixture is a formalization case) | None — matches skill's "pre-resolved" path |
| 4 | resolve | HITL gate hit. Treated prior LBP decisions as the human's ratification; confirmation pass only | **Gate friction (C6 evidence):** for a 100%-pre-resolved project the mandatory stop adds a full turnaround with zero new decisions. Exactly the case C6's flow-through class targets — with the ★★-touching caveat |
| 5 | formalize | Patterns exist and validate | **Quality gates fail:** Evidence sections ≈17% of pattern body (gate: ≥70%). B7 patterns are minimal-viable for tooling, not gate-compliant. Also: gates live in steering, but `archwright-validate.py` checks none of them (no evidence-proportion, no serves-nonempty check) — gates are entirely honor-system |
| 6 | model | **Artifact gap:** no `design/models/` exists; conventions' target layout requires it. The behavior spec's statechart *is* the BallStateService machine, but actor boundaries/event flows/experience layer were never captured | Model is declared "ALWAYS — never skip," yet nothing downstream *requires* its artifact: derive ran fine (B7) without it. Mandate vs. enforcement mismatch |
| 7 | contract | Upstream's `ball-possession-events.yaml` present; validates; behavior spec `consumes` it ✓ | Contract spec is the ONLY one carrying `protects_experience`/`user_story`. Its `protects_experience: ball-always-somewhere` references the same hollow force/experience ID space as #2 |
| 8 | derive | 6 derived specs exist, validate, link-resolve | Derive demands `protects_experience` + `user_story` on ALL specs — 1/7 comply. Confirms **B2** (make flexible or lint-warn). Grep-method specs work; `check.command` variants (dependency specs) bypass target-existence validation |
| 9 | check | 16 pass / 0 fail / 1 skip; violation injection caught by both ★★ specs (B7-verified) | Behavior spec silently reduced to SKIP without Alloy jar — model-layer checking has never run on this fixture |

## Timing (measured)

| Operation | Wall time |
|-----------|-----------|
| Full fixture suite (16 checks) | **0.79s** |
| `--static` batch (6 specs) | 0.07s |
| `--trace` single | 0.04s |
| Alloy compile | 0.04s |

## Prior-Plan Definition of Done — Re-verification

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | Constraint violation blocks `git commit` in LBP | **EXTERNAL** | Proven in LBP (S13); not re-verifiable from this repo. In-repo equivalent proven: violation → exit 1 (B7) |
| 2 | Behavior violation fails conformance test | **EXTERNAL / PARTIAL** | Trace validation catches violations with position+valid_events (A1); no test-suite integration in this repo |
| 3 | Violation report includes provenance (pattern→force→invariant) | **PARTIAL — FAIL as stated** | invariant+pattern present; `from_force: null` (A1/F5); force IDs hollow anyway (phase 2 finding) |
| 4 | Fix violation → checks pass | **PASS** | B7 inject/revert: 14/2/1 → 16/0/1 |
| 5 | Check time <10s | **PASS** | 0.79s full suite |
| 6 | New language ≈ 20-line emitter | **FAIL / unproven** | No emitter exists → ticket C4 |

## Top Findings (ranked)

1. **Forces have no artifact.** The methodology's first-class citizens exist only as unlinked ID strings. Provenance routing (the product's core promise) terminates in nothing. → Proposed ticket **C8: define `design/forces/` (or forces.yaml) artifact + extend link validation to `serves:`/`from_force:`**.
2. **Quality gates are honor-system.** Formalize/derive gates (evidence ≥70%, protects_experience on all, serves nonempty) are checked by no tool; the fixture violates them while passing everything. → fold into Phase 5 CK-01 (structural validation) or B5.
3. **Model mandate lacks teeth + artifact.** "ALWAYS run model" but no `design/models/` requirement is enforced and derive doesn't need it. → C7 (spec-ownership decision) should also settle what model MUST produce.
4. **Resolve gate on pre-resolved projects is pure latency** — strongest concrete evidence yet for C6's flow-through classification.
5. DoD 3 (provenance) remains the biggest brief-vs-reality gap — already scoped in Phase 5 CK-09.
