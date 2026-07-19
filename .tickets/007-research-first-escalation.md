---
id: 007
title: Research-first gate before HITL escalation in passup
status: done
blocked_by: []
created: 2026-07-17
---

# Research-first gate before HITL escalation

Resolution (2026-07-17): ADR 0010 accepted (refines 0007, does not repeal it).
`archwright-passup` step 3 gains the research gate + classification table
(positive evidence required; ambiguity defaults to escalate); conventions ★★
rule, AGENTS.md mirror, and CONTEXT.md glossary amended; hard floor +
digest-review of classified-away events preserved. Deployed.

## Why (operator directive, 2026-07-17)

"We should only escalate on issues that truly need human intervention. We should
first try to resolve through researching related topics, best practices, prior
art, etc."

Current behavior: any ★★ violation is presented as an HITL event (ADR 0007).
In the DemoAR field run this surfaced ★★ violations that research alone could
disposition (e.g., `no-tracked-secrets` FAILing on an icon PNG named
`Res_Credentials_48_Dark.png` — the contrast pair already contained the answer).

## What to build (archwright lane — owner of passup/conventions)

- In `archwright-passup` (and/or conventions): before presenting a ★★ event,
  the agent runs a research pass — prior art, best practices, related specs,
  contrast-pair analysis — and classifies the violation:
  - **check defect / spec noise** → propose the spec/check fix, no HITL
  - **known + owner-accepted** (matches an existing work-queue/decision record) → log, no HITL
  - **genuine new decision** (tradeoff, scope change, security judgment) → HITL with the research attached
- HITL presentations must arrive WITH the research summary and a recommended
  disposition, never as a bare violation.
- Keep the hard floor: anything irreversible, security-material-and-novel, or
  contradicting a ratified resolution still blocks.

## Notes

- This refines, not repeals, ADR 0007 — likely needs a small ADR amendment.
- Session lane split (2026-07-17): DemoAR session applies this as operating
  practice; formalization belongs to the archwright-improvements session.
