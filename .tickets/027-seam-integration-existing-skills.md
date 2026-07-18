---
id: 027
title: "Seam integration: make pipeline skills discovery-aware"
status: done
blocked_by: [020]
---

# Seam integration in existing skills

## Context

ADR 0011 defines the discovery→verification seam, but no pipeline skill consumes it yet. Ticket 024 covers steering/AGENTS/audit-scope; this ticket covers the pipeline skills themselves. Must land BEFORE the field run (023) so downstream phases consume what the field run produces.

## What to build (one focused edit per skill)

| Skill | Update |
|---|---|
| archwright-survey | Source scan gains `design/discovery/` (approved ledger decisions = pre-resolved inputs; artifact gaps = model TODOs); orientation report notes discovery artifacts found |
| archwright-forces | Sources list gains discovery ledgers — `origin: user` decisions + behavioral evidence rank high on the evidence scale |
| archwright-resolve | Seam contract explicit: approved discovery decisions arrive as pre-resolved tensions via the existing batched-confirmation path, citing `D{NNN}` entries |
| archwright-model | Before modeling from scratch, consume `hands-to` model seeds + compiled artifact-gap TODOs from discovery artifacts |
| archwright-formalize | Evidence sections accept `D{NNN}` ledger citations (required for Q3 design-system graduation) |
| archwright-passup | One line: conservation violations route to "re-run the transform" — the transform was unfaithful, not the design wrong |

## Acceptance criteria

- [ ] Each skill above edited; "Does NOT" boundaries unchanged
- [ ] No skill documents unshipped tooling (conservation rule interpretation lands with 026, not here)
- [ ] deploy-skills run for non-kiro targets noted (kiro is symlinked)

Context: ADR 0011; grill Q4/Q6; spec `.memory/specs/discovery-track.md`.
