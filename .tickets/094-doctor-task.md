---
id: "094"
title: "Add mise run doctor task (dependency and capability checker)"
status: done
blocked_by: ["093"]
---

# Add mise run doctor task

## Context

Fresh clones produce a "green" suite with silent SKIPs — the operator doesn't
know they're missing capabilities until they read the skip messages buried in
160 lines of output. There's no way to ask "am I ready?" without running the
full suite.

## What to build

1. `tools/doctor.py` — checks all required + optional deps and reports clearly:
   - Required: python, pyyaml (error if missing)
   - Capability: java, alloy6.jar, hypothesis, node (warn what's lost if missing)
   - Optional: semgrep, smcat, merman-cli (advisory only)
   - Reports versions where available
   - Exits 0 if all required present + no suite-affecting gaps
   - Exits 1 if required deps missing

2. `[tasks.doctor]` in mise.toml pointing to the script

3. Suite header warnings in `run-fixture-tests.sh` — 3 lines at the top that
   emit WARN for any capability gap before tests start (so gaps are visible
   without reading through all output)

## Acceptance criteria

- [x] `mise run doctor` reports all dep categories (required/capability/optional)
- [x] Missing required dep → exit 1 with clear install instructions
- [x] Missing capability dep → exit 0 with warning + what's lost
- [x] Suite header emits WARN lines for capability gaps before tests start
- [x] Doctor output includes install commands for each missing item

## Resolution (2026-08-08)

`tools/doctor.py` checks 10 deps across 3 tiers (required/capability/optional),
reports versions and install hints. `[tasks.doctor]` added to mise.toml.
Suite header in `run-fixture-tests.sh` emits WARN lines for java, alloy jar,
hypothesis, and node before any tests run — gaps are visible immediately.
