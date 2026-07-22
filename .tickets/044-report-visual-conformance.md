---
id: "044"
title: "Visual design-conformance validation: screenshot the report page, analyze sections against the ratified design"
status: done
blocked_by: []
---

# Visual design-conformance validation of the report page

The report's behavior is verified (page.js reducer trace round-trip under node) and its
structure is conformance-tested (bundle/asks/vocabulary in the suite), but the RENDERED
page has never been compared against the intended design — despite that design being
formally captured with decision provenance (`design/discovery/ui/design-system.md` +
wireframes, D-anchored). Research synthesis in `.scratch/research/` (8 files,
2026-07-22): capture/prior-art/VLM generics (4 files), Claude/kiro-cli stack specifics
(3 files), and question-asking methodology (`claude-vqa-practices.md`,
`question-bias-blind-eval.md`, `ui-evaluation-question-taxonomies.md`,
`intent-to-questions.md`).

## Method: blind question-asking, not rubric verification (rewritten 2026-07-22)

The original design (assertion rubric + mechanical checks) was dropped by operator
decision, and the research validates the reversal: **telling the model the expected
answer corrupts the judgment** — appended expectations drop VQA accuracy 12–42 pts and
shift answers toward the prompt-favored option in BOTH directions (arXiv:2408.11261,
2604.16790), so agreement with a stated assertion is near-zero evidence. Visual
sycophancy exceeds text sycophancy, and CoT does not fix it. The replacement
methodology:

1. **Enumerate decisions first, then derive questions.** Free-form question
   generation covers only ~27–34% of a spec (arXiv:2501.03491). So: enumerate the
   active D-anchors (design-system.md, wireframes) as the coverage frame, then derive
   ≥1 NEUTRAL question per decision. Bidirectional traceability — every question
   cites its D-anchor; every active anchor yields a question (the conservation
   principle applied to questions). A decision with no derivable question is recorded
   as not-visually-checkable, never silently dropped.
2. **Questions never contain the expected answer.** One decision, one question (no
   compound "and/or" questions — uninterpretable answers); no presuppositions, no
   hedged suggestions, no sentiment, no provenance/stakes leakage; open-ended
   preferred over binary; when binary is unavoidable, balance polarity across the
   battery. The decision text stays OUT of the answering session: "What happens to
   the page's verdict area when suggestions are present?" — never "Verify that
   suggestions don't block the all-clear."
3. **Question ladder per section** (dependency ladder, matched to measured VLM
   reliability): (a) unprimed DESCRIPTIVE pass first — "describe this section" — as
   grounding audit (reliable; also the anchor for detecting hallucination later);
   (b) perceptual/functional questions (usable); (c) comparative questions only as
   pairwise with order swapped across calls (position bias is large); (d) absolute
   scoring/ranking: never (documented weak). Precise localization and measurement
   are not asked at all (IoU ~0.12–0.36) — and with mechanical checks dropped, such
   properties are out of scope for this harness.
4. **Blind answering, separated judging.** The answering subagent sees ONLY the
   screenshot crops and the neutral questions — never the design decisions, the
   wireframes, or what "should" be there. Answers carry categorical confidence bands
   (not verbalized percentages — systematically overconfident), cited visual evidence
   ("what in the image shows this"), and an explicit abstention path. The JUDGING
   step — joining answers back to the D-anchor decisions and deciding
   match/mismatch/unclear — happens in the main session (which holds the ledger),
   outside the answering model. Describe-then-compare, comparison outside the model.
5. **Findings route to human triage** (pass-up semantics): mismatches become
   candidate findings with the D-anchor, the question, the blind answer, and the
   crop as evidence. Never an auto pass/fail gate. Absence-findings ("X is not
   visible") are low-confidence by construction.

## What to build

1. **Capture harness** (`tools/report/capture.mjs` or similar, playwright library
   mode — no test runner): `page.goto(file://<abs>/report.html)` with the
   determinism recipe (explicit viewport, `deviceScaleFactor: 1`,
   `animations: 'disabled'`, `reducedMotion: 'reduce'`,
   `await document.fonts.ready`, mouse parked at 0,0). Per-section
   `locator.screenshot()` named by report region (posture badge, asks block, model
   view, behavior diagram, disclosure folds) + one fullPage overview; two named runs
   for `colorScheme: light | dark`. Crops pre-resized in the harness: ≤1568 px long
   edge, ≥200 px floor. Playwright is an OPTIONAL dependency: absent →
   SKIP-with-reason (Extension Protocol rule 1), never a suite failure.
2. **Question battery generator:** D-anchor enumeration → neutral question per
   decision, with the traceability table (question ↔ anchor) and the
   not-visually-checkable ledger. The battery is a reviewable artifact (questions are
   themselves checkable for leading-phrasing defects before any analysis runs).
3. **Blind answering fan-out:** subagent dispatch, one section per stage, ≤4 stages
   per batch, 1–2 labeled images per stage, fresh session per section (no anchoring
   across sections), answers written to files (write-then-read), descriptive pass
   before question pass within each stage.
4. **Judging + aggregation** in the main session: join answers to anchors, classify
   match/mismatch/unclear, emit the triage table.

## Settled by operator (2026-07-22)

1. **Invocation = subagent fan-out.** Fresh session per section — also sidesteps the
   long-session/post-compaction inline-image quirk. The bare
   `kiro-cli chat --no-interactive "<prompt> /abs/path.png"` variant is still
   validated once at harness birth as the fallback path.
2. **Pre-resize is mandatory, in the capture harness.** Never rely on downstream
   auto-resize.
3. **Image ordering through the tool path: non-issue.** Tool-mediated images arrive
   instruction-first, which matches the recommended ordering for targeted tasks;
   confirm with one line during birth validation.
4. **Mechanical checks and the assertion rubric: DROPPED** (2026-07-22). The harness
   is question-asking only; measurement-type properties are out of its scope.

## Analysis stack facts (kiro-cli + Claude, verified 2026-07-22)

- Images enter kiro-cli by FILE PATH via the read tool's Image mode (PNG/JPG/GIF/
  WebP; <10 MB, ≤10 images/request documented). Headless+image is not explicitly
  documented — validate at harness birth.
