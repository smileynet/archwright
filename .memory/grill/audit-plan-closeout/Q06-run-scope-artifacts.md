# Q06 — C10 run shape: scope and artifact placement (general policy)

**Status:** DECIDED — Operator policy, generalizes beyond C10
**Date:** 2026-07-17

## Question

How should the dynamodb-game-demo (DynamoRush) run be scoped, and where do design/ artifacts live?

## Research

DynamoRush: clean tree, GitFarm remote, 7 ADRs + 3 grills, no design/ yet, ~4.5K TS files, apps/+packages/ workspace layout (monorepo). Full-depth single-run survey would exceed subagent sizing guidance (>15 files → batching; this is 100×).

## Decision (operator policy — applies to ALL runs, not just C10)

1. **Scope by size:**
   - **Large projects / monorepos** (workspace layouts, multiple apps/packages, or source corpus far beyond survey sizing guidance): break into AREAS, run the full pipeline against each area, then an **all-up reconciliation pass** — dedupe forces across areas, surface cross-area tensions, unify models.
   - **Otherwise: default to full project / all areas in one run.** Area-scoping is the exception for scale, not the norm.
2. **Artifacts are live documents in the primary repo/branch space.** Committed branch-agnostically to the CURRENT project branch unless the user specifies otherwise. No special design branches by default.

## Application to C10

DynamoRush is a monorepo → area-partitioned: per-area pipeline runs (area inventory from survey; order-book matching engine is the most invariant-dense candidate per ADR 0002) followed by all-up reconciliation. Artifacts commit to the current branch. TS trace emitter lives in archwright `tools/stacks/typescript/` with conformance corpus; DynamoRush gets thin emit calls only.

## Implications

- Survey skill gains sizing guidance: monorepo/large detection → propose area partition + reconciliation pass in the intake outline
- "Reconciliation pass" is a new named concept (cross-area synthesis after per-area runs) — glossary entry added
- Conventions: artifact placement rule (current branch, live documents)
- C10 sequencing unchanged: after DoD-5 chain + Extension Protocol scaffolding
