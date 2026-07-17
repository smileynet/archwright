# Q03 — One tool or two: does the DoD-5 chain include CK-01/02?

**Status:** DECIDED — Option A′ (two tools; validate.py owns structural)
**Date:** 2026-07-17

## Question

Phase 5 success criterion 1 has `archwright-check --structural` doing spec schema + link validation — duplicating `archwright-validate.py` (just extended by C8/C9). Merge, duplicate, or split?

## Research

- validate.py today: 6 per-kind validators + force/model link indexes + warnings (C8/C9 investment).
- ADR 0007, conventions, AGENTS.md, fixture script, skills all cite validate.py — corrected by A2 this week; churn cost documented.
- Phase 5 spec line 11 self-warns that `--structural` is a breaking-rename hazard.
- Found: spec's "Design complete (.scratch/check-tool-design.md)" reference is DANGLING (scratch cleaned) — fix during spec amendment.

## Decision

**A′ — two tools, single concern each:**
- `archwright-validate.py` = "are design artifacts well-formed?" (pre-flight, no codebase, gates flow-through phases)
- `archwright-check.py` = "does implementation satisfy specs?" (needs target codebase)
- CK-01/02 drop from the DoD-5 critical path; replaced by Small ticket: validate.py gains `--json` conforming to CK-03's output schema
- Phase 5 success criterion 1 amended to cite validate.py; dangling design-doc ref fixed

## Implications

- DoD-5 chain confirmed: CK-03 → CK-04 → CK-05 → CK-09 → CK-10 (+ validate --json Small ticket + passup skill)
- No churn to ADR 0007 / conventions / skill references
- Same single-concern principle as Q02, applied at tool level
