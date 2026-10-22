---
date: 2026-08-01
topic: PBT + Contract Alloy verification architecture
status: ratified
participants: operator
---

# Grill: PBT Interface, Contract Invariants, PBT Output Mode

Three decisions settling the architecture for tickets 091 (PBT from behavior specs) and 092 (Alloy for contract specs).

## Q1: PBT Interface Design → Hybrid (Option D)

**Decision:** User provides a `step(event, context)` function. PBT generates event sequences, calls `step` for each, reads state via trace emitter output.

**Rationale:**
- Works across all system shapes (game engine, web service, CLI)
- Reuses existing trace emitter infrastructure
- `step` is typically 3-10 lines — minimal user burden
- Clean separation: PBT owns generation, user owns application, emitter owns observation
- Produces a "PBT adapter" pattern for `tools/stacks/<lang>/pbt_harness/`

**Rejected:**
- B (direct calls) — too coupled to specific API shapes; doesn't work for systems without a testable interface
- C (signal-tap only) — can't drive the system without a command channel; observation without action isn't PBT

## Q2: Contract Spec Invariant Syntax → Both sections (Option C)

**Decision:** Contract specs get `structural_invariants:` for model-level truths (Alloy-checked) AND keep `check:` for code conformance (grep/semgrep). Both run in one `archwright-check` invocation.

**Rationale:**
- Different verification targets (model correctness vs code conformance) need different paths
- Parallels behavior spec pattern: `invariants:` = model truth, `check.trace:` = runtime
- Consistent vocabulary across spec kinds
- Extensible: future structural checkers consume `structural_invariants:`

**Rejected:**
- A (structural_invariants only) — loses the code-conformance check
- B (reuse check section) — conflates model truth and code truth; can't do both

## Q3: PBT Output Mode → Inline default + `--emit` (Option C)

**Decision:** `--pbt` runs inline by default (immediate feedback). `--pbt --emit <path>` additionally writes a portable test file for CI.

**Rationale:**
- Fast feedback loop is the core value (Hillel's insight: rapid cycle builds intuition)
- Evidence ledger integration (ADR 0009) requires inline execution
- Precedent: `--trace` runs inline; trace files are the portable artifact
- `--emit` satisfies CI/commit use case without burdening interactive flow

**Rejected:**
- A (file only) — breaks the feedback loop; extra generate→run→interpret step
- B (inline only) — no CI portability

## Implications for ticket 091

The PBT adapter shape:

```
tools/stacks/<lang>/pbt_harness/
  README.md              # how to write a step function for this language
  template_step.py       # example step function (user copies + adapts)
  adapter.py             # reads spec YAML, generates Hypothesis RuleBasedStateMachine
  conformance/           # golden corpus proving the adapter works
```

User workflow:
1. Write a behavior spec (already done)
2. Write a `step(event, context)` function (3-10 lines, maps events to system calls)
3. Run `archwright-check --pbt <spec.yaml> --step <step_module>`
4. PBT generates random valid event sequences, applies via step, checks invariants via emitter
5. Failures shrink to minimal counterexample

## Implications for ticket 092

Contract spec schema addition:

```yaml
kind: contract
id: resource-access
schemas:
  Resource:
    fields:
      readable_by: [User]
      parent: Resource?
structural_invariants:
  - id: no-cycles
    predicate: "no r: Resource | r in r.^parent"
    confidence: "★★"
    from_model: report-actors
check:
  method: grep
  target: src/models/
  pattern: "parent.*=.*self"
  expect: absent
```

`archwright-check.py` dispatch: if `structural_invariants` present → compile to Alloy, check. If `check` present → grep/semgrep as before. Both in one run.
