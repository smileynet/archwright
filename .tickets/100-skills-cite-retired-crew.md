---
id: "100"
title: "Review migration finding: shipped skills cite retired crew-research skills and a drifted subagent-reliability copy"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Owner of subagent-reliability decided; deploy-skills.sh matches"
  - "Each retired-skill citation repointed or removed"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: shipped skills cite retired crew-research skills and a drifted subagent-reliability copy

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

Shipped skills cite retired crew-research material: `archwright-resolve/SKILL.md:77`
(source-authority hierarchy), `:162` (`spec-driven-development`, now `wayfinder` + `to-spec`),
and `archwright-{audit:171,forces:234,survey:102}` (`subagent-reliability` steering).
`steering/subagent-reliability.md` ships an older, drifted copy of crew-research's
`subagent-reliability` (not byte-identical: crew's adds frontmatter and two failure modes), and
`~/.kiro/steering/subagent-reliability.md` on this machine is a plain file, not this repo's
symlink. Decide who owns that file (archwright, grey-matter, or drop it from deploy) and what each
skill cites instead. Evidence: J3, H4 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Owner of subagent-reliability decided; deploy-skills.sh matches
- [ ] Each retired-skill citation repointed or removed
