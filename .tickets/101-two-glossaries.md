---
id: "101"
title: "Review migration finding: two glossaries (GLOSSARY.md vs shipped docs/glossary.md)"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Source of truth for overlapping terms decided and recorded"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: two glossaries (GLOSSARY.md vs shipped docs/glossary.md)

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

Two glossaries now exist: `GLOSSARY.md` (ex `.memory/CONTEXT.md`, 49 terms, all confirmed
against code) and the shipped `docs/glossary.md` (deployed into
`archwright-survey/references/glossary.md`). About 18 terms appear in both; they agree today but
nothing keeps them in sync, and "the glossary" is ambiguous. Decide one source of truth and how the
other is derived, or record the split in both headers. Evidence: J4, C1 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md) and its glossary-verdicts.md.

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Source of truth for overlapping terms decided and recorded
