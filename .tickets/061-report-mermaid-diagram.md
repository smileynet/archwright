---
id: "061"
title: "Report: client-side Mermaid diagram rendering in HTML"
status: open
blocked_by: []
priority: high
---

# Report: client-side Mermaid diagram rendering

## Problem

The report's front door is designed to be an interactive statechart diagram (wf-all-clear#D004, design-system#D006). Currently the HTML renders a `<ul>` bullet list of state names because smcat cannot be invoked from Python's subprocess on Windows (extensionless binary issue, ticket 059).

The markdown already emits correct Mermaid `stateDiagram-v2` syntax with labeled arrows. The HTML should render the same diagram visually — without requiring any external binary at report-generation time.

## What to build

1. Embed Mermaid.js in the self-contained HTML (inline the library — constraint:no-server-dependency means no CDN)
2. Emit a `<pre class="mermaid">` block with the stateDiagram-v2 source (same as REPORT.md)
3. Mermaid initializes on page load and renders the diagram as inline SVG
4. Remove the smcat rendering path (or keep as optional upgrade when smcat is available)
5. Multi-actor: render the primary actor's diagram (first with transitions), with tabs or accordion for others

## Constraints

- P5: self-contained single-file HTML, zero build, file:// works
- no-server-dependency: no CDN links, no fetch calls
- The inlined mermaid.js adds ~300KB gzipped — acceptable for a report artifact

## Acceptance criteria

- [ ] Report HTML renders a visible statechart diagram with nodes and labeled edges
- [ ] Works in Firefox and Chrome when opened via file://
- [ ] No external network requests (fully self-contained)
- [ ] Lacrosse-bosse report shows the step-transition lifecycle as a visual diagram
- [ ] Dark mode: diagram respects the page color scheme
- [ ] Fallback: if JS is disabled, the Mermaid source text is readable as-is
