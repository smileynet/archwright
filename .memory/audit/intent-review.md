# Intent Review — Original Goals vs. Current State

Date: 2026-07-18. Point-in-time assessment at e72382d (suite green). Scratch note — promote conclusions to tickets/ADRs if acted on.

## The Original Goals

1. Make visible all current intent existing as documentation and code
2. Raise conflicts between different documents and code
3. Highlight gaps between "planned" and "implemented" work
4. Core application logic readable by non-technical people, in four quadrants:
   State Machine · Data Models · Interfaces · Invariants
5. Visual-first, layered rendering (C4-like) — low cognitive load, no pages of text
6. Proactive planning helper: desired feature → required changes → downstream-agent work with clear guidance and success criteria

## Verdicts

| # | Goal | Verdict | Evidence |
|---|------|---------|----------|
| 1 | Intent visibility | ✅ Met | survey → forces → formalize pipeline; force files as provenance root; field-proven (DynamoRush) |
| 2 | Doc/code conflicts | ✅ Met | `archwright-audit` (contradictions, stale refs, planned-as-current); `check` catches drift continuously; `passup` routes to owning level |
| 3 | Planned vs implemented | ✅ Mostly | audit's planned-as-current + missing-coverage categories; SKIP-with-reason; baseline separates known debt from new (remaining_delta ratchet) |
| 4 | Non-technical readability | ⚠️ Half | Strong for state machines + interfaces; weak for data models + invariant catalog (see below) |
| 5 | Visual-first, layered | ⚠️ Partial | Diagrams exist and are mandated, but as projections *after* text — not the primary interface; no C4-style zoom layers |
| 6 | Proactive planning | ❌ Unbuilt | Pipeline is retrospective (capture) + corrective (passup); no forward path from "I want X" to a change plan |

## Detail

### Goals 1–3: the verification spine — strong

This is where the project's investment went, and it shows. Intent capture has full provenance (force → pattern → spec → check violation and back). Conflict detection is both point-in-time (audit) and continuous (check with fingerprints, baseline, evidence ledger). The planned/implemented gap is machine-tracked: SKIPs carry reasons, baselines ratchet down, pending adapters are registered, never silent.

Framing caveat on G3: gaps are expressed as *design-vs-code* drift, not roadmap-vs-shipped. There's no standing "gap dashboard" — findings are per-run reports. Adequate, but a product owner wanting "what's promised but not built" gets it indirectly.

### Goal 4: the four quadrants — audit per quadrant

| Quadrant | State | Gap |
|----------|-------|-----|
| **State Machine** | ✅ Best-served. Model phase mandates per-actor FSM diagrams (smcat/Mermaid) + MD companion; behavior specs are the machine layer beneath | Rendering depends on optional tools; fallback is raw Mermaid source (not lay-readable) |
| **Interfaces** | ✅ Good. Event-flow + sequence diagrams; contracts carry producer/consumer direction | — |
| **Data Models** | ❌ Weak. Contract specs are YAML, machine-primary, *event-payload* oriented. Nothing presents "what information is stored and how it's grouped" as logical entities for a lay reader | No entity/ER-style projection exists at all |
| **Invariants** | ⚠️ Scattered. Invariants live inside behavior + constraint specs; contrast pairs make *violations* comprehensible; confidence (★★/★/—) is exactly the trust-boundary vocabulary the goal asks for | No consolidated, human-facing **invariant catalog** — a non-technical person cannot see the safety/trust boundary in one place |

The deep insight: the *machinery* for goal 4 exists (everything is typed, linked, projectable), but the **projection for non-technical readers was never built**. Current artifacts serve agents and engineers.

### Goal 5: visual-first — inverted

Current posture is text-first, visual-as-projection ("diagrams are projections of the model — they don't add information"). That principle is correct for consistency, but the *reading path* still enters through markdown. Missing:

- A layered entry point (C4-ish): system context → actors/composition → per-actor state machines → invariants. `system-overview.md` (reconciliation deliverable) is the closest thing, but it only exists for monorepo runs.
- A rule that every `design/` output leads with the diagram and follows with tables — some model docs do this, it isn't enforced.

### Goal 6: proactive planning — the missing half of the product

Everything built so far answers "does the code honor the design?" Nothing answers "I want feature X — what has to change?" The resolve skill explicitly punts planning to `spec-driven-development`.

Yet the raw material is uniquely good for this: a feature request could be diffed against the domain model (which actors/events/contracts are touched), scored against invariants (what must not break), and emitted as work items whose success criteria *are* the derived specs — machine-checkable definition of done for a downstream agent. That closes the loop the whole modeling investment implies: model → plan → implement → check → passup.

This would be a new pipeline capability (new KIND of thing, not a new instance) → per two-tier governance it needs an ADR + HITL, not just a skill file.

## Candidate Work (not committed — jotted)

Ordered by leverage-per-effort:

1. **Invariant catalog projection** (small). Mechanical: walk specs, group invariants by experience/force served, render one `design/invariants.md` with confidence badges. Pure projection — no new decisions. Directly closes the G4 trust-boundary gap.
2. **Visual entry point** (small-medium). Generalize `system-overview.md` beyond reconciliation: every pipeline run ends with one layered, diagram-led front door in `design/`. Extend diagram/model skills' output contract.
3. **Data-model (entity) view** (medium). New projection from contracts + actor owned-state: logical entities, grouping, who owns what. Needs a small design decision (entities vs. events framing) — worth a grill question first.
4. **`archwright-plan` — feature intake phase** (large, highest value). Feature request → model delta → affected invariants → work items w/ spec-derived success criteria. Needs ADR (new pipeline phase, new artifact kind) + field driver. This is goal 6 wholesale.

## One-line Summary

The verification spine (goals 1–3) is built and field-proven; the comprehension layer (4–5) is half-built — engineered for agents, not yet projected for humans; the forward-planning loop (6) is absent and is the natural next act.
