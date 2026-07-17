#!/usr/bin/env python3
"""archwright-compile-alloy: Compile a behavior spec to an Alloy 6 model.

Usage:
  archwright-compile-alloy <behavior-spec.yaml> [-o output.als]

LIMITATION: transition guards compile to comments only and context variables
are frozen by frame conditions — `alloy:` expressions must reference M.current
and state sigs, not context vars (the compiler warns if they do).

Generates an Alloy 6 model with:
  - var fields for context variables
  - Transition predicates from state/event definitions
  - Invariant assertions from the invariants section
  - Check commands for each invariant
"""

import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from archwright_common import state_events


def load_spec(path):
    """Load a behavior spec YAML file."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if data.get("kind") != "behavior":
        print(f"Error: {path} is not a behavior spec (kind: {data.get('kind')})")
        sys.exit(1)
    return data


def generate_alloy(data):
    """Generate Alloy 6 model from behavior spec data."""
    lines = []
    spec_id = data["id"]

    lines.append(f"-- Auto-generated from behavior spec: {spec_id}")
    lines.append(f"-- Do not edit — regenerate from the spec.")
    lines.append("")

    # Generate sigs for enum context variables
    context = data.get("context", {}).get("variables", {})
    enum_vars = {k: v for k, v in context.items() if v.get("type") == "enum"}
    int_vars = {k: v for k, v in context.items() if v.get("type") in ("int", "float")}

    # Generate state enum
    states = data.get("states", {})
    state_names = list(states.keys())

    lines.append("-- States")
    lines.append("abstract sig State {}")
    for s in state_names:
        sig_name = _to_sig(s)
        lines.append(f"one sig {sig_name} extends State {{}}")
    lines.append("")

    # Generate enum sigs for enum context variables
    for var_name, var_def in enum_vars.items():
        values = var_def.get("values", [])
        lines.append(f"-- Context: {var_name}")
        lines.append(f"abstract sig {_to_sig(var_name)}Val {{}}")
        for v in values:
            lines.append(f"one sig {_to_sig(var_name)}_{_to_sig(v)} extends {_to_sig(var_name)}Val {{}}")
        lines.append("")

    # Generate the machine sig with var fields
    lines.append("-- Machine state")
    lines.append("one sig M {")
    fields = []
    fields.append("  var current: one State")
    for var_name, var_def in enum_vars.items():
        fields.append(f"  , var {_to_field(var_name)}: one {_to_sig(var_name)}Val")
    for var_name, var_def in int_vars.items():
        fields.append(f"  , var {_to_field(var_name)}: one Int")
    lines.append(",\n".join(fields) if not fields else fields[0])
    for f in fields[1:]:
        lines.append(f)
    lines.append("}")
    lines.append("")

    # Initial state
    initial = data.get("initial", state_names[0] if state_names else "unknown")
    lines.append("-- Initial state")
    lines.append("fact init {")
    lines.append(f"  M.current = {_to_sig(initial)}")
    for var_name, var_def in enum_vars.items():
        init_val = var_def.get("initial", var_def.get("values", ["none"])[0])
        lines.append(f"  M.{_to_field(var_name)} = {_to_sig(var_name)}_{_to_sig(init_val)}")
    for var_name, var_def in int_vars.items():
        init_val = var_def.get("initial", 0)
        lines.append(f"  M.{_to_field(var_name)} = {init_val}")
    lines.append("}")
    lines.append("")

    # Generate transition predicates
    lines.append("-- Transitions")
    transition_preds = []
    for state_name, state_def in states.items():
        events = state_events(state_def)
        for event_name, trans in events.items():
            if isinstance(trans, dict):
                target = trans.get("target", state_name)
                pred_name = f"t_{_to_field(state_name)}_{_to_field(event_name)}"
                transition_preds.append(pred_name)
                lines.append(f"pred {pred_name} {{")
                lines.append(f"  M.current = {_to_sig(state_name)}")
                # Add guard if present
                guard = trans.get("guard", {})
                if guard and guard.get("predicate"):
                    lines.append(f"  -- guard: {guard['predicate']}")
                lines.append(f"  M.current' = {_to_sig(target)}")
                # Frame: unchanged vars (simplified)
                for var_name in enum_vars:
                    lines.append(f"  M.{_to_field(var_name)}' = M.{_to_field(var_name)}")
                for var_name in int_vars:
                    lines.append(f"  M.{_to_field(var_name)}' = M.{_to_field(var_name)}")
                lines.append("}")
                lines.append("")

    # Add idle/stutter
    lines.append("pred idle {")
    lines.append("  M.current' = M.current")
    for var_name in enum_vars:
        lines.append(f"  M.{_to_field(var_name)}' = M.{_to_field(var_name)}")
    for var_name in int_vars:
        lines.append(f"  M.{_to_field(var_name)}' = M.{_to_field(var_name)}")
    lines.append("}")
    lines.append("")

    # Behavior fact
    lines.append("-- System: one transition per step")
    lines.append("fact behavior {")
    all_preds = transition_preds + ["idle"]
    lines.append(f"  always ({' or '.join(all_preds)})")
    lines.append("}")
    lines.append("")

    # Generate assertions from invariants.
    # An invariant is mechanically checkable only if it carries an explicit
    # `alloy:` expression (prose predicates are not translatable — Extension
    # Protocol rule 1: skip with reason, never emit broken placeholders).
    invariants = data.get("invariants", [])
    checkable = []
    skipped = []
    skipped_warnings = []
    lines.append("-- Invariants")
    for inv in invariants:
        inv_id = _to_field(inv.get("id", "unknown"))
        predicate = inv.get("predicate", "true")
        description = inv.get("description", "")
        alloy_expr = inv.get("alloy")

        if alloy_expr:
            checkable.append(inv_id)
            # LIMITATION: guards compile to comments and context vars never update
            # (frame conditions freeze them) — an expression over a context var is
            # checked against a model where it cannot change. Warn loudly.
            frozen_refs = [v for v in context if f"M.{_to_field(v)}" in alloy_expr]
            if frozen_refs:
                skipped_warnings.append(
                    f"invariant '{inv.get('id', 'unknown')}' references context var(s) "
                    f"{frozen_refs} — context vars are FROZEN in the generated model "
                    f"(guards/actions not compiled); results may be spurious. "
                    f"Reference M.current and state sigs instead.")
            lines.append(f"-- {description}")
            lines.append(f"-- Spec predicate: {predicate}")
            lines.append(f"assert {inv_id} {{")
            lines.append(f"  {alloy_expr}")
            lines.append("}")
            lines.append("")
        else:
            skipped.append(inv.get("id", "unknown"))
            lines.append(f"-- SKIPPED {inv.get('id', 'unknown')}: prose predicate not mechanically")
            lines.append(f"-- translatable — add an `alloy:` expression to the spec to check it.")
            lines.append(f"-- Spec predicate: {predicate}")
            lines.append("")

    # Check commands (only for checkable invariants)
    lines.append("-- Check commands")
    num_states = len(state_names)
    scope = max(4, num_states)
    steps = max(6, num_states * 2)
    for inv_id in checkable:
        lines.append(f"check {inv_id} for {scope} but {steps} steps")

    return "\n".join(lines), skipped, skipped_warnings


def _to_sig(name):
    """Convert a slug/name to an Alloy sig name (PascalCase)."""
    parts = name.replace("-", "_").split("_")
    return "".join(p.capitalize() for p in parts)


def _to_field(name):
    """Convert a slug/name to an Alloy field name (camelCase)."""
    parts = name.replace("-", "_").split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def main():
    if len(sys.argv) < 2:
        print("Usage: archwright-compile-alloy <behavior-spec.yaml> [-o output.als]")
        sys.exit(2)

    spec_path = sys.argv[1]
    output_path = None

    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    data = load_spec(spec_path)
    alloy_source, skipped, gen_warnings = generate_alloy(data)

    if output_path:
        Path(output_path).write_text(alloy_source, encoding="utf-8")
        print(f"Generated: {output_path}")
    else:
        # Default: same name as spec but .als extension
        default_output = Path(spec_path).with_suffix(".als")
        default_output.write_text(alloy_source, encoding="utf-8")
        print(f"Generated: {default_output}")

    for inv_id in skipped:
        print(f"WARN: invariant '{inv_id}' skipped — no `alloy:` expression (prose predicate not mechanically translatable)")
    for w in gen_warnings:
        print(f"WARN: {w}")


if __name__ == "__main__":
    main()
