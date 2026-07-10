# Domain Model Example: Uniform Runner Contract

This demonstrates the full chain from product desire through to checkable spec, with the domain model as the bridge.

---

## A) What INFORMS the model (upstream)

### Product Desire
```yaml
- id: practice-any-position
  who: player
  statement: "A player wants to practice executing plays from any position"
```

### Pattern (formalized)
```
Pattern: uniform-runner-contract
Serves: practice-any-position, feel-like-real-practice

Resolution: "The execution orchestrator interacts with all fielder controllers
through a uniform interface: assign chains and receive completion signals.
It never distinguishes controller types."
```

### Forces that shape the model
- PlayManager3D must be agnostic (can't type-check controllers)
- Exactly one controller owns body commands per fielder
- Player controller reinterprets chains (stores for validation, drives from input)
- Generation tracking discards stale completions

---

## B) The DOMAIN MODEL (this phase's output)

```yaml
# design/models/execution-actors.yaml

actors:
  - id: play-manager-3d
    purpose: "Step orchestration — assigns chains, tracks completion, advances steps"
    owns:
      - cursor: int                    # current step index
      - generation: int                # monotonically increasing per step
      - pending_slots: Dictionary      # slot_id → generation (awaiting completion)
    accepts_events:
      - START_EXECUTION { context: RuntimeExecutionContext }
      - CHAIN_COMPLETED { slot_id: StringName, generation: int }
    emits_events:
      - STEP_STARTED { step_index, total_steps, slot_count }
      - STEP_COMPLETED { step_index, total_steps }
      - RUN_COMPLETED { total_steps, run_id }
    lifecycle:
      created_by: practice-execution
      active_during: execution running
    invariants:
      - "never references controller types (AI, Player, etc)"
      - "step advances only when pending_slots is empty (strict-join)"
      - "stale generation completions are ignored"
    from_pattern: uniform-runner-contract

  - id: fielder-controller
    purpose: "Body command owner for one fielder — receives chains, emits completion"
    subtypes:
      - ai-fielder-controller: "Drives body from waypoints autonomously"
      - player-fielder-controller: "Drives body from human input, uses chain for validation"
    owns:
      - chain: Array[RuntimeObjective]   # assigned objectives
      - current_index: int               # progress through chain
      - generation: int                  # which assignment this is
      - body: FielderBody3D              # the physical body being commanded
    accepts_events:
      - ASSIGN_CHAIN { chain: Array[RuntimeObjective], generation: int }
    emits_events:
      - CHAIN_COMPLETED { slot_id: StringName, generation: int }
    lifecycle:
      created_by: fielder-manager-3d
      swappable: true                    # can be replaced mid-run via swap_controller()
    invariants:
      - "exactly one controller per body at any time"
      - "chain_completed emitted only when full chain is done"
      - "stale controller (post-swap) completion is harmless (generation mismatch)"
    contract_surface:
      - "assign_chain(chain, generation) — virtual method"
      - "chain_completed(slot_id, generation) — signal"
      - "body — FielderBody3D reference"
    from_pattern: uniform-runner-contract

  - id: fielder-manager-3d
    purpose: "Fielder lifecycle — spawn, place, assign controllers, swap"
    owns:
      - bodies: Dictionary[StringName, FielderBody3D]
      - runners: Dictionary[StringName, FielderController]
    accepts_events:
      - SETUP { context: RuntimeExecutionContext }
      - SWAP_CONTROLLER { slot_id, new_controller }
    emits_events: []
    lifecycle:
      created_by: practice-execution
      active_during: execution running
    invariants:
      - "runners dictionary is the canonical slot→controller map"
      - "swap updates runners and reconnects signals atomically"
    from_pattern: uniform-runner-contract

composition:
  practice-execution:
    invokes:
      - play-manager-3d
      - fielder-manager-3d
      - ball-state-service
    fielder-manager-3d:
      spawns:
        - fielder-controller (one per slot, swappable)

event_flows:
  - from: play-manager-3d
    to: fielder-controller
    event: ASSIGN_CHAIN
    semantics: "assigns next step's objectives to the controller"

  - from: fielder-controller
    to: play-manager-3d
    event: CHAIN_COMPLETED
    semantics: "reports this slot finished its objectives"
    guard: "generation must match current (stale ignored)"

  - from: fielder-manager-3d
    to: fielder-controller
    event: SWAP_CONTROLLER
    semantics: "replaces one controller with another (initial setup or runtime switch)"
```

---

## C) What the model INFORMS (downstream specs)

### Behavior Spec (derived from play-manager-3d actor model)

```yaml
# design/specs/play-manager-step-advancement.yaml
kind: behavior
id: play-manager-step-advancement
from_patterns:
  - "pattern:uniform-runner-contract"
from_model: "model:play-manager-3d"

initial: idle

states:
  idle:
    type: atomic
    on:
      START_EXECUTION:
        target: advancing
  advancing:
    type: atomic
    on:
      CHAINS_ASSIGNED:
        target: waiting_for_completion
  waiting_for_completion:
    type: atomic
    on:
      CHAIN_COMPLETED:
        target: waiting_for_completion
        guard: "pending_slots.size() > 1"
      CHAIN_COMPLETED:
        target: advancing
        guard: "pending_slots.size() == 1 (last slot)"
      # Note: stale generation completions don't trigger transitions
    invariant:
      predicate: "pending_slots is non-empty while in this state"
  run_complete:
    type: final

invariants:
  - id: strict-join
    predicate: "advancing only entered when pending_slots is empty"
    confidence: "★★"
    from_force: "strict-join-waits"

  - id: generation-filtering
    predicate: "CHAIN_COMPLETED with generation != current_generation has no effect"
    confidence: "★★"
    from_force: "single-controller-ownership"
```

### Constraint Spec (derived from play-manager-3d.invariants[0])

```yaml
# design/specs/play-manager-agnosticism.md
kind: constraint
id: play-manager-agnosticism
from_patterns:
  - "pattern:uniform-runner-contract"
from_model: "model:play-manager-3d"
check:
  method: grep
  target: "client/src/execution/play_manager3d.gd"
  pattern: "AIFielderController|PlayerFielderController|PlayerInputSource"
  expect: absent
```

### Contract Spec (derived from fielder-controller.contract_surface)

```yaml
# design/specs/fielder-controller-interface.yaml
kind: contract
id: fielder-controller-interface
from_patterns:
  - "pattern:uniform-runner-contract"
from_model: "model:fielder-controller"

fields:
  body:
    type: reference
    required: true
    description: "FielderBody3D this controller commands"
  chain_completed_signal:
    type: signal
    signature: "(slot_id: StringName, generation: int)"
  assign_chain_method:
    type: method
    signature: "(chain: Array[RuntimeObjective], generation: int) -> void"

lifecycle:
  - state: instantiated
    by: fielder-manager-3d
    invariant: "body is null, no chain assigned"
  - state: active
    by: play-manager-3d (via assign_chain)
    invariant: "body set, chain assigned, generation tracked"
  - state: completed
    by: self
    invariant: "chain_completed emitted with correct slot_id and generation"
```

---

## D) The Full Traceability Chain

```
Product Desire: practice-any-position
  ↓ (creates tension with)
Constraint: play-manager-agnostic + single-controller-ownership
  ↓ (resolved by)
Pattern: uniform-runner-contract (serves: practice-any-position)
  ↓ (modeled as)
Domain Model: actors [play-manager-3d, fielder-controller, fielder-manager-3d]
  ↓ (projected into)
Specs:
  - behavior:play-manager-step-advancement (from actor state machine)
  - constraint:play-manager-agnosticism (from actor invariant "never references types")
  - contract:fielder-controller-interface (from actor contract surface)
  ↓ (verified by)
archwright-check:
  - --static: grep for type references in play_manager3d.gd
  - --trace: runtime events match behavior spec state machine
```

Every level traces back to "a player wants to practice from any position." If the trace breaks at any point, the architecture has lost connection to its purpose.
