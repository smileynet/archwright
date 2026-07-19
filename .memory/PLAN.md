# PLAN: Live Design Checking for Fieldball-Coach-Platform

> **STATUS: Phases 0–4 COMPLETE (2026-07-16); Phase 5 (polyglot check tooling) shipped except the parked tail — DoD-5 chain (CK-03→04→05→09→10), CK-21, all of Phase 5b (CK-06/07/08 + R32 baseline/fingerprints), CK-17/18 (skill invocation contract + repair-loop convergence), CK-19 (changed-only scoping), and the ADR-0009 evidence ledger (ticket 017) are DONE (fixture-suite-verified); CK-01/02 descoped to validate.py. Open remainder: CK-11–16 (ast-grep/SARIF — parked awaiting a field driver per Extension Protocol).**
> **Phase 6 (Discovery Track) OPEN (2026-07-18): ADR 0011 accepted via grill (6 Qs, `.memory/grill/discovery-track/`); spec `.memory/specs/discovery-track.md`; tickets 019–022, 024–028 DONE (026 conservation-check + 025 woz-export consumer + 028 lifecycle examples `examples/{planned,partial,complete}` shipped 2026-07-19). Remaining: 023 (field run — operator-driven) only. Ticket 018 (commit-binding of check evidence — verification-track) DONE 2026-07-19: code_state in check --json + evidence events, soft-decay staleness ratified as ADR 0009 amendment. Target: the operator's game project (not FBC — first non-FBC phase).**
> Loose ends: T7 trace emitter → converted to an Extension Protocol pending-registry row `gdscript.trace_emitter` (grill Q5, audit ticket C11 — the "~20 lines" claim becomes measured data on first real build); R18/S15 → C5, folded into C10's TileRush reconciliation pass (grill Q7). Phase 5 reconciled with the audit plan 2026-07-16 (absorbs B4/C1/C2) and re-reconciled 2026-07-17 (grill: CK-01/02 descoped to validate.py, CK-21 added, passup skill consumes CK-03 output — see the spec's "Grill reconciliation" section).

**Goal:** Archwright checks FBC's `design/` artifacts against real implementation code. Violations surface at commit time (static) and test time (trace). The correction loop (violation → spec → pattern → force) works in practice.

**Target project:** `~/code/fieldball-coach-platform`
**Status:** Phases 0–4 complete; live design checking operational against fieldball-coach-platform. Phase 5 pending.

---

## Task Graph

```
Phase 0: Foundation ✅
├── C1  Commit design/ in FBC
├── T1  Make tools PATH-accessible (mise.toml)
├── U2  Add assurance field to check-results schema
└── U3  Add abstraction_notes to spec-schema.yaml

Phase 1: Static Layer ✅ (depends on Phase 0)
├── T5  Constraint spec check extraction
├── T3  archwright-check --static batch mode
├── T4  Structured JSON output
└── S13 Wire pre-commit hook, prove violations blocked

Phase 2: Trace Layer Design ✅ (depends on Phase 0)
├── U1  Finalize trace JSON schema
├── U4  Add check block to behavior spec schema
├── R20 Trace validation algorithm
└── R18 Growth rules derivation → U5

Phase 3: Trace Layer Implementation ✅ (depends on Phase 2)
├── T7  GDScript trace emitter (~20 lines)
├── T6  Build archwright-check --trace
└── S14 Conformance test for ball-state-lifecycle

Phase 4: Integration ✅ (depends on Phases 1 + 3)
├── U5  Growth rules in spec check.trace.scope fields
├── S15 Selective re-checking via affected algorithm
└── CI  Wire trace + static into unified gate

Phase 5: Polyglot + Agent-Native Check Tool (depends on Phase 4)
├── 5a: Foundation
│   ├── CK-01  Spec YAML schema validation
│   ├── CK-02  Link resolution check
│   ├── CK-03  Structured JSON output contract (MCP-compatible)
│   └── CK-04  Exit code contract
├── 5b: Static Checks + Baseline (CRITICAL PATH)
│   ├── R32   Research: violation fingerprinting
│   ├── CK-05  Grep backend (ripgrep subprocess)
│   ├── CK-06  target_status: pending handling
│   ├── CK-07  Baseline file implementation
│   ├── CK-08  Baseline ratchet enforcement
│   ├── CK-09  Provenance in violation output
│   └── CK-10  Contrast pair generation
├── 5c: ast-grep + GDScript (parallel after S20)
│   ├── S20   Spike: ast-grep + tree-sitter-gdscript on Windows
│   ├── CK-12  Compile tree-sitter-gdscript grammar
│   ├── CK-11  ast-grep backend
│   └── CK-13  GDScript pattern library
├── 5d: SARIF Output (parallel)
│   ├── R31   Research: minimum viable SARIF for GitHub
│   ├── CK-14  SARIF output mode
│   ├── CK-15  GitHub Actions workflow template
│   └── CK-16  Fingerprinting for SARIF dedup
└── 5e: Agent Interface (after 5b)
    ├── CK-17  Update archwright-check skill
    ├── CK-18  remaining_delta convergence tracking
    └── CK-19  Scope selection from git diff
```

