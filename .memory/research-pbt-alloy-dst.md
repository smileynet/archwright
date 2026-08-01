# Research: PBT + Alloy Contracts + DST for Archwright

Compiled 2026-08-01 from direct research (subagents failed 2x, fell back to direct).

---

## 1. Hypothesis Stateful Testing — Adapter Feasibility

### How it works

`RuleBasedStateMachine` defines:
- **Rules** — methods decorated with `@rule(...)` that take generated parameters
- **Invariants** — methods decorated with `@invariant` checked after every rule
- **Preconditions** — `@precondition(lambda self: ...)` gates on current state
- **Bundles** — named pools of values produced by rules and consumed by later rules

Hypothesis generates random sequences of rule invocations, checks invariants after each, then *shrinks* failing sequences to minimal counterexamples.

### Can it be generated dynamically from YAML?

**Yes.** The GitHub gist (technillogue/9dfe791ebaa03108b1a7f8d3f9f0b55a) demonstrates exactly this pattern:

```python
machine = {
    S.BLANK: {E.SET: S.ASSIGNED},
    S.ASSIGNED: {E.CLEAR: S.BLANK, E.JOB: S.BUSY},
    S.BUSY: {E.JOBDONE: S.ASSIGNED},
}

class StateMachineTest(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.director = Director()  # system under test
        self.current_state = S.BLANK

    @rule(event=st.sampled_from(list(E)))
    def transition(self, event):
        next_state = machine[self.current_state].get(event)
        try:
            self.director.step(event)
        except:
            assert next_state is None, "unexpected error"
        else:
            assert next_state, "director wrongly accepted invalid state"
            self.current_state = next_state
            assert self.director.state == next_state, "wrong state"
```

The state machine dict IS the spec — it could trivially be loaded from YAML. The test class uses `@precondition` to only fire valid events for the current state.

### Archwright adapter shape

```python
# Generated from a behavior spec YAML:
spec = load_spec("step-advancement.yaml")  # archwright loader

class GeneratedPBT(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model_state = spec["initial"]
        self.sut = create_system_under_test()  # user provides this

    @rule(event=st.sampled_from(all_events(spec)))
    @precondition(lambda self: current_valid_events(spec, self.model_state))
    def step(self, event):
        # Apply event to SUT
        self.sut.handle(event)
        # Apply event to model (spec state machine)
        self.model_state = transition(spec, self.model_state, event)

    @invariant()
    def check_invariants(self):
        for inv in spec["invariants"]:
            assert evaluate_predicate(inv["predicate"], self.sut.state())
```

### Key limitation

The user must provide a `create_system_under_test()` function and a way to
`handle(event)` on it. This is the interface question for the grill session.

### Performance concern

GitHub issue #4465 reports that `RuleBasedStateMachine` performance degrades
with many rules. For specs with 10+ events × states, dynamic generation might
need a single `@rule(event=sampled_from(...))` approach (as in the gist) rather
than one rule per event.

---

## 2. fast-check Model-Based Testing — Adapter Feasibility

### How it works

fast-check uses a `Command` pattern:
- Each command has `check(model)` (precondition), `run(model, real)` (execute + assert)
- `fc.commands(allCommands)` generates random command sequences
- `fc.asyncModelRun(setup, commands)` runs them against the real system
- Shrinking removes commands from the sequence to find minimal failures

### Can commands be generated from config?

**Yes.** Each command is a class with `check` and `run`. These can be
factory-generated from a state machine definition:

```typescript
function makeCommand(event: string, spec: BehaviorSpec) {
  return class implements fc.AsyncCommand<Model, Real> {
    check(model: Model) {
      return spec.states[model.state].transitions.includes(event);
    }
    async run(model: Model, real: Real) {
      await real.dispatch(event);
      const nextState = spec.transitions[model.state][event];
      model.state = nextState;
      // Check invariants
      for (const inv of spec.invariants) {
        expect(evaluatePredicate(inv, await real.getState())).toBe(true);
      }
    }
  };
}
```

### Comparison with Hypothesis

| Dimension | Hypothesis | fast-check |
|-----------|-----------|-----------|
| Language | Python | TypeScript/JavaScript |
| State machine support | `RuleBasedStateMachine` (first-class) | `fc.commands` (command pattern) |
| Shrinking | Built-in, very mature | Built-in, good |
| Dynamic generation | Works via class inheritance | Works via factory functions |
| Invariant checking | `@invariant` decorator (after every step) | Manual in `run()` |
| Async support | Limited | First-class (`asyncModelRun`) |

### Key insight

fast-check's command pattern is slightly more work to set up but more flexible
for async systems (web services, APIs). Hypothesis is more natural for
in-process state machines.

---

## 3. Alloy for Contract Specs — Compilation Feasibility

### The mapping (schema → Alloy)

| YAML contract concept | Alloy concept | Example |
|---|---|---|
| Type/entity | `sig` | `sig Resource {}` |
| Field (scalar) | Field with type | `name: one String` |
| Field (reference) | Relation | `parent: lone Resource` |
| Field (collection) | Set relation | `readable_by: set User` |
| Constraint: uniqueness | `fact` | `fact { all disj r1, r2: Resource \| r1.id != r2.id }` |
| Constraint: no cycles | `fact` with transitive closure | `fact { no r: Resource \| r in r.^parent }` |
| Invariant to check | `assert` + `check` | `assert NoOrphan { ... } check NoOrphan for 5` |

