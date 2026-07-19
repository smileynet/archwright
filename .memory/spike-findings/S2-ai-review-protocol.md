# Spike S2 Findings: AI-Assisted Semantic Review Protocol

**Date:** 2026-07-10
**Project tested:** oci-vercel (Oracle App Platform)
**Spec reviewed:** constraint:fail-closed
**File reviewed:** src/adapters/oci-cli.ts (~1400 lines)
**Method:** Subagent dispatch with structured prompt + YAML output format

---

## Key Finding

The AI review protocol produces **high-quality, specific, actionable findings** that complement semgrep. It correctly distinguishes between structural patterns that look like violations but aren't (readiness checks that *should* return fail status) and genuine silent-fallback drift.

## Protocol Quality Assessment

| Metric | Result | Notes |
|--------|--------|-------|
| Consistency | High | Structured YAML, cites specific lines |
| Precision | 3 drift / 0 false positive drift | All 3 are real design-alignment issues |
| Actionability | High | Each finding explains WHY it's a problem |
| Semantic judgment | Superior to semgrep | Correctly classified readiness-check catch as aligned |
| False positive rate | 0% (drift findings) | May vary with different specs |

## Findings Produced

| # | Line | Status | Issue |
|---|------|--------|-------|
| 1 | 259 | drift | `findResources` returns empty array when compartmentOcid missing — indistinguishable from "no resources" |
| 2 | 322 | drift | `resolveRuntimeNetworkTarget` silently falls back to stale URL after polling timeout |
| 3 | 370 | drift | `containerInstanceDetailsForRecovery` catches all errors, returns partial data with no signal |

All 3 are genuine design-alignment issues that could cause operator confusion.

## Semgrep vs AI Review Comparison

| Aspect | semgrep | AI Review |
|--------|---------|-----------|
| Speed | <5s | ~30s |
| Determinism | 100% | ~90% (same findings, ordering may vary) |
| CI-gateable | ✅ Yes | ⚠️ Not reliably (non-deterministic) |
| False positives | Medium (flagged readiness-check as violation) | Low (correctly judged intent) |
| Semantic depth | Shallow (AST patterns only) | Deep (understands design intent) |
| New finding discovery | Only what rules express | Finds unforeseen drift patterns |
| Cost | Free | Token cost per review |

**Conclusion:** They're complementary layers:
- **semgrep** = CI gate (fast, deterministic, catches structural patterns)
- **AI review** = periodic design audit (deep, nuanced, catches intent drift)

## Protocol Design Decisions (Validated)

1. **Review per-spec** (not per-file) — provides focused invariants to check against ✅
2. **YAML output format** — parseable, diff-able, trackable across reviews ✅
3. **"Only flag stated invariants" rule** — prevents hallucinated rules ✅
4. **Require specific line citations** — ensures findings are verifiable ✅
5. **Include user_story in prompt** — grounds the review in user impact ✅

## Protocol Improvements Needed

1. **Run 3x for stability** — compare findings across runs, keep only consistent ones
2. **Add "confidence" field** — the reviewer should self-rate how certain each finding is
3. **Cap file size** — large files (>500 lines) should be split into focused sections
4. **Include model context** — telling the reviewer which actor this file implements would improve reasoning

## Recommended Skill Shape

```
archwright-review:
  input: spec + source_files + model_context
  output: design/reviews/{spec-id}-{date}.yaml
  method: dispatch per-spec review, collect findings, deduplicate
  frequency: per-sprint or on-demand ("review X against specs")
  gate: NOT a CI gate — a periodic signal
```

## Decision

**ADOPT** — design the `archwright-review` skill using this protocol. The prompt template and output format are validated. Semgrep handles the CI gate; AI review handles the design audit.
