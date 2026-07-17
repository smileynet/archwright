# mise owns tools/env/tasks — and its Windows python has no python3

One-line: `mise install && mise run setup && mise run rehydrate-alloy` is the full rehydration path.

**Date:** 2026-07-17 · **Source:** mise adoption session

`[env]` sets `PYTHONIOENCODING` + `ARCHWRIGHT_ALLOY_JAR` automatically in-repo.
Gotchas: mise's Windows python ships only `python.exe` (bare `python3` hits the
MS Store stub even under `mise run` — scripts need a python3→python guard);
`cargo:`-backend tools deliberately excluded (rust toolchain too heavy for the
optional merman-cli renderer). On Linux, activate mise in BOTH zsh and bash
profiles — scripts and agent shells run bash.
