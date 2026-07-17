# TypeScript Stack Adapters

All adapters `pending` — see `../REGISTRY.yaml` for reasons and history.
The trace emitter is scheduled: C10 (DynamoRush run) builds it as the first
Extension Protocol adapter with measured cost.

Layout when built (Extension Protocol rule 4 — conformance at birth):

```
typescript/
  trace_emitter/       # TS module emitting trace events per tools/trace-schema.ts
                       #   (lives HERE; target projects get thin emit calls only)
  check-patterns/      # Reusable ast-grep patterns for TS idioms
  conformance/         # Golden corpus: scenario source + expected output, one pair per capability
    <scenario>.ts      #   input source
    <scenario>.expected.json   # expected trace/match output
```

The corpus MUST include at least one violating scenario that produces FAIL —
a checker proven only on passing cases may be vacuous (conventions, Extension
Protocol rule 4).

An adapter reaches ★ when its conformance corpus passes locally; ★★ when the corpus
is wired into `tools/run-fixture-tests.sh` and measured cost (lines, runtime) is
recorded in the registry row. Status is computed by the suite, never hand-declared.
