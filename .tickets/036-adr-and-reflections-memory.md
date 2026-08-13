---
id: "036"
title: "Add ADR 0008 and reflections memory files"
status: done
blocked_by: []
---

# Add ADR 0008 (Tier 3 tool rewrites) and reflections memory files

Port the .memory/ additions from our local branch. These are new files with
no upstream conflict.

## What to build

### .memory/adr/0008-tier3-tool-rewrites.md

ADR documenting the decision to plan Tier 3 rewrites for compile-alloy and
check-compile — the criteria for when a rewrite is triggered (all-paths
invariants, not CI or confidence).

### .memory/reflections/global.md

Global reflections (R1–R10) captured from session history. Methodology-level
lessons that apply to all projects:
- Tool behavior pitfalls (grep -E for alternation, YAML boolean key trap)
- Spec authoring patterns (exclude field normalization, expect semantics)
- Check method conventions (semgrep for structure, grep for text)

### .memory/review-improvements-2026-07-11.md

LBP review improvement recommendations — historical record of the first full
archwright-review findings.

## Conformance notes

- ADR follows the format in existing `.memory/adr/` files
- Reflections follow whatever format we establish in the template (ticket 035)
- Review file is a historical record — place as-is

## Acceptance criteria

- [x] `.memory/adr/0008-tier3-tool-rewrites.md` exists with proper ADR format
- [x] `.memory/reflections/global.md` exists with R1–R10
- [x] `.memory/review-improvements-2026-07-11.md` exists
- [x] No conflicts with existing .memory/ content
