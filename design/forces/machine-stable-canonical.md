---
kind: force
id: machine-stable-canonical
polarity: constraint
hardness: soft
evidence_level: L4
source: "discovery:design-system (P1); discovery:wf-projections#D001"
serves: [agent-closes-the-loop]
---

# Machine Stable Canonical

## Statement

Agents and scripts require one stable, parseable canonical run document whose shape never varies by audience.

## Who Feels It

the world (platform limits, prior decisions)

## Evidence

- `discovery:design-system (P1)`: "JSON is canonical; web and markdown are one-way projections regenerated from it — never edited, never merged sideways"
- `discovery:wf-projections#D001`: "JSON ships the canonical check document untouched, plus generation-time model_view and asks blocks"
