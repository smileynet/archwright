---
kind: pattern
id: plain-surface-progressive-disclosure
name: "Plain Surface, Progressive Disclosure"
scale: feel-finish
confidence: "★"
status: active
serves: [actionable-without-literacy, cold-reader-comprehension]
context: [canonical-doc-projections]
completed_by: []
resolves_into:
  - "constraint:vocabulary-map-surface"
  - "contract:vocabulary-map"
---

# Plain Surface, Progressive Disclosure

## Problem

**The report must be actionable by people who have never heard of archwright, yet experts need exact methodology terms to act precisely.**

## Context

In the context of `canonical-doc-projections`, this pattern governs the language layer of every projected surface (web, markdown).

## Forces

- **Desire:** A developer knows what to do — fix code, revisit a rule, flag a broken check — without archwright literacy (`actionable-without-literacy`).
- **Constraint (soft):** The primary surface reads in product language only; methodology vocabulary is confined to disclosure layers (`plain-language-surface`).
- **Constraint (soft):** Exact methodology terms (spec ids, ★★ marks, check mechanics) must remain reachable for precise expert action (`expert-precision-available`).

## Tension

Plain language and precision pull apart: translate everything and experts lose the exact handle they need to act ("which spec id do I edit?"); keep methodology vocabulary and cold readers bounce off the surface. Two separate reports would fork the truth.

## Evidence

- User decision, verbatim: "we want to ux to focus on non-jargon, low cognitive-complexity reporting that is actionable to users without requiring them to understand archwright specifically" [design-system#D002]
- Rejected alternatives: archwright-vocabulary-verbatim surface (requires methodology literacy); two separate reports for expert vs cold readers (one artifact, layered disclosure instead) [design-system#D002]
- Prior art: NN/g plain-language error-message guidelines (2024) — error text states outcome + action, not internals; NN/g progressive disclosure (2006) — defer secondary detail behind explicit user action [design-system Principles P0]
- Mechanism — translation must be deterministic, not ad-hoc: the design system carries a machine-readable vocabulary token table (violation → "needs attention", "confidence ★★" → "firm rule — needs your sign-off to change", …) so every surface renders the same phrase for the same internal term, and agent quotes match what the human saw [design-system tokens.vocabulary; wf-projections agent-consumption notes]
- Precedent for the disclosure depth: rules render as plain declarative sentences with check mechanics behind a disclosure — "spec ids and check methods never on the surface" [wf-behavior-detail#D002]; the provenance chain renders as Because/Decided/So plain lines [wf-issue-detail#D001]

## Therefore

**One surface, translated by a machine-readable vocabulary map, with methodology terms behind folds.** The primary layer of every projection uses only vocabulary-map surface phrases — outcomes and actions in product language. Internal terms (spec ids, confidence glyphs, check methods, artifact ids) appear solely inside progressive-disclosure details, one click from the surface phrase they underlie. The map is a token table in the design system: adding a new internal term requires adding its surface phrase, and surfaces render from the map — never hand-translated.

## Consequences

- Every new report feature pays a translation cost up front (a vocabulary-map entry) — untranslated terms cannot ship on the surface.
- The map becomes a checkable contract: surface copy can be mechanically scanned for internal-vocabulary leaks.
- Cold readers implicitly learn the methodology through the goal/design/check phrasing — by structure, never by name.
- Does NOT cover: which content each screen shows (structure patterns own that); localization beyond English.

## Verification

- Constraint check: surface layers contain no internal-vocabulary tokens outside disclosure elements — `constraint:vocabulary-map-surface` (checkable against the token table).
- Contract check: the vocabulary map itself is machine-readable and complete for all status/route/confidence terms — `contract:vocabulary-map`.

## Completion

This pattern is complete at its scale; it depends on the vocabulary map staying current as new internal terms appear.
