# ADR 0007: Pipeline Gates Block Only Where Human Input Is Needed

**Status:** Accepted (2026-07-16)
**Supersedes:** the "STOP after every phase" rule in Pipeline Phase Discipline (steering/archwright-conventions.md, AGENTS.md), introduced with the phase-discipline conventions.

## Context

The pipeline (`survey → forces → tensions → resolve → formalize → model → contract → derive → check`) mandated a hard stop after **every** phase: "present the phase output, ask whether to proceed — never auto-advance." Rationale: "skipping review compounds errors silently."

Evidence against universal stops (A3 dry run, `.memory/audit/pipeline-dryrun.md`):
- On a fully pre-resolved project, the resolve stop added a full human turnaround with zero new decisions made (finding 4).
- The stops that were supposed to protect quality did not: the fixture violates formalize/derive quality gates (evidence ≥70%, `protects_experience` on all specs) while sailing through every checkpoint — human checkpoints are review-*availability*, not review-*necessity*, and in practice reviewers rubber-stamp mechanical phases (finding 2).
- The phases where human judgment genuinely changed outcomes in past runs: resolve (decisions), grilling (unknown forces), and violation adjudication (★★).

## Decision

Classify every gate as **HITL-blocking** or **flow-through**:

| Transition | Class | Why |
|------------|-------|-----|
| survey → forces | flow-through | Intake outline is descriptive; errors are cheap and visible downstream |
| forces → tensions | flow-through* | *EXCEPT inferred product desires (L4/L5) — those require the existing HITL validation gate in archwright-forces |
| tensions → resolve | flow-through | Clustering is reversible restructuring |
| **resolve** | **HITL-blocking** | Decisions are the human's. Pre-resolved tensions still stop, but as ONE batched confirmation, not N sequential asks |
| resolve → formalize → model → contract → derive | flow-through | Mechanical elaboration of ratified decisions, gated by validation (below) |
| derive → check | flow-through | Checking is safe by construction |
| **end of span** | **HITL-blocking** | Final acceptance — human reviews the span digest |
| **any ★★ event** | **HITL-blocking** | ★★ violation found, ★★ confidence assigned beyond what resolve ratified, or ★★ demotion proposed → stop immediately |
| **fog** | **HITL-blocking** | Unknown forces / unresolved tension encountered mid-span → stop (grill needed) |

Flow-through advance requires ALL of:
1. **Pre-authorized span** — the human named the run span ("run forces through derive"). Auto-advance never crosses the span boundary. Absent an explicit span, the old per-phase behavior applies.
2. **Mechanical validation passes** — the phase's artifacts pass `archwright-validate.py` (schema + links). Validation failure = stop, not silent retry past the gate.
3. **Digest entry written** — every auto-advanced phase appends its artifact list + notable judgments to the span digest, presented in full at the end-of-span gate.

## Consequences

- Turnaround on mature/pre-resolved projects drops from ~9 round-trips to 2 (resolve confirmation + final digest).
- The original rationale is answered with enforcement rather than ceremony: mechanical validation actually checks artifacts between phases (the old stops never did), and the digest preserves full review surface — batched, not eliminated.
- Risk accepted: an error in a flow-through phase can propagate within a span before the human sees it. Bounded by span size, validation gates, and the ★★/fog tripwires.
- Skills' per-phase "present and STOP" language becomes span-aware (survey updated now; residual per-skill language normalized in B5).
- Quality gates remain honor-system until tooling enforces them (Phase 5 CK-01 extension / A3 finding 2) — this ADR makes that gap more important, not less.

## Rejected Alternatives

- **Keep universal stops:** pure latency on mechanical phases; A3 shows the review they promise doesn't actually happen.
- **Fully autonomous pipeline (no gates):** violates "the human decides" (ADR 0001's division of labor) and the ★★ escalation contract.
- **Confidence-threshold auto-advance (stop only when any ★ artifact created):** nearly every phase touches ★ artifacts; degenerates to universal stops.
