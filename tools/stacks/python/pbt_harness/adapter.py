"""archwright Python PBT adapter (stack adapter, Extension Protocol / ADR 0008).

Reads a behavior spec YAML and generates a Hypothesis RuleBasedStateMachine
that drives a user-provided step function with random valid event sequences,
checking invariants after each transition.

Architecture (grill 2026-08-01, Option D — Hybrid):
- PBT owns generation (random valid events from spec's state machine)
- User owns application (provides a step function: event → system call)
- Trace emitter owns observation (state read via emitter snapshot)

Usage:

    from archwright_pbt import make_pbt_class
    from my_project.step import step_fn

    spec = yaml.safe_load(open("design/specs/my-behavior.yaml"))
    PBTTest = make_pbt_class(spec, step_fn)
    TestCase = PBTTest.TestCase  # run with pytest / unittest

The step function signature:

    def step_fn(event: str, context: dict) -> dict:
        '''Apply event to the system, return the new state snapshot (dict).'''
        ...

Stdlib + hypothesis only. Python >= 3.8.
"""

import yaml
from pathlib import Path

try:
    from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, initialize
    from hypothesis import strategies as st, settings
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


def _state_events(state_def):
    """Extract event→transition mapping (handles YAML 1.1 boolean True key)."""
    return state_def.get("on") or state_def.get(True) or {}


def _all_events(spec):
    """Collect all event names from the spec's state machine."""
    events = set()
    for state_def in spec.get("states", {}).values():
        events.update(_state_events(state_def).keys())
    return sorted(events)


def _valid_events_for(spec, state_name):
    """Return events valid in a given state."""
    state_def = spec.get("states", {}).get(state_name, {})
    return list(_state_events(state_def).keys())


def _resolve_transition(spec, current_state, event):
    """Given current state + event, return the next state (first valid transition).
    Returns None if no transition exists for this event in this state."""
    state_def = spec.get("states", {}).get(current_state, {})
    transitions = _state_events(state_def)
    if event not in transitions:
        return None
    target = transitions[event]
    if isinstance(target, str):
        return target
    if isinstance(target, dict):
        return target.get("target", current_state)
    if isinstance(target, list):
        # Multiple transitions (guarded) — take the first target
        for t in target:
            if isinstance(t, str):
                return t
            if isinstance(t, dict):
                return t.get("target", current_state)
    return None


def _evaluate_predicate(predicate, state_vars, current_state):
    """Evaluate a simple predicate against state variables.
    Returns True (holds), False (violated), or None (untranslatable — skip)."""
    pred = predicate.strip()

    # Equality: X == Y
    if " == " in pred:
        left, right = pred.split(" == ", 1)
        left_val = state_vars.get(left.strip())
        right_val = state_vars.get(right.strip(), right.strip().strip("'\""))
        if left_val is None:
            return None  # untranslatable
        return left_val == right_val

    # Inequality: X != Y
    if " != " in pred:
        left, right = pred.split(" != ", 1)
        left_val = state_vars.get(left.strip())
        right_val = state_vars.get(right.strip(), right.strip().strip("'\""))
        if left_val is None:
            return None
        return left_val != right_val

    # Comparison: X < Y, X <= Y, X > Y, X >= Y
    for op in (" <= ", " >= ", " < ", " > "):
        if op in pred:
            left, right = pred.split(op, 1)
            left_val = state_vars.get(left.strip())
            try:
                right_val = state_vars.get(right.strip())
                if right_val is None:
                    right_val = int(right.strip())
            except (ValueError, TypeError):
                return None
            if left_val is None:
                return None
            op_s = op.strip()
            if op_s == "<=":
                return left_val <= right_val
            elif op_s == ">=":
                return left_val >= right_val
            elif op_s == "<":
                return left_val < right_val
            elif op_s == ">":
                return left_val > right_val

    # Boolean state vars
    if pred in state_vars:
        return bool(state_vars[pred])

    # Negation: not X
    if pred.startswith("not "):
        inner = pred[4:].strip()
        result = _evaluate_predicate(inner, state_vars, current_state)
        if result is None:
            return None
        return not result

    # Unrecognized — skip (never silently pass)
    return None


