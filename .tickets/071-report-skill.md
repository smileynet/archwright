---
id: "071"
title: "Skill: archwright-report — generation, consumption, vocabulary overrides"
status: open
blocked_by: []
priority: low
---

# Skill: archwright-report

## Problem

Report generation is currently documented ad-hoc in AGENTS.md's Commands table. There's no dedicated skill that owns the report workflow: when to generate, how to consume responses, how to override vocabulary for domain projects.

## What to build

1. `skills/archwright-report/SKILL.md` — trigger: "generate report", "run report", "check report"
2. Covers: generating a report (prerequisites: check --json output + design/ dir), consuming response files on next run, vocabulary override mechanism
3. Documents the `mise run report` task
4. Handles field cases: first run (no model → empty-project), partial model, full pipeline output
5. Update AGENTS.md tool→skill ownership table

## Acceptance criteria

- [ ] Skill file created and deployable
- [ ] Documents generate, consume-response, vocabulary-override workflows
- [ ] AGENTS.md updated with tool→skill ownership
- [ ] Skill triggers correctly on "generate report" / "run report"
