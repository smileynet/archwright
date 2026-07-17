# Q04 — Where does promotion/demotion evidence live?

**Status:** DECIDED — Split by author: ledger for machine events, artifact for ratifications
**Date:** 2026-07-17

## Question

C3's open design point: check-generated evidence events (counterexamples, pass streaks) need a home. Spec frontmatter, separate ledger, or derive-from-history?

## Research

- Brief:142 — "promoted (evidence accumulates) or demoted (counterexample found)"
- growth-rules.md:17 — rule 7 exists: promotion = deeper checking + "record evidence in pattern"
- Phase 5 CK-07/08 — `.archwright-baseline.json` is already a fingerprinted, human-gated violation ledger ("never add automatically")
- Force template — evidence_level + prose evidence in-artifact precedent

## Decision

**Split by author:**
- **Machine events → ledger** (`design/.archwright-evidence.json`, keyed by `kind:id`, append-only, fingerprinted — same family as the CK-07 baseline). Check auto-appends: FAIL on ★★/★ spec → demotion-candidate; pass streaks / deeper-check passes → promotion-candidate.
- **Human ratifications → artifact** (confidence field updated + one line in the pattern's Evidence section citing ledger events). ★★ transitions always HITL (ADR 0007, CK-08 precedent).
- Report command joins the two, lists pending candidates; `archwright-passup` (Q02) surfaces ★★ demotion candidates as escalations.

Rejected: A (tools mutating human-authored files — noisy diffs, check-that-edits-what-it-checks smell); C (ephemeral, contradicts growth rule 7).

## Implications

- C3 ADR writes this up; implementation sequences AFTER CK-03 (events need structured output to cite) and naturally alongside CK-07 (shared ledger plumbing)
- Principle for the ADR: tools write tool-owned files; humans write human-owned files
