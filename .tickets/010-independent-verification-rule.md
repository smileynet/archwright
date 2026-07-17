---
id: 010
title: "Explore: independent-verification rule in check skill (changed verdicts)"
status: open
blocked_by: []
created: 2026-07-17
---

# Explore: independent-verification rule for changed check verdicts

Feature suggestion from the ExposeAR field run (2026-07-17) — process
non-disruptively; the underlying bug is already fixed, this is about the practice
that caught it.

## Observation

When `tls-only` gained `include:` scoping, the check flipped to PASS — but an
independent grep found 2 real plain-HTTP literals the tool missed. Root cause was a
checker bug (comment stripping truncated lines at the first `//`, and `http://`
contains `//`). The false PASS was caught ONLY because the verdict was cross-checked
with a second tool before being trusted.

The heuristic that worked: **when a check's verdict changes after a tool or spec
change (fail→pass especially), or when a fix's first verification is the tool that
was just fixed, confirm with an independent method before recording the result.**
Currently this lives only in `.memory/lessons.md`, which future sessions may not
read at the decision moment.

## Suggested exploration

- Does `archwright-check`'s "Interpret results" section want a short rule like:
  "A verdict that flips after tooling/spec changes is unverified until reproduced
  by an independent method (different grep, manual inspection, second tool)"?
- Alternately/additionally: should the check tool flag verdict flips itself (needs
  a baseline — possibly synergizes with CK-07 baseline work)?

## Evidence

- False-PASS episode: archwright commit 7fcd25a (positional comment matching fix),
  `.memory/lessons.md` "include: globs + comment-stripping false-pass" #2–3
- Fixture canary now guards the specific bug (`endpoint-pinned`); the suggested rule
  guards the CLASS (trusting a just-changed checker's verdict)
