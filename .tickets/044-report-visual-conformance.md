---
id: "044"
title: "Visual design-conformance validation: screenshot the report page, analyze sections against the ratified design"
status: open
blocked_by: []
---

# Visual design-conformance validation of the report page

The report's behavior is verified (page.js reducer trace round-trip under node) and its
structure is conformance-tested (bundle/asks/vocabulary in the suite), but the RENDERED
page has never been compared against the intended design — despite that design being
formally captured with decision provenance (`design/discovery/ui/design-system.md` +
wireframes, D-anchored). Research synthesis in `.scratch/research/` (4 files,
2026-07-22): `playwright-screenshot-practices.md`, `visual-regression-prior-art.md`,
`vlm-ui-critique.md`, `design-spec-conformance.md`.

## Why (and the archwright-shaped angle)

Prior art defines "intended design" as *the last human-approved rendering* (pixel
baselines) — none of the surveyed tools carry design intent or provenance. Archwright
already has machine-readable intent: the D-anchor ledger. The novel move is deriving
visual assertions FROM ledger decisions (conservation: every assertion cites its
anchor), not from a pixel baseline. Two verified negative results shape the design:
LLMs fail as pixel-diff comparators (a small CNN beats GPT-4V/Claude/Gemini — InfoQ
2025), and VLMs are weak at spatial grounding (IoU ~0.35–0.45) with two hallucination
modes (wrong element, fabricated element). So: geometry/tokens/contrast go to
mechanical tools, the VLM does semantic judgment only, and absence-assertions are
treated as unreliable.

## What to build

1. **Capture harness** (`tools/report/capture.mjs` or similar, playwright library
   mode — no test runner): `page.goto(file://<abs>/report.html)` with the determinism
   recipe (explicit viewport, `deviceScaleFactor: 1`, `animations: 'disabled'`,
   `reducedMotion: 'reduce'`, `await document.fonts.ready`, mouse parked at 0,0).
   Per-section `locator.screenshot()` named by report region (posture badge, asks
   block, model view, behavior diagram, disclosure folds) + one fullPage overview;
   two named runs for `colorScheme: light | dark`. Respect the ≤2000px long-edge /
   ~1.15MP vision-model budget — viewport-height slices if a section exceeds it.
   Playwright is an OPTIONAL dependency: absent → SKIP-with-reason (Extension
   Protocol rule 1), never a suite failure.
2. **Assertion rubric derived from D-anchors:** a checklist file mapping each visual
   assertion to its ledger anchor (design-system.md#D003/#D004 ask-type rendering,
   wf-all-clear#D003 honest-all-clear, posture badge rules, disclosure-fold
   behavior). Fixed-dimension rubric + severity JSON output (the consistent
   practitioner pattern), design tokens injected as named expectations. Nothing
   invented: an assertion with no anchor is a rubric bug.
3. **Analysis run:** per-section VLM critique against the rubric (section crops, not
   whole-page — whole-page prompts produce generic ungrounded feedback). Mechanical
   adjacent checks where they're ★★-shaped: axe-core contrast on the rendered DOM
   (NOT jsdom — it silently drops color-contrast), token-usage greps if applicable.
4. **Routing:** findings are CANDIDATE violations for human triage (pass-up
   semantics) — every surveyed element-wise conformance tool concedes this with a
   triage workflow. Never an auto pass/fail commit gate.
5. **Postures:** capture at minimum the current dogfood posture + one contrasting
   posture (needs-attention vs all-clear); the behavior diagram must be constant
   across them (glossary: posture).

## Non-vacuity (Extension Protocol rule 4)

A deliberately-broken variant (e.g. CSS token override making status colors
indistinguishable, or a removed posture badge) MUST produce findings. A rubric proven
only on the passing page may be vacuous.

## Governance note

This starts as a REVIEW-track harness (judgment, ★-shaped) — not a new check
`method:`. If it should graduate into a spec-checkable kind (visual constraint specs),
that is a new KIND and needs an ADR + HITL per two-tier governance. Record the
decision either way.

## Acceptance criteria

- [ ] Capture harness produces named per-section PNGs + fullPage overview, light +
      dark, deterministic recipe applied; SKIPs with reason when playwright absent
- [ ] Rubric file exists; every assertion cites a D-anchor; conservation checked
      (no anchor → error)
- [ ] Analysis run produces structured per-section findings (severity + anchor +
      evidence crop); absence-assertions flagged as low-confidence by construction
- [ ] Non-vacuous: broken-variant run produces findings; passing run on the dogfood
      bundle is clean or has triaged candidates
- [ ] Findings route to human triage (span digest / report asks), never auto-gate
- [ ] Governance decision recorded (review-track vs future check-kind ADR)

## Out of scope

- Pixel-baseline regression (Percy/Chromatic-style) — different problem (drift vs
  intent conformance)
- Mermaid-diagram content validation (settled-signal for client-rendered Mermaid is
  an open question in the research; capture waits for it but doesn't judge it)
- CI wiring — local/operator-run first; field data decides if it joins the suite