def make_pbt_class(spec, step_fn, max_steps=50):
    """Generate a Hypothesis RuleBasedStateMachine class from a behavior spec.

    Args:
        spec: Parsed behavior spec dict (with states, initial, invariants)
        step_fn: User's step function: (event: str, context: dict) -> dict
        max_steps: Maximum steps per test run (default 50)

    Returns:
        A RuleBasedStateMachine subclass ready to be used as a TestCase.
    """
    if not HAS_HYPOTHESIS:
        raise ImportError("hypothesis is required for PBT: pip install hypothesis")

    initial_state = spec.get("initial", "")
    all_events = _all_events(spec)
    invariants_list = spec.get("invariants", [])

    class SpecStateMachine(RuleBasedStateMachine):
        def __init__(self):
            super().__init__()
            self._model_state = initial_state
            self._state_vars = {}
            # Initialize the SUT via step with INITIAL
            result = step_fn("INITIAL", {})
            if isinstance(result, dict):
                self._state_vars = result

        @rule(event=st.sampled_from(all_events))
        def apply_event(self, event):
            """Apply a random event. Skip if not valid in current model state."""
            valid = _valid_events_for(spec, self._model_state)
            if event not in valid:
                return  # precondition: skip invalid events silently

            # Apply to real system
            result = step_fn(event, self._state_vars)
            if isinstance(result, dict):
                self._state_vars = result

            # Advance model state
            next_state = _resolve_transition(spec, self._model_state, event)
            if next_state:
                self._model_state = next_state

        @invariant()
        def check_spec_invariants(self):
            """Check all spec invariants after every step."""
            for inv in invariants_list:
                pred = inv.get("predicate", "")
                result = _evaluate_predicate(pred, self._state_vars, self._model_state)
                if result is None:
                    continue  # untranslatable — skip, don't silently pass
                assert result, (
                    f"Invariant '{inv.get('id', '?')}' violated: "
                    f"{pred} (state={self._model_state}, vars={self._state_vars})"
                )

    SpecStateMachine.__name__ = f"PBT_{spec.get('id', 'unknown')}"
    SpecStateMachine.__qualname__ = SpecStateMachine.__name__
    return SpecStateMachine


def run_pbt(spec, step_fn, max_examples=200, max_steps=50):
    """Run PBT inline and return results dict.

    Returns:
        {"status": "pass"|"fail"|"error", "examples_run": int,
         "failure": None|{"invariant": ..., "sequence": [...], "message": ...}}
    """
    if not HAS_HYPOTHESIS:
        return {"status": "error", "message": "hypothesis not installed"}

    PBTClass = make_pbt_class(spec, step_fn, max_steps=max_steps)

    try:
        state_machine = PBTClass.TestCase
        state_machine.settings = settings(
            max_examples=max_examples,
            stateful_step_count=max_steps,
        )
        state_machine().runTest()
        return {"status": "pass", "examples_run": max_examples}
    except AssertionError as e:
        return {
            "status": "fail",
            "message": str(e),
            "examples_run": max_examples,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def load_and_run(spec_path, step_module_path, max_examples=200):
    """Load spec + step module, run PBT, return results.

    Args:
        spec_path: Path to behavior spec YAML
        step_module_path: Path to Python module containing `step` function
    """
    import importlib.util

    # Load spec
    spec_path = Path(spec_path)
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))

    if spec.get("kind") != "behavior":
        return {"status": "error", "message": f"Expected kind: behavior, got: {spec.get('kind')}"}

    # Load step module
    step_path = Path(step_module_path)
    if not step_path.exists():
        return {"status": "error", "message": f"Step module not found: {step_path}"}

    mod_spec = importlib.util.spec_from_file_location("step_module", str(step_path))
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)

    if not hasattr(mod, "step"):
        return {"status": "error", "message": f"Step module must export a 'step' function"}

    return run_pbt(spec, mod.step, max_examples=max_examples)