### Dependency Graph

```
C1 ──┬── T1 ── T5 ── T3 ── T4 ── S13
     │
     ├── U2
     ├── U3
     │
     └── U1 ── U4 ── R20 ── T6 ──┬── S14
                                   │
              R18 ── U5 ───────────┴── S15
```

### Parallel Tracks

- Phase 1 (static) and Phase 2 (trace design) can run in parallel after Phase 0.
- S9 (Alloy abstraction quality) is independent — run any time as exploration.

---

## Phases

### Phase 0: Foundation (1 hour)

| ID | Task | Spec | Status |
|----|------|------|--------|
| C1 | Commit `design/` directory in FBC | [drift-gate](specs/drift-gate.md) | Ready (design/ exists, validated) |
| T1 | Add archwright tools/ to PATH via mise.toml | [drift-gate](specs/drift-gate.md) | ✅ Done |
| U2 | Add `assurance` field to result schema | [check-results](specs/check-results.md) | ✅ Done (in tool output) |
| U3 | Add `abstraction_notes` to spec-schema.yaml | [check-results](specs/check-results.md) | ✅ Done |

### Phase 1: Static Layer Live (2 hours)

| ID | Task | Spec | Status |
|----|------|------|--------|
| T5 | Constraint spec → grep extraction | [static-check-batch](specs/static-check-batch.md) | ✅ Done (existing tool already does this) |
| T3 | `archwright-check --static` batch mode | [static-check-batch](specs/static-check-batch.md) | ✅ Done |
| T4 | Structured JSON output (all tools) | [check-results](specs/check-results.md) | ✅ Done (trace mode outputs JSON) |
| S13 | Pre-commit hook blocks violations | [drift-gate](specs/drift-gate.md) | ✅ PROVEN |

**Milestone:** Constraint specs block bad commits in FBC.

### Phase 2: Trace Layer Design (2 hours)

| ID | Task | Spec | Status |
|----|------|------|--------|
| U1 | Finalize trace JSON schema | [trace-schema](specs/trace-schema.md) | ✅ Done |
| U4 | Add `check` block to behavior spec schema | [trace-schema](specs/trace-schema.md) | ✅ Done |
| R20 | Trace validation algorithm (pseudocode done) | [trace-schema](specs/trace-schema.md) | ✅ Done (implemented) |
| R18 | Growth rules derivation | [growth-rules](specs/growth-rules.md) | Drafted |

**Milestone:** We know exactly how trace validation works and which checks fire on which changes.

### Phase 3: Trace Layer Implementation (3 hours)

| ID | Task | Spec | Status |
|----|------|------|--------|
| T7 | GDScript trace emitter | [conformance-test](specs/conformance-test.md) | Not started (spec ready) |
| T6 | Build `archwright-check --trace` | [trace-validator](specs/trace-validator.md) | ✅ Done |
| S14 | Conformance test: ball-state-lifecycle | [conformance-test](specs/conformance-test.md) | ✅ PROVEN (tool validates traces, catches violations with provenance) |

