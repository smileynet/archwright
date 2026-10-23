---
id: "103"
title: "Review migration finding: sanitization map home and pre-existing denylist hits"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Home for the alias map decided and the AGENTS.md/mise.toml wording updated"
  - "sanitize-check hits aliased or explicitly accepted"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: sanitization map home and pre-existing denylist hits

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

AGENTS.md (Key Constraints) and `mise.toml:170` said the real-name to alias map is held in recall,
which is retired. `mise run sanitize-check` (machine-local `.sanitization-denylist`) already FAILs
at baseline: 53 hit lines across 14 files (12 tickets in 051-076, `steering/archwright-conventions.md`,
`tools/report/derive.py`); names are not reproduced here. Decide where the alias map lives now, and
whether to alias the hits in the current tree. Any history purge is the owner's call, outside
adoption. Evidence: J6, H2 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

**Update 2026-10-22 (public-tree scrub):** the current-tree hits were aliased (sanitize-check
passes). The real-to-alias map now lives in a machine-local, gitignored `.sanitization-aliases`
file beside `.sanitization-denylist` at the repo root (format: `real ==> alias`, one per line).
Remaining decisions: confirm that home (or move both files), update the AGENTS.md/mise.toml
wording that still says "recall", and whether to purge history.

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [x] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Home for the alias map decided and the AGENTS.md/mise.toml wording updated
- [x] sanitize-check hits aliased or explicitly accepted

## History purge (2026-10-23)

- Finding confirmed: `sanitize-check` failed at baseline as described; both real target-project
  names are now aliased in the current tree (sanitize-check passes).
- Owner decided to purge history: file contents, commit messages, and one fixture path rewritten
  and force-pushed; a fresh mirror clone of the remote shows 0 denylist hits.

Still open: confirm the alias-map home (machine-local `.sanitization-aliases` beside
`.sanitization-denylist`) and update the AGENTS.md Key Constraints line and `mise.toml:170`, which
still say "recall". Close once that wording lands.
