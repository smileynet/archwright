# Low-Fidelity Design Validation Techniques: Process Placement & Downstream Artifacts

Research date: 2026-07-18. Question: Where do low-fidelity validation techniques (UI wireframes, Wizard of Oz prototyping, concierge tests) fit in a structured design process, and what artifacts do they hand downstream?

## Summary

Low-fidelity validation techniques divide cleanly by what kind of uncertainty they resolve. Concierge tests are **generative** (problem-space: learn *what* to build), Wizard of Oz is **evaluative** (solution-space: validate *whether* a specific concept works before building the technology), and wireframes are **structural** (layout, hierarchy, flow — cheap to rethink, signaling "still open"). In the Design Sprint framing (Understand → Sketch/Ideate → Decide → Prototype → Validate), wireframes live in Sketch/Decide, WoZ and clickable prototypes live in Prototype/Validate, and concierge tests sit even earlier — pre-sprint discovery or problem-framing. The downstream handoff from each is NOT the artifact itself but the **decisions it de-risked**: validated flows, response/behavior scripts, demand signals, and a shrunk solution space. A recurring finding [L4:established]: the biggest handoff failure is the "artifact gap" — low-fi artifacts intentionally omit states, edge cases, error handling, and interaction rules, and those get decided during development unless explicitly documented at handoff.

## Details

### Technique → phase mapping

Using the Design Sprint's canonical phases (Understand → Sketch → Decide → Prototype → Validate) [L4:established — Atlassian, Figma, Lyssna all agree; Figma adds a "Define" phase] as the reference structured process, and the Lean Startup discovery/validation split for pre-sprint work:

| Technique | Phase | Uncertainty it addresses | Fidelity of the *question*, not the artifact |
|---|---|---|---|
| **Concierge test** | Discovery / problem-framing (pre-sprint, or Understand) | "What should the solution even be?" — problem-solution fit | Generative: no fixed hypothesis yet; human openly delivers the value, adapts per user |
| **UI wireframes (low-fi)** | Sketch → Decide | "Is this the right structure/flow/hierarchy?" | Structural: which screens exist, what's on them, how they connect. Low-fi deliberately signals "still movable, cheap to rethink" (figr.design) |
| **Wizard of Oz prototype** | Prototype → Validate | "Will users actually use this specific solution as intended?" — solution viability, esp. for complex/costly tech (conversational UI, recommendations, real-time lookup, AI) | Evaluative: fixed interface, hidden human simulates the backend; yields realistic behavioral data |
| **Concierge → WoZ sequencing** | — | Learning Loop explicitly recommends concierge FIRST (generate the solution hypothesis), then WoZ (hide the human, test whether the concept "still flies") | The lean-startup ordering: generative before evaluative |

