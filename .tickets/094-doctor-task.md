---
id: "094"
title: "Add mise run doctor task (dependency and capability checker)"
status: open
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

- [ ] `mise run doctor` reports all dep categories (required/capability/optional)
- [ ] Missing required dep → exit 1 with clear install instructions
- [ ] Missing capability dep → exit 0 with warning + what's lost
- [ ] Suite header emits WARN lines for capability gaps before tests start
- [ ] Doctor output includes install commands for each missing item
