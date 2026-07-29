---
id: "078"
title: "Report: behavior-detail 'WHAT THIS PROTECTS' shows all experiences instead of state-specific"
status: done
blocked_by: []
priority: medium
---

# Report: WHAT THIS PROTECTS is not state-specific

## Finding

F06: Every behavior-detail card shows the same full list of ALL experiences (avg 381 chars of identical text). The wireframe (wf-behavior-detail) designs this section to show only the specific product experience that THIS state protects.

## Root cause

`build_model_view` in `derive.py` assigns `protects: [e["id"] for e in model.get("experiences") or []]` — it dumps every experience ID for every state. The join should be: experience → protected_by → spec → actor → state.

## What to fix

1. In `build_model_view`, filter `protects` per state: only include experiences whose `protected_by[].spec` references a spec that applies to this actor
2. When no specific mapping exists, fall back to actor-level experiences (better than all)
3. If a state has no relevant experiences, omit the "WHAT THIS PROTECTS" section (don't show empty)

## Acceptance criteria

- [ ] Each behavior-detail card shows ONLY experiences relevant to its actor (or state)
- [ ] Different actors' cards show different experience text
- [ ] States with no relevant experience omit the section
- [ ] Verified via Playwright: avg content length varies between cards
