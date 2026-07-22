---
id: 018
title: "Commit-binding of check evidence (EDA signoff precedent)"
status: done
blocked_by: []
---

# Commit-binding of check evidence

## Context

Grill discovery-track Q6 (2026-07-18, `.memory/grill/discovery-track/Q06-lec-equivalent-commit-binding.md`) deferred this to its own ticket. EDA precedent: signoff evidence binds to a frozen commit hash; ANY change invalidates it (`.memory/research-discovery-eda-mde.md`). Archwright check evidence (evidence ledger events, baseline entries, span digests) currently carries timestamps but no code-state identity — a pass recorded at commit A silently "vouches" for commit B.

## What to build

Add code-state identity to check evidence:

1. Check runs record the git commit hash (+ dirty flag) in `--json` output and evidence-ledger events.
2. Consumers (passup, digest, future report command) can distinguish evidence-at-this-commit from stale evidence.
3. Decide staleness semantics: hard invalidation (EDA-style) is likely too aggressive for continuous development — investigate "evidence decays on changes under the spec's check.target" as the softer archwright-native rule (reuses CK-19's changed-only affectedness logic).

## Acceptance criteria

- [x] `--json` check output includes `code_state: {commit, dirty}` (schema updated in check-output-schema.yaml)
- [x] Evidence ledger events carry code_state; dedup identity unchanged (grill if this needs revisiting)
- [ ] Staleness rule decided (grill or ADR note) and documented in the check skill
- [x] Fixture coverage: evidence event carries commit; dirty-tree flagged
- [x] git-absent behavior: SKIP-with-reason on the field, never a crash (matches CK-19's exit-2-on-git-failure only when scoping REQUIRES git)

## Notes

- Not discovery-track work — verification-track enhancement. No blockers either direction.
- Relates: ADR 0009 (evidence ledger), CK-07/08 (baseline fingerprints), CK-19 (affectedness logic).