**Milestone:** Behavior specs checked against real execution. Violations detected with provenance.

### Phase 4: Integration (1 hour)

| ID | Task | Spec | Status |
|----|------|------|--------|
| U5 | Add `scope` to behavior specs | [growth-rules](specs/growth-rules.md) | ✅ Done (existing check.target fields suffice) |
| S15 | Selective re-checking works | [growth-rules](specs/growth-rules.md) | Deferred (not needed until check time exceeds 5s) |
| CI | Unified gate (static + trace) | [drift-gate](specs/drift-gate.md) | ✅ Done (pre-commit hook, static layer) |

**Milestone:** Full live test operational. Selective re-checking keeps it fast.

### Phase 5: Polyglot + Agent-Native Check Tool (8-12 hours across sub-phases)

| ID | Task | Spec | Status |
|----|------|------|--------|
| CK-01 | Spec YAML schema validation | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Descoped → validate.py (done) |
| CK-02 | Link resolution check | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Descoped → validate.py `--links` (done) |
| CK-03 | Structured JSON output (MCP-compatible) | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (audit close 2026-07-18; trace mode via ticket 016) |
| CK-04 | Exit code contract | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (0/1/2, suite-verified) |
| R32 | Research: violation fingerprinting | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (2026-07-18) — `aw/v1` scheme recommended, [research-r32-fingerprinting.md](research-r32-fingerprinting.md); CK-07 unblocked (one HITL policy question at pickup: ★★ vs baseline) |
| CK-05 | Grep backend (ripgrep) | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (python grep w/ include globs — tickets 005/006) |
| CK-06 | target_status: pending handling | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (2026-07-18) — distinct `pending` status, disjoint coverage bucket, reason in skips[]; 3 suite checks |
| CK-07 | Baseline file implementation | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (2026-07-18) — `.archwright-baseline.json` w/ aw/v1 fingerprints; suppression = warning + baselined flag; ★★ keeps escalate; behavior/trace never suppressed (defaults ratified via proceed) |
| CK-08 | Baseline ratchet enforcement | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (2026-07-18) — `--update-baseline` remove-only, refuses on errored runs and missing file; suite-verified |
| ADR-9 | Evidence ledger implementation (ticket 017) | [adr/0009](adr/0009-confidence-evidence-lifecycle.md) | Done (2026-07-18) — `.archwright-evidence.json` (activation by existence or `--evidence`); demotion/promotion candidates auto-appended (deduped, streaks, deeper-tier); trace events carry `fingerprints: []` (fog resolved — CK-07 scope cut upheld); ratification stays human; 11 suite checks |
| CK-09 | Provenance in violation output | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (from_pattern/from_force + suggested_route) |
| CK-10 | Contrast pair generation | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (expected/actual in every violation) |
| CK-21 | validate.py emits the CK-03 document (`--json`) | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (added at 2026-07-17 grill) |
| S20 | Spike: ast-grep + GDScript on Windows | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| CK-11 | ast-grep backend | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| CK-12 | Compile tree-sitter-gdscript | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| CK-13 | GDScript pattern library | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| R31 | Research: minimum viable SARIF | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| CK-14 | SARIF output mode | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| CK-15 | GitHub Actions workflow template | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| CK-16 | Fingerprinting for SARIF dedup | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| CK-17 | Update archwright-check skill | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (2026-07-18) — full invocation contract in the check skill (baseline flags, output-field interpretation, PENDING triage, compile-alloy debug aid); passup/derive/review updated alongside |
| CK-18 | remaining_delta convergence tracking | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (2026-07-18) — "Repair loop convergence" section in the check skill: converging/stagnant(3-strike escalate w/ trajectory + fingerprint diagnosis)/regressing(stop immediately); skill-level, no tool change |
| CK-19 | Scope selection from git diff | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (2026-07-18) — `--changed-only [--base <ref>]` (default HEAD): affected = spec changed or changed/untracked file under check.target; no-file-target specs always run; git failure = exit 2; scope reports specs_total/specs_unaffected; 4 suite checks |

