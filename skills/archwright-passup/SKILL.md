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

Structured violations from `python3 <archwright-repo>/tools/archwright-check.py <specs>... --json` (or `archwright-validate.py --json`, or `archwright-check.py --trace <spec.yaml> <trace.json> --json` for trace validation — ticket 016). Each violation carries:

```json
{
  "spec_id": "...", "invariant": "...",
  "confidence": "★★", "severity": "error", "escalate": true,
  "from_pattern": "pattern:...", "from_force": "...",
  "suggested_route": "fix-implementation | fix-check | fix-spec",
  "contrast_pair": {"expected": "<the rule as the design states it>", "actual": "<the finding>"},
  "evidence": ["file:line:text", ...],
  "fingerprints": ["<aw/v1 hash>_<n>", ...],
  "baselined": false
}
```

Authoritative schema: `<archwright-repo>/tools/check-output-schema.yaml`. If handed prose instead of JSON, re-run the check with `--json` — this skill consumes the contract, not transcripts.

**`fingerprints` are the violation's stable identity** (aw/v1, CK-07: content-hashed, line-number-independent, aligned 1:1 with `evidence[]`). Use them to recognize "same violation recurring across runs" vs genuinely new findings, and quote them when a human decides to accept debt — they are the keys for `.archwright-baseline.json` entries (which only humans create).

**Baselined violations (`baselined: true`, present when a baseline is active)** arrive pre-classified as accepted debt: severity already dropped to `warning`, excluded from `remaining_delta` and the run's exit gate. Routing: a baselined ★/— violation is LOG-only (span digest, no action). A baselined ★★ still carries `escalate: true` — it maps onto the research gate's "Known + owner-accepted" row with the baseline entry itself as the citation: log it with the entry's `note`, no HITL stop — UNLESS it trips the hard floor (security-material-and-novel, contradicting a ratified resolution), which a baseline entry cannot waive.

**Trace violations route identically to static ones** (scope.mode `trace`): the document carries at most one violation (replay stops at first failure), its `evidence` is the failing trace step (event/position/state) rather than file:line, and untranslatable predicates/guards arrive in `skips[]`. The lift chain is unchanged — invariant → from_pattern → force.

**`skips[]` are NOT routed.** The document may carry a `skips` array ({spec_id, spec_path, invariant, reason}) — pending adapters, untranslatable predicates, vacuous absence claims. A skip is a coverage statement, not a fault: there is nothing to lift and no level to route it to. Surface skips in the span digest so the human sees the coverage gap, and treat a GROWING skip list of one kind as an Extension Protocol signal (a missing adapter or translator capability wants building — pending-with-reason, research, conformance-at-birth).

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

**★★ events first pass through a research gate (ADR 0010) — escalate only what truly needs a human.** Before presenting any ★★ event, research it: prior art, best practices, related specs/patterns/decision records, and the contrast pair itself. Classify:

| Classification | Evidence required | Disposition |
|----------------|-------------------|-------------|
| Check defect / spec noise | Demonstrable defect (e.g., pattern matches an asset filename, wrong target) | Propose the spec/check fix (★-style propose); note in span digest. No HITL stop |
| Known + owner-accepted | A matching decision record, baseline entry, or work-queue item — cite it | Log with the reference in the span digest. No HITL stop |
| Genuine new decision | Neither of the above — a tradeoff, scope change, or novel security judgment | **Escalate (HITL)** — WITH the research summary and a recommended disposition. Never a bare violation |

Classification requires POSITIVE evidence — ambiguity defaults to escalate. **Hard floor (always blocks, research or not):** irreversible actions, security-material-and-novel findings, or anything contradicting a ratified resolution. Every classified-away ★★ goes in the span digest for end-of-span human review.

| Confidence | Route | What you do |
|:----------:|-------|-------------|
| ★★ | **Research gate above, then escalate genuine decisions — HITL** | Present the lifted signal + contrast pair + owning level + research + recommendation. The human adjudicates: fix implementation, demote the invariant, or re-open the tension. Never auto-FIX a ★★ violation, even an "obvious" one — noise/known dispositions PROPOSE or LOG, they don't silently change design artifacts (ADR 0007 + 0010) |
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
- Auto-FIX ★★ violations (ADR 0007/0010 — research may classify them as noise/known and propose or log, but never silently change design artifacts)
- Escalate a bare ★★ violation without the research pass + recommended disposition (ADR 0010)
- Lift past the owning level (level-terminating — a code bug never reaches the force layer)
- Modify confidence ratings unilaterally (demotion is proposed to the human, a ★★ event)
