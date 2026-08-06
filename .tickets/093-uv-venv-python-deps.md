---
id: "093"
title: "Migrate Python deps to uv + _.python.venv (fix broken setup)"
status: open
blocked_by: []
priority: high
---

# Migrate Python deps to uv + _.python.venv

## Context

`mise run setup` is broken on machines with `require-virtualenv=1` in pip config
(the default for many developers). The `postinstall` approach doesn't work because
it runs at Python install time, before any venv exists. Today's workaround was
manual `PIP_REQUIRE_VIRTUALENV=0 mise exec -- pip install pyyaml`.

Research (2026-08-06, `.scratch/research/mise-python-venv.md` + `mise-uv-integration.md`)
confirms the correct pattern: `_.python.venv` for auto-created venvs + `uv pip install`
for deps (uv ignores pip config entirely, is 10-100x faster).

## What to build

Update `mise.toml`:

1. Add `uv = "latest"` to `[tools]`
2. Add `_.python.venv = { path = ".venv", create = true }` to `[env]`
3. Change `[tasks.setup]` to `uv pip install pyyaml hypothesis`
4. Add `.venv/` to `.gitignore`
5. Update AGENTS.md Dependency Rehydration section (setup now uses uv, respects venv)
6. Verify: fresh `mise install && mise run setup && mise run test` → 160/0/0

## Acceptance criteria

- [ ] `mise run setup` succeeds regardless of pip's `require-virtualenv` setting
- [ ] Python deps install into `.venv/` (not the global mise Python)
- [ ] `mise run test` passes (160/0/0 — suite green at current count)
- [ ] `.venv/` is gitignored
- [ ] AGENTS.md bootstrap instructions updated
- [ ] `hypothesis` installed by default (PBT tests no longer skip)