**Critical path:** CK-01 → CK-03 → CK-05 → CK-07 → CK-17 → CK-19
**Milestone 5a (done):** spec validation + link integrity gate ship as `archwright-validate.py [--links]` — no `--structural` flag exists (CK-01/02 descoped to validate.py, grill 2026-07-17)
**Milestone 5b:** `archwright-check --static` with baseline runs on catalyst-mono (core value)
**Milestone 5c:** ast-grep parses GDScript (structural checks beyond regex)
**Milestone 5d:** SARIF output + GitHub Actions template (ecosystem integration)
**Milestone 5e:** Skill invokes tool in closed repair loop (agent-native)

---

## Outstanding Research

| ID | Question | Location | Status |
|----|----------|----------|--------|
| R20 | Trace validation algorithm | [trace-schema.md](specs/trace-schema.md) § Research: R20 | ✅ Done |
| R18 | Growth rules / change propagation | [growth-rules.md](specs/growth-rules.md) § Research: R18 | Drafted |
| R30 | ast-grep GDScript integration (Windows) | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| R31 | Minimum viable SARIF for GitHub | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Not started |
| R32 | Violation fingerprinting strategy | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Done (2026-07-18) — [research-r32-fingerprinting.md](research-r32-fingerprinting.md) |
| R33 | MCP tool exposure | [polyglot-check-tooling](specs/polyglot-check-tooling.md) | Deferred |

Both research topics are resolved to draft level. Implementation will validate or revise.

---

## Outstanding Spikes

| ID | Question | Location | Blocking? |
|----|----------|----------|-----------|
| S13 | Can static checks block commits? | [drift-gate.md](specs/drift-gate.md) | Yes (Phase 1 gate) |
| S14 | Does trace validation catch real violations? | [conformance-test.md](specs/conformance-test.md) | Yes (Phase 3 gate) |
| S15 | Does selective re-checking work? | [growth-rules.md](specs/growth-rules.md) | No (enhancement) |
| S9 | Does Alloy scale for FBC execution model? | [next-work-proposals.md](next-work-proposals.md) | No (model layer is design-time) |

---

## Spec Index

| Spec | Covers | Path |
|------|--------|------|
| trace-schema | U1, U4, R20 | [specs/trace-schema.md](specs/trace-schema.md) |
| trace-validator | T6 | [specs/trace-validator.md](specs/trace-validator.md) |
| static-check-batch | T3, T5 | [specs/static-check-batch.md](specs/static-check-batch.md) |
| check-results | U2, U3 | [specs/check-results.md](specs/check-results.md) |
| drift-gate | S13, T1, C1, C3 | [specs/drift-gate.md](specs/drift-gate.md) |
| conformance-test | S14, T7, C2 | [specs/conformance-test.md](specs/conformance-test.md) |
| growth-rules | U5, S15, R18 | [specs/growth-rules.md](specs/growth-rules.md) |
| polyglot-check-tooling | CK-01–CK-19, S20, R30–R33 | [specs/polyglot-check-tooling.md](specs/polyglot-check-tooling.md) |

---

## Deferred (not blocking live test)

| Item | Why | Priority |
|------|-----|----------|
| S9 Alloy abstraction quality | Model layer is design-time only | Medium (exploration) |
| S11 Lean theorem compilation | Future ★★ path | Low |
| S12 Mawhorter replication | Validates game predicates | Low |
| V1 CEGAR → pass-up mapping | Theoretical validation | Low |
| V3 Apalache practical test | Alternative backend | Low |
| V4 SARIF adoption | JSON sufficient for now | Low |
| V6 PBT shrinking → contrast pairs | Enhancement | Low |
| R15 Abstraction strategies | Only if model layer goes to CI | Low |
| R16 Runtime monitoring | Superseded by trace validation | Closed |
| R17 Lean feasibility | Future | Low |
| R19 Context assembly formula | Enhancement after live test | Medium |

