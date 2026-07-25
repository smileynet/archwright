---
name: archwright-model
description: "Identify domains and model their state machines from resolved patterns. Maps which actors exist, what state each owns, what events they accept/emit, and how they compose. Use when patterns are formalized but specs need a structural foundation. Trigger: model the domains, identify the actors, what state machines exist, domain boundaries."
metadata:
  type: process
  invocation: both
  practice: null
---

# Archwright Model

Identify domains (actors) and model their state machines from resolved patterns. The bridge between WHY (patterns) and WHAT TO CHECK (specs).

**Core principle:** Every pattern resolution implies one or more state-owning actors. Domain modeling makes those actors explicit — their boundaries, their events, their composition relationships. Specs are then projections of actor models, not standalone inventions.

**This phase is MANDATORY — never skip it.** Even patterns that appear to be "just constraints" have enforcement actors with lifecycle. A build pipeline has states (idle → building → passed). A lint rule has a trigger/check/report cycle. A config authority has valid/invalid states. A constraint without an identified enforcer is an unenforced wish. The model phase forces you to ask "who owns this state?" for every pattern — this is what makes specs precise and checkable rather than aspirational.

## Why This Phase Exists

Patterns say: "Resolve by X." (e.g., "Request/validate model for ball possession")
Specs check: "State S must satisfy invariant I."

The gap: WHO owns state S? What are its boundaries? What events does it accept? How does it compose with other actors? Without explicit domain identification, specs are disconnected from each other and from the system's actual structure.

## The Actor Model Lens

From XState/Harel/Hewitt:
- **An actor has encapsulated state** — only it can update its own state
- **Actors communicate via events** — no shared mutable state
- **Actors can spawn/invoke child actors** — composition is hierarchical
- **An actor's lifecycle is tied to its parent's state** — invoked when parent enters a state, stopped when parent exits

In archwright terms:
- Each domain IS an actor (or actor system)
- Each pattern resolution implies actors (the "who" that does the resolving)
- Specs verify properties of individual actors AND properties of their composition

## Process

### 0. Frame the experience layer (do this FIRST)

Before identifying actors, answer: **what user experiences does this architecture protect?**

For each product desire (from the force inventory), write:
```yaml
experiences:
  - id: experience-slug
    desire: desire-id
    who: coach | player | user
    what_user_sees: "One sentence describing what the user experiences when this works correctly"
    protected_by:
      - spec: "kind:spec-id"
        how: "How this spec protects the experience"
```

This section goes at the TOP of the model YAML. It is the entry point for anyone reading the model.

**Why first:** If you can't articulate what experience an actor protects, the actor may be an implementation accident rather than a design necessity.

### 1. Establish domain vocabulary

Name actors in the user's language, not the codebase's language. The model uses domain names; implementation names are a mapping field. Load `../archwright-survey/references/domains/<domain>/scales.yaml` (deployed; domain from the survey intake outline; fallback `general`) for the project's native scale labels and examples.

```yaml
domain_vocabulary:
  - domain_name: "Play Director"           # what a coach would call it
    implementation_name: PlayManager3D      # what the Godot node is called
    role: "Orchestrates 'everyone do this step, now this step'"
```

**Brownfield projects:** When domain vocabulary stabilizes, recommend renaming implementation to match. Add a `rename_recommendations` section listing current→proposed with priority and rationale. Public APIs and signals first, internal variables last.

### 2. Receive input

Formalized patterns (from `archwright-formalize`) with their resolutions and `resolves_into` declarations.

