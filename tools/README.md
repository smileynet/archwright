# tools/

Mechanical servants for the archwright methodology (the skills are the system;
these are deterministic operations). **Authoritative usage, flags, and exit
codes: [AGENTS.md §Commands](../AGENTS.md#commands)** — this file is a map,
not a second contract. Output-interpretation contracts live with each tool's
owning skill (AGENTS.md §Tool→skill ownership).

| File | One-liner |
|------|-----------|
| `archwright-validate.py` | Schema + link validation for patterns/specs/forces/discovery artifacts (incl. conservation, ticket 026) |
| `archwright-check.py` | Check dispatcher: static (grep/script), behavior (Alloy), trace replay, probe; baseline + evidence ledger + code_state |
| `archwright-compile-alloy.py` | Behavior spec YAML → Alloy 6 model (also the debug path for surprising counterexamples) |
| `archwright-check-compile.mjs` | Intent patterns → check blocks |
| `archwright-forces-gen.py` | Force inventory YAML → `design/forces/*.md` (mechanical projection) |
| `archwright-import-woz.py` | wizard_of_oz `woz-session/v1` JSON → `design/discovery/woz/` artifact (interpretation is skill work) |
| `archwright_common.py` | Shared spec-parsing helpers — imported module, not a CLI |
| `run-fixture-tests.sh` | The repo's regression net over `tests/fixtures/` (count: AGENTS.md test row — single source) |
| `deploy-skills.sh` | Sync skills/steering/references to agent tools (`--tool kiro\|claude\|codex\|agy`) |
| `*-schema.yaml`, `trace-schema.ts` | Pinned contracts: pattern, spec, contract, check-output (CK-03), trace shapes |
| `templates/` | Document templates for patterns, each spec kind, and discovery artifacts |
| `domains/` | Domain overlays (game/web/general): scales, predicates, discovery frameworks + `detect.yaml` |
| `stacks/` | Stack adapters (per-language mechanical components) + `REGISTRY.yaml` (status computed by the suite) |
