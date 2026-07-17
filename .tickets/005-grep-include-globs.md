---
id: 005
title: "include: glob scoping for python-grep checks"
status: done
blocked_by: []
created: 2026-07-17
---

# `include:` glob scoping for python-grep checks

Field-driven (ExposeAR run, lessons.md 2026-07-16 #5): a `tls-only` constraint matched
897 lines repo-wide because there is no way to scope a grep check to `*.cs`. The
check backend needs per-spec file scoping.

## What to build

- `check.include:` on grep-method specs — a glob (string) or list of globs matched
  against the file name (e.g. `"*.cs"`, `["*.ts", "*.tsx"]`).
- `_python_grep` filters candidate files by the glob(s) before matching.
- Documented in `tools/templates/spec-constraint.md` and the derive skill's
  check-method guidance.

## Acceptance criteria

- [x] Spec with `include: "*.gd"` only matches `.gd` files (verified: `.md` decoy not matched)
- [x] List form works (`["*.gd", "*.tscn"]`)
- [x] No `include:` = current behavior (all text files) — suite stays 22/0/0
- [x] Suite gains a feature assertion

Resolution (2026-07-17): implemented in `_python_grep`/`_check_grep`; suite section
"Check-tool feature tests" asserts include-scoping; template + derive skill updated.
