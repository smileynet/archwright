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
   two named runs for `colorScheme: light | dark`. Pre-downscale to the analysis
   model's native limits (see Analysis stack below) — resolution mismatch is the #1
   documented cause of grounding failure. Playwright is an OPTIONAL
   dependency: absent → SKIP-with-reason (Extension Protocol rule 1), never a suite
   failure.
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

## Settled by operator (2026-07-22)

1. **Invocation = subagent fan-out.** Analysis runs as subagent dispatch (fresh
   session per section — also sidesteps the long-session/post-compaction inline-image
   quirk). One section per stage, ≤4 stages per dispatch batch, 1–2 labeled images
   per stage; findings written to files (write-then-read), then aggregated in the
   main session. The bare `kiro-cli chat --no-interactive "<prompt> /abs/path.png"`
   variant is still validated once at harness birth as the fallback path.
2. **Pre-resize is mandatory, in the capture harness.** Crops are resized to
   ≤1568 px long edge (and kept ≥200 px) BEFORE analysis — never rely on downstream
   auto-resize (unverified in the kiro-cli path, and Anthropic's resize takes the
   sizing choice away from us).
3. **Image ordering through the tool path: resolved as non-issue.** Tool-mediated
   images always arrive instruction-first (as read-tool results). That matches the
   recommended ordering for targeted verify tasks, which is the rubric's shape;
   images-first only matters for open-ended gestalt critique, which we don't rely
   on. Confirm with one line during birth validation.

## Analysis stack (targeted research, 2026-07-22 — supplements the generic VLM findings)

The analysis leg runs on kiro-cli + Claude, so the harness targets THEIR documented
mechanics, not generic-VLM folklore (`.scratch/research/claude-vision-specs.md`,
`claude-ui-screenshot-analysis.md`, `kiro-cli-image-workflow.md`):

- **Image ingestion path:** images enter a kiro-cli session by FILE PATH — the agent
  reads them via the read tool's Image mode (PNG/JPG/GIF/WebP; kiro-cli documents
  <10 MB per image, up to 10 images per request). Headless fan-out
  (`kiro-cli chat --no-interactive "<question> /abs/path.png"`) is the scripted
  pattern; headless+image is not explicitly documented together — validate once at
  harness birth and record the result (conformance-at-birth).
- **Sizing (corrects the earlier generic numbers):** Claude vision cost is
  patch-based — ⌈w/28⌉ × ⌈h/28⌉ tokens; the old w×h/750 formula is obsolete.
  Standard tier resizes to 1568 px long edge / 1568-token cap (high-res tier 2576 px
  on Opus 4.7+/Sonnet 5). Pre-downscale section crops to ≤1568 px long edge OURSELVES
  (resolution mismatch = the #1 documented grounding-failure cause; Anthropic
  publishes a reference resized_size()); crops under 200 px risk hallucination —
  keep section crops between those bounds. Anthropic's internal testing: tiling and
  coordinate-grid overlays do NOT help; don't build them.
- **Prompt shape (official + measured):** images BEFORE text for open-ended
  analysis; label every image with a text block ("Image A: wireframe wf-all-clear",
  "Image B: rendered section"); structured severity-classified diff output; ≤5-10
  images per request before recall degrades (two-pass for larger audits).
- **Division of labor (Anthropic-documented):** Claude's spatial
  reasoning/coordinates are "approximate" and counting is unreliable — geometry and
  measurement stay mechanical (DOM assertions, axe-core); Claude judges semantics
  (hierarchy, grouping, ask-type rendering intent).
- **Hybrid comparison beats image-vs-image:** no controlled public measurement, but
  converging evidence favors spec-text + screenshot (Claude can't measure pixels but
  can verify STATED values) — which is exactly the D-anchor rubric shape. The ASCII
  wireframes ride along as gestalt evidence, not as the comparison baseline.



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

- [ ] Headless+image invocation validated once at harness birth (kiro-cli --no-interactive with an image path), result recorded
- [ ] Capture harness produces named per-section PNGs (pre-resized ≤1568px long edge, ≥200px) + fullPage overview, light +
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
