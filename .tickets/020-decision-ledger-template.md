---
id: 020
title: "Generic decision-ledger template (seam contract)"
status: open
blocked_by: []
---

# Decision-ledger template (T2)

`tools/templates/discovery-ledger.md`, adapted from wizard_of_oz `contract:decision-entry`: append-only `D{NNN}` entries — phase, category, origin (user|suggested|inferred), decision, rationale (verbatim), alternatives; `SUPERSEDES D{NNN}` reversals; entries-are-truth repair direction.

Q2: category enum = core 5 (`scope, experience, structure, technical, meta`) + domain extensions from overlay `discovery:` section. Q6: entries carry citable ids — the conservation check's source anchors; template documents the citation obligation for downstream transforms.

## Acceptance
- [ ] Template exists; enum parameterization documented
- [ ] Guard calibrations documented (per Q4)
- [ ] Citation/id fields support the conservation check (ticket 026)

Context: ADR 0011; spec T2; grill Q2/Q4/Q6.
