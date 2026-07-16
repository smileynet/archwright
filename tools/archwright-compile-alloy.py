#!/usr/bin/env python3
"""Compile an Archwright behavior spec to a bounded Alloy 6 model."""

import re
import sys
from pathlib import Path

import yaml


def load_spec(path):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if data.get("kind") != "behavior":
        raise ValueError(f"{path} is not a behavior spec (kind: {data.get('kind')})")
    return data


def _to_sig(name):
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def _to_field(name):
    parts = name.replace("-", "_").split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def _strip_outer_parens(expression):
    expression = expression.strip()
    while expression.startswith("(") and expression.endswith(")"):
        depth = 0
        for index, character in enumerate(expression):
            depth += character == "("
            depth -= character == ")"
            if depth == 0 and index < len(expression) - 1:
                return expression
        expression = expression[1:-1].strip()
    return expression


def _split_top_level(expression, operator):
    depth = 0
    start = 0
    parts = []
    index = 0
    while index <= len(expression) - len(operator):
        character = expression[index]
        depth += character in "({"
        depth -= character in ")}"
        if depth == 0 and expression[index:index + len(operator)] == operator:
            parts.append(expression[start:index].strip())
            start = index + len(operator)
            index = start
            continue
        index += 1
    if parts:
        parts.append(expression[start:].strip())
    return parts


def _value(variable, value, variables):
    definition = variables[variable]
    value = value.strip().strip("'\"")
    value_type = definition.get("type")
    if value_type == "bool" and value.lower() in {"true", "false"}:
        return "TrueVal" if value.lower() == "true" else "FalseVal"
    if value_type == "enum" and value in definition.get("values", []):
        return f"{_to_sig(variable)}_{_to_sig(value)}"
    if value_type in {"int", "float"} and re.fullmatch(r"-?\d+", value):
        return value
    raise ValueError(f"Unsupported value '{value}' for '{variable}'")


def compile_predicate(predicate, variables, states):
    expression = _strip_outer_parens(predicate)
    if expression.startswith("always "):
        return f"always ({compile_predicate(expression[7:], variables, states)})"

    for operator, alloy_operator in ((" implies ", "implies"), (" or ", "or"), (" and ", "and")):
        parts = _split_top_level(expression, operator)
        if parts:
            compiled = [compile_predicate(part, variables, states) for part in parts]
            return f"({' {} '.format(alloy_operator).join(compiled)})"

    if expression.startswith("not "):
        return f"not ({compile_predicate(expression[4:], variables, states)})"

    membership = re.fullmatch(r"([A-Za-z_][\w-]*)\s+in\s+\{([^}]+)\}", expression)
    if membership:
        variable = membership.group(1)
        if variable not in variables:
            raise ValueError(f"Unsupported predicate variable '{variable}'")
        values = [_value(variable, item, variables) for item in membership.group(2).split(",")]
        field = f"M.{_to_field(variable)}"
        return f"({' or '.join(f'{field} = {value}' for value in values)})"

    equality = re.fullmatch(r"([A-Za-z_][\w-]*)\s*(==|!=)\s*([A-Za-z0-9_'\".-]+)", expression)
    if equality:
        variable, operator, value = equality.groups()
        if variable not in variables:
            raise ValueError(f"Unsupported predicate variable '{variable}'")
        comparison = "=" if operator == "==" else "!="
        return f"M.{_to_field(variable)} {comparison} {_value(variable, value, variables)}"

    if expression in states:
        return f"M.current = {_to_sig(expression)}"
    if expression in variables and variables[expression].get("type") == "bool":
        return f"M.{_to_field(expression)} = TrueVal"
    raise ValueError(f"Unsupported predicate: {predicate}")


def _transitions(state_definition):
    return state_definition.get("on") or state_definition.get(True, {})