Key placement rules from sources:
- **WoZ is mid-stage, not earliest-stage.** "Best used after you've identified a viable solution — not in the earliest discovery phase" [L4:established — Learning Loop; NN/g agrees: use it when static prototypes can't answer the question]. Using WoZ too early "might lock you into a suboptimal concept."
- **NN/g scoping rule:** most usability questions DON'T need WoZ — "a prototype with static content will be more than sufficient." Reserve WoZ for interfaces whose value is dynamic response (chatbots, learning algorithms, real-time data) [L4:verified — NN/g 2024].
- **Concierge results must not be read as validation.** The white-glove human touch inflates satisfaction (false-positive bias); concierge converges *toward* a hypothesis, it does not prove one [L4:established — Learning Loop, Kromatic].
- **Wireframes precede prototyping** in every process surveyed: define requirements → sketch → wireframe → review/iterate → handoff to prototyping (mockflow, letsgroto).

### Handoff artifacts (what flows downstream)

The critical insight across sources: what hands downstream is primarily **resolved decisions plus the evidence for them**, with the artifact as carrier. Concretely:

**From wireframes → prototyping/development:**
- The validated screen inventory, layout hierarchy, and navigation flow
- What wireframes deliberately DON'T carry — and must be added before dev handoff or they get decided ad-hoc during implementation: hover/loading/error/empty states, edge cases, responsive breakpoints, interaction rules, data assumptions, accessibility requirements (adora.so; figr.design calls this the "Artifact Gap") [L4:established]
- Modern guidance treats handoff as "a conversation about logic and behavior," not a file transfer (Miro) — annotated wireframes/wireflows with behavior notes are the actual handoff unit

**From a Wizard of Oz study → design/build:**
- The **study protocol** itself is a durable artifact: task list, the response set the wizard used (closed/hybrid method), decision trees for system behavior, tone-of-voice guidelines (NN/g). This is effectively a first draft of the system's *behavioral contract* — what the real backend must produce
- Observed behavioral data: which flows users took, where they stalled, what responses satisfied them → feeds requirements and conversation/interaction design
- Feasibility boundary: NN/g explicitly says involve engineers in crafting wizard responses so the simulation stays within what's buildable — the vetted response set doubles as a feasibility-checked spec seed
- Demand/viability signal (Zappos pattern): usage, conversion, willingness to pay before the technology exists

**From a concierge test → product definition:**
- Rich qualitative findings: which pain points matter, which service steps create the value, what to cut
- A candidate solution hypothesis (the input WoZ then evaluates)
- Willingness-to-pay evidence if the manual service was charged for
- A map of the manual workflow — which becomes the automation roadmap ("swap in automation module-by-module")

**From the Design Sprint Validate phase generally:**
- Test findings against the sprint's long-term goal and sprint questions; a go/no-go/iterate decision; the prototype is explicitly disposable — the *learning* is the deliverable (Atlassian, Figma)

### What decisions each technique resolves

| Technique | Decisions resolved | Decisions explicitly NOT resolved |
|---|---|---|
| Concierge | Is the problem worth solving? What does the solution need to do? Which features matter? Will people pay? | Whether a self-service/automated version works (human touch biases the signal); UI specifics |
| Wireframes | Information architecture, screen flow, content hierarchy, layout; team alignment on scope while change is cheap | Visual design, micro-interactions, states/edge cases, technical feasibility |
| Wizard of Oz | Desirability + usability of a specific dynamic concept; what system responses satisfy users; whether to invest in the expensive technology; realistic usage behavior | Technical feasibility/performance of the real backend; scale economics; anything a static prototype could have answered cheaper |

### Relevance note (archwright context)

The generative/evaluative split maps well onto archwright's vocabulary: concierge tests operate at the **forces** level (discovering desires), WoZ operates at the **check** level for not-yet-built systems (validating a resolution against real user behavior before implementation exists), and the WoZ study protocol (response sets, decision trees) is a proto-**behavior spec** — human-simulated transitions that later become the machine-checked state machine. Low-fi wireframes' "still movable" signal parallels confidence tiers: a wireframe is a — /★ artifact by design.

## Sources

- [L4:verified] [NN/g — The Wizard of Oz Method in UX](https://www.nngroup.com/articles/wizard-of-oz) (Paul & Rosala, 2024) — when to use, study protocol contents, closed/open/hybrid response methods, engineer involvement, origins (Norman & Munro 1973, Kelley 1983). Read in full.
- [L4:verified] [Learning Loop — Concierge vs. Wizard of Oz Experiments](https://learningloop.io/blog/concierge-vs-wizard-of-oz) (Toxboe, 2025) — generative vs evaluative framing, sequencing, signal-quality bias, comparison table, Zappos/Aardvark/CardMunch/Wealthfront examples. Read in full.
- [L4:reported] [Atlassian — Understanding the 5 Key Phases of Design Sprints](https://www.atlassian.com/agile/design/design-sprint) — understand/sketch/decide/prototype/validate structure. Snippet only.
- [L4:reported] [Figma — How to run a design sprint](https://www.figma.com/blog/how-to-run-a-design-sprint/) — six-phase variant (adds Define). Snippet only.
- [L5:reported] [figr.design — Low-fidelity wireframes](https://figr.design/blog/low-fidelity-wireframes) and [Design-to-dev handoff problems](https://figr.design/blog/design-to-dev-handoff-problems) — low-fi as "still open" signal; the Artifact Gap (missing states, tokens, breakpoints, interaction rules). Snippets only.
- [L5:reported] [adora.so — Wireframe to production](https://www.adora.so/blog/wireframe-to-production-closing-the-gap-with-a-visual-source-of-truth/) — what wireframes can't communicate; those details get decided during development. Snippet only.
- [L5:reported] [Miro — Design Handoff Best Practices](https://miro.com/prototyping/design-hand-off/) — handoff as logic/behavior conversation, not file transfer. Snippet only.
- [L5:reported] [mockflow — Wireframing: 5 Stages, Reviews, and Handoff](http://mockflow.com/blog/wireframing-process) — requirements → sketch → wireframe → review → iterate → handoff sequence. Snippet only.
- [L4:reported] [Google Developers — Conversation design: test and iterate](https://developers.google.com/assistant/conversation-design/test-and-iterate) — WoZ as "the MVP of prototypes for voice testing." Snippet only.
- [L4:reported] [CMU/Dow et al., IEEE Pervasive 2005](https://www.cs.cmu.edu/~spdow/files/AEL-IEEEPervasive05.pdf) — WoZ helps designers avoid lock-in to a design or incorrect assumptions. Snippet only.
- [L5:reported] [Smashing Magazine — The Wizard of Oz Method for UX Research](https://www.smashingmagazine.com/2025/07/unmasking-magic-wizard-oz-method-ux-research/) (Yocco, 2025) — relevance to agentic AI. Snippet only.

## Open Questions

1. **Is the WoZ study protocol ever formally treated as a spec seed?** Sources describe response sets and decision trees, but none document a pipeline where the wizard's script becomes the acceptance criteria / behavioral spec for the built system. This looks like an unexploited handoff.
2. **Who owns closing the Artifact Gap?** Sources agree the gap (states, edge cases, breakpoints) causes handoff failure, but disagree on remedy — annotated design files (figr), a "logic layer" doc (Miro), or overlapping designer/dev cycles (inspiringapps). No consensus artifact format.
3. **Concierge in enterprise/internal-tool contexts** — nearly all concierge examples are consumer startups (Zappos, Wealthfront, Food on the Table). How the method adapts when the "customer" is an internal stakeholder is undocumented in these sources.
4. **WoZ signal validity for AI products** — Smashing (2025) flags WoZ's renewed relevance for agentic AI, but a human wizard may be *better* than the eventual model, reintroducing the concierge false-positive bias inside an evaluative method. Threshold unexamined.
5. **Quantitative thresholds** — no source gives sample sizes or decision criteria for "validated" in a WoZ/sprint Validate phase; go/no-go remains judgment-based.
