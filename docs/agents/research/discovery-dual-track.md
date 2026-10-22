# Dual-Track Discovery/Delivery Separation in Product & Design Methodologies

Research date: 2026-07-18. Question: how do product/design methodologies separate discovery (creative, human-intensive) work from delivery (mechanical, execution) work — how are tracks split, what gates connect them, and how does the split fail?

## Summary

Mature product methodologies (dual-track agile, the Double Diamond, Teresa Torres's continuous discovery) all separate discovery from delivery as **two kinds of work, never two kinds of people** — the same team runs both tracks in parallel, with discovery staying 1–2 iterations ahead of delivery. The connecting gate is always an **evidence-based readiness criterion** (validated assumptions, a defined problem statement, behavioral test results), not phase completion or document sign-off. The dominant failure mode across all three traditions is the same: the split degrades into a handoff between separate groups ("mini-waterfall"), or the discovery track silently collapses when delivery pressure spikes.

## Details

### How the tracks are split

**Dual-track agile (Sy 2007 → Patton → Cagan).** Two continuous, parallel streams inside one team: a discovery track (validating what to build via research, prototypes, experiments) and a delivery track (building validated work at sustainable quality/velocity). Discovery runs 1–2 sprints ahead of delivery, feeding it a backlog of evidence-backed items [L4:established — ideaplan, Gothelf, Patton]. Patton is explicit that "no one really named it dual-track" as a process with two teams — it's "two kinds of work, and there's no way around it," done by one team; a product trio (PM, designer, tech lead) *leads* discovery but the whole team participates [L4:reported — jpattonassociates.com]. Ant Murphy adds the operational split: two backlogs — an **opportunity backlog** (things not yet discovered) and a **development backlog** (validated items reshaped into stories) — and risk-proportional discovery: low-risk items (UI tweaks, bug fixes) skip discovery entirely because building is the cheaper way to learn [L5:reported — antmurphy.me].

**Double Diamond (UK Design Council, 2004–2005).** Splits along a different axis: **problem space vs. solution space**, each traversed by a divergent (explore widely) then convergent (narrow to a decision) phase — Discover→Define (first diamond), Develop→Deliver (second diamond). The creative/human-intensive work is the divergent halves; the convergent halves are where decisions crystallize into executable direction [L4:established — Design Council via Wikipedia, courseux, dovetail]. Note the second diamond still contains creative work (Develop is divergent solution exploration); "Deliver" is the only mechanically-flavored quadrant.

**Continuous Discovery Habits (Torres, 2021).** Rejects phase separation entirely: discovery is a weekly *habit* running permanently alongside delivery — weekly customer touchpoints, continuous assumption testing, small experiments. Structure comes from the **Opportunity Solution Tree**: outcome → opportunities (customer needs/pains) → solutions → assumption tests. The product trio does discovery AND stays accountable for delivery — the separation is temporal (weekly cadence) and artifactual (the tree), never organizational [L4:established — producttalk via ideaplan, greatquestion, shortform]. Torres also emphasizes bidirectional flow: "the best teams also work bottom-up — they use their assumption tests to evaluate their solutions and evolve the opportunity space" [L5:reported — quoted via antmurphy.me].

### Gates connecting the tracks

- **Readiness criteria (dual-track):** work graduates from discovery to delivery "only when it has been validated through behavioral evidence, not just when someone is confident it is the right thing to do" [L5:reported — Gothelf/senseandrespond.co]. The handoff happens at defined integration points (sprint planning), where the trio presents the graduating item WITH its evidence — what was tested, what was observed — and engineers interrogate it before accepting. Sprint review is the reverse gate: discovery shares validated/invalidated findings alongside the delivery demo, both treated as equally valuable output.
- **Problem definition (Double Diamond):** the pinch-point between the diamonds is a defined problem statement / design brief — you may not enter solution exploration until the problem is converged. This is a synthesis gate, not an evidence gate.
- **Assumption tests (Torres):** no big gate; instead many small ones — each solution on the tree carries explicit assumptions, and an assumption must be tested (cheaply, weekly) before the solution earns engineering investment. Confidence accumulates continuously rather than passing a single checkpoint.
- **Discovery's definition of done is directional, not exhaustive** (Murphy): the exit question is "do we have enough confidence to build something small?" — not "is the design complete?" Discovery output is direction + confidence, and discovery is equally about killing ideas (its output includes binned opportunities).

### Failure modes of splitting

1. **Mini-waterfall / "duel track."** The original Sy (2007) model "essentially manifested as mini-waterfall handoffs between distinct teams" [L5:reported — devsquad.com]; Patton's essay title ("Dual Track Development is not Duel Track") names the anti-pattern: discovery people vs. delivery people, adversarial handoffs, engineers excluded from learning. Every modern treatment insists on one team precisely because the two-team version was tried and failed.
2. **Discovery collapse under delivery pressure.** "The most common failure mode... when deadlines loom, the discovery track is the first thing deprioritized... within two or three sprints the delivery track is building features that have not been properly validated" [L5:reported — Gothelf]. Countermeasure: discovery capacity as *protected sprint budget* (e.g., a fixed 30% that is off the table), not slack.
3. **Conflating discovery with design.** Discovery validates assumptions; design solves a validated problem. Teams that jump from hypothesis straight to prototype "are running waterfall with extra steps" — the tell is discovery producing design artifacts instead of validated insights [L5:reported — Gothelf].
4. **Linear/one-shot discovery ("project discovery").** Treating discovery as a phase whose output is a guaranteed-correct solution. Discovery raises odds (Cooper's research: problem-first is ~2.5× more likely to succeed than solution-first) but is "by no means a slam dunk" — hence continuous, not stop-start [L5:reported — Murphy citing Cooper, *Winning at New Products*].
5. **Diagram-literalism (Double Diamond).** The model is widely misread as linear left-to-right; the Design Council's 2019 revision ("Framework for Innovation") added explicit iteration loops because practitioners kept treating the diamonds as sequential stage gates [L4:established — Wikipedia/Design Council].
6. **Cadence tax (Torres).** The weekly discovery habit fails "not because teams reject the framework but because the recruiting, scheduling, and synthesis tax makes the weekly cadence physically impossible" [L6:reported — getperspective.ai, a vendor with an AI-tooling interest; treat as directional].
7. **Wrong prioritization model leaking across tracks.** Discovery backlogs must be prioritized by *risk/uncertainty* (which wrong assumption hurts most), delivery backlogs by value/effort — applying the delivery calculus to discovery items quietly starves the riskiest questions [L5:reported — Gothelf].

### Cross-cutting synthesis (relevance to archwright)

- The consensus is that discovery and delivery are **different kinds of work with different validation logics** (uncertainty-reduction vs. execution-quality), and the boundary must be an **evidence gate carried WITH the artifact** at the handoff — closely analogous to archwright's confidence-gated patterns and provenance-carrying specs.
- All three traditions keep the creative track continuous and route delivery feedback *back into* discovery (Torres's bottom-up tree evolution, dual-track's sprint-review learning loop) — structurally the same shape as archwright's pass-up/re-resolve loop.
- The universal failure is separating people rather than work: the moment discovery output becomes a document thrown over a wall, the evidence chain breaks. Archwright's "one agent holds the whole pipeline, HITL only at decision gates" maps to the "one team, two tracks" resolution.

## Sources

- [L4:established] Jeff Patton, "Dual Track Development is not Duel Track" (2017) — https://www.jpattonassociates.com/dual-track-development — origin story, one-team principle, trio-leads-whole-team-participates
- [L4:reported] Marty Cagan, "Dual-Track Scrum," SVPG — https://svpg.com/dual-track-scrum/ — parallel nature; delivery need not wait for fully-defined backlog
- [L5:reported] Jeff Gothelf, "Dual-Track Agile: Managing Discovery and Delivery in a Single Sprint," Sense & Respond Learning (2026) — https://www.senseandrespond.co/blog/dual-track-agile — readiness criteria, integration points, protected-budget countermeasure, pitfalls (read in full)
- [L5:reported] Ant Murphy, "Dual Track: Continuous Discovery & Delivery" (2024) — https://www.antmurphy.me/newsletter/dual-track-continuous-discovery-amp-delivery — opportunity vs. development backlogs, risk-proportional discovery, Cooper citation (read in full)
- [L4:established] Wikipedia, "Double Diamond (design process model)" — https://en.wikipedia.org/wiki/Double_Diamond_(design_process_model) — Design Council origin, divergent/convergent structure, 2019 revision
- [L4:reported] Dovetail, "The Design Process Framework Explained" — https://dovetail.com/design-thinking/double-diamond-model/ — diverge/converge per diamond
- [L4:reported] Ideaplan, "Teresa Torres' OST Framework" — https://www.ideaplan.io/frameworks/opportunity-solution-tree — outcome→opportunity→solution→experiment structure
- [L5:reported] Great Question, "Continuous discovery habits" — https://greatquestion.co/blog/continuous-discovery-habits — the five habits enumerated
- [L6:reported] DevSquad, "What Is Dual-Track Agile?" — https://devsquad.com/blog/dual-track-agile — Sy-era mini-waterfall characterization
- [L6:reported] getperspective.ai, "Continuous Discovery Habits in 2026" — https://getperspective.ai/blog/continuous-discovery-habits-in-2026-operationalizing-teresa-torres-s-framework-with-ai-conversations — cadence-tax failure claim (vendor source, directional only)
- Primary sources not read directly (cited via the above): Desiree Sy, "Adapting Usability Investigations for Agile User-Centered Design," *JUS* (2007); Teresa Torres, *Continuous Discovery Habits* (2021); Robert G. Cooper, *Winning at New Products*.

## Open Questions

1. **Quantified gate criteria:** none of the sources give operational thresholds for "validated" (sample sizes, effect sizes, confidence levels) — the readiness gate is culturally enforced, not mechanically checkable. Is anyone formalizing it?
2. **Applicability to solo/AI-augmented work:** all frameworks assume a team (trio) and weekly human-customer contact; how the split maps when an AI agent performs the mechanical delivery track and one human owns discovery is unexplored in these sources.
3. **Torres primary source:** the OST's rules for when a solution graduates to delivery (vs. more assumption tests) should be checked against *Continuous Discovery Habits* itself rather than secondary summaries.
4. **Design Council 2019 revision:** worth reading the "Framework for Innovation" directly for how they retrofitted iteration/loops onto the diamond — analogous to archwright's flow-through vs. HITL gate distinction.
5. **Protected-capacity numbers:** the 30% discovery budget figure appears in one source without evidence; is there research on the right discovery/delivery capacity ratio?
