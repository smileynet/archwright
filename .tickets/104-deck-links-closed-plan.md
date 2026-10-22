---
id: "104"
title: "Review migration finding: binary deck, broken links, and root-level closed plan"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "LFS decision for the deck recorded"
  - "Both broken links repaired or removed; check-links shows 0 broken"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: binary deck, broken links, and root-level closed plan

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

Hygiene and stale pointers: `docs/presentation/Archwright_Brief.pptx` (822 KB) is tracked
without Git LFS (no `.gitattributes`). Two pre-existing broken links:
`skills/archwright-check/SKILL.md:33` → `../archwright-resolve/references/pass-up.md` (no such file
anywhere) and `docs/agents/PLAN.md:208` → never-committed `next-work-proposals.md`. `audit-plan.md`
(57 KB, CLOSED 2026-07-18) still sits at the repo root. Decide LFS for the deck (current tree only;
history rewrite is separate), repair or drop the two links, and whether `audit-plan.md` moves under
`docs/agents/`. Evidence: J7, H1 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] LFS decision for the deck recorded
- [ ] Both broken links repaired or removed; check-links shows 0 broken
