---
id: "026"
title: "Conservation-check validator rule for seam artifacts"
status: done
blocked_by: ["020", "022"]
---

# Conservation check (T8)

The LEC-equivalent for agent transforms (grill Q6): mechanical citation-graph rule in `archwright-validate.py` for `design/discovery/` artifacts — (1) nothing invented: every output element cites a source id; (2) nothing lost: every active input decision consumed or explicitly deferred. Extension Protocol: ships with golden corpus incl. a violating fixture (orphan output + unaccounted input) wired into run-fixture-tests.sh.

Context: ADR 0011; spec T8; grill Q6; Q06 grill file has the full mechanism.

## Amendment (2026-07-18, skill/tool proposal review)

Also in scope: a minimal discovery-artifact frontmatter schema in `archwright-validate.py` (id; status ∈ proposed/approved/superseded; serves) so `design/discovery/` files are validated and visible to `--links` rather than invisible. Violating fixture: a discovery artifact with an illegal status value.
