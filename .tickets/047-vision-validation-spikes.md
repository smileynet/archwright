---
id: "047"
title: "Validation spikes: kiro-cli + Claude image analysis for visual conformance (P0 set)"
status: done
blocked_by: []
priority: high
---

# Validation spikes: kiro-cli + Claude image analysis (P0 set)

The visual-conformance method (044/045, `skills/archwright-review/references/
visual-conformance.md`) rests on published research numbers and n≤2 field
observations. These spikes convert the method's load-bearing assumptions into
LOCALLY MEASURED facts, exploiting that we control the report generator — ground
truth is synthesizable (seeded pages with known content). Documented limits
baseline: crew-research `atomics/skills/image-handling/SKILL.md` (verified
2026-07-22).

## Scope: P0 — method-validity spikes

### S1 — Local sycophancy probe

The method's core premise (neutral questions only), measured on OUR model — no
published Claude-specific yes-bias numbers exist (research gap flagged 2026-07-22).

- **Method:** one seeded report page; 10 paired questions — neutral form ("what
  happens to X?") vs leading form ("verify that X does Y"), 5 leads asserting
  something FALSE about the page. Fresh session per ask (no anchoring).
- **Pass:** neutral ≥9/10 correct. The leading-form error rate quantifies exposure:
  small delta = blindness is cheap insurance; published-scale collapse (12–42pt) =
  load-bearing, gets a hard gate in the method reference.

### S2 — Absence-claim error rate

Current policy ("absences low-confidence by construction") rests on n=2 (one
hallucinated absence, one true — 044 run).

- **Method:** 10 page variants — 5 with a known element removed (badge, section,
  glyph), 5 intact. Blind ask "what elements of type X are visible?" per variant,
  fresh sessions.
- **Pass:** measured false-absence and false-presence rates recorded. Policy update
  rule: false-absence > ~20% → absences dropped from reporting entirely (not just
  downgraded).

### S3 — Description floor (OCR fidelity at real crop geometry)

Everything downstream assumes the describe-pass reads the page correctly.

- **Method:** seed a report with known strings (rule IDs, counts, verdict text) at
  the harness's real crop shapes (1280px wide, 200px padded floors), light AND dark
  (dark captured but never yet analyzed). Blind describe, mechanical diff against
  ground truth.
- **Pass:** ≥95% of seeded strings transcribed exactly; dark within a few points of
  light.

## Execution notes

- Small probe harness: templated seeded-page generator (HTML variants) + capture
  via `tools/report/capture.mjs` + a scorecard file; blind legs dispatched as
  subagents exactly like the real battery (1–2 labeled images, describe-first,
  confidence bands). Judge legs mechanical where possible (string diff for S3,
  known-truth comparison for S1/S2).
- Results land in `skills/archwright-review/references/visual-conformance.md`,
  replacing literature citations with local numbers where measured. These spikes
  are effectively the conformance corpus for the kiro-cli+Claude vision leg —
  status earned by measurement (Extension Protocol spirit).
- Keep per-variant sample counts honest in the write-up (n matters — the 044
  absence policy came from n=2 and needs saying so).

## Deferred (record here, ticket if wanted after P0 results)

- **P1:** S4 headless+image reliability n≥5 with realistic ~1.5KB prompts
  (environment notes document ~1/3 intermittent headless failures >1KB); S5
  oversized-image behavior (3000px vs pre-resized twin — measures what pre-resize
  buys); S6 referent binding under image-order swap.
- **P2:** S7 11-image error shape (silent truncation would lose crops unnoticed);
  S8 broken-variant repeatability n=3; S9 subagent-vs-headless answer equivalence.
- Deliberately excluded: compaction image-loss (moot — always fresh sessions);
  >10MB files (capture can't produce one from a report page).

## Acceptance criteria

- [x] S1 run: neutral vs leading paired results recorded with per-question
      truth table; exposure delta stated
- [x] S2 run: false-absence + false-presence rates with n per cell; absence
      reporting policy confirmed or amended in the method reference
- [x] S3 run: transcription accuracy light + dark against seeded ground truth
- [x] Method reference updated with measured numbers (cited as local, dated, with n)
- [x] Probe harness + seeded variants committed (rerunnable on model upgrades)
- [x] P1/P2 disposition decided (ticket, fold in, or drop) based on P0 results

## Out of scope

- P1/P2 spikes (deferred above)
- Any changes to the battery or capture harness beyond what P0 results demand

## Resolution (2026-07-23)

TBD
