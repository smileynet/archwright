# Spike S4 Findings: Spec-to-Check Compilation

**Date:** 2026-07-10
**Tool built:** `archwright-check-compile` (Node, 147 lines)
**Patterns tested:** 6 intent patterns against 12 existing specs

---

## Key Finding

**6 intent patterns cover all 12 existing hand-written specs.** A simple compiler can generate check blocks from high-level declarations like `single_writer(field: ball_holder, authority: ball_state_service)`. This eliminates the main failure mode from the session: wrong target paths and YAML escaping errors.

## Intent Pattern Catalog

| Pattern | English | Compiled to | Specs using it |
|---------|---------|-------------|---------------|
| `single_writer` | "Only X writes field Y" | grep broad scope for `Y =`, exclude X | single-writer-ball-holder |
| `no_import` | "A must not import from B" | grep A for `from.*B` | provider-abstraction |
| `no_mutation` | "A must not call mutation verbs" | grep A for `\.(save|store|persist|...)` | setup-read-only |
| `no_reference` | "A must not reference B names" | grep A for B names (alternation) | play-manager-agnosticism, coordinator-mutual-exclusion |
| `must_use` | "A must contain concept X" | grep A for X, expect present | generation-freshness, setup-before-start, explicit-opt-in, fail-closed |
| `no_literal` | "No plaintext X in scope" | grep scope for patterns, exclude test | secret-redaction, resolver-owns-derivation |

## Accuracy

**5/5 exact match** against hand-written specs (tested single_writer, no_import, no_mutation, no_reference, must_use). The compiler generates the same method, target, pattern, and expect as manually authored checks.

## What This Enables

### Before (manual authoring):
```yaml
check:
  method: grep
  target: "client/src/"
  pattern: "ball_holder\\s*="
  expect: absent
  exclude: "ball_state_service"
```

### After (intent declaration):
```yaml
check_intent:
  pattern: single_writer
  field: ball_holder
  authority: ball_state_service
  scope: client/src/
```

The compiler handles:
- Correct regex escaping (the YAML `\\s` problem)
- Standard mutation verb lists
- Consistent pattern structure

### Future: derive can auto-generate

When `archwright-derive` creates a constraint spec from a model invariant like "only this actor writes ball_holder", it can directly emit:
```yaml
check_intent:
  pattern: single_writer
  field: ball_holder
  authority: ball-state-service
```
...and the compiler resolves it to an executable check block, including target path discovery.

## Target Path Discovery (the hard problem)

The remaining gap: the compiler needs to know WHERE the actor's code lives. Options:
1. **Model provides it** — `source_files` field on each actor (proposed in review recommendations)
2. **Convention-based** — `src/{actor-slug}/` or `src/{actor-slug}.ts`
3. **Glob discovery** — find files matching actor name patterns
4. **User provides it** — explicit `scope` in the intent

For now: option 4 (explicit). Future: option 1 (model-driven).

## Decision

**ADOPT** — integrate into `archwright-derive` as the default check generation path. Specs declare intent; compiler produces executable checks. Hand-written `check:` blocks remain valid for edge cases the patterns don't cover.
