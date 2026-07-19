# ADR-0012: Tier 3 Tool Rewrites (compile-alloy, check-compile)

**Date:** 2026-07-13
**Status:** Planned (after Tier 1+2 hardening)
**Context:** Codex review of all archwright tools identified 20 issues in two prototype tools.

## Context

`archwright-compile-alloy` and `archwright-check-compile` were built as proof-of-concept spikes (S3 and S4). They validated:
- Alloy can find counterexamples in 94ms (compile-alloy spike)
- Intent patterns can mechanically produce check blocks (check-compile spike)

Both are non-functional for production use. They are not in the critical path — `archwright-check` handles all current verification. The prototypes exist to prove feasibility, not to ship.

## Decision

Rewrite both tools **after** Tier 1+2 hardening is complete and validated. Do not incrementally patch — the tools need ground-up rewrites to address their combined 20 issues.

## Scope

### archwright-compile-alloy (rewrite)

**When:** When a spec has an invariant that structural checks can't verify AND trace testing can't exhaustively cover. The trigger is an invariant about *all possible paths* (ordering, interleaving, concurrent events) — not just observed paths. If state machines stay small enough that well-chosen trace scenarios cover the space, this rewrite can be deferred indefinitely.

**Example trigger:** "No matter what sequence of concurrent events occurs, the ball is never held by two slots simultaneously" — an interleaving property that traces can't exhaustively test but Alloy can check in bounded scope.

**Not a trigger:** Simple FSM properties verifiable by structural checks (grep/semgrep) or trace validation of observed paths.

**Issues to address:**
1. Actually translate invariants (not tautological placeholders)
2. Handle `on:` → boolean True YAML key (like archwright-check does)
3. Translate guards to Alloy predicates (not comments)
4. Handle all transition formats (string targets, lists, guarded alternatives)
5. Support bool/string context variables (not just int/enum)
6. Validate initial state against declared states
7. Normalize identifiers safely (reserved words, digits, collisions)

**Approach:** Rewrite as Python (consistent with archwright-check). Use the existing `check_trace` FSM walker as the authoritative spec parser — it already handles all formats. Compile from the parsed representation. Only justified when trace validation is provably insufficient for the invariant in question.

**Preferred backend: UPPAAL** (timed automata model checker)

UPPAAL is a better fit than Alloy for behavior spec verification:
- Automata are the native primitive — behavior specs map directly (no relational encoding)
- Properties: `A[] not(violation)`, `E<> goal`, `p --> q` map directly to archwright invariants
- Exhaustive within finite state space (no bounded-scope worries for 2-10 state machines)
- Diagnostic traces (execution paths to violations) — more actionable than Alloy's static instances
- CLI tool `verifyta` integrates easily into archwright-check
- Compilation: spec YAML → UPPAAL `.xml` is a direct FSM→automaton mapping

Retain Alloy for structural/relational specs (data contracts, dependency rules, composition invariants) if those ever need formal checking beyond grep/semgrep.

**Licensing:** UPPAAL is free for academic/non-commercial use. Commercial use requires license from veriaal.dk. Fallback: clean-room BFS/DFS exhaustive reachability checker (~100 lines Python) handles archwright's current 2-10 state machines without UPPAAL's optimizations.

**Spike (when triggered):** Compile `step-advancement.yaml` → UPPAAL `.xml`, run `verifyta` with invariants as properties. Compare effort/time/diagnostics against Alloy spike S3. Acceptance: <100 lines compile code, no manual editing, <1s verification, path-based diagnostics.

### archwright-check-compile (rewrite)

**When:** When there are enough intent patterns in use that manual check-block authoring is a bottleneck (likely after 20+ specs).

**Issues to address:**
1. Actually parse the input YAML file
2. Fix YAML output escaping for generated patterns
3. Align `exclude` field with archwright-check (now supported)
4. Use `grep -E` (now the default) in generated check blocks
5. Add semgrep intent patterns (for AST-level constraints)
6. Generate valid, runnable check blocks (not just examples)

**Approach:** Rewrite as Python. Input: YAML file with `intents:` array. Output: YAML check blocks ready to paste into specs. Validate generated output against archwright-check before presenting.

## Constraints

- Do not rewrite until Tier 1+2 hardening is validated on LBP
- Mark both tools clearly as prototypes in AGENTS.md and README (done in 6c9b69c)
- Add header comments to both tool files noting prototype status
- Neither tool should be referenced in CI or pre-commit hooks until rewritten
- compile-alloy rewrite is not justified by ★★ confidence alone — structural checks and trace validation are sufficient for simple FSMs. Only rewrite when an invariant requires all-paths verification (interleaving, concurrency)
- check-compile rewrite is not justified by having specs — the agent produces check blocks directly. Only rewrite when manual authoring friction is the actual bottleneck

## Consequences

- Users who need Alloy checking must manually edit the generated scaffolding
- Users who need intent compilation must author check blocks by hand (or ask the agent)
- Both tools remain available for interactive exploration/prototyping
- The agent (archwright-derive skill) can produce check blocks directly without needing check-compile
