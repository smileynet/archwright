# All-Up Plan: The Discovery Track

Date: 2026-07-18, rev 2 (wizard_of_oz review incorporated). Synthesizes: `.memory/audit/intent-review.md` (goal gaps), the pipeline-split proposal (folded into ADR 0011), the designwright question (stay in-repo), the operator's field-proven UI session prompts, and **`~/code/wizard_of_oz`** — a shipped WoZ-based game-design tool that turns out to be a working discovery-track prototype. Research base: `.memory/research-discovery-*.md` (4 files).

## What wizard_of_oz Changes

wizard_of_oz is a standalone kiro-cli tool (brainstorm → WoZ simulate → design brief → GDD) with two completed field sessions, its own archwright corpus (26 forces, 8 patterns, model, 16 specs), and mechanical validation (`validate-session.py`, release gates). It de-risks this plan in five specific ways:

### 1. The seam contract is already solved — adopt the decision provenance ledger
wizard_of_oz's core mechanism: an **append-only decision ledger** with fixed schema — `D{NNN}` heading, phase, category, origin (`user | suggested | inferred`), decision, rationale (user's words, verbatim), alternatives. Reversals are `SUPERSEDES D{NNN}` entries; the old entry never edited. **One repair direction**: entries are truth, all projections (counts, briefs, documents) regenerate FROM entries, never the reverse — by fiat, so a drifting agent can't invent entries to match a counter. Formalized as `contract:decision-entry` + `constraint:entries-are-truth` in its design corpus; prior art is event sourcing + W3C PROV.

This is a *stronger* seam contract than the plan's "decisions + evidence" sketch: it adds origin taxonomy (WHO decided — the exact provenance archwright's evidence levels want), mechanical validation, and a proven repair direction. Discovery-track artifacts (wireframe decisions, grill answers) should use this ledger format.

### 2. The facilitation stance generalizes — import four patterns wholesale
Four wizard_of_oz patterns are domain-independent facilitation IP, already written in archwright pattern format:

| Pattern | Core move | Generalizes because |
|---|---|---|
| `facilitated-agency` | Origin taxonomy makes AI influence *measurable*; **rubber-stamp guard** (3+ consecutive `suggested` → "what do YOU think?"); decision surfacing every 5–7 | Since LLM compliance can't be enforced, make deviation measurable and self-correcting — true for any HITL design session |
| `invisible-structure` | Run beats/categories/gates internally; show only the subject matter; mirror user vocabulary, zero jargon | Structure and immersion conflict only at the surface — same for web app reviews as for games. Also directly answers intent-review goal 4 (non-technical readability) |
| `propose-dont-force` | Transitions always proposed, never forced; user can jump phases | Matches ADR 0007 gate philosophy |
| `show-dont-interview` (via `wireframe-first`) | Concrete artifact within 2–3 questions; questions asked *while looking at it* | **Empirically validated the hard way**: the original abstraction-first interview was built, pressure-tested, and replaced — designers hand-wave at abstract questions, decide well in front of artifacts (commits 016585f, d473e76) |

This is also the first real test of archwright's "patterns are reusable IP" thesis — cross-project pattern import with citations back to wizard_of_oz's corpus.

### 3. Domain flexibility has a proven architecture — overlays carry the framing
wizard_of_oz embeds game knowledge (MDA aesthetics, core-loop pattern, MLP 3-feature rule, 5-beat pacing, mechanics palette) as skill references. That content is exactly what archwright's **domain overlays** exist to hold. Split: the discovery skill carries the domain-independent process (stance, ledger, artifact-first, coverage pacing); the overlay carries the domain's question frameworks and vocabulary:

| Domain | Discovery framing (overlay content) |
|---|---|
| game | MDA (brainstorm from aesthetics backward), core loop, MLP 3-feature rule, 5-beat coverage gates — **source: wizard_of_oz references, already written** |
| web | JTBD, user flows / red routes, screen inventory — needs research (subagent pass) |
| general | Fallback: goal → artifact → coverage questions |

"Coverage pacing" generalizes: staged gates + diminishing-returns heuristics (same mechanic 3+ times, "same as before", goals met) — beats are the game-domain parameterization.

### 4. The WoZ→behavior-spec path now has its field driver too
A completed wizard_of_oz session (e.g. salvage-run: decision ledger + simulation log + wireframes + GDD) IS the "wizard script" the research flagged as an unexploited spec seed. An export path — session → force evidence + model seed + draft behavior spec with `from_woz:` provenance — has concrete input sitting on disk. Moves from "demand-gated tail" to a schedulable task with a ready-made conformance corpus.

