---
id: "058"
title: "check command subprocess: python3 resolves to MS Store stub on Windows"
status: done
blocked_by: []
priority: high
---

# check command subprocess: python3 resolves to MS Store stub on Windows

## Context

Spec check commands (method: script or grep with `command:`) containing
`python3 -c "..."` fail on Windows with exit 2 because the bash subprocess
spawned by `_find_bash()` in `archwright-check.py` resolves `python3` to the
Windows MS Store stub (`WindowsApps/python3`), not the mise-managed Python.

The `python3()` shell function alias defined in `run-fixture-tests.sh` is NOT
inherited by the check tool's subprocess — it only lives in the test script's
shell session. The check tool spawns a fresh `[bash, "-c", command]` process
that has no knowledge of the alias.

Affected specs: `allclear-discloses-gaps.md`, `violations-pin-to-diagram.md`
(any spec whose check.command uses `python3`).

Reproduced: 2026-07-27 on Windows 11, mise-managed Python (only `python.exe`
on PATH, no `python3.exe`).

## What to build

The check tool's command execution path must ensure `python3` resolves to a
working Python when running spec check commands. Options:

1. **Prepend a `python3` alias/shim** to the bash command: wrap the user's
   command in `python3() { python "$@"; }; <command>` when python3 isn't
   directly executable (detect once at startup)
2. **Use `sys.executable`** for Python-based commands: the check tool knows
   it's running under Python — pass its own interpreter path as an env var
   (e.g., `ARCHWRIGHT_PYTHON`) that spec commands can reference
3. **Spec convention**: document that commands should use `python` not
   `python3` on Windows — weakest option, breaks cross-platform specs

## Acceptance criteria

- [x] `archwright-check.py --static` on a spec with `command: python3 -c "..."` passes on Windows (mise-managed Python, no system python3)
- [x] Same spec still works on Linux/macOS where `python3` exists natively
- [x] Suite report-generator conformance tests (bundle constraints both-directions) pass on Windows

## Resolution (2026-10-21)

Added _python3_shim_prefix() to tools/check/conformance.py: detects once whether python3 actually runs; if not but python does, prepends a python3() bash function delegating to python, applied at both command-mode call sites (_check_grep, _check_script). Empty prefix on Linux/macOS so native platforms untouched. Mirrors the proven run-fixture-tests.sh guard.
