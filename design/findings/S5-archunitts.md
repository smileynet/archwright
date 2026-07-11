# Spike S5 Findings: ArchUnitTS Evaluation

**Date:** 2026-07-10
**Tool tested:** ArchUnitTS v2.3.3 (npm: `archunit`)
**Project tested:** oci-vercel (TypeScript, node:test runner)
**Constraints tested:** provider-abstraction, process-isolation (cycles), layer-direction

---

## Key Finding

ArchUnitTS **works and is expressive enough** for archwright dependency specs. It validated all 5 test rules correctly (all passed — the architecture is clean). The fluent API is readable and maps naturally to archwright constraint language.

However, it's **not clearly better** than the existing `scripts/check-architecture.mjs` custom script already in the project, and it has TypeScript compatibility issues (`esModuleInterop` requirement).

## Results

| Test | Result | Time |
|------|--------|------|
| control-plane must not depend on adapters | ✅ PASS | 4069ms (cold) |
| brokers.ts must not depend on adapters | ✅ PASS | 35ms |
| MCP layer must not depend on adapters | ✅ PASS | 29ms |
| adapters have no circular dependencies | ✅ PASS | 34ms |
| application layer must not depend on hosted-adapters | ✅ PASS | 28ms |
| **Total (5 rules)** | **5/5 pass** | **~5.8s** |

## Comparison: ArchUnitTS vs Existing Custom Script vs Semgrep

| Aspect | ArchUnitTS | check-architecture.mjs | semgrep |
|--------|-----------|----------------------|---------|
| Performance | ~4s cold + ~30ms/rule | ~4s total | <5s |
| Expressiveness | High (fluent API) | High (custom code) | Medium (AST patterns) |
| Dependency checks | ✅ Native (files/folders) | ✅ Custom import parsing | ⚠️ Import patterns only |
| Cycle detection | ✅ Built-in | ✅ Custom DFS | ❌ Not supported |
| Metrics (LCOM, coupling) | ✅ Rich | ❌ Not included | ❌ Not supported |
| Semantic patterns (catch blocks) | ❌ No | ❌ No | ✅ AST matching |
| TypeScript compat | ⚠️ Needs esModuleInterop | ✅ No issues | N/A |
| Reports (HTML, Mermaid) | ✅ Built-in | ❌ Text only | ❌ JSON only |
| Empty test detection | ✅ Fails by default | ❌ Manual | ❌ Manual |
| Install footprint | 78 packages | 0 (custom script) | Already installed |

## API Quality

The ArchUnitTS fluent API maps cleanly to archwright constraint language:

```typescript
// archwright: "control plane must not import OCI adapters"
projectFiles()
  .inFolder("src")
  .withName("control-plane.ts")
  .shouldNot()
  .dependOnFiles()
  .inFolder("src/adapters");
```

This is arguably more readable than the equivalent grep check. The `shouldNot().dependOnFiles().inFolder()` chain reads like English.

## Issues Encountered

1. **TypeScript compatibility:** ArchUnitTS requires `esModuleInterop` in tsconfig. This project doesn't use it. Workaround: run via `tsx` which is lenient. Not ideal for CI integration.
2. **Cold start:** First rule takes ~4s to build the dependency graph. Subsequent rules are fast (~30ms). Acceptable for CI but noticeable in dev.
3. **No semantic patterns:** Can't express "no silent catch blocks" or "no plaintext passwords in object literals" — that's semgrep's territory.

## Decision

**CONDITIONAL ADOPT** — ArchUnitTS adds value for:
- **Cycle detection** (built-in, no custom code needed)
- **Metrics** (LCOM, coupling factor — useful for design health monitoring)
- **Reports** (HTML dashboards, Mermaid dependency graphs)
- **Readable dependency rules** (fluent API better than grep for complex constraints)

But it **does NOT replace** semgrep (which catches semantic/structural patterns) or the existing custom script (which already works and has no dependencies).

**Recommendation:** Adopt for projects that:
1. Don't already have a custom architecture checker
2. Want metrics and reports beyond pass/fail
3. Use `esModuleInterop` in their tsconfig (or can add it)

For oci-vercel specifically: **skip** — the existing `check-architecture.mjs` already does what's needed, and semgrep covers the semantic patterns ArchUnitTS can't.
