---
id: "005"
title: "include: glob scoping for python-grep checks"
status: done
blocked_by: []
created: 2026-07-17
---

# `include:` glob scoping for python-grep checks

Field-driven (DemoAR run, lessons.md 2026-07-16 #5): a `tls-only` constraint matched
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

Merged with the concurrent session's independent implementation (same day, same ticket id):

- Path-glob form added: a glob containing `/` matches the project-relative POSIX path
  (bare globs match the file name, as here).
- Explicitly-named single-file targets are never filtered — avoids the GNU grep
  `--include` gotcha that false-passed `no-isdk-references` in the field.
- `include:` + `command:` is a loud tool error (declarative checks only).
- BONUS FIX folded in: comment stripping used to truncate lines at the first comment
  token, false-passing any pattern containing the token (`"http://` contains `//`) —
  DemoAR `tls-only` PASSed over two real plain-HTTP URLs. Replaced with positional
  matching (match counts iff it starts before the token). Fixture canaries:
  `no-shell-exec` (include filtering) + `endpoint-pinned` (positional comments).
- Combined suite baseline: 31/0/0 (fixture additions + feature tests).
