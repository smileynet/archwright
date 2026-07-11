# Spike S1 Findings: Semgrep for Architectural Constraints

**Date:** 2026-07-10
**Project tested:** oci-vercel (Oracle App Platform)
**Tool:** semgrep v1.131.0
**Specs covered:** provider-abstraction, secret-redaction, explicit-opt-in, fail-closed

---

## Key Finding

Semgrep catches **structural violations** that grep-based checks cannot express. The highest-value pattern is the **fail-closed silent-catch** rule — it detects catch blocks in adapters that return defaults instead of propagating errors. This is a genuine design-alignment issue (3 instances found in `src/adapters/oci-cli.ts`) that the existing grep check completely misses.

## What Semgrep Adds Over Grep

| Capability | grep | semgrep |
|-----------|------|---------|
| Text pattern matching | ✅ | ✅ |
| AST-aware (catch blocks, object literals) | ❌ | ✅ |
| Metavariable regex (match variable names) | ❌ | ✅ |
| "Pattern NOT inside this context" | ❌ | ✅ |
| Per-rule path filtering (include/exclude) | ❌ | ✅ |
| Structured JSON output for tooling | ❌ | ✅ |
| Language-aware (understands TypeScript syntax) | ❌ | ✅ |

## Results by Rule

| Rule | Findings | Precision | Verdict |
|------|----------|-----------|---------|
| `provider-abstraction` | 0 | N/A (constraint holds) | ✅ Keep — validates abstraction |
| `fail-closed-silent-catch` | 3 | High (all real drift) | ✅ Keep — grep can't express this |
| `secret-redaction-record` | 8 | Medium (FP from adapter internals) | Tune: exclude adapter-internal construction |
| `secret-redaction-log` | 118 | Low (regex "binding" too broad) | Rewrite: tighter metavariable matching |
| `explicit-opt-in-missing` | 0 | N/A (pattern didn't trigger) | Redesign: code doesn't match assumed structure |

## Real Violations Found

### 1. Silent catch in Container Instance status enrichment (line 594)
```typescript
try {
  const result = await this.cli.runJson(...);
  return { ...summary, ...result.data };
} catch {
  return summary;  // ← silently returns partial data
}
```
**Impact:** Operator gets incomplete instance data without knowing the status check failed. The runtime may look healthy when it isn't reachable.

### 2. Silent catch in Container Instance deletion (line 724)
**Impact:** Deletion failure silently succeeds — orphan resources accumulate.

### 3. Silent catch in route removal (line 1344)
**Impact:** Route cleanup failure is invisible — stale routes persist.

## Implications for archwright-check

1. Add `semgrep` as a `check.method` option alongside `grep` and `script`
2. When a constraint involves structural patterns (catch blocks, object shapes, import graphs), prefer semgrep
3. Store semgrep rules alongside specs (co-located in `design/specs/`) or in a shared ruleset
4. Consider: should `archwright-derive` automatically choose grep vs semgrep based on constraint type?

## Rule Authoring Guidance

**Good semgrep patterns for archwright:**
- "Never silently catch in this directory" (fail-closed)
- "Never put field X in object literals outside directory Y" (boundary enforcement)
- "Never import from Z in files matching pattern W" (provider abstraction)
- "Never log variables matching regex R" (redaction)

**Bad semgrep patterns (use grep instead):**
- Simple presence/absence of a string (grep is faster, simpler)
- Single-line patterns without structural context

## Decision

**ADOPT** — semgrep becomes the recommended `check.method` for constraint specs that involve:
- Structural patterns (try/catch, object literals, function signatures)
- Import/dependency rules (more precise than grep for path-qualified imports)
- Context-sensitive violations ("X is fine here, but not there")

Retain grep for simple presence/absence checks (fast, zero-dependency).
