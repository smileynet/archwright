---
id: 002
title: mise.toml — tools, env, tasks for archwright
status: done
blocked_by: [001]
created: 2026-07-17
---

# mise.toml — tools, env, tasks for archwright

## What to build

`mise.toml` at repo root:

- `[tools]`: python 3.12, java (temurin-21), node 22, `npm:state-machine-cat`. NOTE: leave `cargo:merman-cli` out (rust toolchain too heavy for an optional renderer — keep manual). PyYAML via python postinstall or a setup task.
- `[env]`: `PYTHONIOENCODING = "utf-8"` (kills lessons.md #5), `ARCHWRIGHT_ALLOY_JAR = "{{config_root}}/.references/alloy6.jar"` (upstream 410623c added the env override).
- `[tasks]`: `validate`, `check-static`, `test` (fixture suite), `deploy-skills`, `rehydrate-alloy` (curl the v6.2.0 dist jar into `.references/`).
- Run `mise install` and verify each tool resolves inside the repo dir.

## Acceptance criteria

- [x] `mise install` completes
- [ ] `python3 --version` inside repo = mise python (not MS Store stub), incl. inside Git bash
- [x] `java -version` works inside repo
- [x] `echo $PYTHONIOENCODING` = utf-8 inside repo
- [x] `python3 -c "import yaml"` succeeds

## Notes

- Windows backend coverage is less battle-tested than Unix — if `npm:state-machine-cat` fails on Windows, drop to a documented manual install; do not block the ticket on it.

## Resolution notes (2026-07-17)

- All tools installed via `mise install`: python 3.12.13, temurin-21.0.11, node 22.23.1, smcat 15.0.6. `mise run setup` installed pyyaml 6.0.3.
- DEVIATION on the `python3` criterion: mise's Windows python ships only `python.exe` (no `python3` binary or shim), so bare `python3` still resolves to the MS Store stub. Handled at the consumer: `tools/run-fixture-tests.sh` now defines a `python3()` fallback to `python` when `python3` is broken. `mise exec -- python` is the canonical interpreter; AGENTS.md documents this.
- `[env]` verified in-repo: `PYTHONIOENCODING=utf-8`, `ARCHWRIGHT_ALLOY_JAR=<repo>/.references/alloy6.jar`.
