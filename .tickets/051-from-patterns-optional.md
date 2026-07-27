---
id: "051"
title: "Make from_patterns optional when from_model is present"
status: open
blocked_by: []
priority: low
---

# Make from_patterns optional when from_model is present

## Context

During the lacrosse-bosse field run (2026-07-27), all constraint and contract specs derived directly from the model phase (discovery → model → contract/derive) without a formalize phase producing patterns first. Every spec required `from_patterns: []` to pass validation — an empty list that conveys no information.

The current validator requires `from_patterns` on all spec kinds. This is correct when the pipeline goes through formalize (patterns are the normal provenance). But the discovery track (ADR 0011) enables a faster path: discovery decisions can be pre-resolved by the user, flowing directly to model → contract → derive without formalization. In this case, `from_model` alone is sufficient provenance.

## What to build

Change the validator to accept specs with EITHER `from_patterns` OR `from_model` (at least one present), rather than requiring both:

- If `from_patterns` is present and non-empty: valid (normal path)
- If `from_model` is present: valid (discovery-direct path)
- If neither is present: FAIL (no provenance)
- If both are present: valid (fully traced)

This makes `from_patterns: []` unnecessary boilerplate on specs that derive from models without pattern intermediaries.

## Acceptance criteria

- [ ] Specs with `from_model` but no `from_patterns` pass validation
- [ ] Specs with `from_patterns` but no `from_model` still pass (backward compat)
- [ ] Specs with neither `from_model` nor `from_patterns` fail
- [ ] Existing fixture specs still pass (no regression)
- [ ] Suite green at current count