### 5. Relationship verdict (proposed, grill to ratify)
wizard_of_oz **stays a standalone product** (it has its own users, release plan, and identity). Archwright's discovery track *imports its patterns* (with provenance) and *consumes its outputs* (session export). No absorption — same reasoning as the designwright verdict: one-way dependency, no vocabulary fork.

## What the Operator's Workflow Already Got Right (validated against research)

| Practice in the prompts | Research validation |
|---|---|
| ASCII wireframes | Static prototypes suffice for most usability questions [NN/g]; text-based = diffable, version-controlled — same philosophy as Mermaid-first; wizard_of_oz's symbol legend + genre templates are reusable |
| Subagent research before proposing | Matches research-dispatch mandate + grill-with-docs evidence-first pattern |
| Design system before individual screens | Cross-cutting guidance first = pattern-before-instances; prevents per-screen re-litigation |
| One-by-one review w/ rationale, approve each | Grill cadence; evidence-carried-with-artifact graduation gate [dual-track]; upgrade: record each approval as a ledger entry with origin |
| Per-wireframe capture files | Seam artifacts; grill Q-file precedent; upgrade: ledger schema inside each file |

## What Research + wizard_of_oz Add to the Workflow

1. **The artifact-gap annotation**: every wireframe file gets an explicit **"Not resolved here"** section (states, edge cases, error/loading, interaction rules — the #1 handoff failure). That list becomes the model phase's TODO input.
2. **Decision ledger capture** (from wizard_of_oz): approvals/amendments during review recorded as `D{NNN}` entries with origin — rubber-stamp guard active during wireframe review too (3+ consecutive AI-proposed layouts accepted verbatim → prompt).
3. **Show-don't-interview**: first wireframe within 2–3 questions; design-system and detail questions asked while looking at screens, not upfront.
4. **Domain overlay consultation**: framing questions come from the detected domain's overlay; game-UI research feeds validated predicates back through the Extension Protocol.
5. **Technique selection**: wireframes = structural uncertainty; evaluative → WoZ (wizard_of_oz for games; generic WoZ later); generative → forces work.
6. **Freshness on design-system citations**: pattern quality gates apply.

## Specs to Write (`.memory/specs/`, spec-driven-development format)

| Spec | Covers | Notes |
|---|---|---|
| `discovery-track-core.md` | Seam contract (ledger schema, graduation rules, artifact-gap), artifact placement (`design/discovery/<area>/`), facilitation stance (4 imported patterns), coverage-pacing abstraction | The load-bearing spec; ADR 0011 ratifies its decisions |
| `discover-ui-skill.md` | `archwright-discover-ui` skill: research → design system → wireframes → ledger-recorded review loop → seam graduation; templates (wireframe, design-system) | Encodes the operator's two prompts + upgrades |
| `domain-discovery-overlays.md` | `discovery:` section per domain overlay: question frameworks, coverage gates, artifact vocabulary; game sourced from wizard_of_oz, web researched, general fallback | The flexibility requirement lives here |
| `woz-session-export.md` | wizard_of_oz session → archwright seeds: ledger → force/pattern evidence; sim log + wireframes → model seed; draft behavior spec w/ `from_woz:`; conformance corpus = salvage-run session | Schedulable now — field driver exists |

## Tasks (tickets 018+; claim ids per frontier-work protocol)

| # | Task | Depends on | Phase |
|---|---|---|---|
| T0 | **ADR 0011 — discovery track** (post-grill): two tracks/one methodology, seam contract = decision ledger, designwright in-repo w/ split triggers, wizard_of_oz standalone + import/export relationship, artifact placement, gate discipline | grill | D0 |
| T1 | Import facilitation patterns: `skills/archwright-discover-ui/references/facilitation-stance.md` distilling the 4 wizard_of_oz patterns with provenance citations | T0 | D1 |
| T2 | Generic decision-ledger template (`tools/templates/discovery-ledger.md`) adapted from `contract:decision-entry`; category enum domain-parameterized | T0 | D1 |
| T3 | Domain overlay `discovery:` sections — game (port from wizard_of_oz refs), web (subagent research), general (fallback) | T0 | D1 |
| T4 | `archwright-discover-ui` skill + wireframe/design-system templates | T1–T3 | D1 |
| T5 | Field run on the operator's game project; findings → skill edits | T4 | D2 |
| T6 | Steering (Discovery Track section) + AGENTS.md + glossary sync; audit sweep | T4 | D3 |
| T7 | woz-session-export: exporter (skill or tool per grill verdict) + conformance corpus from salvage-run | T0; parallel to T4 | D2+ |

Sequencing: grill → T0 → {T1,T2,T3 parallel} → T4 → {T5, T7} → T6. Estimate: ~5–6 sessions.

## Grill Queue — RESOLVED (2026-07-18, `.memory/grill/discovery-track/`, ADR 0011 Accepted)

1. wizard_of_oz: standalone + import/export; imports are cited snapshots
2. Category enum: core 5 (scope, experience, structure, technical, meta) + overlay extensions
3. Design system: layered — doc permanent in discovery/ui, tensions graduate to patterns, tokens machine-readable + checkable
4. Grills adopt ledger FIELDS (origin, SUPERSEDES) not format; guard calibrated by session type (surfacing in grills, tripwire in creative sessions — agreement with recommendations never penalized)
5. woz-export: exporter tool in wizard_of_oz (session → neutral JSON = inter-project contract); archwright skill interprets. **T7 splits: T7a (wizard_of_oz repo) + T7b (archwright)**
6. LEC-equivalent: golden corpus (process) + conservation check (instance: nothing invented / nothing lost, citation-graph walk). Commit-binding → ticket 018

New task from Q6: **T8 — conservation-check validator rule** for seam artifacts (after T2/T4 define citation fields; own violating fixture per Extension Protocol).

## Demand-gated tail (registered, not scheduled)

| Item | Gate |
|---|---|
| Generic (non-game) WoZ technique in the discovery skill family | First evaluative-uncertainty decision on a non-game project |
| `archwright-plan` feature intake (intent-review goal 6) | Next feature-planning need on a modeled project |
| Concierge/spike intake formalization | First field occurrence |
| Invariant catalog + entity view + visual entry point (intent-review items 1–3) | Independent; invariant catalog remains the cheapest win — note `invisible-structure`'s no-jargon rule is the style guide for these human projections |

## Phase Detail (supplements the task table)

### D0 — ADR 0011 (HITL, post-grill)
Ratifies: two tracks/one methodology (seam = `resolve`); **seam contract = decision ledger** (adopted from wizard_of_oz `contract:decision-entry`: origin taxonomy, append-only, SUPERSEDES reversals, entries-are-truth repair direction) + explicit unresolved list per artifact; designwright stays in-repo (`archwright-discover-*`, split triggers: any 2 of divergent toolchain / independent demand / divergent cadence; if split, consumer never peer); wizard_of_oz stays standalone (import patterns, consume session exports); artifact placement `design/discovery/<area>/` w/ `status: proposed | approved | superseded` + INDEX.md; gate discipline (★★ hard floor applies to discovery-surfaced decisions; discovery queue prioritized by risk/uncertainty). Resolves proposal Q1 (one skill first, rule of two), Q2 (placement), Q4 (evidence-level annotation now, ledger extension deferred).

### D1 — skill + templates (T1–T4)
`archwright-discover-ui` process: (1) subagent research w/ domain overlay consultation, sources tagged; (2) design system — `design/discovery/ui/design-system.md`, every element cites prior art + `serves:` a named force; (3) ASCII wireframes one file each — frontmatter (id, status, serves) + wireframe, design-system elements used, layout rationale, **decision ledger entries** (D{NNN} w/ origin), **Not resolved here** (artifact gap), hands-to (model seed notes); (4) review loop one-by-one — show first, rubber-stamp guard active, approval/amendment recorded as ledger entries, status flips to `approved`; (5) seam graduation — decisions attach to force/pattern evidence, screen-flow graph written as model seed, unresolved lists compiled to model TODO, `--links design/` passes before close. Hard "Does NOT": no behavior specs, no model edits, no skipping per-wireframe approval, no internal vocabulary shown to the user (`invisible-structure`).

### D2 — field runs (T5, T7)
T5: end-to-end on the operator's game project; success = approved wireframes + design system + a model seed the `model` phase actually consumes, with less manual prompting than the current two-prompt workflow. T7: woz-session-export proven against the salvage-run session (its ledger + sim log are the conformance corpus).

### D3 — sync (T6)
Steering Discovery Track section; AGENTS.md skill table + layout; glossary terms (*discovery track*, *seam contract*, *artifact gap*, *decision ledger*); audit sweep (standing practice after shipping interacting features). ADR 0011 supersedes the interim proposal.

## Risks

- **Skill too rigid for creative work** — mitigation: the skill structures capture and gates, never the design conversation itself (wizard_of_oz's `invisible-structure` proves the balance: full internal bookkeeping, zero surfaced machinery)
- **`design/discovery/` becomes a second doc tree that drifts** — mitigation: graduation mandatory (approved decisions MUST thread into forces/patterns); ledger repair direction is one-way by fiat; audit skill scans discovery artifacts from D3
- **Recording overhead degrades conversation flow** — known consequence of the ledger pattern (double bookkeeping per turn); wizard_of_oz field sessions show it's sustainable; watch in T5
- **ASCII wireframes hit fidelity ceiling** (spacing, color, affordance) — accepted: that's the signal for a higher-fidelity technique, out of scope for v1
