---
id: 035
title: "Add reflection template and GDScript trace instrumentation to stacks/"
status: done
blocked_by: []
---

# Add reflection template and move GDScript trace instrumentation

Two template additions that follow upstream's structural precedents.

## 1. Reflection template → tools/templates/reflection.md

A new template for reflection documents (used by archwright-derive Step 1b).
Place in `tools/templates/` alongside existing templates.

## 2. GDScript trace instrumentation → tools/stacks/gdscript/

Our local branch had `tools/templates/trace-instrument-gdscript.md`. Upstream
established `tools/stacks/gdscript/` as the home for GDScript stack-specific
content (ADR 0008, Extension Protocol). Move it there as
`tools/stacks/gdscript/trace-instrument.md`.

## Conformance notes

- Upstream's `tools/stacks/gdscript/conformance/README.md` describes the
  expected layout: `trace_emitter/`, `check-patterns/`, `conformance/`
- The trace instrumentation template is guidance for users, not an adapter
  itself — place at root of `gdscript/` (not in a subdirectory)
- Update `tools/stacks/REGISTRY.yaml` if needed (check if trace_emitter for
  gdscript should be listed as pending)

## Acceptance criteria

- [ ] `tools/templates/reflection.md` exists with correct template structure
- [ ] `tools/stacks/gdscript/trace-instrument.md` exists (moved from templates)
- [ ] No `tools/templates/trace-instrument-gdscript.md` (wrong location)
- [ ] REGISTRY.yaml consistent (gdscript entries present as pending)
