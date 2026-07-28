---
id: "073"
title: "Report: per-project vocabulary override for domain events"
status: open
blocked_by: []
priority: low
---

# Report: per-project vocabulary override

## Problem

Domain-specific events (like lacrosse-bosse's `play_changed`, `ready_pressed`) fall back to crude humanization (underscores→spaces). The vocabulary system supports overrides (`--vocabulary` flag) but there's no documented pattern for domain projects to provide their own event vocabulary.

## What to build

1. Document the vocabulary override pattern: `design/vocabulary.yaml` in the target project
2. Override merges with (not replaces) the base vocabulary
3. Generate a "missing vocabulary" report: events that fell back to humanization
4. `mise run report` in the target project auto-discovers `design/vocabulary.yaml`
5. Lacrosse-bosse: create a vocabulary override with plain-language event labels

## Acceptance criteria

- [ ] Target project can provide `design/vocabulary.yaml` with event overrides
- [ ] Overrides merge with base vocabulary (base terms preserved)
- [ ] Missing events reported at generation time (warning, not error)
- [ ] Lacrosse-bosse vocabulary file maps key events to plain language
- [ ] Report with override shows custom labels instead of humanized fallbacks
