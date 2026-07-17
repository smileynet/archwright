#!/usr/bin/env python3
"""archwright-compile-alloy: Compile a behavior spec to an Alloy 6 model.

Usage:
  archwright-compile-alloy <behavior-spec.yaml> [-o output.als]

Guards and var updates COMPILE (ticket 008): guard predicates over context
vars (enum ==/!=, int comparisons, var-to-var, &&-conjunctions) become
transition preconditions; `assign:` maps on transitions become primed
updates (int/enum literals, var copy, `var + N` / `var - N`). Anything
outside that subset stays a comment, and any invariant whose `alloy:`
expression references the affected vars or target state is SKIPPED with
reason (Extension Protocol rule 1) — reported as `SKIP-INVARIANT:` lines
on stdout for archwright-check to consume.

Generates an Alloy 6 model with:
  - var fields for context variables
  - Transition predicates from state/event definitions (guards + assigns compiled)
  - Invariant assertions from the invariants section
  - Check commands for each non-skipped invariant
"""

import re
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from archwright_common import state_events

# Spec comparison operator → Alloy operator (note: Alloy's ≤ is `=<`)
_OP_MAP = {"==": "=", "!=": "!=", ">=": ">=", "<=": "=<", ">": ">", "<": "<"}


def load_spec(path):
    """Load a behavior spec YAML file."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if data.get("kind") != "behavior":
        print(f"Error: {path} is not a behavior spec (kind: {data.get('kind')})")
        sys.exit(1)
    return data


def _translate_operand(token, enum_vars, int_vars, var_name=None):
    """Translate one comparison operand: int literal, quoted enum literal,
    or context var reference. Returns Alloy expr or None (untranslatable).
    var_name provides the enum namespace when translating an enum literal."""
    token = token.strip()
    if re.fullmatch(r"-?\d+", token):
        return token
    m = re.fullmatch(r"""['"](\w+)['"]""", token)
    if m and var_name in enum_vars:
        return f"{_to_sig(var_name)}_{_to_sig(m.group(1))}"
    if token in enum_vars or token in int_vars:
        return f"M.{_to_field(token)}"
    return None


def _translate_comparison(expr, enum_vars, int_vars):
    """Translate one `lhs OP rhs` comparison where lhs is a context var.
    Returns Alloy expr or None."""
    m = re.fullmatch(r"\s*(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+?)\s*", expr)
    if not m:
        return None
    lhs, op, rhs = m.group(1), m.group(2), m.group(3)
    if lhs not in enum_vars and lhs not in int_vars:
        return None
    if lhs in enum_vars and op not in ("==", "!="):
        return None  # ordering on enums is meaningless
    rhs_expr = _translate_operand(rhs, enum_vars, int_vars, var_name=lhs)
    if rhs_expr is None:
        return None
    return f"M.{_to_field(lhs)} {_OP_MAP[op]} {rhs_expr}"


def _translate_guard(predicate, enum_vars, int_vars):
    """Translate a guard predicate (comparisons joined by &&) to an Alloy
    precondition. Returns Alloy expr or None if ANY conjunct is untranslatable."""
    conjuncts = [c for c in re.split(r"&&|\band\b", predicate) if c.strip()]
    if not conjuncts:
        return None
    parts = []
    for c in conjuncts:
        t = _translate_comparison(c, enum_vars, int_vars)
        if t is None:
            return None
        parts.append(t)
    return " and ".join(parts)


def _translate_assign(var, value, enum_vars, int_vars):
    """Translate one `assign:` entry (var: value) to a primed update.
    Supported values: int literal, enum literal, var copy, `var + N` / `var - N`.
    Returns Alloy expr or None."""
    if var not in enum_vars and var not in int_vars:
        return None
    field = f"M.{_to_field(var)}"
    if isinstance(value, int) and var in int_vars:
        return f"{field}' = {value}"
    if not isinstance(value, str):
        return None
    value = value.strip()
    if var in enum_vars:
        bare = value.strip("'\"")
        if bare in enum_vars[var].get("values", []):
            return f"{field}' = {_to_sig(var)}_{_to_sig(bare)}"
        if value in int_vars or value in enum_vars:
            return f"{field}' = M.{_to_field(value)}"
        return None
    # int var: literal, copy, or var ± N
    if re.fullmatch(r"-?\d+", value):
        return f"{field}' = {value}"
    if value in int_vars:
        return f"{field}' = M.{_to_field(value)}"
    m = re.fullmatch(r"(\w+)\s*([+-])\s*(\d+)", value)
    if m and m.group(1) in int_vars:
        fn = "plus" if m.group(2) == "+" else "minus"
        return f"{field}' = {fn}[M.{_to_field(m.group(1))}, {m.group(3)}]"
    return None


