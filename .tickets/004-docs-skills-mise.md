---
id: 004
title: Docs + skills reference mise as primary rehydration path
status: done
blocked_by: [003]
created: 2026-07-17
---

# Docs + skills reference mise as primary rehydration path

## What to build

- AGENTS.md: "Dependency Rehydration" section becomes mise-first ("install mise → `mise install` → `mise run rehydrate-alloy`"), keep the manual table as fallback for machines without mise. Commands table gains `mise run <task>` forms.
- `skills/archwright-check/SKILL.md` Backend Prerequisites: mention mise path first.
- `skills/archwright-model/SKILL.md` + `skills/archwright-diagram/SKILL.md`: renderer rehydration references mise where applicable.
- Run `tools/deploy-skills.sh` after skill edits (HANDOFF task 6).

## Acceptance criteria

- [x] AGENTS.md documents mise bootstrap + fallback
- [x] Skill files updated and deployed (verify deployed copy contains the change)
- [x] Committed + pushed
