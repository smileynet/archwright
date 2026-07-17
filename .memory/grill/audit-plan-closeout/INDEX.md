# Grill: Audit Plan Close-Out (C3 / C4 / C5 / C10 + DoD)

**Started:** 2026-07-16
**Scope:** Resolve the remaining design decisions in `/audit-plan.md` — confidence lifecycle (C3), trace emitter close-out (C4), growth rules validation (C5), web pipeline run (C10), and what "done" means for the plan (DoD items 5 and 6, Phase 5 sequencing).

## Questions

| # | Question | Status | Decision |
|---|----------|--------|----------|
| [Q01](Q01-dod5-ownership.md) | DoD-5 ownership: block on / amend / execute Phase 5 chain | DECIDED | C′ — execute CK-03→04→05→09→10 under the Phase 5 spec, this line of work as executor; DoD-5 stays literal |
| [Q02](Q02-passup-skill.md) | Where does correction routing (pass-up) live? | DECIDED | New skill `archwright-passup` (13th) — check stays verification-only; ★★ HITL gate gets an owner |
| [Q03](Q03-tool-topology.md) | One tool or two: CK-01/02 vs validate.py | DECIDED | A′ — two tools, single concern each; CK-01/02 → Small "validate --json" ticket |
| [Q04](Q04-evidence-storage.md) | Where does promotion/demotion evidence live? | DECIDED | Split by author: machine events → ledger (CK-07 family); ratifications → artifact (HITL) |
| [Q05](Q05-extension-protocol.md) | C4: prove/descope emitter → Extension Protocol | DECIDED | Codify protocol (findings + conventions, 6 research-backed rules); `tools/stacks/` registry; T7 → pending row; C10 builds first adapter |
| [Q06](Q06-run-scope-artifacts.md) | C10 run scope + artifact placement | DECIDED | Policy: large/monorepo → per-area runs + reconciliation pass; else full project. Artifacts = live docs on current branch |
| [Q07](Q07-ordering.md) | C5 disposition + execution order | DECIDED | C5 folds into C10; 7-block order confirmed |

**Session complete 2026-07-17.** All branches resolved. Fog and ADR dispositions recorded in audit-plan.md §Grill Outcomes.
