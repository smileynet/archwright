---
name: archwright-passup
description: "Route check violations back to the design level that owns them. Consumes structured violations (provenance, contrast pairs, escalation flags), lifts each into the owning level's vocabulary, and routes per confidence. Use after archwright-check finds violations, when deciding whether a failure is a code bug or a design flaw, or when a ★★ invariant broke. Trigger: route violations, pass up, who owns this failure, lift this violation, is this a design problem or a code bug."
metadata:
  type: protocol
  invocation: both
  practice: null
---

# Archwright Passup

The pipeline's upward arc. Check verifies and emits structured violations; this skill lifts them to the level that owns the violated force and routes them per confidence. Hands-down concretizes; pass-up generalizes — same provenance links, opposite direction.

**Core principle:** Pass-up is level-terminating. A signal rises only to the level that owns the violated force, re-expressed in each level's vocabulary at every hop. The height a signal reaches measures how deep the mistake was.

## Input

Structured violations from `python3 tools/archwright-check.py <specs>... --json` (or `archwright-validate.py --json`). Each violation carries:

```json
{
  "spec_id": "...", "invariant": "...",
  "confidence": "★★", "severity": "error", "escalate": true,
  "from_pattern": "pattern:...", "from_force": "...",
  "suggested_route": "fix-implementation | fix-check | fix-spec",
  "contrast_pair": {"expected": "<the rule as the design states it>", "actual": "<the finding>"},
  "evidence": ["file:line:text", ...]
}
```

If handed prose instead of JSON, re-run the check with `--json` — this skill consumes the contract, not transcripts.

## Process

### 1. Triage: the CEGAR fork (spurious vs. real)

For each violation, decide: does this trace/finding reflect the REAL system breaking the design, or an artifact of over-abstraction in the spec/model?

| Signal | Verdict | Action |
|--------|---------|--------|
| Evidence replays against real code/behavior (the file:line really does violate the rule) | **Real** | Continue to lift (step 2) |
| The spec/model abstracted away something the check needs (e.g., a legitimate writer the model never named) | **Spurious** | Refine locally: fix the spec/model at ITS level; no ascent. Route = `fix-spec` |
| The check itself is broken (wrong target path, bad pattern, tool error) | **Check fault** | Route = `fix-check`; repair the check block, re-run. Never touches design |

`suggested_route` from the tool is the heuristic starting point; this triage confirms or overrides it. Spurious counterexamples are not failures — they are the abstraction asking to be refined (promotion: extended-state variable → discrete mode, unnamed writer → named actor).

### 2. Lift: re-express at the owning level

Walk the provenance chain upward: `evidence → invariant → from_pattern → pattern.serves → force`. At each hop, translate the signal into that level's vocabulary (the lift contract, OQ#1 — three components):

1. **Project** — strip detail the parent level doesn't own (file paths, line numbers stay behind as evidence attachments)
2. **Summarize** — name what broke in the parent's terms (trace → "broken verb" → "hollow loop" → "false premise"). This step is AI judgment — the hardest cognitive work in the system (OQ#1's open remainder: can it be made more mechanical?)
3. **Attribute** — pin the signal to the specific force/pattern element that demanded the violated guarantee

**Stop at the first level that owns the violated force.** Do not lift past it:

| The fault is in... | Owning level | Lifted signal reads like |
|--------------------|--------------|--------------------------|
| Code drifted from a correct spec | Implementation | "`fielder.gd:6` writes `ball_holder`; only BallStateService may" |
| Spec mis-states a correct pattern | Spec | "The check forbids X but the pattern's Therefore permits it" |
| Pattern's resolution doesn't survive contact | Pattern | "single-writer resolution breaks under concurrent transfer requests" |
| The force itself was wrong/incomplete | Force (resolve re-opens) | "single-holder assumed no mid-air handoffs — playtests demand them" |

Most violations terminate at Implementation. A signal reaching Force level means the tension needs re-resolution — that is rare and always HITL.

### 3. Route per confidence

Confidence of the violated invariant gates what happens next (the stopping rule — high confidence escalates MORE, not less):

| Confidence | Route | What you do |
|:----------:|-------|-------------|
| ★★ | **Escalate to human — HITL, always stop** | Present the lifted signal + contrast pair + owning level. The human adjudicates: fix implementation, demote the invariant, or re-open the tension. Never auto-fix a ★★ violation, even an "obvious" one — a broken true-invariant is either a real defect or evidence the ★★ was wrongly assigned; both are human calls (ADR 0007) |
| ★ | **Propose fix** | Draft the fix at the owning level (code patch, spec correction, pattern amendment). Present for approval; apply on acceptance |
| — | **Auto-adjust or log** | Fix locally and note it in the span digest. Advisory resolutions absorb signals |

### 4. Dispatch

Hand the routed signal to its owner:

| Route | Dispatch to |
|-------|-------------|
| fix-implementation | Code change (this session or a ticket) — then re-run `archwright-check` |
| fix-check / fix-spec | Repair the spec's check block or abstraction — re-validate, re-check |
| Pattern revision | `archwright-formalize` (amend Therefore/consequences; confidence may demote) |
| Tension re-opened | `archwright-resolve` (HITL — the design decision is being re-made) |

After any dispatch lands: **re-run the check.** Pass-up ends in one of two states — the violation is gone (quiescence for this signal), or it reproduced and the lift terminated too low (lift one level higher and repeat).

### 5. Batch handling

Many violations at once (a full-audit run): classify before lifting. Partition into named failure kinds (same spec, same route, same owning level) and lift each KIND once — do not present 40 raw violations. ★★ violations are never batched away: each gets its own HITL presentation, but grouped in one stop.

## The Payload

The **contrast pair** is the primary artifact at every hop — the violation beside the rule as the design states it. The diff localizes the fault AND carries the fix direction. Present it verbatim at ★★ escalations; use it to draft ★ fixes.

## Does NOT

- Run checks (that's `archwright-check` — this skill consumes its output)
- Decide re-opened tensions (that's `archwright-resolve` — this skill routes to it)
- Auto-fix ★★ violations (HITL gate, ADR 0007 — no exceptions)
- Lift past the owning level (level-terminating — a code bug never reaches the force layer)
- Modify confidence ratings unilaterally (demotion is proposed to the human, a ★★ event)
