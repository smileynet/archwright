---
id: 034
title: "Add skeleton spec gate and reflections layer to skills"
status: open
blocked_by: []
---

# Add skeleton spec gate (formalize) and reflections layer (derive)

Two additive skill enhancements from the research synthesis:

## 1. Skeleton spec gate → archwright-formalize/SKILL.md

Add Step 7 after the existing Step 6. A skeleton spec is the simplest possible
check that validates the pattern's Therefore section.

Content:
- One constraint spec targeting the most obvious code location
- Checks the pattern's PRIMARY invariant
- Lives in `design/specs/skeletons/{pattern-id}.md`
- Confidence: — (advisory)
- Runs immediately after writing the pattern
- Pass → proceed; Fail → route back to resolve

Place this BEFORE the "Does NOT" section in the upstream file.

## 2. Reflections layer → archwright-derive/SKILL.md

Add Step 1b between Step 1 and Step 2. Before generating specs, check for
lessons from prior derivation failures:

- Global reflections (`.memory/reflections/` in archwright repo)
- Project reflections (`.memory/reflections/` in target project)
- Boundary rule: methodology-level → global; project-specific → project

## Conformance notes

- Match upstream's heading style (### numbered steps)
- Keep the Discovery-track sections that upstream added (these skills were
  updated by ticket 027 for seam awareness)
- Don't disrupt the existing step numbering beyond the insertion

## Acceptance criteria

- [ ] Step 7 (skeleton gate) in archwright-formalize/SKILL.md
- [ ] Step 1b (reflections) in archwright-derive/SKILL.md
- [ ] No disruption to upstream's ticket-027 additions (discovery-aware sections)
- [ ] Skills deploy cleanly (symlinks live)
