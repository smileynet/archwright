# Visual Conformance — Method Reference (ticket 044/045)

Single authority for the blind question-asking method. The battery file
(`tools/report/visual-battery.md`) holds project-specific questions; ticket 044 is the
closed decision record with the research citations.

## The loop

1. **Generate** the report bundle(s) — at least two postures when judging
   posture-dependent decisions.
2. **Capture**: `node tools/report/capture.mjs <report.html> -o <dir>` — deterministic
   recipe, per-section crops pre-resized (≤1568px long edge, ≥200px floor via
   context-padding), light + dark, `manifest.json` lists regions. Missing playwright
   → loud exit 2 with install instructions.
3. **Battery**: derive ≥1 neutral question per active D-anchor (conservation both
   directions; undecidable-by-looking anchors get a not-visually-checkable entry).
4. **Blind answering**: subagent fan-out, fresh session per section, 1–2 labeled
   images per stage, unprimed description FIRST, answers → files. The answerer never
   sees decisions, wireframes, or expectations.
5. **Judge** in the main session (which holds the ledger): join answers to anchors,
   classify match / mismatch / unclear, emit a triage table.
6. **Non-vacuity**: a deliberately-broken variant must flip the blind answers in the
   broken dimensions — this probes the questions, not just the page.

## Hard rules (each has an incident behind it)

- **Questions never contain the expected answer.** Stated expectations shift VQA
  answers toward the prompt-favored option in both directions (12–42pt accuracy
  drops) — agreement with a leading question is near-zero evidence.
- **Verify blind claims semantically, never by proxy.** The 044 judge "refuted" a
  true no-transitions finding by counting SVG paths — paths are box outlines, not
  edges. Test the claim itself (are there arrows between states?), not a correlate.
- **Absence claims are low-confidence by construction** — one hallucinated absence
  and one true absence appeared in the same run; mechanical verification at judge
  time is mandatory before reporting either.
- **Findings ruled by ratified decision text route fix-implementation — no HITL.**
  Triage means joining a finding to its D-anchor; if the decision text rules
  directly, fix it (ADR-0010 routing). Escalate only genuine ambiguity or suspected
  legitimate divergence. (Incident: F1–F3 were needlessly escalated, 2026-07-22.)
- **Padded crops leak neighboring context** — region isolation is soft; judge
  region-scoped claims accordingly.
- **Interactive states are unaskable from static capture** (response bar, folds) —
  mark unclear, don't guess; scripted-interaction capture is future work.