**Discovery model seeds (ADR 0011):** if `design/discovery/*/model-seed.md` exists, consume it BEFORE modeling from scratch — its flow edges, per-screen/actor state, and emitted events are approved decisions, each citing a ledger anchor (`<artifact-id>#D{NNN}`). Carry those citations into the model (they are the provenance the conservation principle checks: seed elements you don't adopt need a stated reason). The seed's compiled Not-Resolved-Here TODOs are this phase's work list — states, edge cases, and transitions discovery deliberately left open.

### 3. Identify actors from patterns

For each pattern, ask:
- **Who owns the state that the resolution introduces?** That's an actor.
- **Who receives events?** That's an actor boundary.
- **Who produces events for others?** That's an actor's public interface.

Pattern resolution language maps to actors:
| Resolution language | Actor identified |
|---|---|
| "X owns Y" | X is an actor; Y is its encapsulated state |
| "Only X may write Y" | X is the single writer actor for Y |
| "A requests, B validates" | A and B are separate actors communicating via events |
| "The system checks Z" | The checker is an actor (or invariant on an existing actor) |

**Constraint patterns also imply actors.** Even "organizational" or "rule" patterns have an enforcement actor with lifecycle:

| Pattern type | Actor to identify | Its state machine |
|---|---|---|
| Pipeline/workflow | The orchestrator (turbo, CI, build script) | idle → running → passed/failed |
| Organizational rule | The enforcer (lint rule, build gate, hook) | trigger → check → report/pass/fail |
| Data constraint | The owner (service, module, config file) | valid/invalid; loaded/unloaded |
| Communication pattern | The router (event bus, dispatcher, registry) | idle → routing → delivered/failed |
| Access control | The gatekeeper (auth layer, permission check) | open/closed; allowed/denied |
| Composition rule | The lifecycle manager (parent, spawner) | creating → active → destroying |

If you cannot identify an enforcement actor for a constraint pattern, flag it: "This constraint has no identified enforcer — it may be aspirational rather than architectural."

### 4. Define actor boundaries

For each identified actor:

```yaml
actor:
  id: ball-state-service
  name: BallStateService                 # implementation class name
  domain_name: Ball Authority             # user-comprehensible name
  owns:
    - ball_holder: StringName
    - transfer_state: enum
  accepts_events:
    - REQUEST_TRANSFER { from_slot, to_slot }
    - BALL_ARRIVED { to_slot }
  emits_events:
    - TRANSFER_STARTED { from_slot, to_slot }
    - TRANSFER_COMPLETED { new_holder }
    - TRANSFER_REJECTED { reason }
  lifecycle:
    invoked_by: practice-execution
    active_during: execution running
  persistence: transient  # durable | transient | session-scoped
  invariants:
    - "at most one holder at any time"
    - "only this actor writes ball_holder"
  user_facing_invariants:
    - "The ball is always visibly somewhere — never disappears or duplicates"
    - "When you throw, the ball always arrives"
```

**Event payload notation:** The `{ field, field }` shorthand in `accepts_events`/`emits_events` is a sketch — it names what the event carries without full typing. The **authoritative typed payload** (types, nullability, required/optional) lives in contract specs produced by `archwright-contract`. The model identifies WHICH events exist and WHO produces/consumes them; the contract phase specifies WHAT they carry in detail.

**Planned vs existing:** When modeling a system that is partly designed-but-unbuilt (ratified decisions, no code), mark unimplemented actors `(planned)` in their `name` and state in the model doc what is checkable TODAY vs what activates later. Downstream spec projections against planned actors carry `target_status: pending` (note it in the model's `spec_projections` entries so derive inherits it). Modeling ahead of code is correct — the specs become acceptance criteria — but an unmarked planned actor produces false "N/A" check results that hide real gaps (field-validated: TileRush tutorial area, 16 pending vs 4 active checks, zero false results).

**user_facing_invariants** are REQUIRED. They describe what the user experiences when the technical invariant holds. If you can't write one, the invariant may not serve a user desire.

### 5. Classify boundary entities

Not everything is a full actor or a pure observer. Three intermediate classifications:

| Classification | Criteria | Example |
|---|---|---|
| **Injected policy** | Shares lifecycle with parent; no independent FSM; read by parent or sibling directly (not via events) | RuntimeBranchState (cursor state, read by policy) |
| **Boundary service** | Facade over external system; no domain events emitted; no state machine; input/output plumbing | PlayerInputSource (wraps InputMap) |
| **Configuration authority** | Immutable reference data; no state transitions; provides config consumed by actors | ActionKindRegistry (action kinds, shapes, rules) |

In the YAML output, group these under `boundary_entities:` (separate from `actors:` and `observers:`).

### 6. Map composition (actor hierarchy)

How do actors relate?

```
PracticeFlowCoordinator (root actor, persistent)
├── SetupFlow (invoked in 'setup' state, stopped on exit)
└── PracticeExecution (invoked in 'running' state)
    ├── PlayManager3D (step orchestration)
    ├── FielderManager3D (spawns per-slot controller actors)
    │   └── FielderController[] (one per slot, invoked/swapped)
    ├── BallStateService (possession state)
    ├── RuntimeBranchState (branch cursor, if branching)
    └── RuntimeUILayer (observer, no state mutation)
```

**When composition is flat:** Not all systems have deep hierarchies. If most actors share lifecycle (all created at session start, all persist until quit), the composition IS flat — document WHY it's flat rather than forcing artificial nesting. Flat composition is common in: single-player games (all systems active for whole session), event-driven architectures (actors communicate via bus, no hierarchy), and early-stage projects (nesting emerges as systems mature). A flat diagram with a rationale note is more honest than forced nesting.

### 7. Map event flows between actors

Which events cross actor boundaries?

```
PlayManager3D → FielderController: assign_chain(chain, generation)
FielderController → PlayManager3D: chain_completed(slot_id, generation)
FielderController → BallStateService: REQUEST_TRANSFER(from, to)
BallStateService → FielderController: TRANSFER_COMPLETED(new_holder)
PlayManager3D → RuntimeBranchState: step_completing(step_index)
RuntimeBranchState → PlayManager3D: next_step(step_index)
```

### 8. Output the domain model

Write to `design/models/` in the target project:

**Machine-readable (for derive):** `design/models/<system>-actors.yaml`
```yaml
actors:
  - id: ball-state-service
    ...
composition:
  root: practice-flow-coordinator
  children: ...
event_flows:
  - from: play-manager-3d
    to: fielder-controller
    event: assign_chain
  ...
contract_candidates:        # identity + direction only — see step 9
  - event: assign_chain
    producer: play-manager-3d
    consumers: [fielder-controller]
  ...
```

**Human-readable (for review):** `design/models/<system>-actors.md`

Must contain:

1. **Composition Diagram** (Mermaid flowchart TB) — actor nesting and lifecycle relationships only. No event labels. Shows "who contains whom." Subgraphs for nesting, solid arrows for invocation, dashed for reads.

2. **Event Flow Diagram** (Mermaid flowchart TB) — flat actor boxes with labeled event arrows. Shows "who talks to whom." Dashed arrows for observer reads. No nesting.

3. **Per-Actor State Machine Diagrams** (smcat preferred, Mermaid stateDiagram-v2 fallback) — one per domain actor that has a non-trivial FSM. Stateless services and trivial actors documented in the boundary table only.

4. **Event Sequence Diagrams** (Mermaid sequenceDiagram) — 2-3 key multi-actor scenarios showing events flowing through the system. Pick scenarios that exercise the most important invariants.

5. **Boundary Decision Table** — why each entity is a separate actor vs boundary entity vs observer, citing the heuristic that determined it.

6. **Key Invariants Summary** — numbered list of cross-actor invariants that are candidates for spec derivation. Each names the actors involved and the pattern source. This list is the primary input to `archwright-derive` (behavioral invariants → behavior/constraint specs). Structural contracts flow to `archwright-contract` via the `contract_candidates` list in the model YAML (step 9) — do not restate them here as spec-ready contracts.

**Why both formats:**
- YAML is for tools (derive reads it to produce specs)
- Markdown+Mermaid is for humans (review, onboarding, discussion)
- They represent the same structural decisions — one phase, two projections
- Mermaid is text-based, version-controlled, diffable, renders in GitHub/Marp

### 9. Point downstream: spec projections and contract candidates

Each actor's invariants become constraint or behavior specs (written by `archwright-derive`):
- Actor state machine → behavior spec (states, transitions, guards)
- Actor ownership rules → constraint specs ("only X writes Y")
- Actor composition rules → dependency specs ("X must not import Y")

Actor events do NOT become contract specs here. Emit a **contract-candidates list** in the model YAML — identity and direction only, never payload shapes:

```yaml
contract_candidates:
  - event: possession_changed
    producer: ball-state-service
    consumers: [fielder-controller, runtime-ui-layer]
```

`archwright-contract` formalizes each candidate into a contract spec (typed payloads, stability, persistence), carrying `from_model:` provenance back to this entry. The `{ field }` shorthand in `emits_events` remains a sketch (see step 4) — the contract phase owns the authoritative shape.

**Name candidates per event leg — never per cluster.** A protocol cluster (e.g., createSurface/updateComponents/updateDataModel) lists ONE candidate per message leg; the C7 cluster exception merges the SPECS (one contract spec may cover all legs), never the candidate identities. Coverage validation joins on event names — a cluster-named candidate matches nothing and reports as uncovered (field-verified). When a candidate's payload will ride inside a sibling event's cluster spec, annotate it `folded_into: <owning-event>` — the link validator then follows the fold for coverage (ticket 013).

**Boundary entities as producers:** a boundary entity (e.g., a configuration-authority) may be named as a candidate's `producer:` — that makes it a valid `from_model:` target for the resulting contract spec. Boundary entities that produce no candidates are not valid `from_model` targets.

**Candidate event names are a global namespace across ALL model files** (ADR 0013, ticket 050). `--links` errors when 2+ models declare the same candidate event. When modeling an area in a multi-model project, prefer area-prefixed names for area-local events (`MEASUREMENT_CELL_RESULT`, not `CELL_RESULT`). If the event genuinely IS one cross-area event (a consumer contract both areas speak), mark EVERY declaration `shared: true` — one contract spec still owns the payload, and a `shared: true` no counterpart repeats draws a warning until the other model lands.

## Rendering Guidance

### Label length
- Transition labels ≤ 30 chars. Move details (guards, actions) to invariant tables below the diagram.
- Participant aliases ≤ 15 chars in sequence diagrams.
- Edge labels on flowcharts ≤ 20 chars. Use abbreviations + legend.

### Notes → Tables
- Do NOT embed pattern attributions or invariants in Mermaid `note` blocks — they render as oversized opaque boxes that dominate the diagram.
- Place invariant/pattern tables in markdown immediately after each diagram.

### Direction hints
- State machines with ≤ 4 states: `direction LR` (compact horizontal)
- State machines with composite states: `direction TB` (vertical flow)
- Composition diagrams: `flowchart TB` (hierarchy flows down)
- Event flow diagrams: `flowchart TB` (data flows down)
- Sequence diagrams: max 8 participants (beyond that, split into focused scenarios)

### Tool selection
- Composition + event flows: Mermaid flowchart via `merman-cli`
- Sequence diagrams: Mermaid sequenceDiagram via `merman-cli`
- Per-actor state machines: `smcat` preferred (purpose-built DSL, better nested state layout, SCXML export). Mermaid `stateDiagram-v2` as fallback.

### Verification
Render all diagrams to PNG before presenting. Fix any parse errors or label truncation. Use:
```bash
merman-cli -i model.md -o model.png -t dark -b transparent
smcat -T png actor.smcat
```
**If `merman-cli`/`smcat` are not installed** (they are external tools, not part of archwright — check with `which`): skip PNG rendering, present the Mermaid/smcat source directly, and note that diagrams are unverified. Do not block the phase on missing renderers. To rehydrate: in the archwright repo `mise install` provides `smcat`; elsewhere `npm i -g state-machine-cat` (PNG output also needs Graphviz `dot`). `merman-cli` is always manual: `cargo install merman-cli`.

## Quality Checks

- Model YAML passes direct validation: `python3 tools/archwright-validate.py design/models/<model>.yaml` (shape-detected by the top-level `actors` key since ticket 048 — no `kind` field needed). This is the phase's flow-through validation gate (ADR 0007); fix errors before presenting. `experiences`/`composition` WARNs are advisory but new models should include both.
- Every pattern's resolution has at least one actor identified
- Every actor has explicit: owned state, accepted events, emitted events, lifecycle
- No shared mutable state between actors (if found → it's an implicit actor that needs naming)
- Composition hierarchy matches the actual scene tree / object ownership in the codebase
- Event flow diagram has no orphan events (every emitted event has a receiver)
- Boundary entities (policy, service, authority) are classified — not force-fit into actor or observer
- Not every actor needs a state machine diagram. Stateless services and trivial actors are documented in the boundary table only.
- Observers are catalogued but do NOT get state machine diagrams (they have no state machine)
- All diagrams render without parse errors and without label truncation

## Domain Boundary Heuristics

How to decide what constitutes a separate domain (actor) vs a region within one actor:

### Split into SEPARATE ACTORS when:

| Heuristic | Test | Source |
|-----------|------|--------|
| **Independent state** | Can this thing's state change without the other noticing? | XState actor model |
| **Independent lifecycle** | Can this thing be created/destroyed without the other? | Harel/XState invoke |
| **Event communication** | Do they communicate via messages, not direct state reads? | Actor model (Hewitt) |
| **Single writer** | Does exactly one entity write this state? | DDD aggregate |
| **Independent language** | Does this thing have its own vocabulary for its states/events? | DDD bounded context |
| **Independent change** | Can you change this thing's logic without changing the other? | Team Topologies ISH |

### Keep as ONE ACTOR (possibly with orthogonal regions) when:

| Heuristic | Test | Source |
|-----------|------|--------|
| **Shared lifecycle** | Created and destroyed together, always | Harel statechart |
| **Shared transaction** | Must change atomically together (consistency boundary) | DDD aggregate |
| **Direct state coupling** | One reads the other's internal state directly | Anti-pattern if separate |
| **Synchronized transitions** | A transition in one ALWAYS requires a transition in the other | Coupled = one machine |

### Use ORTHOGONAL REGIONS within one actor when:

| Heuristic | Test | Source |
|-----------|------|--------|
| **Same lifecycle, independent behavior** | Both created/destroyed together, but their state transitions are independent | Harel 1987 |
| **Occasional sync points** | Usually independent, but occasionally synchronize on shared events | UML composite state |
| **Physical subsystems** | Correspond to different physical aspects of the same entity (e.g., movement + possession + animation) | Harel: "obvious application" |

### Worked Example (FBC Execution)

| Entity | Boundary decision | Reasoning |
|--------|------------------|-----------|
| PlayManager3D | Separate actor | Owns cursor + generation independently; communicates via events only |
| BallStateService | Separate actor | Single writer for possession; independent state machine (held/flight); event communication |
| FielderController (per slot) | Separate actor (spawned) | Independent lifecycle (swappable); owns its chain state privately; event-based completion |
| PlayerCameraRig3D | NOT an actor (observer) | Owns no execution state; only reads public state; presentation boundary, not domain boundary |
| RuntimeUILayer | NOT an actor (observer) | Same as camera — reads state, never writes |
| RuntimeBranchState | Region or injected policy | Shares lifecycle with execution; PlayManager3D reads it for next-step; too coupled for separate actor |

## Does NOT

- Write specs (that's `archwright-derive` — but now it READS the model)
- Write contract specs or payload shapes (that's `archwright-contract` — the model emits contract *candidates* only: event identity, producer, consumers)
- Write patterns (those already exist)
- Implement code (models describe structure, not implementation)
- Choose technology (the model is framework-agnostic; mapping to Godot nodes is implementation)

## Relationship to Existing Pipeline

```
... → formalize → MODEL → contract → derive → check
```

The model phase sits between formalize and derive. It transforms pattern resolutions into explicit actor structures that derive can project into specs.

## From XState to Archwright

| XState concept | Archwright equivalent |
|---|---|
| Machine definition | Behavior spec (YAML statechart) |
| Actor | Domain (state-owning entity) |
| Context | Extended state (typed data guards read) |
| Event | Cross-actor message |
| Invoke | Lifecycle-bound child actor |
| Spawn | Dynamically created actor (e.g., per-slot controllers) |
| Guard | Constraint on transition (from a force) |
| Parallel states | Orthogonal regions in one actor |
| Actor system | The composition hierarchy |
