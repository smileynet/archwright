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

### 1. Receive input

Formalized patterns (from `archwright-formalize`) with their resolutions and `resolves_into` declarations.

### 2. Identify actors from patterns

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

### 3. Define actor boundaries

For each identified actor:

```yaml
actor:
  id: ball-state-service
  owns:
    - ball_holder: StringName       # encapsulated state
    - transfer_state: enum          # (idle, in_flight, rejected)
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
  invariants:
    - "at most one holder at any time"
    - "only this actor writes ball_holder"
```

### 4. Map composition (actor hierarchy)

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

### 5. Map event flows between actors

Which events cross actor boundaries?

```
PlayManager3D → FielderController: assign_chain(chain, generation)
FielderController → PlayManager3D: chain_completed(slot_id, generation)
FielderController → BallStateService: REQUEST_TRANSFER(from, to)
BallStateService → FielderController: TRANSFER_COMPLETED(new_holder)
PlayManager3D → RuntimeBranchState: step_completing(step_index)
RuntimeBranchState → PlayManager3D: next_step(step_index)
```

### 6. Output the domain model

Write to `design/models/` (or inline in pattern documentation):

```yaml
# design/models/execution-actors.yaml
actors:
  - id: play-manager-3d
    ...
  - id: ball-state-service
    ...
  - id: fielder-controller
    ...

composition:
  root: practice-flow-coordinator
  children: ...

event_flows:
  - from: play-manager-3d
    to: fielder-controller
    event: assign_chain
  ...
```

### 7. Derive specs FROM the model

Each actor's invariants become constraint or behavior specs:
- Actor state machine → behavior spec (states, transitions, guards)
- Actor ownership rules → constraint specs ("only X writes Y")
- Actor composition rules → dependency specs ("X must not import Y")
- Actor event contracts → contract specs (event payload shapes)

## Quality Checks

- Every pattern's resolution has at least one actor identified
- Every actor has explicit: owned state, accepted events, emitted events, lifecycle
- No shared mutable state between actors (if found → it's an implicit actor that needs naming)
- Composition hierarchy matches the actual scene tree / object ownership in the codebase
- Event flow diagram has no orphan events (every emitted event has a receiver)

## Does NOT

- Write specs (that's `archwright-derive` — but now it READS the model)
- Write patterns (those already exist)
- Implement code (models describe structure, not implementation)
- Choose technology (the model is framework-agnostic; mapping to Godot nodes is implementation)

## Relationship to Existing Pipeline

```
... → formalize → MODEL → derive → check
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
