# Pattern Schema (proposed)

The fields *are* the vocabulary for thinking at the design level, and they double as the compile record:

| Field | Purpose |
|---|---|
| `id` / `name` | the token to reason and talk in |
| `scale` | Premise / Loops&Systems / Verbs&Interactions / Feel&Finish |
| `context` / `above` | where it applies; larger patterns it completes (assume-guarantee up-link) |
| `desires` | attractive forces (typed, optionally weighted) |
| `constraints` | bounding forces, each tagged hard / soft |
| `tension` | the explicit conflict — the problem |
| `resolution` | the generative rule that balances them |
| `consequences` | new forces spawned (drive the next compile step; can pass up) |
| `hands_down` | sub-patterns **and** the architectural commitments implied — **the provenance link** |
| `confidence` | ★★ / ★ / — ; gates AI autonomy and pass-up escalation |
| `evidence` | why we believe it: playtests, prior art, empirical grounding |

## Design Principles

- Every field has a job in either the design conversation or the compilation pipeline (preferably both).
- The schema is a *record format*, not a template — it describes what you capture, not what you generate.
- Forces stay first-class: `desires`, `constraints`, and `tension` are separate fields, not collapsed into a prose "problem statement."
- `hands_down` is the provenance link — it records what this pattern committed to downstream, making pass-up routing possible.
- `confidence` gates everything: AI autonomy (how much it can change without asking), pass-up escalation height, and visualization styling.

## Open Questions

- Should `desires` and `constraints` be typed with a sub-schema (name, weight, polarity, source)?
- Should `consequences` distinguish "intended consequence" from "discovered side-effect"?
- How does `evidence` evolve over time — append-only log, or latest-snapshot?
- Does `hands_down` need to distinguish "sub-patterns invoked" from "architectural commitments made"?

See [Spike S1 in the research plan](../.memory/research-plan.md) for the proposed validation exercise.