---

## Definition of Done

1. `git commit` in FBC with a constraint violation → **blocked by pre-commit hook**
2. `mise run test` in FBC with a behavior violation → **conformance test fails, reports spec/invariant/position**
3. Violation report includes **provenance** (pattern → force → invariant)
4. Fix the violation → both static and trace checks pass
5. Total check time <10s for typical commits
6. Adding a new language (not GDScript) requires only ~20 lines of trace emitter code

---

## Three-Layer Architecture

```
Layer 1: STATIC (at commit time via pre-commit hook)
├── Constraint specs → grep/ast-grep checks
├── Dependency specs → import graph analysis
└── Tool: archwright-check --static

Layer 2: TRACE (at test time via gdUnit4)
├── Behavior specs → JSON trace validation
├── Tests exercise code, emit traces
└── Tool: archwright-check --trace

Layer 3: MODEL (at design time, human-triggered)
├── Behavior specs → Alloy counterexample search
├── Finds design flaws before code exists
└── Tool: archwright-check <spec.yaml> (behavior specs dispatch to Alloy by default — there is no --model flag)
```

Each layer catches different bugs. Each has different portability costs:
- Layer 1: tree-sitter grammar per language (exists for most)
- Layer 2: ~20 lines of trace emitter per language
- Layer 3: Zero (Alloy/Lean are language-agnostic)

---

## Prior Art

| Source | What we take | Citation |
|--------|-------------|----------|
| TLA+ trace validation | JSON trace protocol, replay algorithm | Cirstea et al. 2024 (arXiv:2404.16075) |
| MongoDB conformance checking | Test generation from specs, lessons on state mapping | VLDB 2020 (arXiv:2006.00915) |
| Pact architecture | Thin-adapter pattern for multi-language | docs.pact.io |
| proptest-lockstep | Pure model vs real system comparison | lib.rs/crates/proptest-lockstep (2025) |
| Nx affected | Git diff → affected projects algorithm | nx.dev |
| SGE (Grabowski 2026) | Growth rules, context assembly formula | .scratch/research/spec-growth-engine.md |
| MonPoly | Online MFOTL monitoring for data-rich events | ETH Zurich (zisc.ethz.ch) |
| Copilot/RTLola | Stream-based monitoring, language-agnostic design | NASA, CISPA/Saarland |

---

## Phase 6: Discovery Track (ADR 0011) — OPEN 2026-07-18

Authoritative detail: `.memory/specs/discovery-track.md` (tasks T1–T8) + tickets 019–026. Decisions: ADR 0011 + `.memory/grill/discovery-track/`.

```
Phase 6: Discovery Track
├── 019 T1 facilitation-stance import (wizard_of_oz patterns)   [DONE 2026-07-18]
├── 020 T2 decision-ledger template (seam contract)             [DONE 2026-07-18]
├── 021 T3 overlay discovery: sections (game/web/general)       [DONE 2026-07-18]
├── 022 T4 archwright-discover-ui skill + templates             [DONE 2026-07-18]
├── 023 T5 field run: operator's game project                   (022) [open — operator-driven]
├── 024 T6 docs sync: steering/AGENTS/audit scope               [DONE 2026-07-18]
├── 025 T7b woz-export consumer (exporter T7a in wizard_of_oz)  [DONE 2026-07-19 — archwright-import-woz.py + archwright-woz-import skill; aesthetic→experience mapping; conformance in suite]
├── 026 T8 conservation-check validator rule + discovery schema [DONE 2026-07-19 — suite green, discover-ui §6.5 pending-note removed]
└── 027 seam integration: pipeline skills discovery-aware       [DONE 2026-07-18]
```

Cross-repo: T7a exporter ticketed in `~/code/wizard_of_oz/.tickets/001`. Independent: ticket 018 (commit-binding, verification track); ticket 028 (sanitized example projects across the lifecycle spectrum — fixtures + browsable user docs, added 2026-07-19).
