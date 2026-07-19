---
kind: discovery
id: wf-projections
status: approved
area: ui
serves: []
---

# Wireframe: Markdown + JSON Projections

<!-- Not a screen — the two non-web surfaces of design-system#D001, specified
     against the web structure so all three stay projections of one source. -->

## Markdown projection (secondary user docs + agent source)

Mirrors the web drill as document hierarchy — same order, same plain language,
no interactive elements (design-system#D001, #D006):

```
REPORT.md
# Snackbox — Design Check                    (verdict line, run identity)
## How Snackbox works                        (Mermaid state diagram, plain labels)
## Needs attention                           (decisions, then approvals — cards
                                              as sections; options as task lists;
                                              recommendation marked; rationale
                                              as blockquote fold equivalent)
## Step: Taking payment                      (behavior detail per step:
   What happens here / Rules / Protects /    same D006 drill order; "how we
   <details> How we arrived at this)         arrived" inside <details>)
## What isn't verified
## Stability
```

- Agent-consumption notes: deterministic heading anchors per step/rule id;
  the vocabulary map applies (same surface phrases as web) so agent quotes
  match what the human saw.
- Interactive controls degrade to instructions: "to respond, edit
  responses.json or reply in conversation" — markdown never collects input.

## JSON projection (agents/scripts)

- Canonical run document: the existing check output (CK-03 shape) — unchanged.
- Report bundle adds two derived blocks (generation-time, read-only):
  - `model_view`: states/transitions with plain labels + per-element rule
    rollup (the diagram's data)
  - `asks`: decisions/approvals/suggestions with options, recommendation,
    rationale — exactly what the web cards render
- Response file (the user's saved answers): new schema — per-ask id: chosen
  option | approved | freeform text + run identity (commit) it answered.

## Decisions

### D001 — Markdown mirrors the web drill; JSON = canonical doc + derived view blocks + response schema
- **Category:** structure
- **Origin:** suggested
- **Decision:** Markdown is a non-interactive mirror of the web hierarchy (same order, same vocabulary map, `<details>` for folds, deterministic anchors). JSON ships the canonical check document untouched, plus generation-time `model_view` and `asks` blocks; user responses live in a separate response file keyed by ask id + run identity.
- **Rationale:** "approve all" (user, 2026-07-19 session close-out)
- **Alternatives:** Markdown as full inventory dump (jargon, breaks D002); extending the check document itself with view data (rejected — keeps canonical schema pure; views are derived).

## Not Resolved Here

- [ ] Response-file schema details (versioning, partial responses, conflict when code moved since the run)
- [ ] Whether REPORT.md is one file or per-step files for large projects
- [ ] Mermaid vs pre-rendered image in markdown (renderer support varies by host)
- [ ] ask-id stability across runs (fingerprint reuse?)

## Hands To

- **Flow edges:** none — not a screen; surfaces mirror the web structure [cites D001]
- **State owned/shown:** `model_view` join (model elements ↔ specs ↔ status), `asks` derivation from violations/candidates/skips, response schema [cites D001]
- **Events emitted:** none (static projections); response file is the return channel [cites D001]
