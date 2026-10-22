---
id: "099"
title: "Review migration finding: shipped skills assume the crew-research target-project layout"
status: open
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Supported target layout(s) decided and recorded"
  - "Skills and steering updated (or explicitly kept) to match; fixture suite green"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: shipped skills assume the crew-research target-project layout

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

The shipped skills read and write a **target project's** crew-research layout:
`skills/archwright-survey/SKILL.md:77-81,134`, `archwright-audit:45,168`,
`archwright-forces:161,168`, `archwright-tensions:66`, `archwright-derive:37`, and
`steering/archwright-conventions.md:58,184`. Targets adopted into grey-matter now keep
`GLOSSARY.md`, `docs/adr/`, `docs/agents/{specs,grill}/`, so survey would miss those sources and
forces/tensions would write working scaffolding into a `.memory/` that no longer exists. Decide:
read both layouts, switch the default, or stay crew-shaped. Suggested check: a survey dry run on an
adopted target. Evidence: J2 and "Relocation hazard" in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Supported target layout(s) decided and recorded
- [ ] Skills and steering updated (or explicitly kept) to match; fixture suite green
