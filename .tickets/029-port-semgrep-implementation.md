---
id: "029"
title: "Port semgrep implementation into archwright-check.py"
status: done
blocked_by: []
---

# Port semgrep implementation into archwright-check.py

The upstream `_check_semgrep()` in `tools/archwright-check.py` is a placeholder
that returns "not yet implemented". Our local branch had a working implementation
in the bash-era `archwright-check` script. Port it into the Python stub.

## What to build

Replace the placeholder `_check_semgrep()` (line ~898) with a real implementation
that:

1. Reads `check.rule` (inline YAML) or `check.rules_file` (path to .yaml)
2. Reads `check.target` (directory or file to scan)
3. Reads `check.expect` (`absent` or `present`, default `absent`)
4. Writes inline rules to a tempfile when needed
5. Invokes `semgrep --json --no-git-ignore --config <rule> <target>`
6. Parses JSON output, maps findings to the result format
7. Returns pass/fail/skip/error in the same shape as `_check_grep()`

Graceful degradation: if semgrep is not installed, return status `skipped` with
a clear message (matches upstream's "optional tool" precedent — see AGENTS.md
Dependency Rehydration table).

## Conformance notes

- Follow the existing `_check_grep()` and `_check_script()` patterns for
  result shape (keys: invariant, status, confidence, assurance, message,
  evidence, fingerprints, from_pattern)
- Use `_include_match()` if filtering is needed
- Use `_first_pattern(check)` for provenance
- Respect the `_EVIDENCE_CAP` limit on evidence items
- Keep the function self-contained (no new module-level imports beyond what's
  already imported: subprocess, json, tempfile via local import, os, yaml)

## Acceptance criteria

- [x] `_check_semgrep()` no longer returns "not yet implemented"
- [x] Inline rule (check.rule as dict) works — writes temp file, invokes semgrep, cleans up
- [x] External rules_file (check.rules_file) works
- [x] expect: absent (default) fails when findings exist, passes when none
- [x] expect: present passes when findings exist, fails when none
- [x] Missing semgrep binary → status: skipped (not error)
- [x] Invalid rule / target not found → status: error with message
- [x] Evidence items include path:line:message, capped at _EVIDENCE_CAP
- [x] Suite green (no regressions in existing checks)
