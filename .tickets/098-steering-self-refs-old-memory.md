---
id: "098"
title: "Review migration finding: shipped steering self-references the old .memory/ layout"
status: open
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Steering self-references resolve to the relocated paths, or the decision to keep them is recorded"
  - "Target-project `.memory/` mentions untouched unless 099 decides otherwise"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: shipped steering self-references the old .memory/ layout

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

`steering/archwright-conventions.md:33,92,183` cite archwright's own old paths
(`.memory/audit/pipeline-dryrun.md`, `.memory/research-*.md`, `.memory/reflections/global.md` "in
the archwright repo"). Those moved to `docs/agents/{audit,research,reflections}/`. Adoption doesn't
edit steering, and this file is live global steering through the kiro symlink. The derive skill's
matching line was repointed in the adoption commit (S3). Suggested: repoint the three lines the
same way; leave the target-project mentions at :58,184 (see 099). Evidence: J1, S3 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Steering self-references resolve to the relocated paths, or the decision to keep them is recorded
- [ ] Target-project `.memory/` mentions untouched unless 099 decides otherwise
