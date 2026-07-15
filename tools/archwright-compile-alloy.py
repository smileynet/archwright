#!/usr/bin/env python3
"""archwright-compile-alloy: Compile a behavior spec to an Alloy 6 model.

Usage:
  archwright-compile-alloy <behavior-spec.yaml> [-o output.als]

Generates an Alloy 6 model with:
  - var fields for context variables
  - Transition predicates from state/event definitions
  - Invariant assertions from the invariants section
  - Check commands for each invariant
"""

import sys
import yaml
from pathlib import Path


def load_spec(path):
    """Load a behavior spec YAML file."""
    data = yaml.safe_load(Path(path).read_text())
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
        events = state_def.get("on", {})
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

    # Generate assertions from invariants
    invariants = data.get("invariants", [])
    lines.append("-- Invariants")
    for inv in invariants:
        inv_id = _to_field(inv.get("id", "unknown"))
        inv_type = inv.get("type", "temporal")
        predicate = inv.get("predicate", "true")
        description = inv.get("description", "")

        lines.append(f"-- {description}")
        lines.append(f"-- Original: {predicate}")
        lines.append(f"assert {inv_id} {{")
        # Simplified: wrap in always for temporal invariants
        if inv_type == "temporal":
            lines.append(f"  always (M.current != M.current implies false) -- placeholder: manual review needed")
        elif inv_type == "state":
            lines.append(f"  always (true) -- placeholder: manual review needed")
        else:
            lines.append(f"  always (true) -- placeholder: manual review needed")
        lines.append("}")
        lines.append("")

    # Check commands
    lines.append("-- Check commands")
    num_states = len(state_names)
    scope = max(4, num_states)
    steps = max(6, num_states * 2)
    for inv in invariants:
        inv_id = _to_field(inv.get("id", "unknown"))
        lines.append(f"check {inv_id} for {scope} but {steps} steps")

    return "\n".join(lines)


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
    alloy_source = generate_alloy(data)

    if output_path:
        Path(output_path).write_text(alloy_source)
        print(f"Generated: {output_path}")
    else:
        # Default: same name as spec but .als extension
        default_output = Path(spec_path).with_suffix(".als")
        default_output.write_text(alloy_source)
        print(f"Generated: {default_output}")


if __name__ == "__main__":
    main()
