---
id: "098"
title: "Review migration finding: shipped steering self-references the old .memory/ layout"
status: done
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

- [x] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [x] Steering self-references resolve to the relocated paths, or the decision to keep them is recorded
- [x] Target-project `.memory/` mentions untouched unless 099 decides otherwise

## Resolution (2026-10-22)

done: steering self-references repointed to docs/agents/{audit,research,reflections}/ and docs/adr/ (770bd22)

### Verification
1. ✓ Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence — "Reproduced: grep -rn '\.memory' steering showed :33 (.memory/audit/pipeline-dryrun.md + .memory/adr/0007), :92 (.memory/research-*.md), :183 (.memory/reflections/global.md); all targets exist at docs/agents/audit/, docs/agents/research/, docs/agents/reflections/global.md, docs/adr/0007 -> confirmed"
2. ✓ Steering self-references resolve to the relocated paths, or the decision to keep them is recorded — "Repointed in 770bd22: :33 -> docs/agents/audit/pipeline-dryrun.md + docs/adr/0007-hitl-only-gates.md, :92 -> docs/agents/research/*.md, :185 -> docs/agents/reflections/global.md; validate --links PASS"
3. ✓ Target-project `.memory/` mentions untouched unless 099 decides otherwise — "Target-project mentions (:58,:184) changed only per 099's decision (read-new-then-legacy, write docs/agents/archwright/); no other .memory edits"
