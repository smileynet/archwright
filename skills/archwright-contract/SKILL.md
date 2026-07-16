---
name: archwright-contract
description: "Derive typed data contracts from a domain model. Takes actor definitions and produces state schemas, event payload contracts, interface surfaces, and persistence schemas. Use when a model exists but data shapes haven't been formalized. Trigger: define the contracts, what data shapes exist, what do events carry, what persists."
metadata:
  type: process
  invocation: both
  practice: null
---

# Archwright Contract

Derive typed structural contracts from a domain model. The bridge between WHO owns state (model) and WHAT that state looks like as typed data.

**Core principle:** Data models are derived from behavior, not designed independently. The model phase made the creative decisions (what actors exist, what they own, how they communicate). This phase mechanically projects those decisions into checkable contract specs.

## The Pipeline Position

```
... → formalize → model → CONTRACT → derive → check
```

- **Model** answers: "Who owns what state? Who talks to whom?" (creative)
- **Contract** answers: "What does that state look like? What do those messages carry?" (mostly mechanical)
- **Derive** answers: "What temporal/invariant properties must hold?" (mechanical)

## Process

### 1. Receive input

The domain model (from `archwright-model`):
- `design/models/<system>-actors.yaml` — actor definitions with `owns:`, `emits_events:`, `accepts_events:`, `lifecycle:`
- `contract_candidates:` — the model's list of cross-boundary events (event name, producer, consumers) awaiting formalization. **This phase is the sole producer of contract specs** — the model names WHICH events exist; this phase decides WHAT they carry. Every candidate must end up in exactly one contract spec (or an explicit skip note).

### 2. For each actor, produce structural specs

Route by actor element:

| Model element | Contract spec to produce | Mechanical? |
|---|---|---|
| `actor.owns` (typed fields) | **State schema** — field names, types, ranges, nullability, initial values | Yes |
| `actor.emits_events` (with payload) | **Event payload** — field names, types, required/optional, producer/consumers | Yes |
| `actor.accepts_events` (input surface) | Covered by emitting actor's event payload | — |
| `actor.lifecycle: persistent` | **Persistence schema** — which fields survive save/load, versioning | Creative (one decision: authoritative vs reconstructible) |
| Public/internal classification | **Interface surface** — which events/methods are stable public contract | Creative (one decision per event/method) |

### 3. State schemas

For each actor that has `owns:` fields, produce a contract spec:

```yaml
kind: contract
id: <actor-id>-state-schema
from_patterns: ["pattern:<source-pattern>"]
from_model: "model:<actor-id>"          # provenance back to the model entry
confidence: "<inherited from pattern>"

fields:
  <field_name>:
    type: <type>        # string | int | float | bool | enum | reference | list | map
    required: <bool>
    nullable: <bool>    # can this be null during valid states?
    initial: <value>    # starting value
    min: <value>        # numeric range (if applicable)
    max: <value>
    values: [...]       # enum values (if applicable)
    description: "<what this field represents>"
    from_force: <force-id>

lifecycle:
  - state: "<actor state from behavior spec>"
    invariant: "<what must be true about these fields in this state>"
```

**The derivation is mechanical:** If the model says `owns: {cooldown: float}`, the contract spec declares `cooldown: {type: float, min: 0.0, max: 300.0, initial: 0.0}`. Ranges come from the behavior spec's guards (if `guard: cooldown == 0` is a transition condition, then 0.0 is a boundary value).

### 4. Event payload contracts

For each entry in the model's `contract_candidates:` (every event that crosses an actor boundary):

**Granularity rule — the spec unit is the independently-evolving contract:**
- **Default: one contract spec per event type.** Independent events evolve independently; each gets its own file and lifecycle.
- **Sanctioned exception — protocol cluster:** the tightly-coupled messages of ONE protocol, owned by one authority actor, that evolve in lockstep (e.g., the request/accept/reject legs of a single transfer protocol — the request leg produced by the counterparty belongs to the same protocol). Cluster specs are **named for the protocol** (`ball-possession-events`), not the system.
- **Prohibited: per-system grand event files.** Never collect a system's unrelated events into one `<system>-events.yaml` — that shared artifact kills independent evolution and muddies git history.

```yaml
kind: contract
id: <event-name>              # or <protocol-name>-events for a protocol cluster
from_patterns: ["pattern:<source-pattern>"]
from_model: "model:<producer-actor-id>"   # provenance to the model's candidate entry

events:
  <event_name>:               # one event by default; a cluster lists its lockstep siblings
    producer: <actor-id>
    consumers: [<actor-ids>]
    payload:
      <field_name>:
        type: <type>
        required: <bool>
        nullable: <bool>
        description: "<what this field carries>"
    stability: public | internal
```

**Stability classification (the one creative decision):**
- `public` — consumers rely on this shape. Changing it is a breaking change. Requires versioning.
- `internal` — implementation detail. May change without notice. Consumers should not rely on it.

**Heuristic:** If the event crosses a bounded-context boundary OR is consumed by code you don't control (addon, external team), it's public. If it's consumed only within the same actor system, it's internal.

### 5. Persistence schemas

For each actor where `lifecycle:` indicates durable state (persists across save/load, session restart, or zone exit/entry):

```yaml
kind: contract
id: <actor-id>-persistence-schema
from_patterns: ["pattern:<source-pattern>"]

persisted_fields:
  <field_name>:
    type: <type>
    required: <bool>
    description: "<why this must persist>"
    reconstructible: false  # Cannot be recomputed on load

excluded_fields:
  <field_name>:
    reason: "<why this doesn't need persisting>"
    reconstructible: true  # Can be recomputed from persisted state

versioning:
  strategy: <additive | migration | envelope>
  current_version: 1
```

