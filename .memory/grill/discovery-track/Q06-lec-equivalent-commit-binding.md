# Q6: LEC-equivalent for agent transforms; commit-binding of seam evidence

**Status:** Decided 2026-07-18
**Decision:** 6a — two layers: golden-corpus conformance (process) + **conservation check** (instance). 6b — commit-binding deferred to its own ticket (018).

## Question

EDA re-proves every synthesis output equivalent to golden RTL via an independent tool (LEC). What's the analog for non-deterministic agent transforms (WoZ session → model seed, wireframes → model, pattern → specs)? And does seam evidence get EDA-style commit-binding?

## Research

- Semantic equivalence checking of agent transforms is impossible (non-deterministic, creative). What LEC actually guarantees decomposes into: nothing invented, nothing lost — both checkable WITHOUT understanding the transform, given citations.
- EDA independent-checker principle: the verifier must not share the transformer's reasoning. A citation-graph walk (same machinery as `--links`) satisfies this.
- Archwright precedent: the Alloy vacuous-model incident (2026-07-17) is exactly the failure class LEC prevents — checks passed because the transform silently produced empty output. Conservation's "nothing lost" direction would have caught it.

## Decision Detail — 6a: Conservation Check

| Layer | Guards | Mechanism |
|---|---|---|
| Golden-corpus conformance (Extension Protocol — already policy) | The transform process | Fixture suite incl. violating scenario |
| **Conservation check (new)** | Each instance | Mechanical citation-graph check |

Conservation, bidirectional:
1. **Nothing invented** — every output element cites a source (`D{NNN}`, wireframe id, pattern id); orphan outputs flagged.
2. **Nothing lost** — every active input decision is consumed by an output element or explicitly listed as deferred/unconsumed; unaccounted inputs flagged.

Seam artifacts carry citations by construction (the ledger format provides ids for free). The check becomes a validator rule for seam artifacts.

## Decision Detail — 6b: Commit-Binding

Deferred to ticket 018. It's a verification-track concern (applies to ALL check evidence, not discovery-specific), touches check-output schema + evidence ledger. EDA precedent noted (signoff bound to frozen commit hash; change invalidates evidence). Nothing in the discovery track blocks on it.

## Implications

- T2/T4: seam artifact templates require citation fields.
- Validator (T-follow-on): conservation rule for `design/discovery/` artifacts — new check instance, flows through Extension Protocol with its own violating fixture.
- Ticket 018 created for commit-binding.