### Is it simpler than behavior → Alloy?

**Significantly simpler.** Behavior specs require temporal logic (Alloy 6's
`always`/`eventually`), trace semantics, and event encoding. Contract specs
are purely structural — they map directly to Alloy's original design (relational
logic, no time). This is literally what Jackson built Alloy FOR.

### Prior art

- "Validating ORA-SS data models using Alloy" (2006) — encodes semi-structured
  data schemas in Alloy, automatically validates consistency
- Alloy tutorial (alloytools.org) — mail routing, file systems, access control
- "Formal Software Design with Alloy 6" (haslab.github.io) — textbook-level
  coverage of data model verification

### What Alloy CAN'T check about data models

- Runtime behavior (only static structure)
- Performance characteristics
- Anything requiring unbounded state (Alloy is bounded — scope must be declared)
- Implementation correctness (checks the model, not the code)

### Compilation complexity estimate

~50 lines of Python to translate contract YAML → Alloy `.als`. Much simpler
than the ~200-line `compile-alloy.py` for behavior specs. The hard part is
translating predicate strings to Alloy relational logic — but for structural
properties (no cycles, uniqueness, transitivity, reachability) there are
standard patterns.

---

## 4. Deterministic Simulation Testing (Antithesis) — Relevance

### How DST works

1. **Deterministic hypervisor** — runs entire system in a virtual environment
   where all nondeterminism is controlled (scheduling, network, disk, time)
2. **Fault injection** — systematically injects failures (node crashes, network
   partitions, disk full, OOM) during execution
3. **Property checking** — evaluates assertions during execution; any violation
   is reproducible (deterministic replay)
4. **Coverage-guided exploration** — uses code coverage to guide exploration
   toward unexplored states

### How properties are specified

Antithesis has two property types:
- **Always properties** — must never be violated (disproved by one counterexample)
- **Sometimes properties** — must happen at least once (proved by one example)

Properties are embedded in the code via SDK assertions:
```python
from antithesis import assert_always, assert_sometimes

assert_always(balance >= 0, "Balance never negative", {"account": id})
assert_sometimes(leader_elected, "Leader election happens", {})
```

### Direct mapping to archwright

| Archwright concept | Antithesis equivalent |
|---|---|
| Behavior spec invariant (★★) | Always property |
| Behavior spec scenario | Sometimes property (scenario is reachable) |
| Trace event sequence | Execution history |
| `--trace` validation | Property checking during replay |
| Non-vacuity probe | Sometimes assertion (verifying reachability) |

### Could behavior specs drive DST properties?

**Yes, with a compilation step.** The adapter would:
1. Read behavior spec invariants
2. Generate `assert_always()` calls for each ★★ invariant
3. Generate `assert_sometimes()` calls for each scenario (reachability)
4. User instruments their system with these assertions
5. Antithesis explores all interleavings under fault injection

### Practical requirements for DST

- System must run in Docker/containers
- Must be decomposable into multiple processes (for fault injection)
- Benefits most from distributed/concurrent systems
- Cost: Antithesis is a paid service (not open-source)
- Self-hosted alternatives: FoundationDB simulation approach (custom), Jepsen (for databases)

### Relevance to archwright

- **Near-term:** Low. Most archwright users aren't running distributed systems
  in Docker. The PBT path is far more accessible.
- **Long-term:** High. As archwright moves toward verifying larger systems,
  DST is the ultimate verification layer — it checks the REAL system under
  REAL faults, not a model. The compilation path (spec → assertions) is clean.
- **Key insight:** Antithesis's "always/sometimes" vocabulary maps exactly to
  archwright's confidence system (★★ = always, scenario reachability = sometimes).
  The spec format is already DST-ready; only the compilation target differs.

---

## Summary: Feasibility Assessment

| Research topic | Feasibility | Effort | Priority |
|---|---|---|---|
| Hypothesis PBT adapter | ✅ High — proven pattern exists | Medium (spike: 1 day) | High |
| fast-check PBT adapter | ✅ High — command pattern maps well | Medium (spike: 1 day) | Medium |
| Alloy contract compilation | ✅ Very high — simpler than behavior | Low (~50 lines) | Medium |
| DST integration | ⚠️ Medium — clean mapping but heavy infra | High (service dependency) | Low (long-term) |

## Grill Session Topics

The following need human decisions before implementation:

1. **PBT interface design** (ticket 091) — Option B (call functions) vs Option C
   (signal-tap via trace emitter)? The gist example uses Option B. Archwright's
   trace emitters suggest Option C. Hybrid (D) is also viable.

2. **Contract spec invariant syntax** — Should contract specs get a new
   `structural_invariants:` section (like behavior specs have `invariants:`)?
   Or should we reuse the existing `check:` section with `method: alloy`?

3. **PBT scope** — Should `--pbt` generate a file the user runs in their test
   suite? Or should it run inline like `--trace` does? File generation is more
   portable; inline running is faster feedback.
