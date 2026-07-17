---
id: 006
title: "Multi-target support for grep checks (list-valued target:)"
status: done
blocked_by: []
created: 2026-07-17
---

# Multi-target support for grep checks (list-valued `target:`)

Field-driven (ExposeAR run, lessons.md 2026-07-16 #5): specs in the field wrote
space-separated targets (`target: "a b c"`), which today errors as a single
nonexistent path. A spec legitimately constrains several roots at once.

## What to build

- `check.target:` accepts a YAML list of paths; each is resolved against the
  project root and grepped; matches are unioned.
- Any missing path in the list = tool error (loud, per fail-loud rule) naming
  the missing entry.
- Space-separated single-string targets stay an error (ambiguous with real
  paths containing spaces) — the error message now hints at the list form.
- Documented in `tools/templates/spec-constraint.md` and the derive skill.

## Acceptance criteria

- [x] `target: [client/src, project.godot]` greps both, unions matches
- [x] One missing entry in the list → status error naming it
- [x] Single-string behavior unchanged — suite stays 22/0/0
- [x] Suite gains a feature assertion

Resolution (2026-07-17): implemented in `_check_grep`; suite "Check-tool feature
tests" asserts union + loud-missing; template + derive skill updated.
