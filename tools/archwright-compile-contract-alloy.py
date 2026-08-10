#!/usr/bin/env python3
"""archwright-compile-contract-alloy: Compile a contract spec's structural_invariants to Alloy 6.

Usage:
  archwright-compile-contract-alloy <contract-spec.yaml> [-o output.als]

Generates an Alloy 6 model with:
  - Sigs from fields/sub_schemas (typed relations)
  - Assertions from structural_invariants[].alloy expressions
  - Check commands for each assertion

Contract Alloy models are STATIC (no var, no transitions) — they verify
structural properties of data schemas (e.g., acyclicity, reachability,
cardinality constraints) within a bounded scope.
"""

import sys
import yaml
from pathlib import Path


# Type → Alloy sig/field type mapping
_TYPE_MAP = {
    "string": "String_",  # abstract placeholder (not Alloy native)
    "int": "Int",
    "float": "Int",  # approximate — Alloy has no native float
    "bool": "Bool_",
    "enum": None,  # handled specially: generates an abstract sig per enum field
    "reference": None,  # handled specially: sig reference
    "list": None,  # set relation
    "map": None,  # ternary relation (simplified to set)
    "vector3": "Vec3_",
}


def load_spec(path):
    """Load a contract spec YAML file."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if data.get("kind") != "contract":
        print(f"Error: {path} is not a contract spec (kind: {data.get('kind')})")
        sys.exit(1)
    return data


def _to_sig(name):
    """Convert a slug/name to an Alloy sig name (PascalCase)."""
    parts = name.replace("-", "_").split("_")
    return "".join(p.capitalize() for p in parts)


def _to_field(name):
    """Convert a slug/name to an Alloy field name (camelCase)."""
    parts = name.replace("-", "_").split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _field_type(field_def, all_sigs):
    """Determine the Alloy type for a field definition.
    Returns (multiplicity, type_sig) tuple."""
    ftype = field_def.get("type", "string")
    nullable = field_def.get("nullable", False)
    mult = "lone" if nullable else "one"

    if ftype == "reference":
        # Reference to another sig — use element_type or description hint
        ref = field_def.get("element_type", field_def.get("description", ""))
        # Try to match to a known sig
        ref_sig = _to_sig(ref) if ref else "univ"
        if ref_sig in all_sigs:
            return mult, ref_sig
        return mult, "univ"

    if ftype == "list":
        elem = field_def.get("element_type", "string")
        elem_sig = _to_sig(elem) if elem in ("reference",) or _to_sig(elem) in all_sigs else _TYPE_MAP.get(elem, _to_sig(elem))
        if _to_sig(elem) in all_sigs:
            elem_sig = _to_sig(elem)
        return "set", elem_sig

    if ftype == "enum":
        return mult, None  # handled at field level

    mapped = _TYPE_MAP.get(ftype)
    if mapped is None:
        print(f"WARN: unknown field type '{ftype}' — mapping to 'univ' (universal set)", file=sys.stderr)
        mapped = "univ"
    return mult, mapped


def generate_alloy(data):
    """Generate an Alloy 6 model from a contract spec's schemas and structural_invariants."""
    lines = []
    spec_id = data["id"]
    lines.append(f"-- Auto-generated from contract spec: {spec_id}")
    lines.append(f"-- Static structural model — no transitions (data model verification).")
    lines.append("")

    # Collect all sig names from fields, sub_schemas, and events
    fields = data.get("fields", {})
    sub_schemas = data.get("sub_schemas", {})
    events = data.get("events", {})

    # All known sigs: the main entity + sub_schemas + any reference targets
    all_sigs = set()
    # Main entity sig name from spec id
    main_sig = _to_sig(spec_id)
    all_sigs.add(main_sig)
    for name in sub_schemas:
        all_sigs.add(_to_sig(name))
    # Scan fields for reference targets
    for fname, fdef in fields.items():
        if fdef.get("type") == "reference":
            ref = fdef.get("element_type", "")
            if ref:
                all_sigs.add(_to_sig(ref))
        elif fdef.get("type") == "list":
            elem = fdef.get("element_type", "")
            if elem and elem not in _TYPE_MAP:
                all_sigs.add(_to_sig(elem))

    # Generate placeholder sigs for types we reference but don't define
    builtin_placeholders = set()
    for sig in ("String_", "Bool_", "Vec3_"):
        builtin_placeholders.add(sig)

    # Emit abstract placeholder sigs for non-Alloy-native types we use
    used_placeholders = set()

    # Generate sub_schema sigs first (they're referenced by main sig fields)
    for schema_name, schema_def in sub_schemas.items():
        sig_name = _to_sig(schema_name)
        schema_fields = schema_def.get("fields", {})
        lines.append(f"sig {sig_name} {{")
        field_lines = []
        for fname, fdef in schema_fields.items():
            mult, ftype = _field_type(fdef, all_sigs)
            if ftype is None:
                # Enum: generate inline placeholder
                ftype = f"{sig_name}{_to_sig(fname)}Val"
                used_placeholders.add(ftype)
            if ftype in builtin_placeholders:
                used_placeholders.add(ftype)
            field_lines.append(f"  {_to_field(fname)}: {mult} {ftype}")
        lines.append(",\n".join(field_lines))
        lines.append("}")
        lines.append("")

    # Generate the main entity sig from top-level fields
    if fields:
        lines.append(f"sig {main_sig} {{")
        field_lines = []
        for fname, fdef in fields.items():
            mult, ftype = _field_type(fdef, all_sigs)
            if ftype is None:
                # Enum field: generate a value sig
                ftype = f"{main_sig}{_to_sig(fname)}Val"
                used_placeholders.add(ftype)
            if ftype in builtin_placeholders:
                used_placeholders.add(ftype)
            field_lines.append(f"  {_to_field(fname)}: {mult} {ftype}")
        lines.append(",\n".join(field_lines))
        lines.append("}")
        lines.append("")

    # Emit event payload sigs
    for event_name, event_def in events.items():
        sig_name = _to_sig(event_name)
        all_sigs.add(sig_name)
        payload = event_def.get("payload", {})
        if payload:
            lines.append(f"sig {sig_name} {{")
            field_lines = []
            for fname, fdef in payload.items():
                mult, ftype = _field_type(fdef, all_sigs)
                if ftype is None:
                    ftype = f"{sig_name}{_to_sig(fname)}Val"
                    used_placeholders.add(ftype)
                if ftype in builtin_placeholders:
                    used_placeholders.add(ftype)
                field_lines.append(f"  {_to_field(fname)}: {mult} {ftype}")
            lines.append(",\n".join(field_lines))
            lines.append("}")
            lines.append("")

    # Prepend placeholder sigs (insert after the header)
    placeholder_lines = []
    for ph in sorted(used_placeholders):
        placeholder_lines.append(f"sig {ph} {{}}")
    if placeholder_lines:
        placeholder_lines.append("")

    # Insert placeholders after the header comments
    header_end = 2  # after the two comment lines + blank
    lines = lines[:header_end] + placeholder_lines + lines[header_end:]

    # Generate assertions from structural_invariants
    invariants = data.get("structural_invariants", [])
    checkable = []
    lines.append("-- Structural invariants")
    for inv in invariants:
        inv_id = inv.get("id", "unknown")
        alloy_expr = inv.get("alloy")
        description = inv.get("description", "")
        predicate = inv.get("predicate", "")

        if not alloy_expr:
            lines.append(f"-- SKIPPED {inv_id}: no alloy expression")
            lines.append("")
            continue

        checkable.append(_to_field(inv_id))
        if description:
            lines.append(f"-- {description}")
        if predicate:
            lines.append(f"-- Predicate: {predicate}")
        lines.append(f"assert {_to_field(inv_id)} {{")
        lines.append(f"  {alloy_expr}")
        lines.append("}")
        lines.append("")

    # Check commands
    lines.append("-- Check commands")
    scope = 5  # default scope for structural models
    for assert_name in checkable:
        lines.append(f"check {assert_name} for {scope}")

    return "\n".join(lines), checkable


def main():
    if len(sys.argv) < 2:
        print("Usage: archwright-compile-contract-alloy <contract-spec.yaml> [-o output.als]")
        sys.exit(2)

    spec_path = sys.argv[1]
    output_path = None

    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    data = load_spec(spec_path)

    if not data.get("structural_invariants"):
        print(f"WARN: {spec_path} has no structural_invariants — nothing to compile")
        sys.exit(0)

    alloy_source, checkable = generate_alloy(data)

    if output_path:
        Path(output_path).write_text(alloy_source, encoding="utf-8")
        print(f"Generated: {output_path}")
    else:
        default_output = Path(spec_path).with_suffix(".als")
        default_output.write_text(alloy_source, encoding="utf-8")
        print(f"Generated: {default_output}")

    if not checkable:
        print("WARN: no checkable invariants (all missing `alloy:` expressions)")


if __name__ == "__main__":
    main()
