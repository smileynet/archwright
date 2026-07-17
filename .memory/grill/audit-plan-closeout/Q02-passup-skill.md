# Q02 — Where does correction routing (pass-up) live?

**Status:** DECIDED — Option B (new skill `archwright-passup`)
**Date:** 2026-07-17

## Question

The check-output work (CK-03/09/10) produces violations with provenance, suggested_route, contrast pairs, and escalation flags. Who consumes them? Amend archwright-check, add a new skill, or fold into archwright-resolve?

## Research

- `skills/archwright-check/SKILL.md:33` handles routing in ONE sentence and references `archwright-resolve/references/pass-up.md` — **which does not exist** (verified: not in repo, not deployed). The pipeline's upward arc has no skill owner.
- Glossary: "Pass-up — level-terminating, confidence-gated, follows provenance links"; "Lift — the hardest cognitive work in the system." First-class in theory, homeless in practice.
- A4 claims audit: correction routing = spike-only. figures/pass_up_tower.svg treats pass-up as a top-level concept.
- Bug found in passing: check skill uses "Does NOT Cover" header (same defect B5 fixed in resolve).

## Options

- **A. Amend archwright-check** — rejected: mixes mechanical verification with judgment-heavy routing; buries the ★★ HITL gate (ADR 0007) inside an AFK skill.
- **B. New skill `archwright-passup`** — CHOSEN: consumes structured violations, walks provenance, lifts to the owning level, routes per confidence (★★ → resolve HITL, ★ → propose fix, — → auto-adjust). Absorbs the never-written pass-up.md content. Tool/skill split preserved (CK-09/10 produce payload; skill consumes).
- **C. Fold into archwright-resolve** — rejected: most violations route to fix-implementation and never reach resolve; conflates dispatch with decide.

## Decision

Add `archwright-passup` as the 13th skill. Single concern: consume check violations → lift → route → dispatch. The lift step is the skill's meat (not glue); open question #1 (lift contract) matures inside it.

## Implications

- CK-03/09/10 tool tickets unchanged (payload production)
- check skill step 4 narrows to "hand structured violations to `archwright-passup`" — its routing sentence and dangling reference move out
- survey routing table gains a row (violations need routing → archwright-passup)
- Pipeline picture: hands-down = survey→…→check; pass-up = check → passup → resolve
- Fix in the same change: check's "Does NOT Cover" header → "Does NOT"
- OQ#1 (lift contract) gets a home; skill notes it as open research
