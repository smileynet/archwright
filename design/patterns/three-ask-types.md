---
kind: pattern
id: three-ask-types
name: "Three Ask-Types: Decisions, Approvals, Suggestions"
scale: loops-systems
confidence: "★★"
status: active
serves: [human-owns-judgment, agent-closes-the-loop]
context: []
completed_by: [static-report-response-file]
resolves_into:
  - "behavior:ask-lifecycle"
  - "contract:asks-block"
  - "constraint:decisions-never-auto"
---

# Three Ask-Types: Decisions, Approvals, Suggestions

## Problem

**Delegating routine sign-offs keeps the loop efficient, but judgment calls and firm-rule changes must never resolve without a human — and mixing the two raises cognitive load on both.**

## Context

Root pattern for the report's interaction model. Every actionable item the report raises belongs to exactly one ask-type; the ask taxonomy shapes the overview layout, the response file, and the auto-approve machinery.

## Forces

- **Desire:** Humans own every judgment call; routine sign-offs may be delegated per user preference, never by default (`human-owns-judgment`).
- **Desire:** The agent consumes recorded responses and continues work directly (`agent-closes-the-loop`).
- **Constraint (hard):** Genuine ambiguity and ★★ changes always require a human decision — no configuration can bypass this (`hitl-hard-floor`).
- **Constraint (soft):** Delegation is configured per user/machine, off by default (`per-user-delegation`).

## Tension

A single undifferentiated "needs attention" list forces the human to re-triage every item — routine sign-offs bury judgment calls, and any auto-resolution mechanism applied to the whole list would breach the hard floor. But removing the human from everything routine, with no opt-in, silently erodes ownership.

## Evidence

- User decision, verbatim: "both needs attention cases appear to have a clear right answer, these should be framed as 'approvals needed' … consider situations where user needs to make decision/ resolve ambiguity." [design-system#D003]
- User decision, verbatim: "it should be configuratble via local mise settings to auto-approve (off by default)." [design-system#D004]
- Rejected alternative: single undifferentiated "needs attention" list — mixes routine sign-offs with judgment calls, raising cognitive load on both [design-system#D003]
- Rejected alternatives for delegation config: global config file (approval appetite is per-developer/per-machine; mise.local.toml is gitignored by convention); per-run CLI flag only (repetitive for the routine case) [design-system#D004]
- Third tier, approved recommendation: SUGGESTIONS — optional, non-blocking asks that never change the all-clear verdict and never auto-execute; without the tier, trust nudges either block all-clear or vanish (alarm-fatigue risk) [wf-all-clear#D003]
- Decision-situation inventory grounding the taxonomy in existing machinery: recurring FAIL + deferred fixes, escalate-surviving-research-gate, evidence-ledger candidates, proposed baseline entries, persistent skips, ambiguous routes [wf-overview Decision situations table]
- Escape hatch keeps classification honest: every approval detail carries "Review / Amend Rule" that reclassifies the item as a decision, recorded in the response file [wf-issue-detail#D002, #D003]

```yaml
prior_art:
  - title: "Sheridan & Verplank — Human and Computer Control of Undersea Teleoperators (10-level automation scale)"
    year: 1978
    relationship: confirms
    note: "Levels 3-6 map directly to suggestion / approval / veto-window auto-approval — the optionally-auto-approvable refinement is 47 years old."
  - title: "Parasuraman, Sheridan & Wickens — A Model for Types and Levels of Human Interaction with Automation"
    year: 2000
    relationship: confirms
    note: "Automation tier is a property of the individual function/ask, not the system — matches per-ask classification."
  - title: "Feng, McDonald & Zhang — human roles in AI oversight (arXiv:2506.12469)"
    url: https://arxiv.org/abs/2506.12469
    year: 2025
    relationship: confirms
    note: "Names 'approver' as a distinct human role verbatim."
  - title: "GOV.UK RFC-156/167 — Dependabot auto-merge policy"
    year: 2023
    relationship: confirms
    note: "Field example of conditional auto-approval layered on an approval tier (patch/minor + tests + scanning flips human-approve to auto); argues blanket human review was a false sense of security."
  - title: "Approval-fatigue findings in agentic-AI autonomy frameworks (12-Factor Agents Factor 7 et al.)"
    year: 2025
    relationship: extends
    note: "Known failure mode: over-populating the approval tier — approvals must stay rare, targeted, load-bearing. Design lever for the asks derivation."
```


## Therefore

**Classify every ask into exactly one of three types, with autonomy gated per type.** DECISIONS carry genuine ambiguity: options + freeform input + a marked recommendation with fold-out rationale; never auto-resolvable under any configuration. APPROVALS carry a clear right answer: recommendation + sign-off control; auto-approvable via per-user local config (mise.local), off by default; auto-approved items collapse to a log line. SUGGESTIONS are optional nudges: never blocking, never auto-executed, never part of the verdict. Misclassification is user-correctable in place: an approval reroutes to a decision via an intent-labeled control, and the reroute is itself a recorded response.

## Consequences

- The asks derivation must map every source signal (violations, ledger candidates, baseline proposals, skips) to one type — an unmapped signal class is a derivation bug.
- Demands the ask lifecycle behavior spec (raised → presented → responded/auto-approved/rerouted) and the `asks` block contract.
- The ★★ hard floor lives here structurally: ★★-implicated items and ambiguity classify as DECISIONS by construction (`constraint:decisions-never-auto`).
- Cost: three-way classification is a judgment the generator must make per item; the reroute control is the safety valve for getting it wrong.
- Does NOT cover: response-file mechanics (`static-report-response-file`); exact mise variable name/scoping (contract phase).

## Verification

- Constraint check: no code path resolves a DECISION without a recorded human response — `constraint:decisions-never-auto`.
- Behavior check: ask lifecycle transitions respect type-gated autonomy — `behavior:ask-lifecycle`.

## Completion

This pattern is incomplete unless it also contains:
- The response return channel (`static-report-response-file`) — asks without a response path are rhetorical.
