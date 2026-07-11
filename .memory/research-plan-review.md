# Research Plan: archwright-review Skill

**Created:** 2026-07-10
**Goal:** Design and validate a code review skill that checks implementation alignment against archwright design artifacts (model, specs, experiences).
**Outcome:** A working `archwright-review` skill with at least two complementary checking mechanisms (static + semantic).

---

## Spikes

### S1: Semgrep for Architectural Constraints
**Status:** ✅ Complete
**Priority:** P0 (do first)
**Effort:** 1 session
**Question:** Can semgrep rules express archwright constraint specs with higher precision than grep?

**Findings:**
- semgrep v1.131.0 works well against TypeScript
- 5 rules written covering 4 constraint specs
- 129 findings produced (3 rules triggered, 2 rules = 0 findings = passing)
- **provider-abstraction:** 0 findings → constraint HOLDS (control-plane doesn't import adapters) ✅
- **explicit-opt-in-missing:** 0 findings → couldn't validate (pattern too specific for the code style used)
- **fail-closed-silent-catch:** 3 findings → real drift! Silent catch blocks in OCI adapter return defaults instead of throwing
- **secret-redaction-record:** 8 findings → password field in object literals (legitimate in adapters passing to OCI, but flags boundary awareness)
- **secret-redaction-log:** 118 findings → too broad (regex "binding" matches legitimate uses)

**Assessment:**
- Semgrep catches structural violations grep cannot (AST-aware catch blocks, object literal fields)
- Rules need tuning: the "log" rule needs tighter metavariable matching
- The fail-closed findings are genuine design-alignment issues the grep check missed
- **Decision: ADOPT** — semgrep as `check.method: semgrep` in archwright specs

**Rule quality:**
| Rule | Precision | Recall | Verdict |
|------|-----------|--------|---------|
| provider-abstraction | High | N/A (no violations) | Keep |
| secret-redaction-record | Medium (FP from adapters) | Unknown | Tune exclusions |
| secret-redaction-log | Low (too broad) | High | Rewrite with tighter patterns |
| fail-closed-silent-catch | High (3 real findings) | Medium | Keep, expand |
| explicit-opt-in-missing | N/A (didn't trigger) | Unknown | Needs redesign |

---

### S2: AI-Assisted Semantic Review Protocol
**Status:** ✅ Complete
**Priority:** P0 (do second)
**Effort:** 1 session (faster than expected)
**Question:** What prompting protocol produces consistent, actionable design-alignment findings?

**Findings:**
- Protocol validated: spec + invariants + source file → structured YAML findings
- 3 real drift findings with 0 false positives in test run
- Correctly distinguished structural patterns from intent violations (better than semgrep)
- Output format (YAML with line citations) is parseable and trackable
- Key rule: "only flag stated invariants" prevents hallucinated rules
- Complementary to semgrep: semgrep = CI gate, AI review = periodic design audit

**Decision: ADOPT** — prompt template and output format validated. Build skill.

---

### S3: Trace Validation Feasibility
**Status:** 🔲 Not started
**Priority:** P1 (do third)
**Effort:** 2-3 sessions
**Question:** Can we validate runtime behavior against behavior spec FSMs using JSON traces?

**Method:**
1. Define trace format: `[{state, event, data?, timestamp}]`
2. Instrument one spec (ball-possession or deployment-lifecycle) in test suite
3. Write a trace validator that walks traces against YAML behavior spec
4. Run against existing tests — does it detect spec/implementation mismatches?

**Key references:**
- Cirstea et al. 2024: "Validating Traces of Distributed Programs Against TLA+" (arxiv:2404.16075)
- MongoDB repl-trace-checker (github.com/mongodb-labs/repl-trace-checker)
- XState @xstate/test model-based testing

**Success criteria:**
- Validator catches at least one real mismatch between spec and implementation
- Trace format is minimal (< 5 fields per event)
- Instrumentation cost < 10 lines per spec'd state machine

**Outputs:** Trace schema, validator tool, instrumentation guide, feasibility decision

---

### S4: Spec-to-Check Compilation
**Status:** 🔲 Not started
**Priority:** P2 (do fourth)
**Effort:** 1-2 sessions
**Question:** Can constraint spec intents compile to executable checks automatically?

**Method:**
1. Catalog the intent patterns across all written specs (single-writer, no-import, never-logs, no-mutation)
2. Define a `check_intent` DSL mapping intent → check method + parameters
3. Write a compiler and test on 12 existing specs
4. Measure: does it reproduce hand-written checks?

**Success criteria:**
- Handles top 5 intent patterns without manual intervention
- Generated checks match hand-written for 10/12 specs
- Eliminates the "wrong target path" failure mode

**Outputs:** Intent pattern catalog, compiler prototype, accuracy assessment

---

### S5: ArchUnitTS Evaluation
**Status:** 🔲 Not started
**Priority:** P3 (optional)
**Effort:** 1 session
**Question:** Does ArchUnitTS add value over existing import-graph checking?

**Method:**
1. Install ArchUnitTS in oci-vercel
2. Express provider-abstraction as ArchUnitTS test
3. Compare with existing check-architecture.mjs

**Success criteria:**
- More expressive or more maintainable than existing script
- Handles TypeScript path resolution correctly

**Outputs:** Comparison assessment, adopt/skip decision

---

## Execution Order

```
S1 (semgrep) → S2 (AI protocol) → S3 (trace validation) → S4 (compilation) → S5 (ArchUnitTS)
     ↓                  ↓                    ↓
  CI-able checks    Skill design      Behavioral verification
```

## Decision Gates

After S1 + S2:
- If semgrep provides >80% of static checking value: adopt as default `check.method`
- If AI review protocol is consistent: draft `archwright-review` skill

After S3:
- If trace validation feasible: add `check.trace` execution to `archwright-check`
- If infeasible: document why, keep as future (requires language-specific instrumentation)

## References

- Cirstea et al. (2024) — TLA+ trace validation: arxiv.org/abs/2404.16075
- BitsAI-CR (2025) — Two-stage LLM code review: arxiv.org/html/2501.15134v1
- ArchUnitTS — github.com/LukasNiessen/ArchUnitTS
- ts-arch — github.com/ts-arch/ts-arch
- Tianpan (2026) — LLM reviewer drift: tianpan.co/blog/2026-05-13-ai-code-review-drift
- MongoDB repl-trace-checker — github.com/mongodb-labs/repl-trace-checker
- Semgrep custom rules — docs.semgrep.dev/writing-rules/rule-syntax