def _referenced_vars(text, context):
    """Context var names mentioned (as words) in a predicate/expression string."""
    return {v for v in context if re.search(rf"\b{re.escape(v)}\b", text)
            or f"M.{_to_field(v)}" in text}


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

    # Generate transition predicates.
    # Guards and assigns in the translatable subset compile in; anything
    # outside it stays a comment and TAINTS its referenced vars + target
    # state — invariants touching tainted elements are skipped (a model
    # that ignores a guard would produce spurious counterexamples).
    lines.append("-- Transitions")
    transition_preds = []
    tainted_vars = set()    # context var names whose modeled value is unreliable
    tainted_states = set()  # state sig names reachable without their real guard
    for state_name, state_def in states.items():
        events = state_events(state_def)
        for event_name, trans in events.items():
            if isinstance(trans, dict):
                target = trans.get("target", state_name)
                pred_name = f"t_{_to_field(state_name)}_{_to_field(event_name)}"
                transition_preds.append(pred_name)
                lines.append(f"pred {pred_name} {{")
                lines.append(f"  M.current = {_to_sig(state_name)}")
                # Guard: compile if translatable, else comment + taint
                guard = trans.get("guard", {})
                if guard and guard.get("predicate"):
                    guard_expr = _translate_guard(guard["predicate"], enum_vars, int_vars)
                    if guard_expr is not None:
                        lines.append(f"  {guard_expr}  -- guard: {guard['predicate']}")
                    else:
                        lines.append(f"  -- guard NOT compiled (outside translatable subset): {guard['predicate']}")
                        tainted_vars |= _referenced_vars(guard["predicate"], context)
                        tainted_states.add(_to_sig(target))
                lines.append(f"  M.current' = {_to_sig(target)}")
                # Assigns: compiled updates for assigned vars, frame for the rest
                assigns = trans.get("assign", {}) or {}
                assigned = set()
                for var_name, value in assigns.items():
                    upd = _translate_assign(var_name, value, enum_vars, int_vars)
                    if upd is not None:
                        lines.append(f"  {upd}  -- assign: {var_name}: {value}")
                        assigned.add(var_name)
                    else:
                        lines.append(f"  -- assign NOT compiled (outside translatable subset): {var_name}: {value}")
                        tainted_vars.add(var_name)
                        # var keeps frame condition below — modeled as unchanged
                for var_name in list(enum_vars) + list(int_vars):
                    if var_name not in assigned:
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
    # An `alloy:` expression that touches a TAINTED var or state (one whose
    # guard/assign fell outside the translatable subset) is also skipped —
    # the model would produce spurious counterexamples for it.
    invariants = data.get("invariants", [])
    checkable = []
    skipped = []
    skipped_tainted = []  # (id, reason) — reported as SKIP-INVARIANT for check.py
    lines.append("-- Invariants")
    for inv in invariants:
        inv_id = _to_field(inv.get("id", "unknown"))
        predicate = inv.get("predicate", "true")
        description = inv.get("description", "")
        alloy_expr = inv.get("alloy")

        if not alloy_expr:
            skipped.append(inv.get("id", "unknown"))
            lines.append(f"-- SKIPPED {inv.get('id', 'unknown')}: prose predicate not mechanically")
            lines.append(f"-- translatable — add an `alloy:` expression to the spec to check it.")
            lines.append(f"-- Spec predicate: {predicate}")
            lines.append("")
            continue

        inv_vars = _referenced_vars(alloy_expr, context)
        bad_vars = sorted(inv_vars & tainted_vars)
        bad_states = sorted(s for s in tainted_states if re.search(rf"\b{s}\b", alloy_expr))
        if bad_vars or bad_states:
            parts = []
            if bad_vars:
                parts.append(f"var(s) {bad_vars} have uncompiled guard/assign")
            if bad_states:
                parts.append(f"state(s) {bad_states} reachable without their guard")
            reason = ("model unreliable for this expression: " + "; ".join(parts)
                      + " — outside the translatable subset; checking it would report spurious counterexamples")
            skipped_tainted.append((inv.get("id", "unknown"), reason))
            lines.append(f"-- SKIPPED {inv.get('id', 'unknown')}: {reason}")
            lines.append(f"-- Spec alloy: {alloy_expr}")
            lines.append("")
            continue

        checkable.append(inv_id)
        lines.append(f"-- {description}")
        lines.append(f"-- Spec predicate: {predicate}")
        lines.append(f"assert {inv_id} {{")
        lines.append(f"  {alloy_expr}")
        lines.append("}")
        lines.append("")

    # Check commands (only for checkable invariants)
    lines.append("-- Check commands")
    num_states = len(state_names)
    scope = max(4, num_states)
    steps = max(6, num_states * 2)
    for inv_id in checkable:
        lines.append(f"check {inv_id} for {scope} but {steps} steps")

    return "\n".join(lines), skipped, skipped_tainted


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
    alloy_source, skipped, skipped_tainted = generate_alloy(data)

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
    # Machine-readable skip lines — archwright-check parses these to mark
    # invariants skipped instead of expecting a verdict for them.
    for inv_id, reason in skipped_tainted:
        print(f"SKIP-INVARIANT: {inv_id}: {reason}")


if __name__ == "__main__":
    main()
