---
id: "102"
title: "Review migration finding: ticket tooling still points at crew-research"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Decision on the crew-research fallback recorded (and mise task updated if dropped)"
  - "Missing-resolution warnings backfilled or explicitly accepted"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: ticket tooling still points at crew-research

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

AGENTS.md §Tickets keeps crew-research's `.memory/specs/ticket-cli-spec.md` as the historical
contract authority. `mise.toml` `validate:tickets` (lines 45-50) falls back to
`PYTHONPATH=$HOME/code/crew-research/tools/tkt`; tkt is now the cargo build on PATH. 68 done tickets
lack a `## Resolution` section (every `tkt validate` warning). `docs/agents/PLAN.md` is the declared
status narrative and `tkt sync-plan` is not wired. Decide: drop the crew fallback, backfill or accept
the missing resolutions, and whether PLAN.md stays authoritative. Evidence: J5 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Decision on the crew-research fallback recorded (and mise task updated if dropped)
- [ ] Missing-resolution warnings backfilled or explicitly accepted