def generate_alloy(data):
    spec_id = data["id"]
    states = data.get("states", {})
    if not states:
        raise ValueError("Behavior spec must define states")
    variables = data.get("context", {}).get("variables", {})
    bool_variables = {name: value for name, value in variables.items() if value.get("type") == "bool"}
    enum_variables = {name: value for name, value in variables.items() if value.get("type") == "enum"}
    number_variables = {name: value for name, value in variables.items() if value.get("type") == "int"}
    unsupported = set(variables) - set(bool_variables) - set(enum_variables) - set(number_variables)
    if unsupported:
        raise ValueError(f"Unsupported context types: {sorted(unsupported)}")

    lines = [
        f"-- Auto-generated from behavior spec: {spec_id}",
        "-- Do not edit; regenerate from the spec.",
        "",
        "abstract sig State {}",
    ]
    lines.extend(f"one sig {_to_sig(name)} extends State {{}}" for name in states)
    if bool_variables:
        lines.extend(["", "abstract sig BoolVal {}", "one sig TrueVal, FalseVal extends BoolVal {}"])
    for name, definition in enum_variables.items():
        enum_type = f"{_to_sig(name)}Val"
        lines.extend(["", f"abstract sig {enum_type} {{}}"])
        values = ", ".join(f"{_to_sig(name)}_{_to_sig(value)}" for value in definition.get("values", []))
        lines.append(f"one sig {values} extends {enum_type} {{}}")

    fields = ["var current: one State"]
    fields.extend(f"var {_to_field(name)}: one BoolVal" for name in bool_variables)
    fields.extend(f"var {_to_field(name)}: one {_to_sig(name)}Val" for name in enum_variables)
    fields.extend(f"var {_to_field(name)}: one Int" for name in number_variables)
    lines.extend(["", "one sig M {", "  " + ",\n  ".join(fields), "}", "", "fact init {"])
    initial = data.get("initial", next(iter(states)))
    lines.append(f"  M.current = {_to_sig(initial)}")
    for name, definition in bool_variables.items():
        lines.append(f"  M.{_to_field(name)} = {'TrueVal' if definition.get('initial') else 'FalseVal'}")
    for name, definition in enum_variables.items():
        lines.append(f"  M.{_to_field(name)} = {_value(name, str(definition.get('initial')), variables)}")
    for name, definition in number_variables.items():
        lines.append(f"  M.{_to_field(name)} = {definition.get('initial', 0)}")
    lines.extend(["}", "", "-- Transitions"])

    transition_names = []
    for state_name, state_definition in states.items():
        for event_name, transition in _transitions(state_definition).items():
            transitions = transition if isinstance(transition, list) else [transition]
            for branch, item in enumerate(transitions):
                item = {"target": item} if isinstance(item, str) else item
                suffix = f"_{branch}" if len(transitions) > 1 else ""
                predicate_name = f"t_{_to_field(state_name)}_{_to_field(event_name)}{suffix}"
                transition_names.append(predicate_name)
                lines.extend([f"pred {predicate_name} {{", f"  M.current = {_to_sig(state_name)}"])
                guard = item.get("guard", {})
                if guard.get("predicate"):
                    lines.append(f"  {compile_predicate(guard['predicate'], variables, states)}")
                lines.append(f"  M.current' = {_to_sig(item.get('target', state_name))}")
                effects = item.get("effects", {})
                unknown_effects = set(effects) - set(variables)
                if unknown_effects:
                    raise ValueError(f"Transition effect references unknown variables: {sorted(unknown_effects)}")
                for name in variables:
                    field = _to_field(name)
                    if name in effects:
                        lines.append(f"  M.{field}' = {_value(name, str(effects[name]), variables)}")
                    else:
                        lines.append(f"  M.{field}' = M.{field}")
                lines.extend(["}", ""])

    lines.extend(["pred idle {", "  M.current' = M.current"])
    for name in variables:
        lines.append(f"  M.{_to_field(name)}' = M.{_to_field(name)}")
    lines.extend(["}", "", "fact behavior {", f"  always ({' or '.join(transition_names + ['idle'])})", "}", "", "-- Invariants"])

    invariants = data.get("invariants", [])
    for invariant in invariants:
        invariant_id = _to_field(invariant["id"])
        compiled = compile_predicate(invariant["predicate"], variables, states)
        lines.extend([f"assert {invariant_id} {{", f"  {compiled}", "}", ""])

    model = data.get("check", {}).get("model", {})
    scope = model.get("scope", max(4, len(states)))
    steps = model.get("steps", max(6, len(states) * 2))
    lines.append("-- Check commands")
    lines.extend(f"check {_to_field(invariant['id'])} for {scope} but {steps} steps" for invariant in invariants)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: archwright-compile-alloy <behavior-spec.yaml> [-o output.als]")
        return 2
    try:
        data = load_spec(sys.argv[1])
        output = Path(sys.argv[sys.argv.index("-o") + 1]) if "-o" in sys.argv else Path(sys.argv[1]).with_suffix(".als")
        output.write_text(generate_alloy(data), encoding="utf-8")
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Generated: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
