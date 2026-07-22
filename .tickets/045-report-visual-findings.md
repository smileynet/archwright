---
id: "045"
title: "Report generator: diagram absent in needs-attention, unverified list folded in all-clear, jargon on surface (044 triage F1-F3)"
status: done
blocked_by: []
---

# Report generator conformance fixes (044 triage F1–F3)

Findings from the first visual-conformance run (ticket 044, `.scratch/visual-answers/TRIAGE.md`).
Route: fix-implementation (violations of ratified decisions — no new human judgment needed).

## Findings as re-triaged during implementation

- **F1 original ("diagram absent in needs-attention") REFUTED:** with a stateful model,
  NA posture renders the diagram correctly (verified: dogfood design + injected
  violation → SVG present). The real cause on examples/partial: its actor model has no
  `states` — nothing to draw, fallback is correct. But the fallback NOTE was jargon
  ("v1 join granularity: rules roll up per actor") — a design-system#D002 violation.
- **F2 (jargon on surface):** "(dirty)", the "v1 join granularity" note, and the
  model state label "working out the asks and the map" were genuine D002 violations.
  Commit hash (identification), code evidence in decision cards (necessarily
  technical), and vocabulary surface phrases ("firm rule — needs your sign-off") are
  designed content, not violations.
- **F3 (unverified list folded in AC):** confirmed — pending rules rendered as a
  count-only line, violating wf-all-clear#D002 ("same prominence, never behind a fold").
- **F4 (NEW, from overturning the 044 judge override):** the diagram has NO
  transitions — models carry none, derive never extracts them, smcat source declares
  states only. The blind "no connectors" claim was TRUE; the 044 judge's mechanical
  refutation counted SVG paths that are box outlines, not edges. Split to its own
  ticket (feature: transitions could join from behavior specs).

## Acceptance criteria

- [x] Fallback notes are plain language (both no-model and stateless-model paths)
- [x] Pending rules listed by name in WHAT ISN'T VERIFIED (all postures)
- [x] "(dirty)" → "uncommitted changes present"; jargon state label reworded in the
      dogfood model
- [x] Suite green after changes
- [x] Blind re-verification (fresh subagents, same neutral questions) confirms:
      pending rules named and visible without interaction (certain); fallback note
      readable as plain text; no "(dirty)" token on surface
- [x] F4 filed separately

## Resolution (2026-07-22)

- `derive.py`: both model_view fallback notes rewritten in plain language.
- `render_html.py`: pending skips render as a named list under the count line;
  dirty label now "· uncommitted changes present".
- `design/models/report-actors.yaml`: state label "working out the asks and the map"
  → "working out what needs your attention" (D002).
- Verified: regenerated both postures; suite 143/0/0; blind re-verification stages
  (reverify-ac, reverify-na) cleared F3 and F1-revised with certainty bands.
- Method lesson recorded in TRIAGE.md: a judge's mechanical verification must test
  the SEMANTIC claim (are there edges?), not a proxy (are there paths?) — the 044
  override was wrong and the blind answerer right.
