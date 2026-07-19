# Q07 — C5 disposition + execution order

**Status:** DECIDED
**Date:** 2026-07-17

## Decision

**C5 folds into C10.** Its acceptance criterion ("one validated change-propagation walkthrough of the 6 growth rules, documented") carries over as a C10 deliverable, exercised during the TileRush reconciliation pass. Rationale: real change propagation beats synthetic fixture walks; growth rule 7 is now load-bearing for Q04's evidence design so it gets validated where it matters.

**Execution order confirmed:**

| # | Block | Est. | Depends | Closes |
|---|-------|------|---------|--------|
| 1 | Extension Protocol codification (findings + conventions + tools/stacks/ registry + Q06 policy + Does-NOT-Cover fix) | 3h | — | C4, DoD-6(T7) |
| 2 | DoD-5 chain: CK-03→04→05→09→10 + validate --json + spec amendments | 6h | — | DoD-5 tool side |
| 3 | archwright-passup skill + check narrowing | 2h | 2 | DoD-5 consumer |
| 4 | C3 ADR (evidence split); ledger impl deferred to CK-07 timeframe | 1h | 2 | C3 design |
| 5 | B10 tool-agnostic scrub | 2h | — (before 6) | B10 |
| 6 | C10: TileRush area-partitioned run + reconciliation + first TS emitter + C5 folded | 5h | 1,2,3 | C10, C5, B1-acceptance, C6-fog |
| 7 | Plan close: DoD re-verify, README refresh, archive | 30m | all | Plan DONE |

Blocks 1, 2, 5 mutually independent.