**The creative decision:** For each owned field, ask: "If the game crashes and reloads, must this field be restored from disk, or can it be reconstructed from other persisted state?" The answer determines what goes in `persisted_fields` vs `excluded_fields`.

**The heuristic (from game state serialization research):**
> Persist only authoritative state that cannot be reconstructed deterministically.

- Transient UI state → excluded (reconstructible from game state)
- Cached/derived values → excluded (recomputable)
- Player choices/progress → persisted (authoritative)
- World mutations → persisted (authoritative, cannot be replayed)
- AI blackboard state → depends (if deterministic from world state, exclude)

**When NO persistence is needed:** Produce a brief "no-persistence" document noting that all state is transient. This is itself a structural commitment — it means consumers must not assume state survives across sessions.

### 6. Interface surfaces (optional — for systems with multiple consumers)

When an actor has consumers it doesn't control (external addons, other teams, future extensions):

```yaml
kind: contract
id: <actor-id>-interface
from_patterns: ["pattern:<source-pattern>"]

public_interface:
  methods:
    - name: <method>
      params: {<name>: <type>, ...}
      description: "<what this does>"
      stability: public
  signals:
    - name: <signal>
      payload: {<name>: <type>, ...}
      stability: public

internal:
  methods: [<list of internal methods>]
  signals: [<list of internal signals>]
  note: "Implementation detail — do not connect to or call directly"
```

**Skip this for actors with only one consumer or purely internal communication.** Interface surfaces are worth specifying only when there's a real risk of external coupling to internal details.

### 7. Validate

- Every state schema field traces to the model's `owns:` declaration
- Every model `contract_candidates` entry is covered by exactly one contract spec (or an explicit skip note)
- Every event payload matches the model's `emits_events` signature; every contract spec carries `from_model:` provenance
- Event specs follow the granularity rule: one per event type, protocol clusters named for the protocol, no per-system dumping grounds
- Persisted fields are a subset of owned fields (can't persist what you don't own)
- Stability annotations exist for all cross-boundary events
- No contract spec duplicates information already in a behavior spec (state schemas describe SHAPE, behavior specs describe TRANSITIONS — complementary, not overlapping)

### 8. Present for review

Present the batch grouped by actor:

```
## BallStateService
- State schema: 3 fields (ball_holder, in_flight, requester)
- Events: 3 (possession_changed, transfer_rejected, request_transfer) — all public
- Persistence: none (transient)

## PlayManager3D  
- State schema: 5 fields (resolved_play, objectives, current_step, chains_complete, total_chains)
- Events: 2 (step_completed, run_finished) — both public
- Persistence: none (session-scoped)
```

**Ask:** "Are the stability classifications (public/internal) correct? Any persistence decisions to override?"

## Output Location

Contract specs are written to `design/specs/` alongside behavior and constraint specs, **organized per owning producer actor**. File path is always `design/specs/<spec-id>.yaml` — the deterministic `kind:id` → path mapping is absolute:
- State schemas: `design/specs/<actor-id>-state-schema.yaml`
- Event payloads: `design/specs/<event-name>.yaml` (one per event type; a protocol cluster uses `design/specs/<protocol-name>-events.yaml`)
- Persistence schemas: `design/specs/<actor-id>-persistence.yaml`
- Interface surfaces: `design/specs/<actor-id>-interface.yaml`

## Quality Checks

- Every actor with `owns:` fields has a state schema spec (or explicit "stateless" note)
- Every cross-boundary event has a payload spec with stability annotation
- Every actor with persistent lifecycle has a persistence spec (even if "nothing persists")
- No field appears in a contract spec without appearing in the model's `owns:` or `emits_events`
- Contract specs complement (don't duplicate) behavior specs — shapes here, transitions there

## Does NOT

- Identify actors (that's `archwright-model`)
- Write behavior specs (that's `archwright-derive`)
- Write constraint specs (that's `archwright-derive`)
- Decide actor boundaries (that's `archwright-model`)
- Implement code (specs declare WHAT, not HOW)

## Relationship to Other Phases

| Phase | Produces | Answers |
|-------|----------|---------|
| Model | Actor boundaries, composition, event flows | Who owns what? Who talks to whom? |
| **Contract** | State schemas, event payloads, persistence, interfaces | **What does it look like? What does it carry? What persists?** |
| Derive | Behavior specs, constraint specs | What temporal properties hold? What rules are never violated? |

## When to Skip

- If the system has no cross-boundary communication (single actor, no events) → state schema only, skip events/interface
- If all state is transient (practice session, single-run computation) → note "no persistence" and move on
- If the model has only 1-2 actors with trivial state → contract specs may be overkill. Use judgment.

## Prior Art

- **Event Modeling** (Dymitruk): events come first → command payloads derived → read models derived. Completeness check verifies every field has origin and destination.
- **Z/VDM**: State schema authored first → operation schemas reference it. Interface = operation signatures + pre/post.
- **DDD Aggregates**: Data boundary IS the invariant boundary. Aggregate contains exactly what's needed to enforce its rules.
- **CQRS projections**: Read models mechanically derived from event streams via fold functions.
- **XState typegen (v4)**: The only tool that fully auto-derived typed interfaces from state machine definitions.
- **Design-by-Contract (Eiffel)**: Class invariant implicitly constrains all method contracts. "Short form" generated automatically.
