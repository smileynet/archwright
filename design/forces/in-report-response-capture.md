---
kind: force
id: in-report-response-capture
polarity: constraint
hardness: soft
evidence_level: L4
source: "discovery:design-system#D005; discovery:wf-overview (bottom bar note)"
serves: [human-owns-judgment, agent-closes-the-loop]
---

# In Report Response Capture

## Statement

Every interaction (approve, option choice, freeform, reroute) must be captured inside the report and terminate in one structured response file — the only return channel.

## Who Feels It

the world (platform limits, prior decisions)

## Evidence

- `discovery:design-system#D005`: "Its interactive controls (approve, option choice, freeform text) record state into an artifact an agent or script can process"
- `discovery:wf-overview (bottom bar note)`: "choices accumulate in the page and export as one structured response file the agent processes. Nothing is sent anywhere — the file is the handoff"
