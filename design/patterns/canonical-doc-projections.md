---
kind: pattern
id: canonical-doc-projections
name: "Canonical Document, Projected Surfaces"
scale: loops-systems
confidence: "★★"
status: active
serves: [cold-reader-comprehension, agent-closes-the-loop]
context: []
completed_by: [static-report-response-file, plain-surface-progressive-disclosure]
resolves_into:
  - "contract:model-view-block"
  - "contract:asks-block"
  - "constraint:projections-one-way"
  - "dependency:report-reads-canonical-only"
---

# Canonical Document, Projected Surfaces

## Problem

**Humans need a readable, layered report; agents need one stable, parseable document — and the two audiences must never see contradictory truths.**

## Context

Root structural pattern for the report area. The report is archwright's human-facing output; everything the web page, markdown doc, or a consuming agent shows must trace to one source of record.

## Forces

- **Desire:** A cold reader understands the project's design state from the report alone (`cold-reader-comprehension`).
- **Desire:** An agent consumes the report and the human's responses directly, continuing work without manual translation (`agent-closes-the-loop`).
- **Constraint (soft):** Agents and scripts require one stable canonical run document whose shape never varies by audience (`machine-stable-canonical`).

## Tension

Humans want prose, hierarchy, and progressive disclosure; machines want a fixed schema. Serving both from independently-maintained outputs invites divergence — the human report says one thing, the agent reads another, and reconciling them becomes a merge problem with no authority.

## Evidence

- User decision, verbatim: "a web report as the primary structure for users to consume information provided by archwright, with markdown as secondary user documentation source and a source for agents, and json for agents/scripts" [design-system#D001]
- Rejected alternatives: markdown-primary (the prior de-facto state), terminal-output-primary, interactive SPA dashboard [design-system#D001]
- Prior art — projection architecture: ESLint formatter architecture (docs, 2025) renders one lint result set through pluggable formatters; Playwright's blob→html/json merge pipeline (2023) treats HTML as a projection of the blob report; SARIF (OASIS 2.1.0, 2020) standardizes the canonical-interchange-document approach for static-analysis results [design-system Principles P1]
- Rejected alternative — extending the check document itself with view data: rejected to keep the canonical schema pure; views are derived [wf-projections#D001]
- Mechanism: the canonical document already exists — the CK-03 check output shape — so the report adds derived blocks rather than a second source of truth [wf-projections JSON section]

## Therefore

**One canonical JSON document; every human surface is a one-way projection.** The CK-03 check output remains the canonical run document, unchanged. The report bundle adds two generation-time, read-only derived blocks: `model_view` (model elements + plain labels + per-element rule rollup) and `asks` (decisions/approvals/suggestions with options, recommendation, rationale). Web and markdown are regenerated from the canonical document + blocks — never edited, never merged sideways. Markdown mirrors the web drill hierarchy with deterministic heading anchors so agent quotes match what the human saw.

## Consequences

- The report generator is a pure function of the canonical document — no surface may carry information absent from JSON (new display needs = new derived block, decided at generation time).
- Demands the `model_view` and `asks` contracts (contract phase) and a projection-regeneration discipline check.
- Vocabulary must be applied identically across surfaces — handled by `plain-surface-progressive-disclosure` (vocabulary map).
- Does NOT cover: how responses return (that's `static-report-response-file`); per-step file splits for large projects (open, wf-projections).

## Verification

- Constraint check: generated surfaces are never hand-edited — `constraint:projections-one-way` (generated-artifact discipline).
- Contract checks: `model_view` and `asks` blocks validate against their schemas.

## Completion

This pattern is incomplete unless it also contains:
- The response return channel (`static-report-response-file`)
- The surface language rules (`plain-surface-progressive-disclosure`)
