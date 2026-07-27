---
id: "056"
title: "Report: stability section — run history, trust-earning, promotion suggestions"
status: open
blocked_by: ["053"]
priority: low
---

# Report: stability section

## Problem

The designed all-clear view (wf-all-clear) includes a STABILITY section showing:
- "rules holding N runs straight"
- "last failure [date]"
- "1 guideline has earned trust (12 straight passes) → consider making it a firm rule"

This provides temporal context — not just "is it passing now?" but "has it been stable?" The evidence ledger (ADR 0009) tracks this data already; the report just needs to surface it.

## What to build

1. Read the evidence ledger (`.archwright-evidence.json`) for pass/fail history per spec
2. Compute streak data: consecutive passes per rule, last failure date
3. Surface promotion candidates: rules at ★ confidence with N+ consecutive passes → suggest ★★
4. Render as a STABILITY section below "what isn't verified"

## Acceptance criteria

- [ ] Stability section shows when evidence ledger exists
- [ ] Consecutive-pass streak count per rule displayed
- [ ] Last failure date shown (or "never failed" for new rules)
- [ ] Promotion candidates highlighted with suggestion text
- [ ] Section absent when no evidence ledger exists (graceful degradation)
- [ ] Lacrosse-bosse report shows stability data after 2+ check runs
