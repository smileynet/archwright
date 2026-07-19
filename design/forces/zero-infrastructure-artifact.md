---
kind: force
id: zero-infrastructure-artifact
polarity: constraint
hardness: soft
evidence_level: L4
source: "discovery:design-system#D005; discovery:design-system (P5)"
serves: [cold-reader-comprehension, actionable-without-literacy]
---

# Zero Infrastructure Artifact

## Statement

The report must travel as a self-contained static artifact — no server, no build step, no network required to read or respond.

## Who Feels It

the world (platform limits, prior decisions)

## Evidence

- `discovery:design-system#D005`: "The report ships as static, self-contained HTML"
- `discovery:design-system (P5)`: "Self-contained single-file HTML: zero build, no webfonts, no JS beyond native <details> + optional filter toggles; travels as a CI artifact"