- Claude vision cost is patch-based (⌈w/28⌉ × ⌈h/28⌉ tokens); standard tier = 1568 px
  long edge. Resolution mismatch is the #1 grounding-failure cause; <200 px risks
  hallucination. Tiling and coordinate-grid overlays do NOT help (Anthropic internal
  testing) — don't build them.
- Label every image with its role in text; ≤5–10 images per request before recall
  degrades; decomposed single-attribute questions beat compound ones (arXiv:2310.17050).

## Non-vacuity (Extension Protocol rule 4)

A deliberately-broken report variant (e.g. CSS override neutralizing status colors, or
a removed posture badge) MUST surface as mismatches in the blind answers. A battery
proven only on the passing page may be vacuous. This also probes the method itself:
if the blind answers on the broken variant match the intended design anyway, the
questions are too weak or too leading.

## Governance note

This is a REVIEW-track harness (judgment, ★-shaped) — not a new check `method:`. If it
should graduate into a spec-checkable kind, that is a new KIND and needs an ADR + HITL
per two-tier governance. Record the decision either way.

## Acceptance criteria

- [x] Headless+image invocation validated once at harness birth (kiro-cli
      --no-interactive with an image path), result recorded
- [x] Capture harness produces named per-section PNGs (pre-resized ≤1568px long edge,
      ≥200px) + fullPage overview, light + dark, deterministic recipe applied; SKIPs
      with reason when playwright absent
- [x] Question battery: every question cites a D-anchor; every active anchor has ≥1
      question or a not-visually-checkable entry (conservation, both directions);
      no question contains its expected answer (reviewable before use)
- [x] Blind answering runs see screenshots + questions only (no decisions, no
      wireframes); descriptive pass precedes questions; answers carry confidence
      band + cited visual evidence + abstention path
- [x] Judging joins answers to anchors outside the answering sessions; triage table
      emitted; absence-findings marked low-confidence
- [x] Non-vacuous: broken-variant run produces mismatches; passing run on the dogfood
      bundle is clean or has triaged candidates
- [x] Governance decision recorded (review-track vs future check-kind ADR)

## Out of scope

- Mechanical/deterministic checks (axe-core, token greps, DOM geometry) — dropped by
  operator decision 2026-07-22; if measurement-type conformance is wanted later it is
  a separate ticket
- Pixel-baseline regression (Percy/Chromatic-style) — drift vs intent conformance
- Mermaid-diagram content validation (settled-signal open question; capture waits for
  it but doesn't judge it)
- CI wiring — local/operator-run first; field data decides if it joins the suite

## Resolution (2026-07-22)

- **Harness:** `tools/report/capture.mjs` (playwright library mode, determinism recipe, per-section clips via named selectors + h2-delimited spans, pad-to-floor for sub-200px regions — padding over upscaling since extreme-aspect strips are the hallucination-risk shape, viewport grown to document height so document-space clips don't clamp). Budget verified: all crops ≤1568px long edge / ≥200px floor across 3 capture sets. Playwright installed locally (package.json devDependency, node_modules + lockfile gitignored; public-registry install — CodeArtifact auth was stale). Deviation from AC wording: missing playwright = loud exit 2 with install instructions (operator tool), not a SKIP line — SKIP semantics belong to a suite wrapper if CI wiring ever lands (out of scope by design).
- **Birth validation:** headless+image works — `kiro-cli chat --no-interactive --trust-tools=read "<prompt> <abs>.png"` returned accurate OCR of a real crop (verdict text, commit hash, diagram pill labels). Recorded caveat: padded crops leak neighboring context; region isolation is soft.
- **Battery:** `tools/report/visual-battery.md` — 12 neutral questions covering all active D-anchors both directions (7 anchors → questions incl. shared ones; 10 anchors in the not-visually-checkable ledger with reasons; wf-all-clear#D001 excluded as SUPERSEDED).
- **Blind run (4 subagent stages, light scheme, AC + NA postures):** answers with confidence bands + cited evidence + abstentions in `.scratch/visual-answers/`. Judging (main session) in `TRIAGE.md`: 3 candidate mismatches (F1 diagram absent in needs-attention posture — mechanically confirmed, generator-bug candidate vs wf-all-clear#D005; F2 jargon on primary surface vs design-system#D002; F3 AC folds the unverified-rules list vs wf-all-clear#D002, posture-inconsistent with NA), 4 match clusters (D005 ask anatomy reconstructed unprompted, incl. no-preselection), 1 judge override (blind "no connectors" claim refuted by the SVG's 6 edge paths — the documented absence-hallucination mode, caught by mechanical verification at judge time), 2 unclear (interactive states unobservable in static capture).
- **Non-vacuity: PASS** — CSS-broken variant (glyph + diagram hidden) flipped the blind answers in exactly the broken dimensions.
- **Governance:** stays REVIEW-track (★-shaped judgment harness, owner archwright-review — AGENTS.md ownership row added). Not a check `method:`; graduating it would need an ADR per two-tier governance.
- Suite green (143/0/0 — harness not suite-wired by design); sanitize-check PASS. Findings F1–F3 handed to operator triage.
