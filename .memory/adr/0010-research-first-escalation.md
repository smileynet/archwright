# ADR 0010: Research-First Disposition for ★★ Events

**Status:** Accepted (2026-07-17)
**Refines:** ADR 0007 (which classified any ★★ event as HITL-blocking). This ADR does not repeal the gate — it inserts a mandatory research pass before it and narrows what reaches the human.
**Source:** Operator directive, ticket 007 (`.tickets/007-research-first-escalation.md`): "We should only escalate on issues that truly need human intervention. We should first try to resolve through researching related topics, best practices, prior art, etc."

## Context

ADR 0007 made every ★★ event an unconditional HITL stop. Field evidence (ExposeAR run, 2026-07-17) showed this over-fires: a ★★ `no-tracked-secrets` violation blocked on an icon PNG named `Res_Credentials_48_Dark.png` — the contrast pair already contained everything needed to classify it as check noise. Bare-violation escalations spend the human's attention on dispositions the agent could research.

The confidence stopping rule (finding 8) says high confidence escalates MORE — that remains true. What changes is the QUALITY of the escalation: research is preparation for the human's decision, not a substitute for it.

## Decision

Before presenting any ★★ event, the agent MUST run a research pass — prior art, best practices, related specs/patterns/decision records, contrast-pair analysis — and classify the event:

| Classification | Disposition | HITL? |
|----------------|-------------|-------|
| **Check defect / spec noise** — the check or spec is wrong, not the system (e.g., pattern matches an asset filename) | Propose the spec/check fix through normal channels (★-style propose; fix is applied on acceptance, batched into the span digest) | No stop |
| **Known + owner-accepted** — matches an existing decision record, baseline entry, or work-queue item | Log with the reference; note in the span digest | No stop |
| **Genuine new decision** — a tradeoff, scope change, or novel security judgment | Escalate WITH the research summary and a recommended disposition attached — never as a bare violation | **Yes — blocks** |

**Hard floor (always blocks, research or not):** anything irreversible, security-material-and-novel, or contradicting a ratified resolution. Demotion proposals and ★★ assignments beyond what resolve ratified remain HITL per ADR 0007.

**Unchanged:** ★★ violations are never auto-FIXED silently. The first two dispositions propose or log — they do not apply changes to design artifacts without the accept/digest path.

## Consequences

- `archwright-passup` step 3 gains the research pass and classification table; HITL presentations carry research + recommendation.
- Conventions' "HITL-blocking gates" ★★ row is amended: "any ★★ event" → "any ★★ event classified (after a research pass) as a genuine new decision, plus the hard floor."
- The span digest gains ★★-disposition entries (what was classified away from HITL and why) — the human reviews these at span end, preserving batched oversight of the agent's classifications.
- Risk accepted: the agent may misclassify a genuine decision as noise. Mitigations: the hard floor, digest review at span end, and the rule that classification requires positive evidence (a matching record, a demonstrable check defect) — ambiguity defaults to escalate.

## Rejected Alternatives

- **Keep unconditional ★★ HITL (status quo):** field-proven to over-fire; erodes the gate's signal value.
- **Drop the ★★ gate entirely:** repeals finding 8's stopping rule; novel security judgments must block.
- **Threshold-based (auto-classify by violation count/age):** mechanical rules can't distinguish noise from novel decisions; research + positive evidence can.
