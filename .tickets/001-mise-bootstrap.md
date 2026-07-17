---
id: 001
title: Bootstrap mise on this machine
status: done
blocked_by: []
created: 2026-07-17
---

# Bootstrap mise on this machine

## Why

Rehydrating archwright's external deps (python, java, node/smcat, alloy jar) is currently a manual per-machine table in AGENTS.md, with Windows-specific hacks (MS Store python stubs, `/tmp/pyshim`, `PYTHONIOENCODING`). mise centralizes tools, env, and tasks in one committed `mise.toml`.

## What to build

- Check `mise --version`; if absent install via `winget install --id jdx.mise` (Windows) and activate for Git bash + PowerShell.
- Verify `mise doctor` reports a healthy install.

## Acceptance criteria

- [ ] `mise --version` succeeds in a fresh shell
- [ ] `mise doctor` shows no blocking problems
