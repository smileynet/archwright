---
kind: pattern
id: static-report-response-file
name: "Static Report, Response File Return Channel"
scale: loops-systems
confidence: "★"
status: active
serves: [human-owns-judgment, agent-closes-the-loop]
context: [canonical-doc-projections, three-ask-types]
completed_by: []
resolves_into:
  - "contract:response-file"
  - "constraint:no-server-dependency"
---

# Static Report, Response File Return Channel

## Problem

**Recording human responses demands interaction, but the report must remain a static self-contained artifact — no server, no build step, no network.**

## Context

In the context of `canonical-doc-projections`, this pattern owns the return direction: how the asks raised by `three-ask-types` get their answers back to the agent.

## Forces

- **Desire:** Humans own judgment calls — their responses must be captured faithfully (`human-owns-judgment`).
- **Desire:** An agent consumes the responses directly and continues work (`agent-closes-the-loop`).
- **Constraint (soft):** The report travels as a self-contained static artifact — readable and answerable with no infrastructure (`zero-infrastructure-artifact`).
- **Constraint (soft):** Every interaction terminates in one structured response file — the only return channel (`in-report-response-capture`).

## Tension

Interactive response collection normally implies a server (endpoints, sessions, persistence); a static file normally implies read-only. Choosing a server breaks CI-artifact distribution and cold-reader zero-setup; choosing pure read-only turns every ask into an out-of-band conversation the agent can't reliably consume.

## Evidence

- User decision, verbatim: "let's start with static html that records state to something an agent can process, as a backlog item we'll explore a live gui" [design-system#D005]
- Rejected/deferred alternatives: local companion server (`--serve` + localhost endpoint) — deferred to the live-GUI backlog item; agent-only interaction without a report artifact [design-system#D005]
- Prior art — self-contained static reports as CI artifacts: Playwright self-contained HTML report (2024); coverage.py static htmlcov (2024) [design-system Principles P5]
- Mechanism, approved: "choices accumulate in the page and export as one structured response file the agent processes. Nothing is sent anywhere — the file is the handoff" [wf-overview#D006 + bottom-bar note]
- Rejected alternatives for accumulation: per-card immediate export (one file per decision is agent-hostile); auto-save to browser storage only (no visible handoff moment) [wf-overview#D006]
- Identity requirement: responses key to ask-ids stable across runs — direction is aw/v1 fingerprint reuse — plus the run identity (commit) they answered [model-seed Derived Data; wf-projections JSON section]

## Therefore

**In-page state accumulation exporting one structured response file.** The report ships as static, self-contained HTML (no webfonts, no JS beyond native `<details>` and small vanilla handlers). Interactive controls (approve, option choice, freeform text, reroute) accumulate state in the page; a response bar appears once any control is used and offers one action — save the structured response file. The file keys each entry by ask-id (aw/v1 fingerprint lineage) and records the run identity (commit) it answered. The agent discovers and processes the file; nothing is transmitted. A live served GUI is an explicit backlog item, out of this pattern's scope.

## Consequences

- Demands the response-file contract (schema, versioning, partial-response and staleness semantics — contract phase owns the details).
- The response file becomes a first-class pipeline input: the agent's next run must consume or explicitly defer every recorded response.
- Response conflicts (code moved since the run) resolve at consumption time using the recorded run identity — same soft-staleness stance as commit-binding (code_state).
- Cost: no live validation or immediate effect — the human's answers take effect only when an agent processes the file.
- Does NOT cover: live-GUI interaction (backlogged); where the report/response files live in a target project (model/contract settle the home dir).

## Verification

- Constraint check: the report bundle has no server/network dependency — `constraint:no-server-dependency` (no fetch/XHR/websocket usage; opens from file://).
- Contract check: exported response files validate against `contract:response-file`.

## Completion

This pattern is complete at its scale once the response-file contract exists; the live-GUI backlog item would extend, not replace, it.
