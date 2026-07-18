# ADR 0011: The Discovery Track

**Status:** Proposed (2026-07-18) — pending grill ratification (`.memory/grill/discovery-track/`)
**Refines:** ADR 0007 (the HITL/flow-through partition this ADR names as two tracks). Extends the pipeline upstream of `resolve`; changes nothing downstream of it.
**Source:** Operator directive 2026-07-18 ("a design pipeline… vs a pure archwright pipeline that is largely mechanical"), research synthesis (`.scratch/research/`, 4 tracks), wizard_of_oz corpus review, operator's field-proven UI session prompts. Plan: `.scratch/discovery-track-plan.md`.

## Context

Archwright's pipeline (survey→check) captures and verifies *existing* intent. The HITL-dense creative work that *generates* intent — grill sessions, UI wireframes, Wizard-of-Oz simulation, concierge tests, spikes — happens today as ad-hoc prompting outside the methodology, with no artifact contract into it. Research across three traditions (dual-track agile, agent orchestration, EDA flows) converges: separate the *kinds of work*, never the process/ownership — split-into-two-pipelines is dual-track's founding failure mode ("duel track" mini-waterfall), multi-pipeline agent architectures cost ~15x tokens with coordination failures as the largest failure class, and EDA's creative/mechanical boundary is a repeating ladder, not one wall.

A working prototype exists: wizard_of_oz (`~/code/wizard_of_oz`) — a shipped, twice-field-run WoZ game-design tool, itself archwright-modeled (26 forces, 8 patterns, 16 specs), whose decision-provenance ledger and facilitation patterns solve this ADR's hardest sub-problems.

## Decision

**One methodology, two tracks, one seam.**

1. **Two tracks, named.** The *discovery track* (HITL-dense, divergent: grill, wireframes, WoZ, concierge, spikes, future feature intake) and the *verification track* (the existing survey→check pipeline, flow-through per ADR 0007). Same agent, same repo, same `design/` artifact space. No new pipeline, no new agent, no design branches.

2. **The seam is `resolve`.** Discovery outputs enter the pipeline as pre-resolved tensions with evidence (already ADR 0007's batched-confirmation path). Discovery hands over **resolved decisions + evidence + an explicit unresolved list — never bare artifacts** (wireframes/prototypes are evidence; the decision record is the deliverable).

3. **The seam contract is the decision ledger**, adopted from wizard_of_oz `contract:decision-entry`: append-only `D{NNN}` entries carrying phase, category, **origin (user | suggested | inferred)**, decision, rationale (user's words, verbatim), alternatives; reversals via `SUPERSEDES D{NNN}` (old entry never edited); **one repair direction** — entries are truth, every projection regenerates from them. Prior art: event sourcing, W3C PROV.

4. **Facilitation stance imported** from wizard_of_oz patterns with provenance: `facilitated-agency` (origin taxonomy + rubber-stamp guard: 3+ consecutive `suggested` → "what do YOU think?"; decision surfacing every 5–7), `invisible-structure` (machinery internal, subject-matter language only — no jargon to the user), `propose-dont-force` (transitions proposed, never forced), `wireframe-first`/show-don't-interview (concrete artifact within 2–3 questions; questions asked while looking at it — empirically validated when wizard_of_oz's abstraction-first interview failed pressure-testing and was rebuilt).

5. **Every discovery artifact carries an artifact-gap section** ("Not resolved here": states, edge cases, error/loading, interaction rules). The gap list is a first-class output — it becomes the model phase's TODO input.

6. **Domain flexibility via overlays.** The discovery skill family carries domain-independent process (stance, ledger, artifact-first, coverage pacing with diminishing-returns heuristics); `tools/domains/<domain>/` gains a `discovery:` section holding the domain's question frameworks (game: MDA/core-loop/MLP/5-beat, ported from wizard_of_oz; web: researched; general: fallback). Games are accommodated first; nothing game-specific lives in the skill.

7. **Placement:** discovery artifacts live in the target project at `design/discovery/<area>/`, one file per artifact, frontmatter `status: proposed | approved | superseded`, INDEX.md per area (grill precedent). Graduation is mandatory: on approval, decisions thread into force/pattern evidence and model seeds; `--links` must pass. Discovery artifacts join the audit skill's scan scope.

8. **Gate discipline:** discovery inherits consequence-based gating — the ★★ hard floor (ADR 0010) applies to discovery-surfaced decisions; the discovery queue is prioritized by risk/uncertainty, not value/effort (delivery prioritization applied to discovery is a named dual-track failure mode).

9. **Project boundaries:** discovery stays **in-repo** as a skill family (`archwright-discover-*`) — no separate "designwright" project (one-way schema dependency; rule-of-two; vocabulary-fork risk). Named split triggers (any 2 → revisit): divergent toolchain, independent demand for discovery-without-specs, divergent release cadence; if split, designwright is a schema consumer, never a peer. **wizard_of_oz stays standalone**: archwright imports its patterns (cited) and consumes its session exports (`from_woz:` provenance); no absorption.

## Consequences

- New skill family starting with `archwright-discover-ui` (operator's UI workflow, upgraded); specs + task graph in `.scratch/discovery-track-plan.md` (T0–T7).
- `steering/archwright-conventions.md` gains a Discovery Track section (seam contract, gate list, queue discipline); glossary gains *discovery track, seam contract, decision ledger, artifact gap*.
- wizard_of_oz session export becomes the first `from_woz:` behavior-spec seed path — conformance corpus: the salvage-run session (Extension Protocol applies: violating scenario required).
- Recording overhead: the facilitator does double bookkeeping (conversation outward, ledger inward) — accepted; wizard_of_oz field sessions show it sustains. Watch in the first field run.
- `.scratch/pipeline-split-proposal.md` is superseded by this ADR once accepted.

## Rejected Alternatives

- **Two separate pipelines / separate design phase:** dual-track's documented failure mode (handoffs, mini-waterfall); re-litigated and rejected with three independent research tracks.
- **Separate designwright project:** premature (zero instances built), creates cross-repo schema versioning + silent staleness (observed with claude/codex skill copies), invites vocabulary fork.
- **Absorb wizard_of_oz:** it has its own users, release plan, identity; absorption gains nothing the import/export relationship doesn't.
- **Free-form capture (no ledger):** unparseable for graduation, no origin audit, no rubber-stamp guard — wizard_of_oz rejected free-prose notes for the same reasons with field evidence.

## Open Items (grill queue — dispositions to ratify)

| # | Question | Recommended disposition |
|---|----------|------------------------|
| Q1 | wizard_of_oz relationship | Standalone + import/export (Decision 9) |
| Q2 | Ledger category enum | Fixed core + domain-extension via overlay `discovery:` section |
| Q3 | Design-system artifact placement | `design/discovery/ui/design-system.md` (discovery artifact, graduates evidence into patterns) |
| Q4 | Grill sessions adopt the ledger format? | Yes — unify capture across discovery techniques (Q-files become ledger-bearing) |
| Q5 | woz-export: skill or tool? | Tool for the mechanical parse (ledger is regex-parseable) + skill for interpretation |
| Q6 | LEC-equivalent for agent transforms; commit-binding of seam evidence | Golden-corpus conformance (per Extension Protocol); commit-binding deferred to its own ticket |
