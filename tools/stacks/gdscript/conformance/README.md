# GDScript Stack Adapters

All adapters `pending` — see `../REGISTRY.yaml` for reasons and history.

Layout when built (Extension Protocol rule 4 — conformance at birth):

```
gdscript/
  trace_emitter/       # GDScript autoload emitting trace events per tools/trace-schema.ts
  check-patterns/      # Reusable ast-grep/grep patterns for Godot idioms
  conformance/         # Golden corpus: scenario source + expected output, one pair per capability
    <scenario>.gd      #   input source
    <scenario>.expected.json   # expected trace/match output
```

An adapter reaches ★ when its conformance corpus passes locally; ★★ when the corpus
is wired into `tools/run-fixture-tests.sh` and measured cost (lines, runtime) is
recorded in the registry row. Status is computed by the suite, never hand-declared.
