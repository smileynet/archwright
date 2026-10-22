---
id: "099"
title: "Review migration finding: shipped skills assume the crew-research target-project layout"
status: done
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

- [x] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [x] Supported target layout(s) decided and recorded
- [x] Skills and steering updated (or explicitly kept) to match; fixture suite green

## Resolution (2026-10-22)

done: skills read both layouts (grey-matter first) and write working files to docs/agents/archwright/ (770bd22); no tool hardcoded a target .memory path

### Verification
1. ✓ Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence — "Reproduced: grep -rn '\.memory' skills steering confirmed survey:77-81,134; audit:45,168; forces:161,168; tensions:66; derive:37; steering:58,184 (+ forces:121, resolve:120 bare CONTEXT.md); adopted target wizard_of_oz has GLOSSARY.md + docs/adr and no tracked .memory -> survey would miss sources; tools/ grep: no hardcoded target .memory path -> tool changes not needed, re-scoped to skills+steering"
2. ✓ Supported target layout(s) decided and recorded — "Decided+recorded in steering/archwright-conventions.md 'Target layout rule': read grey-matter paths (GLOSSARY.md, docs/adr/, docs/agents/specs/, docs/agents/grill/, docs/agents/) first, fall back to legacy .memory/; write working files to docs/agents/archwright/, .memory/ only if target still tracks .memory/"
3. ✓ Skills and steering updated (or explicitly kept) to match; fixture suite green — "Skills survey/audit/forces/tensions/derive/resolve + steering + GLOSSARY.md updated in 770bd22; mise run test -> 165 passed, 0 failed, 0 skipped; validate --links design/ PASS; sanitize-check PASS"
